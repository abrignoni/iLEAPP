"""open_sqlite_db_readonly and attach_sqlite_db_readonly on staged copies.

Shared file: kept byte-identical in iLEAPP, ALEAPP, RLEAPP, VLEAPP and DLEAPP.

Two things are checked.

1. Paths with characters a URI gives meaning to ('#', '?', '%', a space,
   non-ASCII) open the file named, not a truncated one. A URI built by f-string
   from the raw path stops at '#' or '?', so SQLite opens a different file and
   the tables read as absent. A negative control shows that form failing here.

2. A database in WAL mode staged with no -wal beside it is read as the
   database file alone. It must read those rows without SQLite creating a -wal
   or -shm in the staged folder (Apple's SQLite 3.54.0 refuses the mode=ro
   open of such a file outright). A database staged with its -wal must still read the rows
   that exist only in that log: immutable=1 ignores the log, so it must never
   be used when a -wal is present.
"""
import os
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs  # pylint: disable=wrong-import-position

# '?' cannot appear in a Windows file name.
SPECIAL_NAMES = ['hash#1712', 'pct%41', 'two words', 'café ñ']
if not ilapfuncs.is_platform_windows():
    SPECIAL_NAMES.append('q?x=1')


def _make_db(path, rows):
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE t (x INTEGER)')
    con.executemany('INSERT INTO t VALUES (?)', [(r,) for r in rows])
    con.commit()
    con.close()


def _make_wal_db(source_dir):
    """A WAL database whose last two rows exist only in its -wal.

    Returns (db_path, rows_in_db_file, rows_in_db_plus_wal). The writing
    connection is left open while the caller copies the files, so the log is
    not checkpointed into the database first.
    """
    path = os.path.join(source_dir, 'w.db')
    con = sqlite3.connect(path)
    con.execute('PRAGMA journal_mode=WAL')
    con.execute('PRAGMA wal_autocheckpoint=0')
    con.execute('CREATE TABLE t (x INTEGER)')
    con.executemany('INSERT INTO t VALUES (?)', [(1,), (2,)])
    con.commit()
    con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    con.executemany('INSERT INTO t VALUES (?)', [(3,), (4,)])
    con.commit()
    return path, con


def _count(db, table='t'):
    try:
        return db.execute(f'SELECT count(*) FROM {table}').fetchone()[0]
    finally:
        db.close()


class SpecialCharacterPaths(unittest.TestCase):
    """The URI names the file on disk, whatever characters its path holds."""

    def setUp(self):
        self.base = tempfile.mkdtemp()
        self.plain = os.path.join(self.base, 'plain.db')
        _make_db(self.plain, [1])

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def _special_db(self, name):
        folder = os.path.join(self.base, name)
        os.makedirs(folder)
        path = os.path.join(folder, name + '.db')
        _make_db(path, [1, 2, 3])
        return folder, path

    def test_open_reads_the_named_file(self):
        for name in SPECIAL_NAMES:
            with self.subTest(name=name):
                folder, path = self._special_db(name)
                db = ilapfuncs.open_sqlite_db_readonly(path)
                self.assertIsNotNone(db)
                self.assertEqual(_count(db), 3)
                self.assertEqual(os.listdir(folder), [name + '.db'])

    def test_attach_reads_the_named_file_read_only(self):
        for name in SPECIAL_NAMES:
            with self.subTest(name=name):
                folder, path = self._special_db(name)
                db = ilapfuncs.open_sqlite_db_readonly(self.plain)
                try:
                    db.execute(ilapfuncs.attach_sqlite_db_readonly(path, 'other'))
                    self.assertEqual(
                        db.execute('SELECT count(*) FROM other.t').fetchone()[0], 3)
                    with self.assertRaises(sqlite3.OperationalError):
                        db.execute('INSERT INTO other.t VALUES (9)')
                finally:
                    db.close()
                self.assertEqual(os.listdir(folder), [name + '.db'])

    def test_unquoted_uri_really_fails(self):
        """Negative control: the raw f-string URI must miss the file here."""
        _folder, path = self._special_db('hash#1712')
        with self.assertRaises(sqlite3.OperationalError):
            con = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
            try:
                con.execute('SELECT count(*) FROM t').fetchone()
            finally:
                con.close()


class WalModeStagedCopies(unittest.TestCase):
    """A WAL database reads its committed state and its staged folder is left alone."""

    def setUp(self):
        self.base = tempfile.mkdtemp()
        self.source = os.path.join(self.base, 'source')
        os.makedirs(self.source)
        self.source_db, self.writer = _make_wal_db(self.source)

    def tearDown(self):
        self.writer.close()
        shutil.rmtree(self.base, ignore_errors=True)

    def _stage(self, name, suffixes):
        folder = os.path.join(self.base, name)
        os.makedirs(folder)
        for suffix in suffixes:
            shutil.copyfile(self.source_db + suffix, os.path.join(folder, 'w.db' + suffix))
        return folder, os.path.join(folder, 'w.db')

    def test_wal_header_confirms_the_fixture(self):
        with open(self.source_db, 'rb') as handle:
            self.assertEqual(handle.read(20)[18:20], b'\x02\x02')
        self.assertGreater(os.path.getsize(self.source_db + '-wal'), 0)

    def test_without_wal_reads_rows_and_creates_no_sidecars(self):
        folder, path = self._stage('no_wal', [''])
        with mock.patch.object(ilapfuncs, 'logfunc') as log:
            db = ilapfuncs.open_sqlite_db_readonly(path)
        self.assertIsNotNone(db)
        self.assertEqual(_count(db), 2)
        self.assertEqual(sorted(os.listdir(folder)), ['w.db'])
        self.assertTrue(any('immutable=1' in str(c) for c in log.call_args_list))

    def test_attach_without_wal_reads_rows_and_creates_no_sidecars(self):
        folder, path = self._stage('no_wal_attach', [''])
        plain = os.path.join(self.base, 'plain.db')
        _make_db(plain, [1])
        db = ilapfuncs.open_sqlite_db_readonly(plain)
        try:
            db.execute(ilapfuncs.attach_sqlite_db_readonly(path, 'other'))
            self.assertEqual(db.execute('SELECT count(*) FROM other.t').fetchone()[0], 2)
        finally:
            db.close()
        self.assertEqual(sorted(os.listdir(folder)), ['w.db'])

    def test_with_wal_and_no_shm_reads_the_log(self):
        _folder, path = self._stage('wal_no_shm', ['', '-wal'])
        self.assertEqual(ilapfuncs.get_sqlite_db_uri_query(path), 'mode=ro')
        db = ilapfuncs.open_sqlite_db_readonly(path)
        self.assertIsNotNone(db)
        self.assertEqual(_count(db), 4)

    def test_attach_with_wal_reads_the_log(self):
        _folder, path = self._stage('wal_attach', ['', '-wal'])
        plain = os.path.join(self.base, 'plain.db')
        _make_db(plain, [1])
        db = ilapfuncs.open_sqlite_db_readonly(plain)
        try:
            db.execute(ilapfuncs.attach_sqlite_db_readonly(path, 'other'))
            self.assertEqual(db.execute('SELECT count(*) FROM other.t').fetchone()[0], 4)
        finally:
            db.close()

    def test_journal_beside_it_keeps_mode_ro(self):
        folder, path = self._stage('journal', [''])
        with open(os.path.join(folder, 'w.db-journal'), 'wb'):
            pass
        self.assertEqual(ilapfuncs.get_sqlite_db_uri_query(path), 'mode=ro')

    def test_rollback_mode_keeps_mode_ro(self):
        path = os.path.join(self.base, 'rollback.db')
        _make_db(path, [1])
        self.assertEqual(ilapfuncs.get_sqlite_db_uri_query(path), 'mode=ro')

    def test_missing_or_non_sqlite_file_keeps_mode_ro(self):
        missing = os.path.join(self.base, 'missing.db')
        self.assertEqual(ilapfuncs.get_sqlite_db_uri_query(missing), 'mode=ro')
        other = os.path.join(self.base, 'notes.txt')
        with open(other, 'w', encoding='utf-8') as handle:
            handle.write('not a database')
        self.assertEqual(ilapfuncs.get_sqlite_db_uri_query(other), 'mode=ro')


if __name__ == '__main__':
    unittest.main()
