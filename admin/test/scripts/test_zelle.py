"""Synthetic tests for the Zelle (com.zellepay.zelle) module; the fixture is built by synthetic_zelle.py."""
import datetime
import fnmatch
import inspect
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import synthetic_zelle as fx  # noqa: E402  pylint: disable=wrong-import-position
from scripts.artifacts import zelle  # noqa: E402  pylint: disable=wrong-import-position

UTC = datetime.timezone.utc


class Context:
    def __init__(self, root, name):
        self.root = Path(root).resolve()
        patterns = zelle.__artifacts_v2__[name]['paths']
        self.files = [str(p) for p in self.root.rglob('*') if p.is_file()
                      and any(fnmatch.fnmatchcase('root/' + p.relative_to(self.root).as_posix(), pat)
                              for pat in patterns)]

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return Path(path).relative_to(self.root).as_posix()


def run_with_source(root, name):
    headers, rows, source = inspect.unwrap(getattr(zelle, name))(Context(root, name))
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    assert all(len(row) == len(names) for row in rows)
    return [dict(zip(names, row)) for row in rows], source


def run(root, name):
    return run_with_source(root, name)[0]


def build(case):
    tmp = tempfile.TemporaryDirectory()
    fx.CASES[case](tmp.name)
    return tmp


class ZelleTests(unittest.TestCase):
    def test_events_are_utc_and_skip_connection_plumbing(self):
        with build('synthetic') as root:
            rows = run(root, 'zelle_risk_sdk_events')
        first = rows[0]
        self.assertEqual(first['Event Time'], fx.FIRST_OPEN)
        self.assertEqual(first['Event Time'].tzinfo, UTC)
        types = {r['Event Type'] for r in rows}
        self.assertEqual(types, {'Plugin start', 'Started successfully', 'GuiReq received', 'Received msg',
                                 'Risk reason', 'Device state', 'Credentials', 'Error'})
        messages = ' '.join(r['Log Message'] for r in rows)
        for plumbing in ('socket', 'Found Dlg', 'Credential Enrolled', 'environment'):
            self.assertNotIn(plumbing, messages)
        status = [r for r in rows if r['Event'] == 'Connect']
        self.assertEqual([r['Status'] for r in status], ['MobileAuthStarted'])
        self.assertEqual(sum(r['Event'] == 'Application has started successfully' for r in rows), 3)

    def test_other_app_container_is_ignored(self):
        with build('synthetic') as root:
            for name in ('zelle_risk_sdk_events', 'zelle_risk_sdk_log_summary'):
                rows, source = run_with_source(root, name)
                self.assertTrue(rows)
                self.assertEqual(len(source.split('\n')), 1)
                self.assertIn(fx.CONTAINER, source)
                self.assertNotIn(fx.OTHER_CONTAINER, source)

    def test_backup_layout_without_metadata_plist(self):
        with build('synthetic_backup') as root:
            self.assertEqual(len(run(root, 'zelle_risk_sdk_log_summary')), 1)
            self.assertTrue(run(root, 'zelle_preferences'))

    def test_summary_counts_levels_and_hosts(self):
        with build('synthetic') as root:
            row = run(root, 'zelle_risk_sdk_log_summary')[0]
        self.assertEqual(row['Entries'], row['Debug Entries'] + row['Error Entries'])
        self.assertEqual(row['Error Entries'], 2)
        self.assertEqual(row['Start Entries'], 3)
        self.assertEqual(row['Hosts'], 'risk-east.example.test')
        self.assertLess(row['First Entry'], row['Last Entry'])

    def test_invalid_entry_time_does_not_stop_the_log(self):
        with build('synthetic_minimal') as root:
            log = next(Path(root).rglob('log1.txt'))
            text = log.read_text(encoding='utf-8')
            log.write_text(text + '+++ [13-45-2026 99:00:00] [ERROR] [HttpPlugin]\nbroken entry\n', encoding='utf-8')
            rows = run(root, 'zelle_risk_sdk_events')
        self.assertEqual(rows[-1]['Event Time'], '')
        self.assertEqual(rows[-1]['Event Type'], 'Error')

    def test_device_integrity_rows(self):
        with build('synthetic') as root:
            rows = run(root, 'zelle_device_integrity')
        results = {(r['Check'], r['Result']) for r in rows}
        self.assertIn(('Root status', 'NotRooted'), results)
        self.assertIn(('Malware status', 'NoMalwareDetected'), results)
        self.assertIn(('Root scan list', 'not found'), results)
        self.assertIn(('Signature files version', '1.2'), results)
        self.assertIn(('STEP 1', 'Initializing InAuth Sdk'), results)
        self.assertIn(('Root detection', 'started'), results)
        self.assertIn(('Malware detection', 'started'), results)
        self.assertFalse(any(r['Check'].startswith('SDK ') for r in rows))
        self.assertFalse(any('keyplane' in r['Message'] for r in rows))
        self.assertFalse(any('SYNTHETIC-NOT-A-KEY' in r['Message'] for r in rows))
        self.assertEqual({r['PID'] for r in rows}, {500, 777})
        self.assertTrue(all(isinstance(r['Log Time'], str) for r in rows))

    def test_preferences_expand_archived_super_properties_only(self):
        with build('synthetic') as root:
            rows = run(root, 'zelle_preferences')
        files = {r['Preference File'] for r in rows}
        self.assertEqual(files, {'com.zellepay.zelle.plist', 'Mixpanel.plist', 'Mixpanel.plist (superProperties)',
                                 'CLSUserDefaults.plist'})
        keys = {r['Key'] for r in rows}
        self.assertIn('Current App Screen', keys)
        self.assertNotIn('mixpanel-AppStore-timedEvents', keys)
        self.assertNotIn('mixpanel-AppStore-superProperties', keys)
        push = next(r for r in rows if r['Key'] == 'PushIDKey')
        self.assertEqual(push['Value'], bytes(range(32)).hex())

    def test_optional_preference_key_may_be_absent(self):
        with build('synthetic_minimal') as root:
            keys = {r['Key'] for r in run(root, 'zelle_preferences')}
        self.assertNotIn('SKPurchaseIntentUpdatesLastChecked', keys)

    def test_timed_events_are_unix_seconds_and_sorted(self):
        with build('synthetic') as root:
            rows = run(root, 'zelle_mixpanel_timed_events')
        self.assertEqual([r['Event Name'] for r in rows], ['login', 'Enable Touch ID', 'Add Profile Photo'])
        self.assertEqual(rows[0]['Start Time'], fx.FIRST_OPEN + datetime.timedelta(days=1))

    def test_unreadable_plists_do_not_raise(self):
        with build('synthetic') as root:
            for plist in Path(root).rglob('*.plist'):
                if plist.name != '.com.apple.mobile_container_manager.metadata.plist':
                    plist.write_bytes(b'not a plist')
            self.assertEqual(run(root, 'zelle_preferences'), [])
            self.assertEqual(run(root, 'zelle_mixpanel_timed_events'), [])

    def test_unreadable_container_metadata_is_not_a_match(self):
        with build('synthetic') as root:
            for meta in Path(root).rglob('.com.apple.mobile_container_manager.metadata.plist'):
                meta.write_bytes(b'garbage')
            self.assertEqual(run(root, 'zelle_risk_sdk_events'), [])


if __name__ == '__main__':
    unittest.main()
