"""Retain shutdown client occurrences without inventing a SIGTERM time."""
# Exercise the shared parser to assert both returned projections together.
# pylint: disable=protected-access
import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from scripts.artifacts import sysShutdown as mod


class FileContext:
    def __init__(self, root, files):
        self.root, self.files = str(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(path).replace(self.root + '/', '')


def client(pid, path='/usr/bin/tool'):
    return f'remaining client pid: {pid} ({path})\n'


class ShutdownEOFTests(unittest.TestCase):
    def run_logs(self, payloads, package=False):
        with tempfile.TemporaryDirectory() as root:
            files = []
            if package:
                p = Path(root) / 'sysdiagnose_fixture.tar.gz'
                with tarfile.open(p, 'w:gz') as archive:
                    for name, data in payloads:
                        member = tarfile.TarInfo('system_logs.logarchive/Extra/' + name)
                        member.size = len(data)
                        archive.addfile(member, io.BytesIO(data))
                files.append(str(p))
            else:
                for name, data in payloads:
                    p = Path(root) / name
                    p.write_bytes(data)
                    files.append(str(p))
            hashes = {}
            for file in files:
                Path(file).chmod(0o444)
                hashes[file] = hashlib.sha256(Path(file).read_bytes()).hexdigest()
            result = mod._parse_shutdown_logs(FileContext(root, files))
            self.assertEqual(hashes, {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files})
            return result

    def test_complete_and_trailing_counters_delay_and_indicator(self):
        text = 'After 2 s, these clients are still here\n' + client(1) + client(2)
        text += 'SIGTERM: [1700000000]\n' + client(3)
        text += 'After 4.5 s, these clients are still here\n' + client(4, '/private/var/db/tail')
        rows, reboots, sources = self.run_logs([('shutdown.log', text.rstrip().encode())])
        self.assertEqual([r[1] for r in rows], [1, 2, 3, 4])
        self.assertTrue(all(r[0] == reboots[0][0] for r in rows[:2]))
        self.assertEqual(rows[2], (None, 3, '3', '/usr/bin/tool', None, '', 'shutdown.log'))
        self.assertEqual(rows[3], (None, 4, '4', '/private/var/db/tail', 4.5, 'path in /private/var/db/', 'shutdown.log'))
        self.assertEqual(reboots[0][1:], (1, 1, 2.0, 'shutdown.log'))
        self.assertEqual(sources, 'shutdown.log')

    def test_no_sigterm_and_global_dedupe_reset(self):
        data = (client(7) + client(7)).encode()
        rows, reboots, sources = self.run_logs([('shutdown.log', data), ('shutdown.0.log', data)])
        self.assertEqual([(r[0], r[1], r[2]) for r in rows], [(None, 1, '7'), (None, 2, '7')])
        self.assertEqual(reboots, [])
        self.assertTrue(all(r[-1] == 'shutdown.log' for r in rows))
        self.assertEqual(sources, 'shutdown.log\nshutdown.0.log')

    def test_later_file_sigterm_does_not_date_earlier_tail(self):
        # The earlier tail (pid 7) has no dated twin in the later file, so it stays undated.
        rows, reboots, _ = self.run_logs([('shutdown.log', client(7).encode()), ('shutdown.0.log', (client(8) + 'SIGTERM: [1700000000]\nAfter 3 s, these clients are still here\n').encode())])
        self.assertEqual([(r[0], r[2], r[-1]) for r in rows], [(None, '7', 'shutdown.log'), (reboots[0][0], '8', 'shutdown.0.log')])
        self.assertEqual(len(reboots), 1)

    def test_later_file_sigterm_twin_drops_earlier_tail_without_dating_it(self):
        # Same entry number, PID, path and delay: the undated copy is dropped, not dated.
        rows, reboots, _ = self.run_logs([('shutdown.log', client(7).encode()), ('shutdown.0.log', (client(7) + 'SIGTERM: [1700000000]\nAfter 3 s, these clients are still here\n').encode())])
        self.assertEqual(rows, [(reboots[0][0], 1, '7', '/usr/bin/tool', None, '', 'shutdown.0.log')])
        self.assertEqual(len(reboots), 1)

    def prefix_logs(self):
        live = 'After 2 s, these clients are still here\n' + client(1) + 'SIGTERM: [1700000000]\n'
        live += 'After 2 s, these clients are still here\n' + client(2) + client(3, '/private/var/tmp/x')
        packed = live
        live += 'SIGTERM: [1700000100]\n'
        return live.encode(), packed.encode()

    def test_undated_copy_read_second_is_dropped_by_dated_twin(self):
        live, packed = self.prefix_logs()
        rows, reboots, _ = self.run_logs([('shutdown.log', live), ('shutdown.0.log', packed)])
        self.assertEqual([(r[1], r[2], r[-1]) for r in rows], [(1, '1', 'shutdown.log'), (2, '2', 'shutdown.log'), (3, '3', 'shutdown.log')])
        self.assertTrue(all(r[0] is not None for r in rows))
        self.assertEqual(len(reboots), 2)

    def test_undated_copy_read_first_is_dropped_by_dated_twin(self):
        live, packed = self.prefix_logs()
        rows, reboots, _ = self.run_logs([('shutdown.0.log', packed), ('shutdown.log', live)])
        self.assertEqual([(r[1], r[2], r[-1]) for r in rows], [(1, '1', 'shutdown.0.log'), (2, '2', 'shutdown.log'), (3, '3', 'shutdown.log')])
        self.assertEqual([r[0] for r in rows[1:]], [reboots[1][0]] * 2)
        self.assertEqual(len(reboots), 2)

    def test_undated_row_without_dated_twin_is_kept_undated(self):
        live, packed = self.prefix_logs()
        packed += client(9).encode()  # a client line the live copy does not hold at that entry number
        for order in ([('shutdown.log', live), ('shutdown.0.log', packed)], [('shutdown.0.log', packed), ('shutdown.log', live)]):
            rows, _, _ = self.run_logs(order)
            self.assertEqual([(r[0], r[1], r[2], r[-1]) for r in rows if r[0] is None], [(None, 4, '9', 'shutdown.0.log')])
            self.assertEqual(len(rows), 4)

    def test_twin_key_includes_delay(self):
        # A dated row with another delay is not a twin, so the undated row is kept.
        packed = client(5).encode()
        live = ('After 3 s, these clients are still here\n' + client(5) + 'SIGTERM: [1700000000]\n').encode()
        rows, _, _ = self.run_logs([('shutdown.log', live), ('shutdown.0.log', packed)])
        self.assertEqual([(r[0] is None, r[4]) for r in rows], [(False, 3.0), (True, None)])

    def test_tar_actual_helper_and_appledouble(self):
        rows, reboots, sources = self.run_logs([('shutdown.log', client(1).encode()), ('shutdown.0.log', (client(2) + 'SIGTERM: [1700000000]\n').encode()), ('._shutdown.log', client(99).encode())], package=True)
        self.assertEqual([r[2] for r in rows], ['1', '2'])
        self.assertIsNone(rows[0][0])
        self.assertEqual(len(reboots), 1)
        self.assertIn('sysdiagnose_fixture.tar.gz >> system_logs.logarchive/Extra/shutdown.log', sources)
        self.assertNotIn('._shutdown', sources)

    def test_empty_and_read_failure_are_not_trailing_occurrences(self):
        rows, reboots, sources = self.run_logs([('shutdown.log', b'After 2 s, these clients are still here\n')])
        self.assertEqual((rows, reboots, sources), ([], [], 'shutdown.log'))
        bad = unittest.mock.Mock()
        bad.read.side_effect = OSError('fixture read failure')
        streams = [(bad, 'bad/shutdown.log'), (io.BytesIO(client(8).encode()), 'good/shutdown.log')]
        with patch.object(mod, 'get_sysdiagnose_files', return_value=iter(streams)), patch.object(mod, 'logfunc') as log:
            rows, reboots, sources = mod._parse_shutdown_logs(FileContext('/input', []))
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0][0])
        self.assertEqual(sources, 'good/shutdown.log')
        self.assertEqual(reboots, [])
        log.assert_called_once()


if __name__ == '__main__':
    unittest.main()
