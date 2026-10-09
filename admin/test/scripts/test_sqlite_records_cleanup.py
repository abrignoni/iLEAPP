"""Synthetic regression tests for streaming SQLite connection ownership."""
import contextlib
import gc
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts import ilapfuncs  # pylint: disable=wrong-import-position


class RecordsCleanupTests(unittest.TestCase):
    """Connections are closed without waiting for garbage collection."""
    def setUp(self):
        # unittest exits this context after tearDown, including test failures.
        self.temp = self.enterContext(
            tempfile.TemporaryDirectory())  # pylint: disable=consider-using-with
        self.path = str(pathlib.Path(self.temp) / 'synthetic.sqlite')
        with contextlib.closing(sqlite3.connect(self.path)) as db:
            db.execute('CREATE TABLE sample (value INTEGER)')
            db.executemany('INSERT INTO sample VALUES (?)', [(1,), (2,)])
            db.commit()
        self.opened = []
        real_open = ilapfuncs.open_sqlite_db_readonly
        def tracked(path):
            db = real_open(path)
            if db is not None:
                self.opened.append(db)
            return db
        patch = mock.patch.object(ilapfuncs, 'open_sqlite_db_readonly', tracked)
        patch.start()
        self.addCleanup(patch.stop)
        self.addCleanup(self.cleanup_connections)

    def records(self, query, attach_query=None):
        """Read the synthetic database through the public helper."""
        return ilapfuncs.get_sqlite_db_records(self.path, query, attach_query)

    def cleanup_connections(self):
        """Release captured connections even when a regression assertion fails."""
        for db in self.opened:
            db.close()

    def assert_closed(self):
        """A closed connection rejects further SQL."""
        self.assertTrue(self.opened)
        for db in self.opened:
            with self.assertRaises(sqlite3.ProgrammingError):
                db.execute('SELECT 1')

    def test_exhaustion_preserves_named_rows_and_closes(self):
        """Rows retain named-column access after cleanup."""
        rows = list(self.records('SELECT value FROM sample ORDER BY value'))
        self.assertEqual([r['value'] for r in rows], [1, 2])
        self.assert_closed()

    def test_empty_query_closes(self):
        """An empty result also releases the connection."""
        self.assertEqual(list(self.records('SELECT * FROM sample WHERE 0')), [])
        self.assert_closed()

    def test_failed_query_closes(self):
        """An invalid query is logged and its connection is closed."""
        with mock.patch.object(ilapfuncs, 'logfunc') as log:
            self.assertEqual(list(self.records('SELECT * FROM absent')), [])
            self.assertTrue(log.called)
        self.assert_closed()

    def test_failed_attach_closes(self):
        """An invalid attachment releases the connection."""
        with mock.patch.object(ilapfuncs, 'logfunc'):
            self.assertEqual(list(self.records('SELECT 1', 'INVALID SQL')), [])
        self.assert_closed()

    def test_explicit_early_close(self):
        """An early consumer can deterministically release the iterator."""
        with contextlib.closing(self.records('SELECT value FROM sample')) as rows:
            self.assertEqual(next(rows)[0], 1)
        self.assert_closed()

    def test_caller_failure_closes(self):
        """A consumer exception within closing releases resources."""
        with self.assertRaisesRegex(RuntimeError, 'synthetic'):
            with contextlib.closing(self.records('SELECT value FROM sample')) as rows:
                next(rows)
                raise RuntimeError('synthetic')
        self.assert_closed()

    def test_logging_failure_still_closes(self):
        """Even an exception from logging must release the database."""
        with mock.patch.object(ilapfuncs, 'logfunc', side_effect=OSError('synthetic')):
            with self.assertRaises(OSError):
                list(self.records('INVALID SQL'))
        self.assert_closed()

    def test_missing_database_is_empty(self):
        """An unavailable source yields no rows."""
        with mock.patch.object(ilapfuncs, 'logfunc'):
            rows = ilapfuncs.get_sqlite_db_records(self.path + '.absent', 'SELECT 1')
            self.assertEqual(list(rows), [])

    def test_repeated_reads_do_not_depend_on_garbage_collection(self):
        """Repeated queries release handles with the collector disabled."""
        enabled = gc.isenabled()
        gc.disable()
        try:
            for _ in range(1000):
                self.assertEqual(len(list(self.records('SELECT * FROM sample'))), 2)
            self.assert_closed()
        finally:
            if enabled:
                gc.enable()


if __name__ == '__main__':
    unittest.main()
