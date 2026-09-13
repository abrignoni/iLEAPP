#!/usr/bin/env python3
"""Focused tests for iOS system-history and file-system event artifacts."""

import gzip
import sqlite3
import struct
import tempfile
import unittest
from pathlib import Path

from scripts.artifacts.diagnosticLogd import diagnosticLogdEvents
from scripts.artifacts.fileSystemEvents import (
    iosFileSystemEvents,
    iosFileSystemEventsAppContainers,
    iosFileSystemEventsCommunications,
    iosFileSystemEventsLocation,
    iosFileSystemEventsPackageManagement,
    iosFileSystemEventsRemoved,
    iosFileSystemEventsRestoreBackup,
    iosFileSystemEventsSecurity,
    iosFileSystemEventsUpdates,
    iosFileSystemEventsWeb,
)
from scripts.artifacts.installHistory import iosInstallHistory
from scripts.artifacts.lockdownEvents import lockdownEvents


class _Context:
    def __init__(self, paths):
        self.paths = [str(path) for path in paths]

    def get_files_found(self):
        return self.paths

    def get_relative_path(self, path):
        return Path(path).name


class IOSSystemHistoryArtifactsTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_lockdown_events_preserve_local_timestamp_and_message(self):
        path = self.root / "lockdownd.log"
        path.write_text(
            "05/23/25 19:35:47.154568 pid=84 "
            "password_changed_callback: Device passcode changed.\n"
            "05/23/25 19:40:18.879256 pid=84 main: Starting Up\n"
            "not an event\n",
            encoding="utf-8",
        )

        headers, rows, source = lockdownEvents.__wrapped__(_Context([path]))

        self.assertEqual(len(rows), 2)
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][1], "Device passcode changed")
        self.assertEqual(rows[0][2], 84)
        self.assertEqual(rows[1][1], "Lockdownd startup")
        self.assertEqual(source, "lockdownd.log")

    def test_diagnostic_logd_converts_offset_to_utc(self):
        path = self.root / "logd.0.log"
        path.write_text(
            "2025-12-20 09:51:53+1300 logd[32]: "
            "Time zone changed, updating file headers\n"
            "2025-12-20 10:00:00+1300 logd[32]: ordinary record\n"
            "2025-12-20 10:01:00+1300 logd[32]: logd shutting down\n",
            encoding="utf-8",
        )

        headers, rows, _source = diagnosticLogdEvents.__wrapped__(_Context([path]))

        self.assertEqual(len(rows), 2)
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][0].isoformat(), "2025-12-19T20:51:53+00:00")
        self.assertEqual(rows[0][1], "+1300")
        self.assertEqual(rows[1][2], "Shutdown-related log entry")

    def test_install_history_operation_types(self):
        path = self.root / "installHistory.db"
        with sqlite3.connect(path) as database:
            database.execute(
                "CREATE TABLE logs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, "
                "build TEXT, date TEXT, operationType INTEGER)"
            )
            database.execute(
                "INSERT INTO logs (name, build, date, operationType) VALUES (?, ?, ?, ?)",
                ("iOS Update", "23A123", "2026-07-01 12:34:56", 304),
            )
            database.execute(
                "INSERT INTO logs (name, build, date, operationType) VALUES (?, ?, ?, ?)",
                ("Future Event", "23B456", "2026-07-02 12:34:56", 999),
            )

        headers, rows, _source = iosInstallHistory.__wrapped__(_Context([path]))

        self.assertEqual(len(rows), 2)
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][2], "Successful install completed")
        self.assertEqual(rows[1][2], "Unknown operation (999)")
        self.assertEqual(rows[1][3], 999)

    def test_fsevents_v3_and_concatenated_gzip_members(self):
        first_record = (
            b"private/var/mobile/example.txt\x00"
            + struct.pack("<QIQI", 100, 0x00800011, 42, 0)
        )
        second_record = (
            b"private/var/mobile/renamed.txt\x00"
            + struct.pack("<QIQI", 101, 0x00800008, 43, 7)
        )
        first_page = struct.pack("<4sII", b"3SLD", 0, 12 + len(first_record)) + first_record
        second_page = struct.pack("<4sII", b"3SLD", 0, 12 + len(second_record)) + second_record
        path = self.root / "0000000000000065"
        path.write_bytes(gzip.compress(first_page) + gzip.compress(second_page))

        headers, rows, _source = iosFileSystemEvents.__wrapped__(_Context([path]))

        self.assertEqual(len(rows), 2)
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][0], 100)
        self.assertEqual(rows[0][1], "private/var/mobile/example.txt")
        self.assertIn("Created", rows[0][2])
        self.assertIn("Content modified", rows[0][2])
        self.assertEqual(rows[0][4], "File")
        self.assertEqual(rows[1][6], 7)
        self.assertEqual(rows[1][7], "3")

    def test_fsevents_v1_and_v2_pages(self):
        v1_record = b"v1/path\x00" + struct.pack("<QI", 1, 0x00800001)
        v2_record = b"v2/path\x00" + struct.pack("<QIQ", 2, 0x01000002, 99)
        v1_page = struct.pack("<4sII", b"1SLD", 0, 12 + len(v1_record)) + v1_record
        v2_page = struct.pack("<4sII", b"2SLD", 0, 12 + len(v2_record)) + v2_record
        path = self.root / "0000000000000002"
        path.write_bytes(gzip.compress(v1_page + v2_page))

        headers, rows, _source = iosFileSystemEvents.__wrapped__(_Context([path]))

        self.assertEqual(len(rows), 2)
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][5], None)
        self.assertEqual(rows[0][7], "1")
        self.assertEqual(rows[1][5], 99)
        self.assertEqual(rows[1][7], "2")

    def test_fsevents_items_of_interest_reports(self):
        records = [
            ("mobile/Library/SMS/sms.db", 0x00800010),
            ("MobileSoftwareUpdate/restore.log", 0x00800010),
            ("mobile/Containers/Data/Application/GUID/Documents/item", 0x00800001),
            ("root/Library/Caches/locationd/cache", 0x00800010),
            ("Keychains/keychain-2.db", 0x00800004),
            ("mobile/Library/Safari/History.db", 0x00800010),
            ("cache/apt/pkgcache.bin", 0x00800010),
            ("tmp/deleted-item", 0x00800002),
        ]
        record_data = b"".join(
            path.encode("utf-8") + b"\x00" + struct.pack("<QIQI", event_id, flags, 1, 0)
            for event_id, (path, flags) in enumerate(records, 1)
        )
        page = struct.pack("<4sII", b"3SLD", 0, 12 + len(record_data)) + record_data
        path = self.root / "0000000000000008"
        path.write_bytes(gzip.compress(page))
        context = _Context([path])

        expected = (
            (iosFileSystemEventsCommunications, "mobile/Library/SMS/sms.db"),
            (iosFileSystemEventsUpdates, "MobileSoftwareUpdate/restore.log"),
            (
                iosFileSystemEventsAppContainers,
                "mobile/Containers/Data/Application/GUID/Documents/item",
            ),
            (iosFileSystemEventsLocation, "root/Library/Caches/locationd/cache"),
            (iosFileSystemEventsSecurity, "Keychains/keychain-2.db"),
            (iosFileSystemEventsRestoreBackup, "MobileSoftwareUpdate/restore.log"),
            (iosFileSystemEventsWeb, "mobile/Library/Safari/History.db"),
            (iosFileSystemEventsPackageManagement, "cache/apt/pkgcache.bin"),
            (iosFileSystemEventsRemoved, "tmp/deleted-item"),
        )
        for artifact, expected_path in expected:
            _headers, rows, _source = artifact.__wrapped__(context)
            self.assertEqual([row[1] for row in rows], [expected_path])


if __name__ == "__main__":
    unittest.main()
