"""Stored fav values survive SQLite affinity and committed WAL selection."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from scripts.artifacts import megaCloud


class TestMegaRawFav(unittest.TestCase):
    def make_store(self, root, affinity='', missing=False, wal=False):
        path = root / 'megaclient_statecache14_account.db'
        db = sqlite3.connect(path)
        if wal:
            db.execute('CREATE TABLE unrelated (n)')
            db.commit()
            db.execute('PRAGMA journal_mode=WAL')
        fav = '' if missing else ',fav ' + affinity
        db.execute('CREATE TABLE nodes (nodehandle,parenthandle,name,type' + fav + ')')
        values = [None, 0, 1, -1, 2, 0.0, 1.5, '', '0', '1', 'unknown', b'', b'0', b'\x00\xff']
        for n, value in enumerate(values):
            row = (n + 1, -1, 'name' + str(n), 0)
            db.execute('INSERT INTO nodes VALUES (' + ','.join('?' * (4 if missing else 5)) + ')', row if missing else row + (value,))
        db.execute('INSERT INTO nodes SELECT * FROM nodes WHERE nodehandle=1')
        db.commit()
        return path, db

    def test_affinities_missing_and_wal(self):
        for affinity, missing, wal in [('', False, False), ('INTEGER', False, False), ('TEXT', False, False), ('', True, False), ('', False, True)]:
            with self.subTest(affinity=affinity, missing=missing, wal=wal), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                path, db = self.make_store(root, affinity, missing, wal)
                direct = db.execute('SELECT nodehandle,' + ('NULL' if missing else 'fav') + ' FROM nodes').fetchall()
                oracle = dict(direct)
                context = SimpleNamespace(get_files_found=lambda path=path: [str(path)], get_relative_path=lambda p: Path(p).name)
                headers, rows, sources = megaCloud.mega_cloud_files.__wrapped__(context)
                self.assertEqual(headers[12], 'fav (as stored)')
                self.assertEqual(len(rows), len(oracle))
                self.assertEqual(sources, str(path))
                for row, value in zip(rows, oracle.values()):
                    self.assertEqual(len(row), 25)
                    self.assertIs(type(row[12]), type(value))
                    self.assertEqual(row[12], value)
                    self.assertEqual(row[24], path.name)
                db.close()

    def test_conflicting_alias_sorted_first_wins(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            files = []
            for folder, value in [('a', 0), ('b', 1)]:
                target = root / folder
                target.mkdir()
                path, db = self.make_store(target)
                db.execute('UPDATE nodes SET fav=?', (value,))
                db.commit()
                db.close()
                files.append(str(path))
            ctx = SimpleNamespace(get_files_found=lambda: list(reversed(files)), get_relative_path=lambda p: str(Path(p).relative_to(root)))
            _, rows, sources = megaCloud.mega_cloud_files.__wrapped__(ctx)
            self.assertEqual({r[12] for r in rows}, {0})
            self.assertEqual(sources.splitlines(), files)


if __name__ == '__main__':
    unittest.main()
