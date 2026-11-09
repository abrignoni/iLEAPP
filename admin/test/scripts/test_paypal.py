"""paypal: PayPal (com.yourcompany.PPClient) stores, SYNTHETIC input only."""
import hashlib
import importlib.util
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import paypal as module

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('synthetic_paypal', HERE / 'synthetic_paypal.py')
SYNTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNTH)

ARTIFACTS = (module.paypalRememberedAccount, module.paypalAccountKeys, module.paypalDatedKeys,
             module.paypalAppSettings, module.paypalSecuritySdkStarts, module.paypalCachedRequests,
             module.paypalAnalyticsEvents, module.paypalMparticleSessions)


def _files(folder):
    return sorted(str(path) for path in Path(folder).rglob('*') if path.is_file())


def _run(function, files):
    context = SimpleNamespace(get_files_found=lambda: list(files), get_relative_path=lambda value: Path(value).name)
    return function.__wrapped__(context)


def _rows(function, files):
    return _run(function, files)[1]


def _count(path, query):
    db = sqlite3.connect(path)
    try:
        return db.execute(query).fetchone()[0]
    finally:
        db.close()


def _digests(files):
    return {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in files}


class PayPalTest(unittest.TestCase):
    """Each paypal artifact against fabricated containers."""

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder, True)

    def _tree(self, variant):
        SYNTH.write_tree(self.folder, variant)
        return _files(self.folder)

    def _path(self, relative):
        return str(Path(self.folder) / relative)

    def test_full_row_counts_match_an_independent_count(self):
        files = self._tree('full')
        cache = self._path(f'{SYNTH.DATA_ROOT}/Library/Caches/{SYNTH.BUNDLE}/Cache.db')
        events = self._path(f'{SYNTH.DATA_ROOT}/Library/Caches/com.paypal.lighthouseanalytics/lighthouseanalytics.db')
        mparticle = self._path(f'{SYNTH.DATA_ROOT}/Documents/mParticle28.db')
        log = Path(self._path(f'{SYNTH.DATA_ROOT}/Library/Application Support/Thales-v2/slog-TSH-48bbb8-01.log'))
        expected = {
            module.paypalRememberedAccount: 1,
            module.paypalCachedRequests: _count(cache, 'SELECT COUNT(*) FROM cfurl_cache_response'),
            module.paypalAnalyticsEvents: _count(events, 'SELECT COUNT(*) FROM events'),
            module.paypalMparticleSessions: _count(mparticle, 'SELECT COUNT(*) FROM sessions'),
            module.paypalSecuritySdkStarts: sum(' SDKV ' in line for line in log.read_text(encoding='utf-8').splitlines()),
        }
        for function, count in expected.items():
            with self.subTest(function.__name__):
                self.assertEqual(len(_rows(function, files)), count)
        self.assertGreater(min(expected.values()), 0)

    def test_decoy_container_of_another_app_is_not_reported(self):
        files = self._tree('full')
        decoy = [name for name in files if SYNTH.DECOY_UUID in name]
        self.assertTrue(decoy)
        for function in (module.paypalSecuritySdkStarts, module.paypalMparticleSessions):
            with self.subTest(function.__name__):
                _, rows, source = _run(function, files)
                self.assertTrue(rows)
                self.assertNotIn(SYNTH.DECOY_UUID, source)
        # the decoy holds the same rows again, so reading it would double the counts
        self.assertEqual(len(_rows(module.paypalSecuritySdkStarts, files)), 3)
        self.assertEqual(len(_rows(module.paypalMparticleSessions, files)), 3)

    def test_third_party_names_need_the_container_marker(self):
        files = [name for name in self._tree('full') if not name.endswith(module.MARKER)]
        for function in (module.paypalSecuritySdkStarts, module.paypalMparticleSessions):
            with self.subTest(function.__name__):
                self.assertEqual(_rows(function, files), [])

    def test_remembered_account_fields(self):
        row = _rows(module.paypalRememberedAccount, self._tree('full'))[0]
        self.assertEqual(row[0], 'Pat Example')
        self.assertEqual(row[2], 'pat.example@example.invalid')
        self.assertEqual(row[4], 'SYNTHACCT0001A')
        self.assertEqual(row[5], 1)
        self.assertEqual(row[6], 'US')
        self.assertEqual(row[8], '')

    def test_account_keys_expand_the_notification_dictionary(self):
        rows = _rows(module.paypalAccountKeys, self._tree('full'))
        settings = {row[1]: row[2] for row in rows if row[0] == 'SYNTHACCT0001A'}
        self.assertEqual(settings['Push notification preference: SendMoney'], 'true')
        self.assertEqual(settings['Social tooltip flag (socialTooltipViewedFirstTimeShown)'], 'Yes')
        self.assertIn('pat.example@example.invalid', {row[0] for row in rows})

    def test_dated_keys_include_dates_and_kronos_and_skip_non_dates(self):
        rows = _rows(module.paypalDatedKeys, self._tree('full'))
        keys = {row[1] for row in rows}
        self.assertIn('gdprConsentedDate', keys)
        self.assertIn('com.paypalPKPeerPaymentRecurringPaymentsLastUpdatedKey', keys)
        self.assertIn('KronosStableTime.Timestamp (read as Unix seconds)', keys)
        self.assertNotIn('gdprConsented', keys)
        self.assertEqual([row[0] for row in rows], sorted(row[0] for row in rows))

    def test_settings_skip_server_flags_and_order_versions_numerically(self):
        rows = _rows(module.paypalAppSettings, self._tree('full'))
        keys = [row[1] for row in rows]
        self.assertNotIn('isPasskeyLoginEnabled', keys)
        self.assertNotIn('RCSDefault-hubCaching', keys)
        markers = [key for key in keys if key.startswith('appLaunchedFirstTime:')]
        self.assertEqual(markers, ['appLaunchedFirstTime:8.9.1', 'appLaunchedFirstTime:8.98.0',
                                   'appLaunchedFirstTime:8.107.2'])
        deposit = {row[1]: row[2] for row in rows if row[0] == 'Direct-deposit key'}
        self.assertEqual(set(deposit.values()), {'present, empty'})
        self.assertIn(('OptInData', 'pn_user'), {(row[0], row[1]) for row in rows})

    def test_sdk_starts_read_the_header_and_millisecond_times(self):
        rows = _rows(module.paypalSecuritySdkStarts, self._tree('full'))
        self.assertEqual(rows[0][1], '7.2.3.rc01 (Release)')
        self.assertEqual((rows[0][2], rows[0][3]), ('iOS 26.2', 'iPhone99,9'))
        self.assertEqual(rows[0][0].microsecond, 871000)
        self.assertLess(rows[0][0], rows[1][0])

    def test_cached_requests_show_host_and_path_but_never_the_query(self):
        rows = _rows(module.paypalCachedRequests, self._tree('full'))
        self.assertEqual(rows[0][2:4], ('slc.stats.paypal.com', '/counter1.cgi'))
        for row in rows:
            self.assertNotIn('?', row[3])
            self.assertNotIn('SYNTHTOKEN', ' '.join(str(cell) for cell in row))
        beacon, other = rows[0], rows[2]
        self.assertEqual((beacon[4], beacon[6]), ('192.0.2.10', '10'))
        self.assertEqual(beacon[1], beacon[0])
        self.assertEqual((other[1], *other[4:7]), ('', '', '', ''))

    def test_analytics_events_tolerate_bad_json_and_prefer_the_payload(self):
        rows = _rows(module.paypalAnalyticsEvents, self._tree('full'))
        first, second, bad = rows
        self.assertEqual(first[1], 'appTransition:didFinishLaunching')
        self.assertEqual(first[6], 'Mobile')          # channel is only in the payload, not in original_event
        self.assertEqual(first[8], 'Yes')
        self.assertEqual(second[1], 'authentication_queued_im')   # eventName fallback
        self.assertEqual(second[8], 'No')
        self.assertEqual(bad[1:18], ('',) * 17)
        self.assertEqual((first[18], first[19]), (-1, 0))

    def test_empty_stores_give_no_rows_but_keep_the_account(self):
        files = self._tree('empty')
        for function in (module.paypalCachedRequests, module.paypalAnalyticsEvents, module.paypalMparticleSessions,
                         module.paypalAccountKeys):
            with self.subTest(function.__name__):
                self.assertEqual(_rows(function, files), [])
        self.assertEqual(len(_rows(module.paypalRememberedAccount, files)), 1)
        self.assertTrue(_rows(module.paypalSecuritySdkStarts, files))

    def test_missing_tables_and_keys_do_not_raise(self):
        files = self._tree('sparse')
        for function in ARTIFACTS:
            with self.subTest(function.__name__):
                headers, rows, _ = _run(function, files)
                self.assertTrue(headers)
                if function not in (module.paypalDatedKeys, module.paypalAppSettings):
                    self.assertEqual(rows, [])
        self.assertEqual(_rows(module.paypalRememberedAccount, files), [])

    def test_unreadable_plist_and_database_are_skipped(self):
        files = self._tree('full')
        for name in files:
            if name.endswith(('.plist', 'Cache.db', 'lighthouseanalytics.db')) \
                    and not name.endswith(module.MARKER):
                Path(name).write_bytes(b'not a database or a plist')
        for function in ARTIFACTS:
            with self.subTest(function.__name__):
                _run(function, files)

    def test_artifacts_never_write_to_the_evidence(self):
        files = self._tree('full')
        before = _digests(files)
        for function in ARTIFACTS:
            _run(function, files)
        self.assertEqual(_digests([name for name in files if Path(name).exists()
                                   and not name.endswith(('-shm', '-wal'))]),
                         {name: digest for name, digest in before.items()
                          if not name.endswith(('-shm', '-wal'))})


if __name__ == '__main__':
    unittest.main()
