"""Actual SQLite name storage classes, joins and WAL states for Kik users."""
from collections import Counter
import hashlib
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from scripts.artifacts import kikLocaladmin as module


class Context:
    def __init__(self, files):
        self.files = files

    def get_files_found(self):
        return self.files


def name_cases():
    return [None, '', 'A', ' ', '0', '1', '-1', 'é', '\x00', 0, 1, -1,
            0.0, 0.5, b'', b'0', b'\xff', b'\x00']


def write_database(path, wal=False, no_affinity=False, empty=False):
    """Referenced genuine column affinities/keys, or explicit no-affinity stress variant."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    if wal:
        db.execute('pragma journal_mode=WAL')
        db.execute('pragma wal_autocheckpoint=0')
    name_type = '' if no_affinity else 'VARCHAR'
    db.execute('CREATE TABLE ZKIKUSER (Z_PK INTEGER PRIMARY KEY, ZFIRSTNAME ' + name_type +
               ', ZLASTNAME ' + name_type + ', ZDISPLAYNAME VARCHAR, ZUSERNAME VARCHAR, '
               'ZPPURL VARCHAR, ZGROUPTAG VARCHAR, ZJID VARCHAR, ZFLAGS INTEGER)')
    member_key = '' if no_affinity else ', PRIMARY KEY(Z_9MEMBERSINVERSE,Z_9MEMBERS)'
    db.execute('CREATE TABLE Z_9MEMBERS(Z_9MEMBERSINVERSE INTEGER,Z_9MEMBERS INTEGER' + member_key + ')')
    db.execute('CREATE TABLE Z_9ADMINSINVERSE(Z_9ADMINS INTEGER,Z_9ADMINSINVERSE INTEGER,'
               'PRIMARY KEY(Z_9ADMINS,Z_9ADMINSINVERSE))')
    db.execute('CREATE TABLE ZKIKUSEREXTRA(Z_PK INTEGER PRIMARY KEY,ZUSER INTEGER,'
               'ZENTITYUSERDATA BLOB,ZROSTERENTRYDATA BLOB)')
    db.commit()
    if wal:
        db.execute('pragma wal_checkpoint(TRUNCATE)')
    if empty:
        return db
    rows = []
    for first in name_cases():
        for last in name_cases():
            ident = len(rows) + 1
            rows.append((ident, first, last, f'display {ident}', 'user & <é>', None,
                         None, None, [258, 0, None][ident % 3]))
    rows += [(5000, None, None, 'group & <one>', None, 'group-url', 'tag', 'jid', 0),
             (5001, None, None, 'group two', None, None, b'raw-tag', 'jid2', 258)]
    db.executemany('INSERT INTO ZKIKUSER VALUES(?,?,?,?,?,?,?,?,?)', rows)
    # First-name-only alphabetic user, with two member links, two admin links, two extras.
    joined_user = 2 * len(name_cases()) + 1
    db.executemany('INSERT INTO Z_9MEMBERS VALUES(?,?)', [(5000, joined_user), (5001, joined_user)])
    if no_affinity:
        db.execute('INSERT INTO Z_9MEMBERS VALUES(?,?)', (5000, joined_user))
    db.executemany('INSERT INTO Z_9ADMINSINVERSE VALUES(?,?)', [(joined_user, 9000), (joined_user, 9001)])
    db.executemany('INSERT INTO ZKIKUSEREXTRA VALUES(?,?,?,?)',
                   [(ident * 10, ident, b'\x00\xff' if ident % 2 else None,
                     0 if ident % 2 else 'raw & <text>') for ident in range(1, 325)] +
                   [(joined_user * 10 + 1, joined_user, b'', None)])
    # A selected unmatched group link keeps its blank lookup fields.
    db.execute('INSERT INTO Z_9MEMBERS VALUES(?,?)', (9999, 3))
    db.commit()
    return db


class KikNamePredicateTest(unittest.TestCase):
    def test_actual_varchar_matrix_and_join_multiplicity(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'kik.sqlite'
            db = write_database(path)
            storage = db.execute('select typeof(ZFIRSTNAME),count(*) from ZKIKUSER where Z_PK<5000 '
                                 'group by 1').fetchall()
            db.close()
            headers, rows, source = module.kikLocaladmin.__wrapped__(Context([path]))
            expected_ids = [i * 18 + j + 1 for i, first in enumerate(name_cases())
                            for j, last in enumerate(name_cases())
                            if (first is not None and first != '') or (last is not None and last != '')]
            counts = Counter(row[0] for row in rows)
            self.assertEqual(set(counts), set(expected_ids))
            self.assertEqual(len(rows), 327)
            self.assertEqual(counts[37], 8)
            self.assertEqual(counts[3], 1)
            self.assertEqual(next(row for row in rows if row[0] == 3)[6:10], ('', '', '', ''))
            self.assertEqual(dict(storage), {'blob': 72, 'null': 18, 'text': 234})
            self.assertEqual(len(headers), 12)
            self.assertEqual(source, str(path))
            self.assertEqual({type(row[10]) for row in rows}, {bytes, type(None)})
            self.assertEqual({type(row[11]) for row in rows}, {int, str, type(None)})

    def test_no_affinity_zero_blob_and_repeated_links(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'kik.sqlite'
            db = write_database(path, no_affinity=True)
            storage = dict(db.execute('select typeof(ZFIRSTNAME),count(*) from ZKIKUSER '
                                      'where Z_PK<5000 group by 1').fetchall())
            db.close()
            _, rows, _ = module.kikLocaladmin.__wrapped__(Context([path]))
            self.assertEqual(storage, {'blob': 72, 'integer': 54, 'null': 18, 'real': 36, 'text': 144})
            self.assertEqual(len(rows), 331)
            self.assertEqual(Counter(row[0] for row in rows)[37], 12)
            self.assertTrue(any(count == 2 for count in Counter(rows).values()))
            self.assertIn(253, {row[0] for row in rows})  # Empty BLOB first, NULL last.
            self.assertIn(163, {row[0] for row in rows})  # Integer zero first, NULL last.

    def test_actual_wal_first_main_empty_and_protected_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'writer/kik.sqlite'
            writer = write_database(path, wal=True)
            control = root / 'main-only.sqlite'
            shutil.copy2(path, control)
            db = sqlite3.connect(f'file:{control}?mode=ro', uri=True)
            self.assertEqual(db.execute('select count(*) from ZKIKUSER').fetchone()[0], 0)
            db.close()
            target = root / 'protected'
            target.mkdir()
            for p in path.parent.iterdir():
                shutil.copy2(p, target / p.name)
                (target / p.name).chmod(0o444)
            target.chmod(0o555)
            other = root / 'empty/kik.sqlite'
            db = write_database(other, empty=True)
            db.close()
            hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()}
            _, rows, source = module.kikLocaladmin.__wrapped__(
                Context([target / 'kik.sqlite-wal', target / 'kik.sqlite', other]))
            self.assertEqual(len(rows), 327)
            self.assertEqual(source, str(target / 'kik.sqlite'))
            self.assertEqual(hashes, {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in target.iterdir()})
            _, rows, source = module.kikLocaladmin.__wrapped__(Context([other, target / 'kik.sqlite']))
            self.assertEqual(rows, [])
            self.assertEqual(source, str(other))
            self.assertEqual(module.kikLocaladmin.__wrapped__(Context([]))[1:], ([], ''))
            writer.close()
            target.chmod(0o755)


if __name__ == '__main__':
    unittest.main()
