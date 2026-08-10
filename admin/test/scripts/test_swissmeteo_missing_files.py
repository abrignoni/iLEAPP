"""Swissmeteo artifacts must return a result tuple even when files are absent.

When the app is not on the device, plz_interaction and swissmeteo_plz logged
'No Swissmeteo'/'No app_open' and then fell off the end of the function,
returning None. The artifact_processor wrapper unpacks three values, so every
extraction without Swissmeteo reported

    TypeError: cannot unpack non-iterable NoneType object

as a parsing error. A second latent crash sat in plz_interaction: with the
favorites database present but localdata.sqlite absent, the localdata cursor
stayed None and get_location_infos(None, ...) would raise AttributeError.

These tests run both artifacts through the missing-file and partial-file
shapes and require a well-formed (headers, rows, source) result each time.
"""
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts.swissmeteo import plz_interaction, swissmeteo_plz  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

TS_MS = 1756684800000  # 2025-09-01 00:00:00 UTC in milliseconds


class TestSwissmeteoMissingFiles(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Context.clear()
        Context.set_report_folder(self.tmpdir)

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_prediction_db(self):
        db_path = pathlib.Path(self.tmpdir) / 'favorites_prediction_db.sqlite'
        db = sqlite3.connect(db_path)
        db.execute('CREATE TABLE plz_interaction '
                   '(timestamp INTEGER, plz INTEGER, lat REAL, lon REAL)')
        db.execute('INSERT INTO plz_interaction VALUES (?, 1000, 46.5, 6.6)',
                   (TS_MS,))
        db.execute('CREATE TABLE app_open (timestamp INTEGER, lat REAL, lon REAL)')
        db.execute('INSERT INTO app_open VALUES (?, 46.5, 6.6)', (TS_MS,))
        db.commit()
        db.close()
        return str(db_path)

    def _make_localdata_db(self):
        db_path = pathlib.Path(self.tmpdir) / 'localdata.sqlite'
        db = sqlite3.connect(db_path)
        db.execute('CREATE TABLE plz (plz_pk INTEGER, x REAL, y REAL, '
                   'altitude REAL, primary_name TEXT)')
        db.execute("INSERT INTO plz VALUES (1000, 538000, 152000, 500, 'Lausanne')")
        db.commit()
        db.close()
        return str(db_path)

    def test_plz_interaction_returns_tuple_when_app_absent(self):
        # The real-world trigger: the path globs matched only a stray
        # localdata.sqlite (another app's file), never the favorites database.
        Context.set_files_found([self._make_localdata_db()])
        result = plz_interaction.__wrapped__(Context)
        self.assertIsNotNone(result)
        data_headers, data_list, _source = result
        self.assertEqual(len(data_headers), 4)
        self.assertEqual(data_list, [])

    def test_swissmeteo_plz_returns_tuple_when_app_absent(self):
        Context.set_files_found([self._make_localdata_db()])
        result = swissmeteo_plz.__wrapped__(Context)
        self.assertIsNotNone(result)
        data_headers, data_list, _source = result
        self.assertEqual(len(data_headers), 4)
        self.assertEqual(data_list, [])

    def test_plz_interaction_without_localdata_keeps_raw_rows(self):
        """favorites db present, localdata.sqlite absent: no cursor, no crash."""
        Context.set_files_found([self._make_prediction_db()])
        _headers, data_list, source = plz_interaction.__wrapped__(Context)
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0][1], 1000)
        self.assertTrue(str(source).endswith('favorites_prediction_db.sqlite'))

    def test_plz_interaction_with_localdata_enriches_rows(self):
        Context.set_files_found([self._make_prediction_db(),
                                 self._make_localdata_db()])
        _headers, data_list, _source = plz_interaction.__wrapped__(Context)
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0][1], 'Lausanne')
        # Coordinates as text, not a map URL: a report links to nothing outside
        # its own folder, so no openstreetmap.org destination is emitted.
        self.assertNotIn('openstreetmap.org', data_list[0][2])
        self.assertRegex(data_list[0][2], r'^-?\d+\.\d+, -?\d+\.\d+$')

    def test_swissmeteo_plz_parses_app_open_rows(self):
        Context.set_files_found([self._make_prediction_db()])
        _headers, data_list, _source = swissmeteo_plz.__wrapped__(Context)
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0][1], 46.5)
        self.assertNotIn('openstreetmap.org', data_list[0][3])
        self.assertEqual(data_list[0][3], '46.5, 6.6')


if __name__ == '__main__':
    unittest.main()
