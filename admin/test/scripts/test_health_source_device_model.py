"""Actual SQLite coverage for stored model values and unchanged source selection."""
import datetime
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from scripts.artifacts.health import health_source_devices


class TestHealthSourceDeviceModel(unittest.TestCase):
    """Check raw storage classes, optional layouts and the existing selectors."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def database(self, name, models, optional=(), affinity='', wal=False):
        """Create a writer-owned SQLite state, keeping live WAL connection open."""
        path = self.root / name / 'Health/healthdb.sqlite'
        path.parent.mkdir(parents=True)
        connection = sqlite3.connect(path)
        self.addCleanup(connection.close)
        if wal:
            connection.execute('PRAGMA journal_mode=WAL')
            connection.execute('PRAGMA wal_autocheckpoint=0')
        columns = ['creation_date', 'name', 'manufacturer', 'model ' + affinity,
                   'hardware', 'firmware', 'software', 'localIdentifier', *optional]
        connection.execute('CREATE TABLE source_devices (' + ','.join(columns) + ')')
        connection.commit()
        if wal:
            connection.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        for model in models:
            row = [700000000.75, 'Device', 'Maker', model, 'fixture-id', 'fw', 'sw',
                   'local-tacl', *[17 if c == 'sync_provenance' else None for c in optional]]
            connection.execute('INSERT INTO source_devices VALUES (' +
                               ','.join('?' for _ in row) + ')', row)
        connection.commit()
        return path, connection

    @staticmethod
    def rows(path):
        """Use a deterministic fixture-only metadata lookup."""
        context = SimpleNamespace(get_source_file_path=lambda _: str(path),
                                  lookup_metadata=lambda _, key: 'lookup:' + str(key))
        return health_source_devices.__wrapped__(context)

    def test_four_optional_shapes_preserve_raw_native_values(self):
        """Known mapping, NULL, numeric, text and BLOB stay beside mapped Model."""
        values = ['0x0034', None, 0, 2.5, '', b'\xff\x00']
        for index, optional in enumerate([(), ('sync_provenance',), ('sync_identity',),
                                          ('sync_provenance', 'sync_identity')]):
            with self.subTest(optional=optional):
                path, _ = self.database(str(index), values, optional)
                headers, rows, source = self.rows(path)
                self.assertEqual(len(headers), 10 + len(optional))
                self.assertEqual([r[4] for r in rows], values)
                self.assertEqual([type(r[4]) for r in rows], [type(v) for v in values])
                self.assertEqual(rows[0][3], 'Apple Watch Series 5')
                self.assertEqual(rows[0][5:10], ('fixture-id', 'lookup:fixture-id',
                                               'fw', 'sw', 'local'))
                self.assertEqual(rows[0][0], datetime.datetime(2023, 3, 8, 20, 26, 40,
                                                               tzinfo=datetime.timezone.utc))
                self.assertEqual(source, str(path))

    def test_declared_affinity_matches_direct_stored_sql_values(self):
        """The raw model follows actual SQLite affinity rather than input literals."""
        for affinity in ['', 'TEXT', 'INTEGER']:
            with self.subTest(affinity=affinity):
                path, connection = self.database('affinity' + affinity,
                                                  [0, '0', 2.5, '0x0034'], affinity=affinity)
                expected = connection.execute('SELECT model FROM source_devices').fetchall()
                rows = self.rows(path)[1]
                self.assertEqual([(r[4],) for r in rows], expected)
                self.assertEqual([type(r[4]) for r in rows], [type(r[0]) for r in expected])

    def test_existing_like_null_and_suffix_policy_and_repeats(self):
        """Wildcard/NULL exclusion and terminal suffix trimming stay unchanged."""
        path, connection = self.database('filters', ['unknown', 'unknown'])
        for name, local in [('__NONE__', 'ok'), ('aaNONEbb', 'ok'), (None, 'ok'),
                            ('ok', None), ('ok', 'aaNONEbb')]:
            connection.execute('INSERT INTO source_devices VALUES (?,?,?,?,?,?,?,?)',
                               (700000000, name, 'Maker', 'filtered', '', '', '', local))
        connection.commit()
        rows = self.rows(path)[1]
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], rows[1])
        self.assertEqual([r[9] for r in rows], ['local', 'local'])

    def test_own_live_wal_differs_from_main_only(self):
        """Own WAL records disappear from a main-only derivative."""
        live, _ = self.database('wal', ['0x200A'], wal=True)
        main = self.root / 'main/Health/healthdb.sqlite'
        main.parent.mkdir(parents=True)
        shutil.copyfile(live, main)
        self.assertEqual(self.rows(live)[1][0][3:5], ('AirPods Max', '0x200A'))
        self.assertEqual(self.rows(main)[1], [])


if __name__ == '__main__':
    unittest.main()
