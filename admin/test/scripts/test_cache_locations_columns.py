#!/usr/bin/env python3
"""Synthetic tests for the Cache Locations artifact's course, altitude and accuracy columns."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from leapp_functions.app.artifact_result import ArtifactResult

from scripts.artifacts.iOSCacheLocations import CacheSQLite_Locations


class _Context:
    def __init__(self, path):
        self.path = str(path)

    def get_files_found(self):
        return [self.path]

    def get_relative_path(self, path):
        return Path(path).name

    def create_artifact_result(self, headers=None, source_path=None, **_kwargs):
        # No LAVA run is active here, so the result keeps its rows in memory.
        return ArtifactResult(headers=headers, source_path=source_path,
                              source_path_formatter=self.get_relative_path)


class CacheLocationsColumnsTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def _database(self, columns, row):
        path = Path(self.temp_dir.name) / 'Cache.sqlite'
        db = sqlite3.connect(path)
        try:
            with db:
                db.execute(f'CREATE TABLE ZRTCLLOCATIONMO (Z_PK INTEGER PRIMARY KEY, {", ".join(columns)})')
                db.execute(f'INSERT INTO ZRTCLLOCATIONMO ({", ".join(columns)}) '
                           f'VALUES ({", ".join("?" * len(columns))})', row)
        finally:
            db.close()
        return path

    def _run(self, path):
        result = CacheSQLite_Locations.__wrapped__(_Context(path))
        rows = list(result)
        headers = result.headers if hasattr(result, 'headers') else None
        return headers, rows

    def test_all_columns(self):
        path = self._database(
            ['ZTIMESTAMP', 'ZLATITUDE', 'ZLONGITUDE', 'ZHORIZONTALACCURACY', 'ZSPEED', 'ZCOURSE',
             'ZCOURSEACCURACY', 'ZALTITUDE', 'ZVERTICALACCURACY', 'ZSPEEDACCURACY'],
            (800000000.0, 42.5, -73.5, 10.0, 18.6, 190.1, 5.0, 61.2, 3.0, 0.4))
        headers, rows = self._run(path)
        self.assertEqual(len(rows), 1)
        row = tuple(rows[0])
        if headers:
            self.assertEqual(len(row), len(headers))
        self.assertEqual(row[1:5], (42.5, -73.5, 10.0, 18.6))
        self.assertEqual(row[6:11], (190.1, 5.0, 61.2, 3.0, 0.4))

    def test_invalid_course_reported_as_stored(self):
        path = self._database(
            ['ZTIMESTAMP', 'ZLATITUDE', 'ZLONGITUDE', 'ZHORIZONTALACCURACY', 'ZSPEED', 'ZCOURSE',
             'ZCOURSEACCURACY', 'ZALTITUDE', 'ZVERTICALACCURACY', 'ZSPEEDACCURACY'],
            (800000000.0, 42.5, -73.5, 65.0, -1.0, -1.0, -1.0, 0.0, -1.0, -1.0))
        _headers, rows = self._run(path)
        row = tuple(rows[0])
        self.assertIsNone(row[5])                      # mph blank for speed -1, as before
        self.assertEqual(row[6], -1.0)                 # course -1 kept as stored
        self.assertEqual(row[9], -1.0)

    def test_older_schema_without_new_columns(self):
        # an older store without the course / speed accuracy columns still parses
        path = self._database(
            ['ZTIMESTAMP', 'ZLATITUDE', 'ZLONGITUDE', 'ZHORIZONTALACCURACY', 'ZSPEED', 'ZCOURSE',
             'ZALTITUDE', 'ZVERTICALACCURACY'],
            (800000000.0, 42.5, -73.5, 10.0, 5.0, 90.0, 12.0, 4.0))
        _headers, rows = self._run(path)
        self.assertEqual(len(rows), 1)
        row = tuple(rows[0])
        self.assertEqual(row[6], 90.0)
        self.assertIsNone(row[7])                      # ZCOURSEACCURACY absent -> empty
        self.assertEqual(row[8:10], (12.0, 4.0))
        self.assertIsNone(row[10])                     # ZSPEEDACCURACY absent -> empty


if __name__ == '__main__':
    unittest.main()
