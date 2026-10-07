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
        self.assertEqual(sources, 'shutdown.log, shutdown.0.log')

    def test_later_file_sigterm_does_not_date_earlier_tail(self):
        rows, reboots, _ = self.run_logs([('shutdown.log', client(7).encode()), ('shutdown.0.log', (client(7) + 'SIGTERM: [1700000000]\nAfter 3 s, these clients are still here\n').encode())])
        self.assertIsNone(rows[0][0])
        self.assertEqual(rows[1][0], reboots[0][0])
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(reboots), 1)

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
