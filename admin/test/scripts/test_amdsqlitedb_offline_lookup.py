"""AMDSQLiteDB usage events must resolve app names offline, from the evidence.

The artifact used to query http://itunes.apple.com/lookup per unique adamId to
name apps missing from storeUser.db current_apps. On an offline forensic
workstation every lookup failed (103 'ERROR fetching data' lines in one case
run), and the design sent case-derived identifiers to an external service. The
online lookup was removed: names now come from current_apps (installed apps)
and purchase_history_apps (the account's purchase history, which retains
uninstalled apps), both inside the extraction.

These tests pin the offline resolution order, the guard for old storeUser.db
schemas without purchase_history_apps, the no-storeUser.db fallback, and that
the module performs no network I/O.
"""
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.artifacts.AMDSQLiteDB as amd_module  # pylint: disable=wrong-import-position
from scripts.artifacts.AMDSQLiteDB import AMDSQLiteDB_UsageEvents  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

TS = 1756684800  # 2025-09-01 00:00:00 UTC

INSTALLED = 111111111   # in current_apps
UNINSTALLED = 222222222  # only in purchase_history_apps
UNRESOLVED = 333333333   # in neither


class TestAmdSqliteDbOfflineLookup(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Context.clear()
        Context.set_report_folder(self.tmpdir)

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_amd_db(self, adam_ids):
        db_path = pathlib.Path(self.tmpdir) / 'AMDSQLite.db.0'
        db = sqlite3.connect(db_path)
        db.execute('CREATE TABLE AMDAppStoreUsageEvents '
                   '(time INTEGER, type TEXT, adamId INTEGER, appVersion TEXT, '
                   'foregroundDuration REAL, userId INTEGER)')
        db.executemany('INSERT INTO AMDAppStoreUsageEvents VALUES (?, "2", ?, "1.0", 12.5, 42)',
                       [(TS, adam_id) for adam_id in adam_ids])
        db.commit()
        db.close()
        return str(db_path)

    def _make_store_user_db(self, with_history_table=True):
        db_path = pathlib.Path(self.tmpdir) / 'storeUser.db'
        db = sqlite3.connect(db_path)
        db.execute('CREATE TABLE current_apps (item_id INTEGER, item_name TEXT, '
                   'bundle_id TEXT, vendor_name TEXT)')
        db.execute('INSERT INTO current_apps VALUES (?, "Installed App", '
                   '"com.example.installed", "Example Vendor")', (INSTALLED,))
        db.execute('CREATE TABLE account_events (account_id INTEGER, apple_id TEXT)')
        db.execute('INSERT INTO account_events VALUES (42, "user@example.com")')
        if with_history_table:
            db.execute('CREATE TABLE purchase_history_apps (store_item_id INTEGER, '
                       'title TEXT, bundle_id TEXT, developer_name TEXT)')
            db.execute('INSERT INTO purchase_history_apps VALUES (?, "Removed App", '
                       '"com.example.removed", "Removed Vendor")', (UNINSTALLED,))
        db.commit()
        db.close()
        return str(db_path)

    def _run(self, adam_ids, store_user=True, with_history_table=True):
        files = [self._make_amd_db(adam_ids)]
        if store_user:
            files.append(self._make_store_user_db(with_history_table))
        Context.set_files_found(files)
        headers, data_list, _source = AMDSQLiteDB_UsageEvents.__wrapped__(Context)
        name_idx = [h[0] if isinstance(h, tuple) else h for h in headers].index('App Name')
        return headers, data_list, name_idx

    def test_installed_app_resolves_from_current_apps(self):
        _headers, rows, name_idx = self._run([INSTALLED])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][name_idx], 'Installed App')
        self.assertEqual(rows[0][0], datetime(2025, 9, 1, tzinfo=timezone.utc))

    def test_uninstalled_app_resolves_from_purchase_history(self):
        """The case the online lookup existed for: app gone from current_apps."""
        _headers, rows, name_idx = self._run([UNINSTALLED])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][name_idx], 'Removed App')
        self.assertEqual(rows[0][name_idx + 1], 'com.example.removed')

    def test_unknown_adam_id_is_labeled_not_dropped(self):
        _headers, rows, name_idx = self._run([UNRESOLVED])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][name_idx], f'Unknown ({UNRESOLVED})')

    def test_old_store_user_schema_without_history_table_still_runs(self):
        _headers, rows, name_idx = self._run([INSTALLED, UNINSTALLED],
                                             with_history_table=False)
        self.assertEqual(len(rows), 2)
        names = {row[name_idx] for row in rows}
        self.assertIn('Installed App', names)
        self.assertIn(f'Unknown ({UNINSTALLED})', names)

    def test_no_store_user_db_still_runs(self):
        _headers, rows, name_idx = self._run([INSTALLED], store_user=False)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][name_idx], f'Unknown ({INSTALLED})')

    def test_row_count_matches_events_exactly(self):
        """Resolution must never multiply or drop event rows."""
        _headers, rows, _ = self._run([INSTALLED, INSTALLED, UNINSTALLED, UNRESOLVED])
        self.assertEqual(len(rows), 4)

    def test_module_performs_no_network_io(self):
        """The offline guarantee: no url-opening machinery in the module."""
        source = pathlib.Path(amd_module.__file__).read_text(encoding='utf-8')
        for marker in ('urlopen', 'urllib.request', 'requests.get', 'http.client'):
            self.assertNotIn(marker, source)


if __name__ == '__main__':
    unittest.main()
