"""Coherent terminal gaps using actual SQLite message stores."""
import ast
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from scripts.artifacts import SMSmissingROWIDs as parser


def query():
    """Use the actual parser query without mocking SQLite."""
    tree = ast.parse(Path(parser.__file__).read_text(encoding='utf-8'))
    return next(n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)
                and isinstance(n.value, str) and 'WITH LastROWID' in n.value)


class TerminalRowidTest(unittest.TestCase):
    """Terminal records belong to the greatest live ROWID."""

    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE message (id INTEGER PRIMARY KEY AUTOINCREMENT, date, guid)')
        self.db.executemany('INSERT INTO message VALUES (?, ?, ?)',
                            [(1, 200, 'one'), (5, 900, 'five'), (9, 100, 'nine')])

    def tearDown(self):
        self.db.close()

    def test_nonchronological_and_null_anchor(self):
        self.db.execute('INSERT INTO message VALUES (12, 999, "removed")')
        self.db.execute('DELETE FROM message WHERE id=12')
        self.assertEqual(self.db.execute(query()).fetchall(), [
            (200, 900, 'one', 'five', 1, 5, 3),
            (900, 100, 'five', 'nine', 5, 9, 3),
            (100, 'Time of Extraction', 'nine', 'Unknown', 9, 12, 3)])
        self.db.execute('UPDATE message SET date=NULL, guid=NULL WHERE id=9')
        self.assertEqual(self.db.execute(query()).fetchall()[-1],
                         (None, 'Time of Extraction', None, 'Unknown', 9, 12, 3))

    def test_sequence_admission_and_arithmetic(self):
        for value, expected in [(9, None), (8, None), (None, None),
                                ('12', ('12', 3)), ('12tail', ('12tail', 3)),
                                ('unknown', None), (12.5, (12.5, 3.5))]:
            with self.subTest(value=value):
                self.db.execute('UPDATE sqlite_sequence SET seq=? WHERE name="message"', (value,))
                rows = self.db.execute(query()).fetchall()
                self.assertEqual(len(rows), 2 if expected is None else 3)
                if expected is not None:
                    self.assertEqual(rows[-1], (100, 'Time of Extraction', 'nine',
                                               'Unknown', 9, *expected))
        self.db.execute('DELETE FROM sqlite_sequence')
        self.assertEqual(len(self.db.execute(query()).fetchall()), 2)
        self.db.execute('DELETE FROM message')
        self.db.execute('INSERT INTO sqlite_sequence VALUES ("message", 99)')
        self.assertEqual(self.db.execute(query()).fetchall(), [])

    def test_committed_wal_anchor(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sms.db'
            live = sqlite3.connect(path)
            try:
                live.execute('PRAGMA journal_mode=WAL')
                live.execute('PRAGMA wal_autocheckpoint=0')
                live.execute('CREATE TABLE message (id INTEGER PRIMARY KEY AUTOINCREMENT, date, guid)')
                live.execute('INSERT INTO message VALUES (1, 900, "main")')
                live.commit()
                live.execute('PRAGMA wal_checkpoint(TRUNCATE)')
                live.execute('INSERT INTO message VALUES (9, 100, "wal")')
                live.execute('INSERT INTO message VALUES (12, 100, "removed")')
                live.execute('DELETE FROM message WHERE id=12')
                live.commit()
                copy = Path(directory) / 'copy'
                copy.mkdir()
                for suffix in ['', '-wal', '-shm']:
                    shutil.copyfile(str(path) + suffix, copy / ('sms.db' + suffix))
                with sqlite3.connect(copy / 'sms.db') as snapshot:
                    self.assertEqual(snapshot.execute(query()).fetchall()[-1],
                                     (100, 'Time of Extraction', 'wal', 'Unknown', 9, 12, 3))
                with sqlite3.connect('file:' + str(path) + '?immutable=1', uri=True) as main:
                    self.assertEqual(main.execute(query()).fetchall(), [])
            finally:
                live.close()


if __name__ == '__main__':
    unittest.main()
