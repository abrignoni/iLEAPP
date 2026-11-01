"""Burner Cache artifacts report no rows, rather than stopping, when the cache query fails.

get_sqlite_db_records_regexpr logged a failed query and returned None, which every Burner
Cache artifact iterates, so a Cache.db without the cfurl cache tables stopped each one with
"TypeError: 'NoneType' object is not iterable". It now returns no rows after logging, and
closes the connection it opened.
"""
import os
import shutil
import sqlite3
import tempfile
import types
import unittest
from unittest import mock

from scripts.artifacts import burnerCache
from scripts.context import Context
from scripts.search_files import FileInfo

CACHES = 'private/var/mobile/Containers/Data/Application/A/Library/Caches/com.adhoclabs.burner'


class BurnerCacheQueryFailureTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        folder = os.path.join(self.tmpdir, CACHES)
        os.makedirs(folder)
        self.path = os.path.join(folder, 'Cache.db')
        db = sqlite3.connect(self.path)
        db.execute('CREATE TABLE unrelated (x)')
        db.commit()
        db.close()
        Context.clear()
        Context.set_data_folder(self.tmpdir)
        Context.set_report_folder(self.tmpdir)
        Context.set_files_found([self.path])
        Context.set_seeker(types.SimpleNamespace(directory=self.tmpdir,
                                                 file_infos={self.path: FileInfo(f'{CACHES}/Cache.db', 0, 0)}))
        patcher = mock.patch.object(burnerCache, 'logfunc')
        self.log = patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_the_helper_logs_and_returns_no_rows(self):
        rows = burnerCache.get_sqlite_db_records_regexpr(self.path, 'SELECT * FROM cfurl_cache_response')

        self.assertEqual(rows, [])
        self.assertTrue(any('no such table' in c.args[0] for c in self.log.call_args_list))

    def test_every_artifact_reports_no_rows(self):
        for artifact in (burnerCache.burnerCache_accounts, burnerCache.burnerCache_contacts,
                         burnerCache.burnerCache_numbers, burnerCache.burnerCache_messages):
            _, rows, _ = artifact.__wrapped__(Context)
            # These artifacts return (plain rows, HTML rows).
            for row_list in (rows if isinstance(rows, tuple) else (rows,)):
                self.assertEqual(row_list, [], artifact.__name__)


if __name__ == '__main__':
    unittest.main()
