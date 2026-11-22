"""Health joins to units, series statistics and achievement templates keep one row per record."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.artifacts.health import (  # noqa: E402
    health_achievements, health_headphone_audio_levels, health_heart_rate,
    health_resting_heart_rate)


def names(headers):
    return [header[0] if isinstance(header, tuple) else header for header in headers]


def context_for(folder):
    return SimpleNamespace(get_source_file_path=lambda name: str(folder / name),
                           lookup_metadata=lambda *_args: 'Model',
                           get_apple_os_version=lambda *_args: 'Version')


def rows_of(function, folder):
    headers, rows, _source = function.__wrapped__(context_for(folder))
    labels = names(headers)
    return labels, [dict(zip(labels, row)) for row in rows]


class HealthSampleAndTemplateJoins(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = pathlib.Path(self.temporary.name)
        con = sqlite3.connect(self.folder / 'healthdb_secure.sqlite')
        con.executescript('''
            CREATE TABLE samples(data_id INTEGER, start_date REAL, end_date REAL, data_type INTEGER);
            CREATE TABLE objects(data_id INTEGER, creation_date REAL, type INTEGER, provenance INTEGER);
            CREATE TABLE quantity_samples(data_id INTEGER, quantity REAL, original_quantity REAL,
                original_unit INTEGER);
            CREATE TABLE unit_strings(ROWID INTEGER PRIMARY KEY, unit_string TEXT);
            CREATE TABLE quantity_sample_statistics(owner_id INTEGER, min REAL, max REAL);
            CREATE TABLE data_provenances(source_id INTEGER, device_id INTEGER, source_version TEXT,
                tz_name TEXT);
            CREATE TABLE ACHAchievementsPlugin_earned_instances(ROWID INTEGER PRIMARY KEY,
                template_unique_name TEXT, earned_date TEXT, created_date REAL,
                value_in_canonical_unit REAL, value_canonical_unit TEXT);
            CREATE TABLE ACHAchievementsPlugin_templates(unique_name TEXT, source_name TEXT);

            INSERT INTO data_provenances VALUES (1, 1, 'version', 'UTC');
            INSERT INTO unit_strings(ROWID, unit_string) VALUES (7, 'count/min'), (8, 'dBASPL');
            INSERT INTO samples VALUES (1, 100, 101, 5), (2, 200, 201, 5), (3, 300, 301, 173),
                (4, 400, 401, 118);
            INSERT INTO objects VALUES (1, 102, 1, 1), (2, 202, 1, 1), (3, 302, 1, 1), (4, 402, 1, 1);
            INSERT INTO quantity_samples VALUES (1, 1.25, 75, 7), (2, 1.5, NULL, NULL),
                (3, 60, 60, 8), (4, 55, 55, 7);
            INSERT INTO quantity_sample_statistics VALUES (1, 1.0, 2.0), (3, 50, 70);
            INSERT INTO ACHAchievementsPlugin_templates VALUES ('Known', 'Template Source');
            INSERT INTO ACHAchievementsPlugin_earned_instances VALUES
                (1, 'Known', '2024-01-01', 100, 5, 'count'),
                (2, 'NotInStore', '2024-01-02', 200, 6, 'count');
        ''')
        con.commit()
        con.close()
        con = sqlite3.connect(self.folder / 'healthdb.sqlite')
        con.executescript('''
            CREATE TABLE sources(name TEXT, bundle_id TEXT, source_options INTEGER);
            CREATE TABLE source_devices(name TEXT, manufacturer TEXT, hardware TEXT);
            INSERT INTO sources VALUES ('Source', 'example.bundle', 0);
            INSERT INTO source_devices VALUES ('Device', 'Maker', 'Hardware');
        ''')
        con.commit()
        con.close()

    def test_unit_and_statistics_joins_fill_their_columns(self):
        _labels, rows = rows_of(health_heart_rate, self.folder)
        self.assertEqual(len(rows), 2)
        first, second = rows
        self.assertEqual(first['Original Value (as stored)'], 75)
        self.assertEqual(first['Original Unit (as stored)'], 'count/min')
        self.assertEqual((first['Series Min (as stored)'], first['Series Max (as stored)']), (1.0, 2.0))
        self.assertIsNone(second['Original Unit (as stored)'])
        self.assertIsNone(second['Series Min (as stored)'])

    def test_joins_do_not_cross_data_types(self):
        _labels, rows = rows_of(health_headphone_audio_levels, self.folder)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Original Unit (as stored)'], 'dBASPL')
        self.assertEqual(rows[0]['Series Max (as stored)'], 70)

    def test_headphone_parent_note_needs_points_in_sqlite(self):
        con = sqlite3.connect(self.folder / 'healthdb_secure.sqlite')
        con.executescript('''
            CREATE TABLE quantity_sample_series(data_id INTEGER, hfd_key INTEGER, count INTEGER);
            CREATE TABLE quantity_series_data(series_identifier INTEGER, timestamp REAL, value REAL);
            INSERT INTO quantity_sample_series VALUES (3, 33, 1);
        ''')
        con.commit()
        _labels, rows = rows_of(health_headphone_audio_levels, self.folder)
        self.assertEqual(rows[0]['Record Kind'], 'series parent')
        self.assertEqual(rows[0]['Series Parent Value Note'], '')
        con.execute('INSERT INTO quantity_series_data VALUES (33, 300, 60)')
        con.commit()
        con.close()
        _labels, rows = rows_of(health_headphone_audio_levels, self.folder)
        self.assertIn('equivalent continuous level', rows[0]['Series Parent Value Note'])

    def test_source_stays_and_bundle_id_is_left_to_provenances(self):
        for function in (health_heart_rate, health_headphone_audio_levels,
                         health_resting_heart_rate):
            with self.subTest(function=function.__name__):
                labels, rows = rows_of(function, self.folder)
                self.assertNotIn('Bundle ID', labels)
                self.assertIn('Provenance ROWID', labels)
                self.assertEqual(rows[0]['Source'], 'Source')
                self.assertNotIn('example.bundle', [str(value) for value in rows[0].values()])

    def test_template_join_keeps_earned_rows_without_a_template(self):
        _labels, rows = rows_of(health_achievements, self.folder)
        self.assertEqual(len(rows), 2)
        self.assertEqual((rows[0]['Template Source Name'], rows[0]['Template In Store']),
                         ('Template Source', 'yes'))
        self.assertEqual((rows[1]['Template Source Name'], rows[1]['Template In Store']),
                         (None, 'no'))


if __name__ == '__main__':
    unittest.main()
