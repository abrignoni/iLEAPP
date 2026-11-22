"""Heart rate rows: one per sample, series points after their parent, contexts kept as stored."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.artifacts.health import health_heart_rate, health_provenances
from scripts.context import Context


def names(headers):
    return [header[0] if isinstance(header, tuple) else header for header in headers]


def context_for(folder):
    return SimpleNamespace(get_source_file_path=lambda name: str(folder / name),
                           lookup_metadata=lambda *_args: 'Model',
                           get_apple_os_version=lambda *_args: 'Version')


class HealthHeartContextPairs(unittest.TestCase):
    def parse(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = pathlib.Path(temporary)
            con = sqlite3.connect(folder / 'healthdb_secure.sqlite')
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
                INSERT INTO quantity_sample_series VALUES (4,44,3);
                INSERT INTO quantity_series_data VALUES (44,400,2),(44,401,2);
            ''')
            for index in range(1, 6):
                con.execute('INSERT INTO samples VALUES (?,?,?,5)', (index, index * 100, index * 100 + 1))
                con.execute('INSERT INTO objects VALUES (?,?,?,1)', (index, index * 100 + 2, 2 if index == 5 else 1))
                if index != 5:
                    con.execute('INSERT INTO quantity_samples VALUES (?,1)', (index,))
            con.commit()
            con.close()
            con = sqlite3.connect(folder / 'healthdb.sqlite')
            con.executescript('''
                CREATE TABLE sources(name TEXT, source_options INTEGER);
                CREATE TABLE source_devices(name TEXT, manufacturer TEXT, hardware TEXT);
                INSERT INTO sources VALUES ('Source', 0);
                INSERT INTO source_devices VALUES ('Device', 'Maker', 'Hardware');
            ''')
            con.commit()
            con.close()
            headers, rows, _ = health_heart_rate.__wrapped__(context_for(folder))
            return names(headers), [dict(zip(names(headers), row)) for row in rows]

    def test_one_row_per_sample_with_points_after_their_parent(self):
        headers, rows = self.parse()
        self.assertEqual(headers[:4], ['Start', 'End', 'Record Added or Deleted', 'Record Kind'])
        self.assertEqual([row['Record Kind'] for row in rows],
                         ['sample', 'sample', 'sample', 'series parent', 'series point',
                          'series point', 'deleted sample record'])
        parent = rows[3]
        self.assertEqual((parent['Series Points Declared'], parent['Series Points Read']), (3, 2))
        self.assertIn('2 of 3 declared points in SQLite', parent['Series Point Status'])
        self.assertEqual({row['Heart Rate (BPM)'] for row in rows[4:6]}, {120.0})
        self.assertEqual({row['Value (count/s, as stored)'] for row in rows[4:6]}, {2.0})

    def test_distinct_contexts_are_kept_and_named_only_when_sourced(self):
        _headers, rows = self.parse()
        self.assertEqual(rows[0]['Heart Rate Context'], 'Background; Background Tachogram')
        self.assertEqual(rows[0]['Heart Rate Context Value'], '1.0; 8.0')
        self.assertEqual(rows[0]['Other Metadata (as stored)'], 'Unrelated=99.0')
        self.assertEqual(rows[1]['Heart Rate Context'], '')
        for row in rows[3:6]:  # A point repeats its parent's context.
            self.assertEqual(row['Heart Rate Context'], 'Streaming PPG; not established')
            self.assertEqual(row['Heart Rate Context Value'], '2.0; 11.0')

    def test_deleted_sample_record_has_no_value(self):
        _headers, rows = self.parse()
        deleted = rows[-1]
        self.assertEqual(deleted['Record Kind'], 'deleted sample record')
        self.assertIsNone(deleted['Value (count/s, as stored)'])
        self.assertEqual(deleted['Heart Rate (BPM)'], '')

    def test_unreadable_secure_database_is_not_reported_as_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = pathlib.Path(temporary)
            (folder / 'healthdb_secure.sqlite').write_bytes(b'\0' * 8)
            con = sqlite3.connect(folder / 'healthdb.sqlite')
            con.executescript('''
                CREATE TABLE sources(name TEXT, bundle_id TEXT, product_type TEXT, mod_date REAL, deleted INTEGER);
                CREATE TABLE source_devices(creation_date REAL, name TEXT, manufacturer TEXT, model TEXT,
                    hardware TEXT, firmware TEXT, software TEXT, localIdentifier TEXT, FDAUDI TEXT);
                INSERT INTO sources VALUES ('Source', 'bundle', 'product', 100, 0);
                INSERT INTO source_devices VALUES (200, 'Device', 'Maker', 'Model', 'Hardware', NULL, NULL, NULL, NULL);
            ''')
            con.commit()
            con.close()
            _headers, heart, _ = health_heart_rate.__wrapped__(context_for(folder))
            headers, registered, _ = health_provenances.__wrapped__(context_for(folder))
        self.assertEqual(heart, [])
        kinds = [dict(zip(names(headers), row))['Record Kind'] for row in registered]
        self.assertEqual(kinds, ['registered source', 'registered device'])

    def test_null_product_type_gives_a_blank_os_version(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = pathlib.Path(temporary)
            con = sqlite3.connect(folder / 'healthdb_secure.sqlite')
            con.executescript('''
                CREATE TABLE data_provenances(origin_product_type TEXT, origin_build TEXT,
                    local_product_type TEXT, local_build TEXT);
                INSERT INTO data_provenances VALUES (NULL, 'BUILD', NULL, 'BUILD');
            ''')
            con.commit()
            con.close()
            context = context_for(folder)
            context.get_apple_os_version = Context.get_apple_os_version
            with self.assertRaises(TypeError):  # The shared lookup does not accept NULL.
                context.get_apple_os_version('BUILD', None)
            headers, rows, _ = health_provenances.__wrapped__(context)
        self.assertEqual(len(rows), 1)
        row = dict(zip(names(headers), rows[0]))
        self.assertEqual((row['Origin OS Version'], row['Local OS Version']), ('', ''))


if __name__ == '__main__':
    unittest.main()
