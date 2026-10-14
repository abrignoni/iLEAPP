#!/usr/bin/env python3
"""Synthetic tests for the routined visit artifacts (Cache.sqlite, Cloud-V2.sqlite).

Each test builds a small routined database with the columns observed on iOS 18.7.8 and runs
the artifact over it, so the parsing logic is checked without any device image.
"""

import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.artifacts.routinedVisits import routinedCacheVisits, routinedCloudVisits

COCOA = 978307200
ENTRY = 800000000.5          # Cocoa seconds -> 2026-05-09 06:13:20.5 UTC
EXIT = 800003600.0


def _utc(cocoa):
    # convert_cocoa_core_data_ts_to_utc keeps whole seconds (the LAVA column is an integer epoch)
    return datetime.fromtimestamp(int(cocoa + COCOA), tz=timezone.utc)


class _Context:
    def __init__(self, path):
        self.path = str(path)

    def get_files_found(self):
        # the seeker hands the sidecars over too; the artifacts must skip them
        return [self.path, self.path + '-wal', self.path + '-shm']

    def get_relative_path(self, path):
        return Path(path).name


class RoutinedVisitsTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

    def _database(self, name, statements):
        path = self.root / name
        db = sqlite3.connect(path)
        try:
            with db:                                   # commits
                for statement, values in statements:
                    db.execute(statement, values)
        finally:
            db.close()                                 # Windows cannot delete an open file
        return path

    def test_cache_visits(self):
        path = self._database('Cache.sqlite', [
            ('CREATE TABLE ZRTVISITMO (Z_PK INTEGER PRIMARY KEY, ZDATAPOINTCOUNT, ZSOURCE, ZTYPE, '
             'ZCONFIDENCE, ZDETECTIONDATE, ZENTRYDATE, ZEXITDATE, ZLOCATIONDATE, '
             'ZLOCATIONLATITUDE, ZLOCATIONLONGITUDE, ZLOCATIONUNCERTAINTY)', ()),
            ('INSERT INTO ZRTVISITMO VALUES (1, 4, 1, 3, 1.0, ?, ?, ?, ?, 42.5, -73.5, 35.0)',
             (EXIT + 60, ENTRY, EXIT, ENTRY)),
            # an arrival-only row: no exit time
            ('INSERT INTO ZRTVISITMO VALUES (2, 2, 1, 1, 0.5, ?, ?, NULL, ?, 41.25, -73.0, 50.0)',
             (ENTRY + 7200, ENTRY + 7200, ENTRY + 7200)),
        ])
        headers, rows, source = routinedCacheVisits.__wrapped__(_Context(path))
        self.assertEqual(source, str(path))
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(len(row), len(headers))
        first, second = rows
        self.assertEqual(first[0], _utc(ENTRY))
        self.assertEqual(first[1], _utc(EXIT))
        self.assertEqual(first[2], _utc(EXIT + 60))
        self.assertEqual(first[4:7], (42.5, -73.5, 35.0))
        self.assertEqual(first[9], 3)                  # type as stored
        self.assertIsNone(second[1])                   # no exit stays empty
        self.assertEqual(second[9], 1)
        self.assertEqual(first[-1], 'Cache.sqlite')

    def test_cache_visits_missing_table(self):
        path = self._database('Cache.sqlite', [('CREATE TABLE ZRTCLLOCATIONMO (Z_PK)', ())])
        _headers, rows, _source = routinedCacheVisits.__wrapped__(_Context(path))
        self.assertEqual(rows, [])

    def test_cloud_visits_with_place_address_and_device(self):
        path = self._database('Cloud-V2.sqlite', [
            ('CREATE TABLE ZRTDEVICEMO (Z_PK INTEGER PRIMARY KEY, ZDEVICECLASS, ZDEVICEMODEL, '
             'ZDEVICENAME)', ()),
            ('CREATE TABLE ZRTMAPITEMMO (Z_PK INTEGER PRIMARY KEY, ZNAME, ZCATEGORY)', ()),
            ('CREATE TABLE ZRTADDRESSMO (Z_PK INTEGER PRIMARY KEY, ZMAPITEM, ZSUBTHOROUGHFARE, '
             'ZTHOROUGHFARE, ZLOCALITY, ZADMINISTRATIVEAREA, ZPOSTALCODE, ZCOUNTRY)', ()),
            ('CREATE TABLE ZRTLEARNEDPLACEMO (Z_PK INTEGER PRIMARY KEY, ZMAPITEM, ZCUSTOMLABEL)', ()),
            ('CREATE TABLE ZRTLEARNEDVISITMO (Z_PK INTEGER PRIMARY KEY, ZDEVICE, ZPLACE, '
             'ZCONFIDENCE, ZCREATIONDATE, ZENTRYDATE, ZEXITDATE, ZEXPIRATIONDATE, '
             'ZLOCATIONALTITUDE, ZLOCATIONLATITUDE, ZLOCATIONLONGITUDE, ZLOCATIONUNCERTAINTY, '
             'ZPLACECONFIDENCE)', ()),
            ('INSERT INTO ZRTDEVICEMO VALUES (1, ?, ?, NULL)', ('iPhone', 'D321AP')),
            ('INSERT INTO ZRTMAPITEMMO VALUES (7, ?, ?)', ('Example Park', 'Park')),
            ('INSERT INTO ZRTADDRESSMO VALUES (1, 7, ?, ?, ?, ?, ?, ?)',
             ('12', 'Main St', 'Albany', 'New York', '12203', 'United States')),
            ('INSERT INTO ZRTLEARNEDPLACEMO VALUES (3, 7, NULL)', ()),
            ('INSERT INTO ZRTLEARNEDVISITMO VALUES (1, 1, 3, 1.0, ?, ?, ?, ?, 90.0, 42.6, -73.8, '
             '20.0, 0.9)', (EXIT + 86400, ENTRY, EXIT, EXIT + 86400 * 30)),
            # a visit with no place: still reported, with the joined columns empty
            ('INSERT INTO ZRTLEARNEDVISITMO VALUES (2, NULL, NULL, 0.5, NULL, ?, NULL, NULL, NULL, '
             '41.0, -73.0, 100.0, NULL)', (ENTRY + 3,)),
        ])
        headers, rows, _source = routinedCloudVisits.__wrapped__(_Context(path))
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(len(row), len(headers))
        named = rows[0]
        self.assertEqual(named[0], _utc(ENTRY))
        self.assertEqual(named[8:10], ('Example Park', 'Park'))
        self.assertEqual(named[11:16], ('12 Main St', 'Albany', 'New York', '12203', 'United States'))
        self.assertEqual(named[16:18], ('iPhone', 'D321AP'))   # class and model as stored
        self.assertIsNone(named[18])
        unnamed = rows[1]
        self.assertIsNone(unnamed[8])
        self.assertIsNone(unnamed[11])                 # no address -> empty, not ' '
        self.assertIsNone(unnamed[16])


if __name__ == '__main__':
    unittest.main()
