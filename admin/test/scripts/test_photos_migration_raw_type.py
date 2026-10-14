"""Stored migration values, optional-column projection and WAL selection."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts.photosMigration import photos_migration


COLUMNS = ('Z_PK', 'Z_ENT', 'Z_OPT', 'ZMIGRATIONDATE', 'ZINDEX',
           'ZMIGRATIONTYPE', 'ZFORCEREBUILDREASON', 'ZSOURCEMODELVERSION',
           'ZMODELVERSION', 'ZOSVERSION', 'ZORIGIN', 'ZSTOREUUID',
           'ZGLOBALKEYVALUES')


def write_fixture(path, values, affinity='', missing=(), wal=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    if wal:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
    columns = [c for c in COLUMNS if c not in missing]
    db.execute('CREATE TABLE ZMIGRATIONHISTORY (' + ','.join(
        c + (' ' + affinity if c == 'ZMIGRATIONTYPE' else '')
        for c in columns) + ')')
    if wal:
        db.commit()
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    for i, value in enumerate(values):
        row = [i + 1, 9, 1, 700000000 + i, i, value, 'reason',
               'source', 'model', '21D50', 'origin', 'uuid', b'global']
        db.execute('INSERT INTO ZMIGRATIONHISTORY VALUES (' +
                   ','.join('?' for _ in columns) + ')',
                   [v for c, v in zip(COLUMNS, row) if c in columns])
    db.commit()
    return db


def context(paths):
    return SimpleNamespace(get_files_found=lambda: [str(p) for p in paths],
                           get_apple_os_version=lambda build: 'mapped:' + str(build))


class TestPhotosMigrationRawType(unittest.TestCase):
    def test_storage_classes_and_other_fields(self):
        values = [None, 0, 1, 2, 3, -1, 99, -(2**63), 2**63 - 1,
                  0.0, 1.5, '1', '', 'unknown', '雪', b'', b'\x00\xff']
        with tempfile.TemporaryDirectory() as tmp:
            for affinity in ['', 'INTEGER', 'TEXT']:
                path = Path(tmp) / (affinity or 'NONE') / 'Photos.sqlite'
                writer = write_fixture(path, values, affinity)
                writer.close()
                with sqlite3.connect(path) as db:
                    stored = db.execute('SELECT ZMIGRATIONTYPE FROM '
                                        'ZMIGRATIONHISTORY ORDER BY '
                                        'ZMIGRATIONDATE').fetchall()
                _, rows, source = photos_migration.__wrapped__(context([path]))
                self.assertEqual(source, str(path))
                self.assertEqual(len(rows), len(values))
                for i, (row, raw) in enumerate(zip(rows, stored)):
                    self.assertEqual(len(row), 10)
                    self.assertIs(type(row[2]), type(raw[0]))
                    self.assertEqual(row[2], raw[0])
                    self.assertEqual(row[1], i)
                    self.assertEqual(row[3:], ('reason', 'source', 'model',
                                              '21D50', 'mapped:21D50',
                                              'origin', 'uuid'))

    def test_missing_columns_and_first_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / 'a/Photos.sqlite'
            second = Path(tmp) / 'b/Photos.sqlite'
            write_fixture(first, [1, 1], missing=('ZMIGRATIONTYPE',
                                                'ZSOURCEMODELVERSION')).close()
            write_fixture(second, [99]).close()
            _, rows, source = photos_migration.__wrapped__(context([first, second, first]))
            self.assertEqual(source, str(first))
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(r[2] is None and r[4] is None for r in rows))
            _, rows, source = photos_migration.__wrapped__(context([second, first]))
            self.assertEqual(source, str(second))
            self.assertEqual([r[2] for r in rows], [99])

    def test_committed_wal_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'Photos.sqlite'
            writer = write_fixture(path, [0, 99, None], wal=True)
            try:
                self.assertGreater(Path(str(path) + '-wal').stat().st_size, 0)
                _, rows, _ = photos_migration.__wrapped__(context([path]))
                self.assertEqual([r[2] for r in rows], [0, 99, None])
            finally:
                writer.close()

    def test_null_zero_dates_and_repeated_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'Photos.sqlite'
            writer = write_fixture(path, [1, 1, 1, 1])
            writer.execute('UPDATE ZMIGRATIONHISTORY SET ZMIGRATIONDATE = '
                           'CASE WHEN Z_PK = 1 THEN NULL WHEN Z_PK = 2 '
                           'THEN 0 ELSE 700000000 END')
            writer.commit()
            writer.close()
            _, rows, _ = photos_migration.__wrapped__(context([path]))
            self.assertEqual(len(rows), 4)
            self.assertIsNone(rows[0][0])
            self.assertEqual(rows[1][0], 0)
            self.assertEqual(rows[2][0], rows[3][0])
            self.assertEqual([r[2] for r in rows], [1, 1, 1, 1])
