"""The sqlite existence-check helpers must close the database they open.

does_table_exist_in_db, does_view_exist_in_db and does_column_exist_in_db each open a
connection through open_sqlite_db_readonly and return a bool, so nothing escapes for the
caller to close. They used to leave the connection to the garbage collector, which shows
up as `ResourceWarning: unclosed database` and, on a full extraction, means one held
handle per probe - artifacts probe the same NoteStore.sqlite several times over.

get_sqlite_db_records is deliberately not covered here: it returns its cursor for the
caller to iterate, so closing the connection inside it would break every caller.

Closure is asserted by using the connection afterwards - a closed sqlite3 connection
raises ProgrammingError - rather than by watching for ResourceWarning, which only fires
when the collector happens to run.
"""
import pathlib
import sqlite3
import shutil
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs  # pylint: disable=wrong-import-position


class TestSqliteHelpersCloseDb(unittest.TestCase):
    """Every helper that opens a connection and returns a bool must close it."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = pathlib.Path(self.tmpdir) / 'probe.sqlite'
        db = sqlite3.connect(self.db_path)
        db.execute('CREATE TABLE ZTABLE (Z_PK INTEGER, ZNAME TEXT)')
        db.execute('CREATE VIEW ZVIEW AS SELECT Z_PK FROM ZTABLE')
        db.commit()
        db.close()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _call_and_capture(self, func, *args):
        """Run a helper, returning its result plus the connections it opened."""
        real_open = ilapfuncs.open_sqlite_db_readonly
        opened = []

        def spy(path):
            db = real_open(path)
            opened.append(db)
            return db

        with mock.patch.object(ilapfuncs, 'open_sqlite_db_readonly', spy):
            result = func(*args)
        return result, opened

    def _assert_all_closed(self, opened):
        self.assertTrue(opened, 'helper opened no connection at all')
        for db in opened:
            with self.assertRaises(sqlite3.ProgrammingError):
                db.execute('SELECT 1')

    def test_table_check_closes_on_hit(self):
        found, opened = self._call_and_capture(
            ilapfuncs.does_table_exist_in_db, str(self.db_path), 'ZTABLE')
        self.assertTrue(found)
        self._assert_all_closed(opened)

    def test_table_check_closes_on_miss(self):
        """The early `return True` is the leak-prone path, but the miss must close too."""
        found, opened = self._call_and_capture(
            ilapfuncs.does_table_exist_in_db, str(self.db_path), 'ZNOSUCHTABLE')
        self.assertFalse(found)
        self._assert_all_closed(opened)

    def test_view_check_closes_on_hit(self):
        found, opened = self._call_and_capture(
            ilapfuncs.does_view_exist_in_db, str(self.db_path), 'ZVIEW')
        self.assertTrue(found)
        self._assert_all_closed(opened)

    def test_view_check_closes_on_miss(self):
        found, opened = self._call_and_capture(
            ilapfuncs.does_view_exist_in_db, str(self.db_path), 'ZNOSUCHVIEW')
        self.assertFalse(found)
        self._assert_all_closed(opened)

    def test_column_check_closes_on_hit(self):
        found, opened = self._call_and_capture(
            ilapfuncs.does_column_exist_in_db, str(self.db_path), 'ZTABLE', 'ZNAME')
        self.assertTrue(found)
        self._assert_all_closed(opened)

    def test_column_check_closes_on_miss(self):
        found, opened = self._call_and_capture(
            ilapfuncs.does_column_exist_in_db, str(self.db_path), 'ZTABLE', 'ZNOSUCHCOL')
        self.assertFalse(found)
        self._assert_all_closed(opened)

    def test_column_check_survives_an_unopenable_database(self):
        """It had no `if db:` guard, so a None connection raised AttributeError.

        The sibling helpers already returned False in that case. An artifact calling
        this one against an unreadable db lost all of its rows to a crash instead.
        """
        missing = str(pathlib.Path(self.tmpdir) / 'not-here.sqlite')
        self.assertFalse(ilapfuncs.does_column_exist_in_db(missing, 'ZTABLE', 'ZNAME'))

    def test_the_helpers_agree_on_an_unopenable_database(self):
        missing = str(pathlib.Path(self.tmpdir) / 'not-here.sqlite')
        self.assertFalse(ilapfuncs.does_table_exist_in_db(missing, 'ZTABLE'))
        self.assertFalse(ilapfuncs.does_view_exist_in_db(missing, 'ZVIEW'))


if __name__ == '__main__':
    unittest.main()
