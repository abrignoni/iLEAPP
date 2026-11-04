"""The 'latitude' and 'longitude' header types: NUMERIC columns, so LAVA sorts coordinates as numbers.

Untyped coordinates are TEXT, so in SQLite's text order -10.5 sorts before -2.25 and 100.1
before 37.2 (LAVA's UINT collation orders them differently, but not by value either). A header
declared ('Latitude', 'latitude') or ('Longitude', 'longitude') gets NUMERIC affinity like a
'number' header: values that read as numbers are stored as REAL or INTEGER, anything else stays
as written text, and the written form of a converted value can change ('37.7700' is 37.77).
"""
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position


class TestLavaCoordinateType(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')

    def tearDown(self):
        if lavafuncs.lava_db is not None:
            lavafuncs.lava_db.close()
            lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write(self, rows):
        headers = [('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Note']
        table_name, column_map, object_columns = lavafuncs.lava_create_sqlite_table('coordinate_artifact', headers)
        lavafuncs.lava_insert_sqlite_data(table_name, rows, object_columns, headers, column_map)
        return table_name, object_columns

    def test_coordinates_map_to_numeric(self):
        self.assertEqual(lavafuncs.get_sql_type('latitude'), 'NUMERIC')
        self.assertEqual(lavafuncs.get_sql_type('longitude'), 'NUMERIC')

    def test_columns_are_declared_numeric_and_listed_as_typed(self):
        table_name, object_columns = self._write([('1.5', '2.5', 'a')])
        declared = {row[1]: row[2] for row in lavafuncs.lava_db.execute(f'PRAGMA table_info("{table_name}")')}
        self.assertEqual((declared['latitude'], declared['longitude'], declared['note']), ('NUMERIC', 'NUMERIC', 'TEXT'))
        self.assertEqual(object_columns, {'latitude': 'latitude', 'longitude': 'longitude'})

    def test_coordinates_sort_as_numbers(self):
        table_name, _ = self._write([('37.2', '-2.25', 'a'), ('-10.5', '100.1', 'b'), ('-2.25', '-10.5', 'c'),
                                     (5.75, 8, 'd')])
        lat = [row[0] for row in lavafuncs.lava_db.execute(f'SELECT "latitude" FROM "{table_name}" ORDER BY "latitude"')]
        lon = [row[0] for row in lavafuncs.lava_db.execute(f'SELECT "longitude" FROM "{table_name}" ORDER BY "longitude"')]
        self.assertEqual(lat, [-10.5, -2.25, 5.75, 37.2])
        self.assertEqual(lon, [-10.5, -2.25, 8, 100.1])

    def test_what_numeric_storage_keeps_and_rewrites(self):
        rows = [('37.7700', '0.0', 'trailing zeros'), ('N/A', '37.774929,-122.419416', 'not one number'),
                ('', None, 'empty and null')]
        table_name, _ = self._write(rows)
        stored = lavafuncs.lava_db.execute(
            f'SELECT "latitude", typeof("latitude"), "longitude", typeof("longitude") FROM "{table_name}" '
            'ORDER BY rowid').fetchall()
        self.assertEqual(stored, [(37.77, 'real', 0, 'integer'),
                                  ('N/A', 'text', '37.774929,-122.419416', 'text'),
                                  ('', 'text', None, 'null')])


if __name__ == '__main__':
    unittest.main()
