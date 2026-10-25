"""Lockdown Mode flag and passkey record-load artifacts, through the real two-stage logarchive chain.

The artifacts read the table logarchive_artifacts builds, which holds only rows its own marker list
collected, so the main test runs the real ileapp.py on a synthetic 'log show' export and reads what each
stage wrote. Everything in the export is invented (processes, uuids, counts, times); the message shapes
follow lines read on an iOS 26.6.2 log.
"""
import inspect
import json
import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import logarchive  # pylint: disable=wrong-import-position

PROFILE = {'leapp': 'ileapp', 'format_version': 1,
           'plugins': ['logarchive', 'logarchive_artifacts', 'logarchive_lockdown_mode',
                       'logarchive_passkey_store', 'logarchive_shortcut_actions', 'logarchive_vpn_state']}
ZONE = timezone(timedelta(hours=-5))
BASE = datetime(2026, 3, 14, 10, 0, 0, tzinfo=ZONE)

PHOTOS = '/System/Library/PrivateFrameworks/PhotosCore.framework/Photos'
SAFARI = '/Applications/MobileSafari.app/MobileSafari'
CALLSD = '/usr/libexec/callservicesd'
SHARED = ('Determining if Shared Albums enabled: Found <private> with:\nisEnabledForSharedStreams: NO\n'
          'isProvisionedForDataclass: YES\nisEDUMode: NO\nisLockdownMode: {value}')
RUNNER = '/System/Library/PrivateFrameworks/WorkflowKit.framework/BackgroundShortcutRunner'
GROUP = 'B974676E-0000-4000-8000-000000000001'

# (seconds after base, process, subsystem, category, message, expected artifact or None)
LINES = [
    (1, PHOTOS, 'com.apple.photos.backend', 'PhotoSharing', SHARED.format(value='NO'), 'lockdown'),
    (2, PHOTOS, 'com.apple.photos.backend', 'PhotoSharing', SHARED.format(value='YES'), 'lockdown'),
    (3, CALLSD, 'com.apple.calls.copresencecore', 'Default',
     'CPSystemStateObserver computeSharePlayAllowed result <private> && lockdownModeEnabled:<private>', None),
    (4, '/usr/libexec/lockdownd', 'com.apple.mobile.lockdownd', 'Default', 'lockdownd: isLockdownMode is not used here', None),
    (5, SAFARI, 'com.apple.mobilesafari', 'Keychain',
     '-[WBSSavedAccountStore _fetchAndFilterPasskeysData]: Loaded 3 passkey keychain records from personal keychain',
     'passkey'),
    (6, SAFARI, 'com.apple.mobilesafari', 'Keychain',
     '-[WBSSavedAccountStore _fetchAndFilterPasskeysData]_block_invoke: Loaded 3 passkey keychain records '
     f'from group {GROUP}', 'passkey'),
    (7, SAFARI, 'com.apple.mobilesafari', 'Keychain',
     '-[WBSSavedAccountStore _fetchAndFilterRecentlyDeletedPasskeysData]: Loaded 0 recently deleted passkey '
     'keychain records from personal keychain', 'passkey'),
    (8, SAFARI, 'com.apple.SafariCore', 'Passwords', 'Could not fetch passkeys: -25300', None),
    (9, SAFARI, 'com.apple.example', 'Keychain', 'Loaded 3 passkey keychain records from personal keychain', None),
    (10, PHOTOS, 'com.apple.example', 'PhotoSharing', 'isLockdownMode: YES', None),
    (11, RUNNER, 'com.apple.shortcuts', 'RunningLifecycle',
     'Signpost ID: 1 - Signpost Name: 8A  enableTelemetry=YES actionID=com.example.app.DoThingIntent '
     '(signpost.telemetry:string2)', 'shortcut'),
    (12, RUNNER, 'com.apple.shortcuts', 'RunningLifecycle', 'Signpost ID: FFFFFFFF - Signpost Name: 81DE2  enableTelemetry=YES ', None),
    (13, RUNNER, 'com.apple.shortcuts', 'Daemon', 'actionID=com.example.app.Other is mentioned here', None),
    (14, CALLSD, 'com.apple.networkextension', 'Default',
     'VPN connectivity state is now NEVPNConnectivityStateDisconnected, visibility state is now 0, does not use '
     'policy-based routing', 'vpn'),
    (15, CALLSD, 'com.apple.networkextension', 'Default',
     'VPN connectivity state is now NEVPNConnectivityStateConnected, visibility state is now 1, does not use '
     'policy-based routing', 'vpn'),
    (16, CALLSD, 'com.apple.networkextension', 'Default', 'NEVPNConnectivityManager: invoking delegate', None),
]


def build_export():
    records = []
    for index, (seconds, process, subsystem, category, message, _kind) in enumerate(LINES):
        stamp = (BASE + timedelta(seconds=seconds)).strftime('%Y-%m-%d %H:%M:%S.000000%z')
        records.append({'timestamp': stamp, 'processImagePath': process, 'processID': 2000 + index,
                        'subsystem': subsystem, 'category': category, 'eventMessage': message,
                        'traceID': 1000 + index})
    return json.dumps(records).encode('utf-8')


def rows_of(kind):
    return [number for number, line in enumerate(LINES, start=1) if line[5] == kind]


def like_patterns(sql):
    return set(re.findall(r"LIKE '([^']*)'", sql))


class ChainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        root = pathlib.Path(cls.folder.name)
        extraction = root / 'extraction'
        extraction.mkdir()
        (extraction / 'logarchive_synthetic_wave3.json').write_bytes(build_export())
        profile = root / 'wave3.ilprofile'
        profile.write_text(json.dumps(PROFILE), encoding='utf-8')
        output = root / 'out'
        output.mkdir()
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / 'ileapp.py'), '-t', 'fs', '-i', str(extraction),
             '-o', str(output), '-m', str(profile)],
            capture_output=True, text=True, check=False, env=dict(os.environ, TZ='UTC'), cwd=REPO_ROOT,
            timeout=600)
        cls.log = completed.stdout + completed.stderr
        cls.returncode = completed.returncode
        reports = sorted(output.glob('iLEAPP_Output_*'))
        cls.db = None
        if reports and (reports[-1] / '_lava_artifacts.db').exists():
            cls.db = sqlite3.connect(f'file:{reports[-1] / "_lava_artifacts.db"}?mode=ro', uri=True)

    @classmethod
    def tearDownClass(cls):
        if cls.db is not None:
            cls.db.close()
        cls.folder.cleanup()

    def numbers(self, table):
        return sorted(int(row[0]) for row in self.db.execute(f'SELECT row_number FROM {table}'))

    def test_run_completed(self):
        self.assertEqual(self.returncode, 0, self.log[-2000:])
        self.assertIsNotNone(self.db, self.log[-2000:])
        self.assertNotIn('duplicate', self.log.lower())

    def test_collection_stage_holds_only_the_markers(self):
        self.assertEqual(self.numbers('logarchive_artifacts'), sorted(rows_of('lockdown') + rows_of('passkey') + rows_of('shortcut') + rows_of('vpn')))

    def test_lockdown_rows(self):
        self.assertEqual(self.numbers('logarchive_lockdown_mode'), rows_of('lockdown'))
        messages = [row[0] for row in self.db.execute(
            'SELECT event_message FROM logarchive_lockdown_mode ORDER BY row_number')]
        self.assertTrue(messages[0].endswith('isLockdownMode: NO'))
        self.assertTrue(messages[1].endswith('isLockdownMode: YES'))

    def test_passkey_rows(self):
        self.assertEqual(self.numbers('logarchive_passkey_store'), rows_of('passkey'))

    def test_shortcut_action_rows(self):
        self.assertEqual(self.numbers('logarchive_shortcut_actions'), rows_of('shortcut'))

    def test_vpn_state_rows(self):
        self.assertEqual(self.numbers('logarchive_vpn_state'), rows_of('vpn'))


class MarkerTest(unittest.TestCase):
    def test_dependent_patterns_are_collected(self):
        collected = like_patterns(inspect.getsource(logarchive.logarchive_artifacts.__wrapped__))
        for function in (logarchive.logarchive_lockdown_mode, logarchive.logarchive_passkey_store,
                         logarchive.logarchive_shortcut_actions, logarchive.logarchive_vpn_state):
            for pattern in like_patterns(inspect.getsource(function.__wrapped__)):
                with self.subTest(function=function.__name__, pattern=pattern):
                    self.assertIn(pattern, collected)


if __name__ == '__main__':
    unittest.main()
