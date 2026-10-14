#!/usr/bin/env python3
"""Synthetic tests for the routined vehicle event artifact (Local.sqlite).

Each test builds a small routined database with the columns observed on iOS 18.7.8 and runs
the artifact over it, so the parsing logic is checked without any device image.
"""

import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.artifacts.routinedParkedCar import routinedParkedCar, routinedVehicles

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


class RoutinedVehicleEventsTest(unittest.TestCase):
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

    def test_vehicle_event_and_history(self):
        path = self._database('Local.sqlite', [
            ('CREATE TABLE ZRTVEHICLEEVENTMO (Z_PK INTEGER PRIMARY KEY, ZLOCATIONQUALITY, '
             'ZUSERSETLOCATION, ZUSUALLOCATION, ZDATE, ZLOCDATE, ZLOCLATITUDE, ZLOCLONGITUDE, '
             'ZLOCUNCERTAINTY, ZIDENTIFIER, ZNOTES, ZVEHICLEIDENTIFIER)', ()),
            # the history table has no vehicle, notes or location-quality columns
            ('CREATE TABLE ZRTVEHICLEEVENTHISTORYMO (Z_PK INTEGER PRIMARY KEY, ZDATE, ZLOCDATE, '
             'ZLOCLATITUDE, ZLOCLONGITUDE, ZLOCUNCERTAINTY, ZIDENTIFIER)', ()),
            ('INSERT INTO ZRTVEHICLEEVENTMO VALUES (1, 2, 0, 0, ?, ?, 42.64, -73.69, 5.0, ?, NULL, ?)',
             (ENTRY, ENTRY - 30, 'EVENT-A', 'Example Car')),
            ('INSERT INTO ZRTVEHICLEEVENTHISTORYMO VALUES (1, ?, ?, 42.64, -73.69, 5.0, ?)',
             (ENTRY, ENTRY - 30, 'EVENT-A')),
            ('INSERT INTO ZRTVEHICLEEVENTHISTORYMO VALUES (2, ?, ?, 42.65, -73.70, 25.0, ?)',
             (EXIT, EXIT - 10, 'EVENT-B')),
        ])
        headers, rows, _source = routinedParkedCar.__wrapped__(_Context(path))
        self.assertEqual(len(rows), 3)                 # not merged: the repeat stays
        for row in rows:
            self.assertEqual(len(row), len(headers))
        event = rows[0]
        self.assertEqual(event[0], _utc(ENTRY))
        self.assertEqual(event[1], _utc(ENTRY - 30))
        self.assertEqual(event[5:7], ('EVENT-A', 'Example Car'))
        self.assertEqual(event[11], 'ZRTVEHICLEEVENTMO')
        history = rows[1:]
        self.assertEqual({r[11] for r in history}, {'ZRTVEHICLEEVENTHISTORYMO'})
        self.assertEqual([r[5] for r in history], ['EVENT-A', 'EVENT-B'])
        self.assertTrue(all(r[6] is None and r[7] is None for r in history))

    def test_non_positive_times_are_empty(self):
        path = self._database('Local.sqlite', [
            ('CREATE TABLE ZRTVEHICLEEVENTHISTORYMO (Z_PK INTEGER PRIMARY KEY, ZDATE, ZLOCDATE, '
             'ZLOCLATITUDE, ZLOCLONGITUDE, ZLOCUNCERTAINTY, ZIDENTIFIER)', ()),
            ('INSERT INTO ZRTVEHICLEEVENTHISTORYMO VALUES (1, 0, -1, 42.0, -73.0, 5.0, ?)', ('X',)),
        ])
        _headers, rows, _source = routinedParkedCar.__wrapped__(_Context(path))
        self.assertIsNone(rows[0][0])
        self.assertIsNone(rows[0][1])

    def test_vehicles(self):
        path = self._database('Local.sqlite', [
            ('CREATE TABLE ZRTVEHICLEMO (Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER, '
             'ZENDDATE TIMESTAMP, ZSTARTDATE TIMESTAMP, ZBLUETOOTHADDRESS VARCHAR, '
             'ZVEHICLEMODELNAME VARCHAR, ZVEHICLENAME VARCHAR)', ()),
            # inserted out of order: the artifact sorts by start time
            ('INSERT INTO ZRTVEHICLEMO VALUES (1, 1, 1, ?, ?, NULL, NULL, ?)',
             (EXIT, ENTRY + 600, 'Example Car')),
            ('INSERT INTO ZRTVEHICLEMO VALUES (2, 1, 1, ?, ?, ?, ?, ?)',
             (ENTRY + 300, ENTRY, '00:11:22:33:44:55', 'Example Model', 'Example Car')),
            ('INSERT INTO ZRTVEHICLEMO VALUES (3, 1, 1, 0, -1, NULL, NULL, NULL)', ()),
        ])
        headers, rows, source = routinedVehicles.__wrapped__(_Context(path))
        self.assertEqual(source, str(path))            # the sidecars are not cited
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertEqual(len(row), len(headers))
        self.assertEqual(rows[0][:2], (None, None))    # zero / negative times are empty
        self.assertEqual(rows[1], (_utc(ENTRY), _utc(ENTRY + 300), 'Example Car', 'Example Model',
                                   '00:11:22:33:44:55'))
        self.assertEqual(rows[2], (_utc(ENTRY + 600), _utc(EXIT), 'Example Car', None, None))

    def test_vehicles_table_absent(self):
        path = self._database('Local.sqlite', [
            ('CREATE TABLE ZRTVEHICLEEVENTMO (Z_PK INTEGER PRIMARY KEY, ZDATE)', ()),
        ])
        _headers, rows, source = routinedVehicles.__wrapped__(_Context(path))
        self.assertEqual(rows, [])
        self.assertEqual(source, str(path))


if __name__ == '__main__':
    unittest.main()
