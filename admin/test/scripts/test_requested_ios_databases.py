#!/usr/bin/env python3
"""Focused parser tests for the iOS databases requested in July 2026."""

import json
import plistlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.artifacts.appleAccountDeviceList import appleAccountDeletedDeviceList, \
    appleAccountDeviceList
from scripts.artifacts.keyboard import keyboardVulgarWordUsage
from scripts.artifacts.personalizationPortrait import personalizationPortraitLocations
from scripts.artifacts.powerlog import powerlogApplicationRuntime
from scripts.artifacts.recents import appleRecents
from scripts.artifacts.safariTabs import safariTabsDatabase
from scripts.artifacts.storeSystem import storeSystemAppInstalls, storeSystemAppPackages, \
    storeSystemAppUpdates
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

    def _devicelist_database(self, statements):
        return self._database(
            "mobile/Library/Application Support/com.apple.akd/devicelist.db", statements)

    DEVICE_LIST_SCHEMA = (
        "CREATE TABLE device_list (mid TEXT PRIMARY KEY, name TEXT, serial_number TEXT, "
        "model TEXT, os TEXT, os_version TEXT, dc TEXT, clcg TEXT, clbg TEXT, clhs TEXT, "
        "dec TEXT, circle_status INTEGER, build_number TEXT, trusted INTEGER, "
        "last_updated_date DOUBLE, additional_info BLOB, altDSID TEXT, services TEXT, "
        "last_cache_updated_date DOUBLE)")
    DELETED_DEVICE_LIST_SCHEMA = (
        "CREATE TABLE deleted_device_list (mid TEXT PRIMARY KEY, reason INTEGER, "
        "last_updated_date DOUBLE, altDSID TEXT, deleted_date DOUBLE)")

    def test_apple_account_device_list(self):
        path = self._devicelist_database([
            (self.DEVICE_LIST_SCHEMA, ()),
            ("INSERT INTO device_list VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
             "?, ?, ?)",
             ("MID000", "Test iPhone", "SERIAL00", "iPhone11,2", "iOS", "18.7.8", "1", "1",
              "0", "1", "1", 0, "22H352", 1, 1781275553.938,
              b'{"phones":[{"imei":"000000000000000","slotID":1}]}', "ALTDSID00",
              "itunesstore,icloud", 1781315778.68896)),
        ])
        headers, rows, _ = appleAccountDeviceList.__wrapped__(_Context(path))
        self.assertEqual(len(headers), len(rows[0]))
        self.assertIn("2026-06-12T14:45:53", rows[0][0].isoformat())
        self.assertEqual(rows[0][2], "Test iPhone")
        self.assertEqual(rows[0][8], "000000000000000")
        self.assertEqual(rows[0][9], "Yes")

    def test_apple_account_device_list_unparsable_additional_info(self):
        path = self._devicelist_database([
            (self.DEVICE_LIST_SCHEMA, ()),
            ("INSERT INTO device_list (mid, name, additional_info, trusted) VALUES (?, ?, ?, ?)",
             ("MID001", "Test iPad", b"\x00\x01not json", 2)),
        ])
        headers, rows, _ = appleAccountDeviceList.__wrapped__(_Context(path))
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][8], "")
        self.assertEqual(rows[0][9], 2)
        self.assertIn("not json", rows[0][-1])

    def test_apple_account_deleted_device_list(self):
        path = self._devicelist_database([
            (self.DEVICE_LIST_SCHEMA, ()),
            (self.DELETED_DEVICE_LIST_SCHEMA, ()),
            ("INSERT INTO deleted_device_list VALUES (?, ?, ?, ?, ?)",
             ("MID002", 3, 1781275553.938, "ALTDSID00", 1781315778.68896)),
        ])
        headers, rows, _ = appleAccountDeletedDeviceList.__wrapped__(_Context(path))
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][2], 3)
        self.assertEqual(rows[0][3], "MID002")

    # storeSystem.db changes shape between iOS versions: iOS 14 has no
    # install_finished_timestamp on app_install and no package_type on
    # mapi_app_update, and neither iOS 14 nor iOS 17 has delta_algorithm or
    # extracted_content_size on app_package. The current-schema fixtures below
    # carry those columns and the legacy ones leave them out.
    APP_INSTALL_CURRENT = (
        "CREATE TABLE app_install (pid INTEGER PRIMARY KEY, account_id INTEGER, "
        "bundle_id TEXT, bundle_name TEXT, bundle_version TEXT, bundle_url TEXT, "
        "vendor_name TEXT, item_id INTEGER, storefront TEXT, client_id TEXT, "
        "transaction_id TEXT, phase INTEGER, update_type INTEGER, source_type INTEGER, "
        "redownload INTEGER, install_finished_timestamp DATETIME, last_start_date DATETIME, "
        "timestamp DATETIME, store_metadata BLOB)")
    APP_INSTALL_LEGACY = (
        "CREATE TABLE app_install (pid INTEGER PRIMARY KEY, account_id INTEGER, "
        "bundle_id TEXT, bundle_name TEXT, bundle_version TEXT, bundle_url TEXT, "
        "vendor_name TEXT, item_id INTEGER, storefront TEXT, client_id TEXT, "
        "transaction_id TEXT, phase INTEGER, update_type INTEGER, source_type INTEGER, "
        "redownload INTEGER, last_start_date DATETIME, timestamp DATETIME, "
        "store_metadata BLOB)")
    APP_PACKAGE_LEGACY = (
        "CREATE TABLE app_package (pid INTEGER PRIMARY KEY, parent_id, archive_type INTEGER, "
        "bytes_total INTEGER, disk_usage INTEGER, compression INTEGER, package_type INTEGER, "
        "package_url TEXT, request_count INTEGER, variant_id TEXT, timestamp DATETIME)")
    MAPI_LEGACY = (
        "CREATE TABLE mapi_app_update (pid INTEGER PRIMARY KEY, bundle_id TEXT, "
        "install_date DATETIME, item_id INTEGER, metadata BLOB, "
        "store_software_version_id INTEGER, timestamp DATETIME, update_state INTEGER)")

    # 2026-04-29T17:35:08Z as a Cocoa timestamp.
    COCOA_TS = 799176908

    def _store_metadata_plist(self):
        """A minimal NSKeyedArchiver payload shaped like store_metadata."""
        return plistlib.dumps({
            '$archiver': 'NSKeyedArchiver',
            '$version': 100000,
            '$top': {'root': plistlib.UID(1)},
            '$objects': [
                '$null',
                {'itemName': plistlib.UID(2), 'artistName': plistlib.UID(3),
                 'genre': plistlib.UID(4), 'purchaseDate': plistlib.UID(5),
                 'appleID': plistlib.UID(6)},
                'Test App', 'Test Developer', 'Utilities', '2025-10-22T12:55:30Z',
                'user@example.com',
            ],
        }, fmt=plistlib.PlistFormat.FMT_BINARY)

    def test_store_system_installs_current_schema(self):
        path = self._database("containers/Data/System/GUID/Documents/Persistence/"
                              "storeSystem.db", [
            (self.APP_INSTALL_CURRENT, ()),
            ("INSERT INTO app_install (pid, bundle_id, bundle_name, bundle_version, "
             "vendor_name, item_id, timestamp, phase, store_metadata) "
             "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
             (1, "com.example.app", "Example", "1.2.3", "Example Ltd", 12345,
              self.COCOA_TS, 10, self._store_metadata_plist())),
        ])
        headers, rows, _ = storeSystemAppInstalls.__wrapped__(_Context(path))
        self.assertEqual(len(headers), len(rows[0]))
        self.assertIn("2026-04-29T17:35:08", rows[0][0].isoformat())
        self.assertEqual(rows[0][5], "Test App")          # itemName wins over bundle_name
        self.assertEqual(rows[0][6], "com.example.app")
        self.assertEqual(rows[0][9], "Test Developer")    # artistName wins over vendor_name
        self.assertEqual(rows[0][12], "user@example.com")

    def test_store_system_installs_legacy_schema(self):
        """iOS 14 lacks install_finished_timestamp; the query must still run."""
        path = self._database("containers/Data/System/GUID/Documents/Persistence/"
                              "storeSystem.db", [
            (self.APP_INSTALL_LEGACY, ()),
            ("INSERT INTO app_install (pid, bundle_id, bundle_name, timestamp) "
             "VALUES (?, ?, ?, ?)", (1, "com.example.app", "Example", self.COCOA_TS)),
        ])
        headers, rows, _ = storeSystemAppInstalls.__wrapped__(_Context(path))
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][1], '')                  # absent column reads as empty
        self.assertEqual(rows[0][5], "Example")           # falls back to bundle_name

    def test_store_system_packages_legacy_schema(self):
        """iOS 14 and 17 lack delta_algorithm and extracted_content_size."""
        path = self._database("containers/Data/System/GUID/Documents/Persistence/"
                              "storeSystem.db", [
            (self.APP_INSTALL_LEGACY, ()),
            (self.APP_PACKAGE_LEGACY, ()),
            ("INSERT INTO app_install (pid, bundle_id, bundle_name) VALUES (?, ?, ?)",
             (7, "com.example.app", "Example")),
            ("INSERT INTO app_package (pid, parent_id, bytes_total, disk_usage, timestamp) "
             "VALUES (?, ?, ?, ?, ?)", (1, 7, 1000, 2000, self.COCOA_TS)),
        ])
        headers, rows, _ = storeSystemAppPackages.__wrapped__(_Context(path))
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][1], "com.example.app")   # joined through parent_id
        self.assertEqual(rows[0][4], 1000)
        self.assertEqual(rows[0][6], '')                  # extracted_content_size absent
        self.assertEqual(rows[0][9], '')                  # delta_algorithm absent

    def test_store_system_updates_legacy_schema(self):
        """iOS 14 lacks package_type, and the catalog blob is JSON rather than a plist."""
        catalog = json.dumps({
            'attributes': {
                'name': 'Catalog App',
                'artistName': 'Catalog Developer',
                'genreDisplayName': 'Productivity',
                'url': 'https://apps.apple.com/us/app/id1',
                'platformAttributes': {'ios': {
                    'releaseDate': '2013-11-26',
                    'latestVersionInfo': {'versionDisplay': '7.4.3',
                                          'releaseTimestamp': '2025-12-17T21:04:59Z'},
                }},
            },
        }).encode('utf-8')
        path = self._database("containers/Data/System/GUID/Documents/Persistence/"
                              "storeSystem.db", [
            (self.MAPI_LEGACY, ()),
            ("INSERT INTO mapi_app_update (pid, bundle_id, item_id, metadata, timestamp, "
             "update_state) VALUES (?, ?, ?, ?, ?, ?)",
             (1, "com.example.app", 42, catalog, self.COCOA_TS, 1)),
        ])
        headers, rows, _ = storeSystemAppUpdates.__wrapped__(_Context(path))
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][4], "Catalog App")
        self.assertEqual(rows[0][8], "7.4.3")
        self.assertIn("2025-12-17T21:04:59", rows[0][2].isoformat())
        self.assertEqual(rows[0][14], '')                 # package_type absent

    def test_store_system_missing_tables(self):
        path = self._database("containers/Data/System/GUID/Documents/Persistence/"
                              "storeSystem.db", [("CREATE TABLE unrelated (a)", ())])
        for processor in (storeSystemAppInstalls, storeSystemAppUpdates,
                          storeSystemAppPackages):
            headers, rows, source = processor.__wrapped__(_Context(path))
            self.assertEqual(rows, [])
            self.assertEqual(source, "")
            self.assertTrue(headers)

    def test_apple_account_deleted_device_list_missing_table(self):
        path = self._devicelist_database([(self.DEVICE_LIST_SCHEMA, ())])
        headers, rows, source = appleAccountDeletedDeviceList.__wrapped__(_Context(path))
        self.assertEqual(rows, [])
        self.assertEqual(source, "")
        self.assertTrue(headers)


if __name__ == "__main__":
    unittest.main()
