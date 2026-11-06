"""Synthetic tests for the Zelle (com.zellepay.zelle) module; the fixture is built by synthetic_zelle.py."""
import datetime
import fnmatch
import inspect
import sqlite3
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


def run(root, name):
    headers, rows, _ = inspect.unwrap(getattr(zelle, name))(Context(root, name))
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    assert all(len(row) == len(names) for row in rows)
    return [dict(zip(names, row)) for row in rows]


def build(case):
    tmp = tempfile.TemporaryDirectory()
    fx.CASES[case](tmp.name)
    return tmp


class ZelleTests(unittest.TestCase):
    def test_sdk_events_are_utc_and_skip_connection_plumbing(self):
        with build('synthetic') as root:
            rows = run(root, 'zelle_risk_sdk_events')
        first = rows[0]
        self.assertEqual(first['Event Time'], fx.FIRST_OPEN)
        self.assertEqual(first['Event Time'].tzinfo, UTC)
        types = {r['Event Type'] for r in rows}
        self.assertEqual(types, {'SDK start', 'Request to SDK', 'Server response', 'Risk reason', 'Device state',
                                 'Credentials', 'Error'})
        messages = ' '.join(r['Log Message'] for r in rows)
        for plumbing in ('socket', 'Found Dlg', 'Credential Enrolled', 'environment'):
            self.assertNotIn(plumbing, messages)
        status = [r for r in rows if r['Event'] == 'Connect']
        self.assertEqual([r['Status'] for r in status], ['MobileAuthStarted'])
        self.assertEqual(sum(r['Event'] == 'Application has started successfully' for r in rows), 3)

    def test_other_app_container_is_ignored(self):
        with build('synthetic') as root:
            for name in ('zelle_risk_sdk_events', 'zelle_risk_sdk_log_summary'):
                sources = {r['Source File'] for r in run(root, name)}
                self.assertEqual(len(sources), 1)
                self.assertIn(fx.CONTAINER, next(iter(sources)))
                self.assertNotIn(fx.OTHER_CONTAINER, next(iter(sources)))

    def test_backup_layout_without_metadata_plist(self):
        with build('synthetic_backup') as root:
            self.assertEqual(len(run(root, 'zelle_risk_sdk_log_summary')), 1)
            self.assertTrue(run(root, 'zelle_preferences'))

    def test_summary_counts_levels_and_servers(self):
        with build('synthetic') as root:
            row = run(root, 'zelle_risk_sdk_log_summary')[0]
        self.assertEqual(row['Entries'], row['Debug Entries'] + row['Error Entries'])
        self.assertEqual(row['Error Entries'], 2)
        self.assertEqual(row['SDK Starts'], 3)
        self.assertEqual(row['Servers'], 'risk-east.example.test')
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
        self.assertFalse(any('keyplane' in r['Message'] for r in rows))
        self.assertFalse(any('SYNTHETIC-NOT-A-KEY' in r['Message'] for r in rows))
        self.assertEqual({r['PID'] for r in rows}, {500, 777})
        self.assertTrue(all(isinstance(r['Local Time'], str) for r in rows))

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

    def test_firebase_rows_and_cross_values(self):
        with build('synthetic') as root:
            rows = run(root, 'zelle_firebase_analytics')
        by = {(r['Record Type'], r['Name']): r for r in rows}
        self.assertEqual(by[('Event', '_f')]['Time'], fx.FIRST_OPEN)
        self.assertEqual(by[('Measurement plist', 'first_open_timestamp_ms')]['Time'], fx.FIRST_OPEN)
        self.assertEqual(by[('Measurement plist', 'last_engagement_end')]['Time'],
                         max(r['Time'] for r in rows if r['Record Type'] == 'Event'))
        self.assertEqual(by[('Event', '_s')]['Count'], 3)
        self.assertEqual(by[('User Property', '_sno')]['Value'], 3)
        # a zero time is shown as blank with the raw value kept
        failed = by[('Measurement plist', 'last_failed_upload')]
        self.assertEqual((failed['Time'], failed['Value']), ('', 0.0))

    def test_firebase_missing_user_attributes_table(self):
        with build('synthetic_minimal') as root:
            rows = run(root, 'zelle_firebase_analytics')
        self.assertFalse(any(r['Record Type'] == 'User Property' for r in rows))
        self.assertTrue(any(r['Record Type'] == 'Event' for r in rows))

    def test_firebase_database_without_tables(self):
        with build('synthetic_minimal') as root:
            db = next(Path(root).rglob('google-app-measurement.sql'))
            con = sqlite3.connect(db)
            con.execute('DROP TABLE events')
            con.commit()
            con.close()
            rows = run(root, 'zelle_firebase_analytics')
        self.assertEqual({r['Record Type'] for r in rows}, {'Measurement plist'})

    def test_unreadable_plists_do_not_raise(self):
        with build('synthetic') as root:
            for plist in Path(root).rglob('*.plist'):
                if plist.name != '.com.apple.mobile_container_manager.metadata.plist':
                    plist.write_bytes(b'not a plist')
            self.assertEqual(run(root, 'zelle_preferences'), [])
            self.assertEqual(run(root, 'zelle_mixpanel_timed_events'), [])
            self.assertTrue(run(root, 'zelle_firebase_analytics'))

    def test_unreadable_container_metadata_is_not_a_match(self):
        with build('synthetic') as root:
            for meta in Path(root).rglob('.com.apple.mobile_container_manager.metadata.plist'):
                meta.write_bytes(b'garbage')
            self.assertEqual(run(root, 'zelle_risk_sdk_events'), [])


if __name__ == '__main__':
    unittest.main()
