"""is_sqlite_sidecar and sqlite_databases drop the files SQLite keeps beside a database.

A pattern such as '*/Foo.sqlite*' also matches Foo.sqlite-wal, -shm and -journal. Those are not
databases, and queried on their own they raise sqlite3.DatabaseError. The helper only filters the
list an artifact loops over: the seeker stages a sidecar because the pattern matches it, and
sqlite_wal.WalStates finds the log at <database>-wal on disk, so a WAL-recovery artifact keeps
working. These tests pin both.
"""
import os
import pathlib
import shutil
import sqlite3
import tempfile
import unittest

from scripts.ilapfuncs import is_sqlite_sidecar, open_sqlite_db_readonly, sqlite_databases
from scripts.sqlite_wal import KIND_COMMITTED, WalStates


class SqliteSidecarHelperTest(unittest.TestCase):

    def test_sidecars_are_recognised_and_databases_are_not(self):
        for path in ('a/Foo.sqlite-wal', 'a/Foo.db-shm', 'a/Foo.sqlite3-journal', 'A/FOO.DB-WAL'):
            self.assertTrue(is_sqlite_sidecar(path), path)
        for path in ('a/Foo.sqlite', 'a/Foo.db', 'a/wal.db', 'a/walk.sqlite', 'a/Foo.sqlite-wal.bak',
                     'a/journal', 'a/shm'):
            self.assertFalse(is_sqlite_sidecar(path), path)

    def test_a_path_object_is_accepted(self):
        self.assertTrue(is_sqlite_sidecar(pathlib.Path('x/y.db-wal')))

    def test_databases_keep_their_order_and_come_back_as_text(self):
        found = ['b.db', 'b.db-wal', 'a.db', 'a.db-shm', 'a.db-journal']
        self.assertEqual(sqlite_databases(found), ['b.db', 'a.db'])
        self.assertEqual(sqlite_databases([]), [])


class SidecarsStayAvailableToWalRecoveryTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, 'store.db')
        self.writer = sqlite3.connect(self.path)
        self.writer.execute('PRAGMA journal_mode=WAL')
        self.writer.execute('PRAGMA wal_autocheckpoint=0')
        self.writer.execute('CREATE TABLE t(x)')
        self.writer.commit()
        self.writer.execute('INSERT INTO t VALUES (1)')
        self.writer.commit()

    def tearDown(self):
        self.writer.close()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_filtering_the_loop_list_leaves_the_log_for_wal_recovery(self):
        found = [self.path, self.path + '-wal', self.path + '-shm']
        databases = sqlite_databases(found)

        self.assertEqual(databases, [self.path])
        # the log is still on disk beside the database, which is where WalStates looks for it
        self.assertTrue(os.path.exists(self.path + '-wal'))
        states = WalStates(databases[0], include=(KIND_COMMITTED,))
        self.assertEqual(states.wal_path, self.path + '-wal')
        reader = open_sqlite_db_readonly(databases[0])
        try:
            rows = reader.execute('SELECT count(*) FROM t').fetchone()[0]
        finally:
            reader.close()
        self.assertEqual(rows, 1)  # the row that only the -wal holds is still read


if __name__ == '__main__':
    unittest.main()
