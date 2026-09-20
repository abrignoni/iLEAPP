"""Cover PowerLog reading its databases out of a sysdiagnose that is still packed.

A full file system extraction can hold sysdiagnoses as sysdiagnose_*.tar.gz under
DiagnosticLogs/sysdiagnose, and each one carries the telemetry databases as they stood
when it was taken (logs/powerlogs/*.PLSQL, .EPSQL and .BGSQL). SQLite needs a file on
disk and get_sysdiagnose_files() yields a stream, so the module copies each database out
once, into the session temp directory the rotated .PLSQL.gz archives already use, and
every artifact in the module reads that copy.

Every test here points the system temp directory at one it owns: the first copy made in
a run also sweeps the temp directory for abandoned copies from earlier runs.
"""
import contextlib
import io
import os
import pathlib
import sqlite3
import sys
import tarfile
import tempfile
import unittest
import zlib
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import powerlog  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from leapp_functions.app.artifact_result import ArtifactResult  # pylint: disable=wrong-import-position

SD = 'sysdiagnose_2026.01.02_03-04-05-0500_iPhone-OS_iPhone_23A000'
PLSQL = f'{SD}/logs/powerlogs/powerlog_2026-01-02_03-05_ABCD1234.PLSQL'
EPSQL = f'{SD}/logs/powerlogs/log_2026-01-02_03-05_EFGH5678.EPSQL'
BGSQL = f'{SD}/logs/powerlogs/log_2026-01-02_03-05_IJKL9012.BGSQL'


class _Context:
    """The two Context methods the PowerLog source listing calls."""

    def __init__(self, files):
        self._files = files

    def get_files_found(self):
        return self._files

    @staticmethod
    def get_relative_path(full_path):
        return Context.get_relative_path(full_path)

    def create_artifact_result(self, headers=None, source_path=None, **_kwargs):
        # No LAVA run is active here, so the result keeps its rows in memory and reads
        # back like a list.
        return ArtifactResult(headers=headers, source_path=source_path,
                              source_path_formatter=self.get_relative_path)


def _make_archive(directory, members, name=f'{SD}.tar.gz'):
    """Write a gzipped tar laid out like a sysdiagnose; members maps inner path -> bytes."""
    path = os.path.join(directory, name)
    with tarfile.open(path, 'w:gz') as tar:
        for inner, data in members.items():
            info = tarfile.TarInfo(inner)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return path


def _torch_db(directory):
    """A real PowerLog database: two torch rows and one time-offset entry."""
    path = os.path.join(directory, 'build.PLSQL')
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE PLCameraAgent_EventForward_Torch '
                '(timestamp REAL, BundleId TEXT, Level INTEGER)')
    con.execute('CREATE TABLE PLStorageOperator_EventForward_TimeOffset '
                '(timestamp REAL, system REAL)')
    con.executemany('INSERT INTO PLCameraAgent_EventForward_Torch VALUES (?, ?, ?)',
                    [(1767340000.0, 'com.example.torch', 0), (1767343600.0, None, 1)])
    con.execute('INSERT INTO PLStorageOperator_EventForward_TimeOffset VALUES (?, ?)',
                (1767330000.0, 5.0))
    con.commit()
    con.close()
    with open(path, 'rb') as handle:
        data = handle.read()
    os.remove(path)
    return data


class PackedSysdiagnoseSourceTests(unittest.TestCase):
    """What the module finds in a packed sysdiagnose, and where it puts it."""

    def setUp(self):
        self.system_temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.system_temp.cleanup)
        patcher = mock.patch.object(powerlog.tempfile, 'gettempdir',
                                    return_value=self.system_temp.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        inputs = tempfile.TemporaryDirectory()
        self.addCleanup(inputs.cleanup)
        self.inputs = inputs.name
        powerlog._remove_gz_temp()  # pylint: disable=protected-access

    def tearDown(self):
        powerlog._remove_gz_temp()  # pylint: disable=protected-access

    def test_each_family_is_copied_out_with_its_archive_and_member_as_the_source(self):
        archive = _make_archive(self.inputs, {
            PLSQL: b'plsql bytes',
            EPSQL: b'epsql bytes',
            BGSQL: b'bgsql bytes',
            f'{SD}/logs/other/powerlog_elsewhere.PLSQL': b'outside logs/powerlogs',
            f'{SD}/logs/powerlogs/notes.txt': b'not a database',
        })
        for extension, member, data in (('.PLSQL', PLSQL, b'plsql bytes'),
                                        ('.EPSQL', EPSQL, b'epsql bytes'),
                                        ('.BGSQL', BGSQL, b'bgsql bytes')):
            sources = powerlog._powerlog_sources(  # pylint: disable=protected-access
                _Context([archive]), extension)
            self.assertEqual(len(sources), 1, f'{extension}: {sources}')
            copy_path, evidence_path = sources[0]
            self.assertEqual(evidence_path, f'{archive} >> {member}')
            with open(copy_path, 'rb') as handle:
                self.assertEqual(handle.read(), data)

    def test_the_archive_is_read_once_for_every_artifact(self):
        archive = _make_archive(self.inputs, {PLSQL: b'plsql', EPSQL: b'epsql'})
        real_helper = powerlog.get_sysdiagnose_files
        with mock.patch.object(powerlog, 'get_sysdiagnose_files',
                               side_effect=real_helper) as helper:
            for extension in ('.PLSQL', '.EPSQL', '.BGSQL', '.PLSQL'):
                powerlog._powerlog_sources(  # pylint: disable=protected-access
                    _Context([archive]), extension)
        self.assertEqual(helper.call_count, 1,
                         'the archive was read again by a later artifact')

    def test_copies_live_in_the_session_dir_and_go_when_the_run_ends(self):
        archive = _make_archive(self.inputs, {PLSQL: b'plsql'})
        copy_path, _ = powerlog._powerlog_sources(  # pylint: disable=protected-access
            _Context([archive]))[0]
        session_dir = powerlog._GZ_TEMP['dir']  # pylint: disable=protected-access
        self.assertTrue(copy_path.startswith(session_dir))
        self.assertTrue(session_dir.startswith(self.system_temp.name))

        powerlog._remove_gz_temp()  # pylint: disable=protected-access

        self.assertFalse(os.path.exists(copy_path), 'the extracted copy survived the run')
        self.assertEqual(powerlog._SYSDIAG_CACHE, {})  # pylint: disable=protected-access

    def test_a_member_that_fails_part_way_is_not_queried(self):
        archive = os.path.join(self.inputs, f'{SD}.tar.gz')

        class _Breaks(io.RawIOBase):
            """Hands over the first chunk, then fails like a corrupt gzip stream."""

            def __init__(self):
                super().__init__()
                self.calls = 0

            def readable(self):
                return True

            def readinto(self, buffer):
                self.calls += 1
                if self.calls > 1:
                    raise zlib.error('Error -3 while decompressing data')
                buffer[:4] = b'SQLi'
                return 4

        def helper(*_args, **_kwargs):
            yield _Breaks(), f'{archive} >> {PLSQL}'

        with mock.patch.object(powerlog, 'get_sysdiagnose_files', side_effect=helper), \
                mock.patch.object(powerlog, 'logfunc') as log:
            sources = powerlog._powerlog_sources(  # pylint: disable=protected-access
                _Context([archive]))

        self.assertEqual(sources, [])
        left = [name for _, _, names in os.walk(self.system_temp.name) for name in names]
        self.assertEqual(left, [], 'a partial copy was left on disk')
        self.assertIn(archive, log.call_args[0][0])

    def test_a_truncated_archive_yields_nothing_and_does_not_stop_the_run(self):
        archive = _make_archive(self.inputs, {PLSQL: os.urandom(256 * 1024)})
        with open(archive, 'r+b') as handle:
            handle.truncate(os.path.getsize(archive) // 2)
        with contextlib.redirect_stdout(io.StringIO()):
            sources = powerlog._powerlog_sources(  # pylint: disable=protected-access
                _Context([archive]))
        self.assertEqual(sources, [])

    def test_rows_report_the_archive_and_member_relative_to_the_extraction(self):
        archive = _make_archive(self.inputs, {PLSQL: _torch_db(self.inputs)})
        saved = Context._data_folder  # pylint: disable=protected-access
        Context.set_data_folder(self.inputs)
        self.addCleanup(Context.set_data_folder, saved)

        headers = (('Timestamp', 'datetime'), 'Bundle ID', 'Level (as stored)',
                   'Time Offset (seconds)', 'Source File')
        result, _ = powerlog._parse_powerlog_table(  # pylint: disable=protected-access
            _Context([archive]), headers, 'PLCameraAgent_EventForward_Torch',
            ('timestamp', 'BundleId', 'Level'),
            lambda ts, offset, row, rel: (ts, row[1], row[2], offset, rel))
        rows = list(result)

        # The helper hands rows to LAVA as it reads them. If it ever goes back to
        # collecting them into a list, every one of these tables is held in memory twice.
        self.assertIsInstance(result, ArtifactResult)
        self.assertEqual(len(rows), 2)
        self.assertEqual({row[4] for row in rows}, {f'{SD}.tar.gz >> {PLSQL}'})
        self.assertEqual([row[3] for row in rows], [5, 5])
        self.assertEqual(rows[0][0].timestamp(), 1767340005.0)


if __name__ == '__main__':
    unittest.main()
