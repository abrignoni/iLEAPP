"""Cross-core regression coverage for ALEAPP #1646. Author: @AlexisBrignoni, Codex.

Exercise real table/log decoding and real descriptor exhaustion in a child process.
The generated tables use literal Snappy blocks; no external database writer is needed.
"""
import errno
import io
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ccl_leveldb as leveldb  # pylint: disable=wrong-import-position
from scripts import ilapfuncs  # pylint: disable=wrong-import-position


def varint(value):
    result = bytearray()
    while value > 127:
        result.append((value & 127) | 128)
        value >>= 7
    return bytes(result + bytes([value]))


def blob(value):
    return varint(len(value)) + value


def block(entries):
    return (b''.join(b'\0' + varint(len(key)) + varint(len(value)) + key + value
                    for key, value in entries) + struct.pack('<II', 0, 1))


def table_bytes(entries, compressed=False):
    raw = block(entries)
    data = raw
    if compressed:
        # A single Snappy literal, including the extended-length form.
        size = len(raw) - 1
        length_bytes = size.to_bytes((size.bit_length() + 7) // 8, 'little')
        literal = bytes([size << 2]) if size < 60 else bytes([(59 + len(length_bytes)) << 2]) + length_bytes
        data = varint(len(raw)) + literal + raw
    index_offset = len(data) + 5
    index = block([(b'z', varint(0) + varint(len(data)))])
    footer = (b'\0\0' + varint(index_offset) + varint(len(index))).ljust(40, b'\0')
    return (data + bytes([int(compressed)]) + bytes(4) + index + bytes(5)
            + footer + struct.pack('<Q', leveldb.LdbFile.MAGIC))


def log_block(payload):
    # The existing reader does not validate the CRC.
    return struct.pack('<IHB', 0, len(payload), 1) + payload


def log_bytes(records, sequence=20):
    payload = struct.pack('<QI', sequence, len(records))
    for state, key, value in records:
        payload += bytes([state]) + blob(key)
        if state:
            payload += blob(value)
    return log_block(payload)


def internal_key(key, sequence, state=1):
    return key + struct.pack('<Q', (sequence << 8) | state)




class LevelDbLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.handles = []
        original_open = pathlib.Path.open

        def tracked_open(path, *args, **kwargs):
            handle = original_open(path, *args, **kwargs)
            self.handles.append(handle)
            return handle

        self.track = patch.object(pathlib.Path, 'open', tracked_open)

    def mixed_store(self):
        (self.root / '000001.ldb').write_bytes(table_bytes([
            (internal_key(b'a', 3), b'one'), (internal_key(b'b', 4, 0), b'')]))
        (self.root / '000002.sst').write_bytes(table_bytes([
            (internal_key(b'c', 5), b'two')], compressed=True))
        (self.root / '000003.log').write_bytes(log_bytes([
            (1, b'd', b'three'), (0, b'e', b'')]))
        manifest = log_block(b'\x07\x02\x01\x64' + blob(b'a') + blob(b'z'))
        (self.root / 'MANIFEST-000001').write_bytes(manifest)

    def assert_closed(self):
        self.assertTrue(self.handles)
        self.assertTrue(all(handle.closed for handle in self.handles))

    def test_records_metadata_order_reverse_and_repeat_passes(self):
        self.mixed_store()
        with self.track, leveldb.RawLevelDb(self.root) as db:
            records = list(db.iterate_records_raw())
            self.assertEqual(records, list(db.iterate_records_raw()))
            self.assertEqual(dict(db.manifest.file_to_level), {1: 2})
            self.assertEqual(len(list(db.manifest)), 1)
            self.assertEqual([r.origin_file.name for r in db.iterate_records_raw(reverse=True)],
                             ['000003.log', '000003.log', '000002.sst', '000001.ldb', '000001.ldb'])
        self.assert_closed()
        self.assertEqual([r.user_key for r in records], [b'a', b'b', b'c', b'd', b'e'])
        self.assertEqual([r.value for r in records], [b'one', b'', b'two', b'three', b''])
        self.assertEqual([r.seq for r in records], [3, 4, 5, 20, 21])
        self.assertEqual([r.state for r in records], [leveldb.KeyState.Live, leveldb.KeyState.Deleted,
                         leveldb.KeyState.Live, leveldb.KeyState.Live, leveldb.KeyState.Deleted])
        self.assertEqual([r.was_compressed for r in records], [False, False, True, False, False])
        self.assertEqual([r.offset for r in records], [0, 15, 0, 19, 28])
        self.assertEqual([r.file_type for r in records], [leveldb.FileType.Ldb] * 3 + [leveldb.FileType.Log] * 2)

    def test_context_close_releases_paused_and_interleaved_iterators(self):
        self.mixed_store()
        with self.track, leveldb.RawLevelDb(self.root) as db:
            first = db.iterate_records_raw()
            second = db.iterate_records_raw()
            self.assertEqual(next(first), next(second))
            self.assertEqual(next(first), next(second))
        self.assert_closed()
        first.close()
        second.close()
        db.close()
        with self.assertRaises(ValueError):
            next(db.iterate_records_raw())

    def test_generator_close_releases_only_its_reader(self):
        self.mixed_store()
        with self.track, leveldb.RawLevelDb(self.root) as db:
            iterator = db.iterate_records_raw()
            next(iterator)
            iterator.close()
            self.assertEqual(sum(not h.closed for h in self.handles), 1)  # manifest only
            self.assertEqual(len(list(db.iterate_records_raw())), 5)
        self.assert_closed()

    def test_backup_files_are_ignored_as_before(self):
        (self.root / '000001.ldb').write_bytes(table_bytes([(internal_key(b'a', 3), b'one')]))
        for name in ['000002.ldb.bak', '000003.log.bak', '000004.sst.bak', 'LOCK', 'CURRENT']:
            (self.root / name).write_bytes(b'not a table')
        with leveldb.RawLevelDb(self.root) as db:
            self.assertEqual([record.user_key for record in db.iterate_records_raw()], [b'a'])

    def test_invalid_table_constructor_releases_handle_while_exception_is_live(self):
        path = self.root / '000001.ldb'
        for content in [b'short', table_bytes([(internal_key(b'a', 1), b'b')])[:-8] + bytes(8)]:
            path.write_bytes(content)
            with self.track:
                try:
                    leveldb.LdbFile(path)
                except (OSError, ValueError):
                    self.assert_closed()
                else:
                    self.fail('invalid table accepted')

    def test_failed_manifest_and_database_construction_release_handles(self):
        self.mixed_store()
        (self.root / 'MANIFEST-000001').write_bytes(log_block(b'\x07\x02'))
        with self.track:
            try:
                leveldb.RawLevelDb(self.root)
            except (TypeError, ValueError):
                self.assert_closed()
            else:
                self.fail('invalid manifest accepted')

    def test_iteration_error_releases_current_file(self):
        (self.root / '000001.log').write_bytes(log_block(b'short batch'))
        with self.track, leveldb.RawLevelDb(self.root) as db:
            try:
                list(db.iterate_records_raw())
            except struct.error:
                self.assert_closed()
            else:
                self.fail('invalid log accepted')



    @unittest.skipIf(sys.platform == 'win32', 'RLIMIT_NOFILE is Unix-only')
    def test_real_descriptor_limit_in_child_process(self):
        result = subprocess.run([sys.executable, '-B', __file__, '--descriptor-stress'],
                                cwd=REPO_ROOT, capture_output=True, text=True, check=False, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('160 tables; two raw passes; exhausted-descriptor logging: PASS', result.stdout)


class LoggingLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.old_path = ilapfuncs.OutputParameters.screen_output_file_path
        self.addCleanup(setattr, ilapfuncs.OutputParameters, 'screen_output_file_path', self.old_path)
        self.log_temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.log_temp.cleanup)
        self.addCleanup(ilapfuncs.close_screen_log)
        ilapfuncs.OutputParameters.screen_output_file_path = str(pathlib.Path(self.log_temp.name) / 'log.html')

    def test_descriptor_errors_fall_back_to_console(self):
        for code in (errno.EMFILE, errno.ENFILE):
            output = io.StringIO()
            with patch('builtins.open', side_effect=OSError(code, 'descriptor exhaustion')), patch('sys.stdout', output):
                ilapfuncs.logfunc('original parser failure')
            self.assertIn('HTML log unavailable', output.getvalue())
            self.assertIn('original parser failure', output.getvalue())
            ilapfuncs.close_screen_log()

    def test_unrelated_logging_errors_remain_visible(self):
        with patch('builtins.open', side_effect=PermissionError(errno.EACCES, 'permission denied')):
            with self.assertRaises(PermissionError):
                ilapfuncs.logfunc('message')

    def test_normal_html_and_console_logging(self):
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / 'log.html'
            ilapfuncs.OutputParameters.screen_output_file_path = str(path)
            with patch('sys.stdout', new_callable=io.StringIO) as output:
                ilapfuncs.logfunc('normal message')
            self.assertEqual(path.read_text(), 'normal message<br>' + ilapfuncs.OutputParameters.nl)
            self.assertEqual(output.getvalue(), 'normal message\n')


def descriptor_stress():
    """Lower limits in this child only; fail if large stores still need N handles."""
    import resource  # pylint: disable=import-outside-toplevel
    with tempfile.TemporaryDirectory() as temp:
        root = pathlib.Path(temp)
        db_path = root / 'large_store.ldb'
        db_path.mkdir()
        key = internal_key(b'fixture:1700000000000000%1', 1)
        table = table_bytes([(key, b'preserved value')])
        for index in range(160):
            (db_path / f'{index:06d}.ldb').write_bytes(table)
        original = resource.getrlimit(resource.RLIMIT_NOFILE)
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, original[1]))
        handles = []
        try:
            with leveldb.RawLevelDb(db_path) as db:
                first = list(db.iterate_records_raw())
                assert len(first) == 160
                assert first == list(db.iterate_records_raw())
            # Exhaust descriptors for real, then exercise the actual logger.
            while True:
                try:
                    handles.append(open(root / 'held', 'ab'))  # pylint: disable=consider-using-with
                except OSError as exc:
                    assert exc.errno == errno.EMFILE
                    break
            ilapfuncs.OutputParameters.screen_output_file_path = str(root / 'log.html')
            ilapfuncs.logfunc('descriptor exhaustion remains recoverable')
        finally:
            for handle in handles:
                handle.close()
            resource.setrlimit(resource.RLIMIT_NOFILE, original)
            ilapfuncs.close_screen_log()
    print('160 tables; two raw passes; exhausted-descriptor logging: PASS')


if __name__ == '__main__':
    if sys.argv[1:] == ['--descriptor-stress']:
        descriptor_stress()
    else:
        unittest.main()
