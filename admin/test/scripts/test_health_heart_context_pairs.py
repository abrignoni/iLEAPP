"""Deduplicate heart context lookup pairs, preserving samples and series readings."""
import collections
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.artifacts.health import health_heart_rate


class HealthHeartContextPairs(unittest.TestCase):
    def parse(self, os_version):
        with tempfile.TemporaryDirectory() as temporary:
            folder = pathlib.Path(temporary)
            secure = folder / 'healthdb_secure.sqlite'
            source = folder / 'healthdb.sqlite'
            con = sqlite3.connect(secure)
            con.executescript('''
                CREATE TABLE samples(data_id INTEGER, start_date REAL, end_date REAL, data_type INTEGER);
                CREATE TABLE quantity_samples(data_id INTEGER, quantity REAL);
                CREATE TABLE metadata_keys(key TEXT);
                CREATE TABLE metadata_values(object_id INTEGER, key_id INTEGER, numerical_value REAL);
                CREATE TABLE objects(data_id INTEGER, creation_date REAL, type INTEGER, provenance INTEGER);
                CREATE TABLE data_provenances(source_id INTEGER, device_id INTEGER, source_version TEXT, tz_name TEXT);
                CREATE TABLE quantity_sample_series(data_id INTEGER, hfd_key INTEGER, count INTEGER);
                CREATE TABLE quantity_series_data(series_identifier INTEGER, timestamp REAL, value REAL);
                INSERT INTO metadata_keys VALUES ('_HKPrivateHeartRateContext'),
                    ('_HKPrivateHeartRateContext'), ('Unrelated');
                INSERT INTO data_provenances VALUES (1, 1, 'version', 'UTC');
                INSERT INTO metadata_values VALUES (1,1,1),(1,1,1),(1,2,1),(1,1,8),(1,3,99),
                    (3,1,NULL),(3,1,NULL),(4,1,2),(4,1,2),(4,2,11);
                INSERT INTO quantity_sample_series VALUES (4,44,2);
                INSERT INTO quantity_series_data VALUES (44,400,2),(44,400,2);
            ''')
            for index in range(1, 6):
                con.execute('INSERT INTO samples VALUES (?,?,?,5)', (index, index * 100, index * 100 + 1))
                con.execute('INSERT INTO objects VALUES (?,?,?,1)', (index, index * 100 + 2, 2 if index == 5 else 1))
                con.execute('INSERT INTO quantity_samples VALUES (?,1)', (index,))
            con.commit()
            con.close()
            con = sqlite3.connect(source)
            con.executescript('''
                CREATE TABLE sources(name TEXT, source_options INTEGER);
                CREATE TABLE source_devices(name TEXT, manufacturer TEXT, hardware TEXT);
                INSERT INTO sources VALUES ('Source', 0);
                INSERT INTO source_devices VALUES ('Device', 'Maker', 'Hardware');
            ''')
            con.commit()
            con.close()
            context = SimpleNamespace(get_source_file_path=lambda name: str(folder / name),
                                      get_installed_os_version=lambda: os_version,
                                      lookup_metadata=lambda *_args: 'Model')
            return health_heart_rate.__wrapped__(context)

    def test_series_and_different_contexts_survive_identical_pairs(self):
        headers, rows, _ = self.parse('17.3')
        self.assertEqual(headers[:2], (('Date', 'datetime'), ('Date added to Health', 'datetime')))
        self.assertEqual(headers[-1], 'Heart Rate Context Value')
        self.assertEqual(len(rows), 8)
        self.assertEqual(collections.Counter(row[-1] for row in rows),
                         collections.Counter({1.0: 1, 8.0: 1, None: 2, 2.0: 2, 11.0: 2}))
        background = [row for row in rows if row[3] == 'Background']
        self.assertEqual({row[-1] for row in background}, {1.0, 8.0})
        self.assertEqual(len(background), 2)
        self.assertEqual({row[2] for row in rows if row[-1] in (2.0, 11.0)}, {120})
        series = [row for row in rows if row[-1] == 2.0]
        self.assertEqual(series[0], series[1])  # Legitimate repeated series records remain.
        self.assertNotIn(99.0, [row[-1] for row in rows])

    def test_older_os_keeps_distinct_contexts_and_dates_first(self):
        headers, rows, _ = self.parse('14.3')
        self.assertEqual(headers[:3], (('Start Date', 'datetime'), ('End Date', 'datetime'),
                                      ('Date added to Health', 'datetime')))
        self.assertEqual(len(rows), 6)
        self.assertEqual(collections.Counter(row[-1] for row in rows),
                         collections.Counter({1.0: 1, 8.0: 1, None: 2, 2.0: 1, 11.0: 1}))
        self.assertEqual({row[3] for row in rows}, {60})


if __name__ == '__main__':
    unittest.main()
