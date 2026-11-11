"""AnyDesk iOS artifacts: container scoping, withheld secrets, unmatched lines, absent files."""
import plistlib
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position
from scripts.artifacts import anydesk

APP = 'Containers/Data/Application/'
SUPPORT = 'Library/Application Support/'
LINE = 'Incoming    2024-01-05, 10:15    User    900000001    900000001\r\n'


def write(root, rel, data):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode())
    return str(path)


def run(func, files):
    context = SimpleNamespace(get_files_found=lambda: files,
                              get_relative_path=lambda p: str(p).replace(chr(92), '/'))
    return func.__wrapped__(context)


class TestAnyDesk(unittest.TestCase):
    def test_history_lines_and_unmatched_line(self):
        with tempfile.TemporaryDirectory() as d:
            trace = write(d, f'{APP}U1/{SUPPORT}.anydesk/connection_trace.txt',
                          'Incoming    2024-01-05, 10:15    User                              900000001    900000001\r\n'
                          'Incoming    2024-01-06, 10:15    Passwd    some name    900000002    900000003\r\n'
                          'garbage\r\n\r\n')
            _, rows, source = run(anydesk.anydeskConnectionHistory, [trace])
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0][:7], ('2024-01-05 10:15', 'Incoming', 'User', '', '900000001', '900000001', ''))
        self.assertEqual(rows[1][2:6], ('Passwd', 'some name', '900000002', '900000003'))
        self.assertEqual(rows[2][:8], ('', '', '', '', '', '', '', 'garbage'))
        self.assertTrue(source)

    def test_lines_that_would_split_inside_a_token_go_to_raw_line(self):
        no_mode = 'Incoming    2024-01-05, 10:15    900000001    900000001'
        digit_mode = 'Incoming    2024-01-05, 10:15    User9    900000001'
        with tempfile.TemporaryDirectory() as d:
            trace = write(d, f'{APP}U1/{SUPPORT}.anydesk/connection_trace.txt',
                          f'{no_mode}\r\n{digit_mode}\r\n{LINE}')
            _, rows, _ = run(anydesk.anydeskConnectionHistory, [trace])
        self.assertEqual(len(rows), 3)
        for row, raw in zip(rows[:2], (no_mode, digit_mode)):
            self.assertEqual(row[:7], ('',) * 7)
            self.assertEqual(row[7], raw)
        self.assertEqual(rows[2][:3], ('2024-01-05 10:15', 'Incoming', 'User'))

    def test_preferences_list_is_per_container(self):
        with tempfile.TemporaryDirectory() as d:
            files = []
            for uuid, listed in (('U1', [900000001]), ('U2', [])):
                files.append(write(d, f'{APP}{uuid}/{SUPPORT}.anydesk/connection_trace.txt', LINE))
                files.append(write(d, f'{APP}{uuid}/Library/Preferences/com.anydesk.AnyDesk.plist',
                                   plistlib.dumps({'user.preference.already.connected.users': listed})))
            _, rows, _ = run(anydesk.anydeskConnectionHistory, files)
        self.assertEqual(sorted(r[6] for r in rows), ['No', 'Yes'])

    def test_source_file_separates_containers(self):
        with tempfile.TemporaryDirectory() as d:
            files = [write(d, f'{APP}{uuid}/{SUPPORT}.anydesk/connection_trace.txt', LINE) for uuid in ('U1', 'U2')]
            headers, rows, _ = run(anydesk.anydeskConnectionHistory, files)
        self.assertEqual(headers[0], 'Date and Time')
        self.assertEqual(headers[-1], 'Source File')
        self.assertEqual(len({r[-1] for r in rows}), 2)
        self.assertTrue(rows[0][-1].endswith('U1/Library/Application Support/.anydesk/connection_trace.txt'))

    def test_unreadable_plist_or_non_list_key_leaves_cross_check_blank(self):
        for plist_bytes in (b'not a plist', plistlib.dumps({'user.preference.already.connected.users': 'x'})):
            with tempfile.TemporaryDirectory() as d:
                files = [write(d, f'{APP}U1/{SUPPORT}.anydesk/connection_trace.txt', LINE),
                         write(d, f'{APP}U1/Library/Preferences/com.anydesk.AnyDesk.plist', plist_bytes)]
                _, rows, _ = run(anydesk.anydeskConnectionHistory, files)
            self.assertEqual(rows[0][6], '')

    def test_no_plist_leaves_cross_check_blank(self):
        with tempfile.TemporaryDirectory() as d:
            trace = write(d, f'{APP}U1/{SUPPORT}.anydesk/connection_trace.txt', LINE)
            _, rows, _ = run(anydesk.anydeskConnectionHistory, [trace])
        self.assertEqual(rows[0][6], '')

    def test_secrets_withheld_and_foreign_file_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            service = write(d, f'{APP}U1/{SUPPORT}.anydesk/service.conf',
                            'ad.anynet.pkey=SECRET\nad.anynet.cert=SECRET\nad.telemetry.last_cid=123\n')
            system = write(d, f'{APP}U1/{SUPPORT}.anydesk/system.conf',
                           'ad.anynet.id=900000100\nad.anynet.token_x=SECRET\nempty=\n')
            foreign = write(d, f'{APP}U2/{SUPPORT}.other/system.conf', 'ad.anynet.id=1\n')
            _, rows, _ = run(anydesk.anydeskSettings, [service, system, foreign])
        self.assertNotIn('SECRET', repr(rows))
        self.assertEqual(len(rows), 6)
        self.assertIn(('system.conf', 'ad.anynet.id', '900000100'), [r[:3] for r in rows])
        self.assertIn(('system.conf', 'empty', ''), [r[:3] for r in rows])

    def test_settings_skip_comments_hex_bytes_and_name_source(self):
        with tempfile.TemporaryDirectory() as d:
            user = write(d, f'{APP}U1/{SUPPORT}.anydesk/user.conf', '# comment=1\n  # indented=2\nad.ui.lang=en\n')
            plist = write(d, f'{APP}U1/Library/Preferences/com.anydesk.AnyDesk.plist',
                          plistlib.dumps({'some.blob': b'\x01\xff'}))
            headers, rows, _ = run(anydesk.anydeskSettings, [user, plist])
        self.assertEqual(headers[-1], 'Source File')
        self.assertEqual([r[:3] for r in rows],
                         [('user.conf', 'ad.ui.lang', 'en'), ('com.anydesk.AnyDesk.plist', 'some.blob', '01ff')])
        self.assertTrue(rows[0][3].endswith('user.conf') and rows[1][3].endswith('.plist'))

    def test_startup_banner_after_unbannered_block_and_uncounted_lines(self):
        with tempfile.TemporaryDirectory() as d:
            trace = write(
                d, f'{APP}U1/{SUPPORT}anydesk.trace',
                'no level or stamp here\n'
                '   info 2024-01-01 00:00:00.000         ad   main   1 2                 main - * Version 6.0.0 (pre)\n'
                '   info 2024-01-01 00:00:01.000         ad   main   1 2                 main - x\n')
            _, rows, _ = run(anydesk.anydeskTraceStartups, [trace])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1:6], ('No', '6.0.0', 'pre', '', 2))

    def test_startup_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            trace = write(
                d, f'{APP}U1/{SUPPORT}anydesk.trace',
                '   info 2024-01-01 00:00:00.000         ad    svc   1 2   3            x - early\n'
                ' * * *\n'
                '   info 2024-01-02 00:00:00.000         ad   main   1 2                 main - * AnyDesk iOS Startup *\n'
                '   info 2024-01-02 00:00:00.001         ad   main   1 2                 main - * Version 7.1.2 (rel abc)\n'
                '   info 2024-01-02 00:00:00.002         ad   main   1 2                 main - * Build deadbeef\n'
                '   info 2024-01-02 00:00:01.000         ad    svc   1 2   3            anynet.connection_mgr - Main relay connection established.\n'
                'warning 2024-01-02 00:00:02.000         ad    svc   1 2   3            anynet.connection_mgr - Main relay connection failed (result_quit).\n')
            _, rows, _ = run(anydesk.anydeskTraceStartups, [trace])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][:3], ('2024-01-01 00:00:00.000', 'No', ''))
        self.assertEqual(rows[1][1:5], ('Yes', '7.1.2', 'rel abc', 'deadbeef'))
        self.assertEqual(rows[1][5:10], (5, 1, 1, 1, 0))

    def test_unreadable_plist_and_empty_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            bad = write(d, f'{APP}U1/Library/Preferences/com.anydesk.AnyDesk.plist', b'not a plist')
            _, rows, source = run(anydesk.anydeskSettings, [bad])
            self.assertEqual(rows, [])
            self.assertTrue(source)
        for func in (anydesk.anydeskConnectionHistory, anydesk.anydeskSettings, anydesk.anydeskTraceStartups):
            self.assertEqual(run(func, [])[1:], ([], ''))


if __name__ == '__main__':
    unittest.main()
