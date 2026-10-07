"""MapsSync raw entities preserve SQLite values without changing fixed labels."""
import inspect
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import mapsSync


def make_store(path, layout, values, affinity='', with_entity=True, wal=False):
    """Build query schemas and optionally leave committed rows in a WAL."""
    connection = sqlite3.connect(path)
    columns = ['Z_PK', 'ZCREATETIME', 'ZMODIFICATIONTIME', 'ZQUERY', 'ZLATITUDE',
               'ZLONGITUDE', 'ZMAPITEM']
    if with_entity:
        columns.append('Z_ENT' + (' ' + affinity if affinity else ''))
    if layout == 'modern':
        columns += ['ZLOCATIONDISPLAY', 'ZLATITUDE1', 'ZLONGITUDE1', 'ZROUTEREQUESTSTORAGE']
    connection.execute('CREATE TABLE ZHISTORYITEM (' + ','.join(columns) + ')')
    if layout != 'basic':
        extra = 'ZMAPITEMSTORAGE' if layout == 'modern' else 'ZNAME'
        connection.execute('CREATE TABLE ZMIXINMAPITEM (Z_PK,' + extra + ')')
        connection.executemany('INSERT INTO ZMIXINMAPITEM VALUES (?,?)',
                               [(1, None if layout == 'modern' else 'first'),
                                (1, None if layout == 'modern' else 'second')])
    connection.execute('CREATE TABLE Z_PRIMARYKEY (Z_ENT,Z_NAME)')
    connection.execute("INSERT INTO Z_PRIMARYKEY VALUES (14,'UnrelatedEntity')")
    connection.commit()
    if wal:
        connection.execute('PRAGMA journal_mode=WAL')
        connection.execute('PRAGMA wal_autocheckpoint=0')
    for number, entity in enumerate(values):
        row = [number, 700000000 + number, 700000001 + number, 'query', 40, -74,
               99 if number == len(values)-1 else 1]
        if with_entity:
            row.append(entity)
        if layout == 'modern':
            row += ['display', 41, -73, None]
        connection.execute('INSERT INTO ZHISTORYITEM VALUES (' +
                           ','.join('?' for _ in row) + ')', row)
    connection.commit()
    return connection


class TestMapsSyncRawEntities(unittest.TestCase):
    """Check native rows against an independent SQLite cursor projection."""

    def check_store(self, layout, with_entity=True, affinity='', wal=False):
        with tempfile.TemporaryDirectory() as directory:
            main = Path(directory) / 'MapsSync_0.0.1'
            values = [None, 0, 0.5, '0', b'\xff', '', b'', -1, 12, 14, 16, 999, 'text', 14]
            connection = make_store(main, layout, values, affinity, with_entity, wal)
            try:
                inputs = [str(main) + '-wal', main, str(main) + '-shm']
                context = SimpleNamespace(get_files_found=lambda: inputs,
                                          get_relative_path=lambda path: Path(path).name)
                headers, rows, source = inspect.unwrap(mapsSync.mapsSync)(context)
                raw = 'h.Z_ENT' if with_entity else 'NULL'
                join = '' if layout == 'basic' else ' LEFT JOIN ZMIXINMAPITEM m ON m.Z_PK=h.ZMAPITEM'
                expected = connection.execute('SELECT h.Z_PK,' + raw +
                                              ' FROM ZHISTORYITEM h' + join).fetchall()
                self.assertEqual([(r[2], r[4]) for r in rows], expected)
                self.assertEqual([type(r[4]) for r in rows], [type(r[1]) for r in expected])
                self.assertEqual(len(rows), 14 if layout == 'basic' else 27)
                self.assertEqual(source, main.name)
                self.assertEqual(len(headers), 13)
                if layout != 'modern':
                    self.assertEqual({r[3] for r in rows}, {'Unknown'})
                else:
                    labels = connection.execute('SELECT h.Z_PK,CASE WHEN h.Z_ENT=14 THEN '
                                                "'coordinates of search' WHEN h.Z_ENT=16 THEN "
                                                "'location search' WHEN h.Z_ENT=12 THEN "
                                                "'navigation journey' END FROM ZHISTORYITEM h" + join).fetchall()
                    self.assertEqual([(r[2], r[3]) for r in rows], labels)
                if wal:
                    self.assertGreater(Path(str(main) + '-wal').stat().st_size, 32)
            finally:
                connection.close()

    def test_modern_wal_storage_classes(self):
        self.check_store('modern', wal=True)

    def test_modern_affinities(self):
        for affinity in ['TEXT', 'INTEGER']:
            with self.subTest(affinity=affinity):
                self.check_store('modern', affinity=affinity)

    def test_ios15_present_and_absent(self):
        for presence in [True, False]:
            with self.subTest(presence=presence):
                self.check_store('ios15', with_entity=presence)

    def test_basic_present_and_absent(self):
        for presence in [True, False]:
            with self.subTest(presence=presence):
                self.check_store('basic', with_entity=presence)

    def test_real_zero_retains_real_storage_type(self):
        with tempfile.TemporaryDirectory() as directory:
            main = Path(directory) / 'MapsSync_0.0.1'
            connection = make_store(main, 'basic', [0.0])
            connection.close()
            context = SimpleNamespace(get_files_found=lambda: [main],
                                      get_relative_path=lambda path: Path(path).name)
            _, rows, _ = inspect.unwrap(mapsSync.mapsSync)(context)
            self.assertEqual(rows[0][4], 0.0)
            self.assertIs(type(rows[0][4]), float)

    def test_modern_missing_entity_keeps_existing_query_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            main = Path(directory) / 'MapsSync_0.0.1'
            connection = make_store(main, 'modern', [14], with_entity=False)
            connection.close()
            context = SimpleNamespace(get_files_found=lambda: [main],
                                      get_relative_path=lambda path: Path(path).name)
            _, rows, source = inspect.unwrap(mapsSync.mapsSync)(context)
            self.assertEqual((rows, source), ([], ''))

    def test_empty_store(self):
        with tempfile.TemporaryDirectory() as directory:
            main = Path(directory) / 'MapsSync_0.0.1'
            connection = make_store(main, 'modern', [])
            connection.close()
            context = SimpleNamespace(get_files_found=lambda: [main],
                                      get_relative_path=lambda path: Path(path).name)
            _, rows, source = inspect.unwrap(mapsSync.mapsSync)(context)
            self.assertEqual((rows, source), ([], ''))


if __name__ == '__main__':
    unittest.main()
