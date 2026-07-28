#!/usr/bin/env python3
"""Focused parser tests for the iOS databases requested in July 2026."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.artifacts.keyboard import keyboardVulgarWordUsage
from scripts.artifacts.personalizationPortrait import personalizationPortraitLocations
from scripts.artifacts.powerlog import powerlogApplicationRuntime
from scripts.artifacts.recents import appleRecents
from scripts.artifacts.safariTabs import safariTabsDatabase
from scripts.artifacts.wifiAnalytics import wifiAnalyticsGeotags


class _Context:
    def __init__(self, path):
        self.path = str(path)

    def get_files_found(self):
        return [self.path]

    def get_relative_path(self, path):
        return Path(path).name


class RequestedIOSDatabasesTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _database(self, relative_path, statements):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as db:
            for statement, values in statements:
                db.execute(statement, values)
        return path

    def test_recents(self):
        path = self._database("mobile/Library/Recents/Recents", [
            ("CREATE TABLE recents (sending_address, original_source, dates, last_date, "
             "weight, record_hash, count, group_kind)", ()),
            ("CREATE TABLE contacts (recent_id, kind, address, display_name)", ()),
            ("CREATE TABLE metadata (recent_id, key, value)", ()),
            ("INSERT INTO recents VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
             ("me@example.com", "com.apple.mobilemail", "1000,2000", 2000, 1, "hash", 2, 3)),
            ("INSERT INTO contacts VALUES (?, ?, ?, ?)", (1, 1, "you@example.com", "You")),
            ("INSERT INTO metadata VALUES (?, ?, ?)", (1, "key", b"\x01\x02")),
        ])
        headers, rows, _ = appleRecents.__wrapped__(_Context(path))
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][9], "0102")
        self.assertIn("1970-01-01T00:00:01", rows[0][1])

    def test_safari_tabs(self):
        path = self._database("mobile/Library/Safari/SafariTabs.db", [
            ("CREATE TABLE bookmarks (id, title, url, parent, last_modified, date_closed, "
             "deleted, order_index)", ()),
            ("INSERT INTO bookmarks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
             (1, "Private", None, None, None, None, 0, 0)),
            ("INSERT INTO bookmarks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
             (2, "Example", "https://example.com", 1, 100, None, 0, 1)),
        ])
        headers, rows, _ = safariTabsDatabase.__wrapped__(_Context(path))
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][6], "Private")
        self.assertEqual(rows[0][7], "Private")

    def test_vulgar_words(self):
        path = self._database("mobile/Library/Keyboard/VulgarWordUsage.db", [
            ("CREATE TABLE vword_usage (ROWID INTEGER PRIMARY KEY, app TEXT, recipient TEXT, "
             "vword TEXT, word_reading TEXT, usage_count INTEGER, "
             "last_use_timestamp REAL, journaled)", ()),
            ("INSERT INTO vword_usage VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
             (1, "com.example", "recipient", "example", "", 4, 100, 1)),
        ])
        headers, rows, _ = keyboardVulgarWordUsage.__wrapped__(_Context(path))
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][6], 4)

    def test_wifi_analytics(self):
        path = self._database(
            "root/Library/Application Support/com.apple.wifianalyticsd/"
            "DeviceAnalyticsModel.sqlite",
            [
                ("CREATE TABLE ZGEOTAG (Z_PK, Z_ENT, ZDATE, ZLATITUDE, ZLONGITUDE, ZBSS)", ()),
                ("CREATE TABLE ZBSS (Z_PK, ZLASTSEEN, ZBSSID, ZNETWORK)", ()),
                ("CREATE TABLE ZNETWORK (Z_PK, ZSSID)", ()),
                ("INSERT INTO ZGEOTAG VALUES (?, ?, ?, ?, ?, ?)", (1, 2, 100, 41.0, -87.0, 3)),
                ("INSERT INTO ZBSS VALUES (?, ?, ?, ?)", (3, 200, "aa:bb", 4)),
                ("INSERT INTO ZNETWORK VALUES (?, ?)", (4, "Network")),
            ],
        )
        headers, rows, _ = wifiAnalyticsGeotags.__wrapped__(_Context(path))
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][-1], "Network")

    def test_personalization_portrait(self):
        path = self._database("mobile/Library/PersonalizationPortrait/PPSQLDatabase.db", [
            ("CREATE TABLE sources (id, bundle_id, group_id, seconds_from_1970)", ()),
            ("CREATE TABLE loc_records (id, source_id, cll_latitude_degrees, "
             "cll_longitude_degrees, clp_name, clp_thoroughfare, clp_subThoroughfare, "
             "clp_locality, clp_subLocality, clp_administrativeArea, "
             "clp_subAdministrativeArea, clp_postalCode, clp_ISOcountryCode, clp_country, "
             "extraction_os_build, category, algorithm, initial_score, is_sync_eligible)", ()),
            ("INSERT INTO sources VALUES (?, ?, ?, ?)", (1, "com.apple.mobilemail", "group", 100)),
            ("INSERT INTO loc_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
             "?, ?, ?, ?)", (1, 1, 41.0, -87.0, "Place", "Road", "1", "City", "", "IL", "",
                             "12345", "US", "United States", "23A", "cat", "alg", 0.5, 1)),
        ])
        headers, rows, _ = personalizationPortraitLocations.__wrapped__(_Context(path))
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][-1], "Yes")

    def test_powerlog_runtime(self):
        path = self._database("PowerLog/CurrentPowerlog.PLSQL", [
            ("CREATE TABLE PLAppTimeService_Aggregate_AppRunTime "
             "(timestamp, BundleID, BackgroundTime, ScreenOnTime)", ()),
            ("INSERT INTO PLAppTimeService_Aggregate_AppRunTime VALUES (?, ?, ?, ?)",
             (1635847545, "com.apple.mobilesafari", 2.0, 30.0)),
        ])
        headers, rows, _ = powerlogApplicationRuntime.__wrapped__(_Context(path))
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][1], "com.apple.mobilesafari")


if __name__ == "__main__":
    unittest.main()
