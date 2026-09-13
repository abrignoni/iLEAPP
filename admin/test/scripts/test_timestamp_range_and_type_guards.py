"""Guard artifacts against timestamp values that crash the whole module.

Two failure shapes observed in a single iOS 26 case run:

* webkit_cache_records: a cache record carried a double far outside the
  platform's time_t range; datetime.fromtimestamp() raised OverflowError on
  Windows and one bad record aborted the artifact, losing every webkit cache
  record in the case.

* health_achievements: ACHAchievementsPlugin_earned_instances stores
  created_date as REAL (Core Data seconds) in older schemas but as TEXT in the
  iOS 26 schema. convert_cocoa_core_data_ts_to_utc() did str + int and the
  TypeError aborted the artifact.

These tests pin the guards: out-of-range cache timestamps become None instead
of an exception, and health_achievements handles both schema generations.
"""
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts.webkit import cache_record_timestamp  # pylint: disable=wrong-import-position
from scripts.artifacts.health import health_achievements  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

# 2025-09-01 00:00:00 UTC expressed as Core Data seconds (Cocoa epoch 2001-01-01).
COCOA_2025_09_01 = 1756684800 - 978307200


class TestCacheRecordTimestamp(unittest.TestCase):
    """One corrupt double must not cost the examiner every cache record."""

    def test_valid_timestamp_converts(self):
        self.assertEqual(cache_record_timestamp(1756684800.0),
                         datetime(2025, 9, 1, tzinfo=timezone.utc))

    def test_post_2038_timestamp_still_converts(self):
        """64-bit time_t values beyond 2038 are valid on every current platform."""
        self.assertEqual(cache_record_timestamp(2 ** 33).year, 2242)

    def test_absurdly_large_double_returns_none(self):
        self.assertIsNone(cache_record_timestamp(1e300))

    def test_absurdly_negative_double_returns_none(self):
        self.assertIsNone(cache_record_timestamp(-1e18))


class TestHealthAchievementsSchemas(unittest.TestCase):
    """created_date must parse whether the column is REAL or TEXT."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Context.clear()
        Context.set_report_folder(self.tmpdir)

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_db(self, created_date_type, rows):
        db_path = pathlib.Path(self.tmpdir) / 'healthdb_secure.sqlite'
        db = sqlite3.connect(db_path)
        db.execute(f'''CREATE TABLE ACHAchievementsPlugin_earned_instances
                       (ROWID INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_unique_name TEXT, earned_date REAL,
                        created_date {created_date_type},
                        value_in_canonical_unit REAL,
                        value_canonical_unit TEXT, external_identifier TEXT,
                        creator_device INTEGER, sync_provenance INTEGER,
                        sync_identity INTEGER NOT NULL)''')
        db.executemany(
            '''INSERT INTO ACHAchievementsPlugin_earned_instances
               (template_unique_name, earned_date, created_date,
                value_in_canonical_unit, value_canonical_unit, creator_device,
                sync_identity)
               VALUES (?, ?, ?, ?, ?, ?, 1)''', rows)
        db.commit()
        db.close()
        Context.set_files_found([str(db_path)])
        return db_path

    def test_real_created_date_converts_to_datetime(self):
        """The pre-iOS-26 schema: created_date is Core Data seconds (REAL)."""
        self._make_db('REAL', [('FirstWorkout', 730.0, float(COCOA_2025_09_01),
                                1.0, 'count', 1)])
        _headers, data_list, _source = health_achievements.__wrapped__(Context)
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0][0],
                         datetime(2025, 9, 1, tzinfo=timezone.utc))

    def test_text_numeric_created_date_converts_to_datetime(self):
        """A numeric string is still a Core Data timestamp."""
        self._make_db('TEXT', [('FirstWorkout', 730.0, str(COCOA_2025_09_01),
                                1.0, 'count', 1)])
        _headers, data_list, _source = health_achievements.__wrapped__(Context)
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0][0],
                         datetime(2025, 9, 1, tzinfo=timezone.utc))

    def test_text_non_numeric_created_date_passes_through(self):
        """The iOS 26 shape that crashed the artifact: text that is not a number.

        The value must survive to the report untouched rather than abort the
        module; asserting pass-through also documents that we have not seen the
        real text format and are not guessing a parse for it.
        """
        self._make_db('TEXT', [('FirstWorkout', 730.0, '2025-10-13 06:53:59',
                                1.0, 'count', 1)])
        _headers, data_list, _source = health_achievements.__wrapped__(Context)
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0][0], '2025-10-13 06:53:59')

    def test_null_created_date_does_not_crash(self):
        self._make_db('TEXT', [('FirstWorkout', 730.0, None, 1.0, 'count', 1)])
        _headers, data_list, _source = health_achievements.__wrapped__(Context)
        self.assertEqual(len(data_list), 1)
        self.assertIsNone(data_list[0][0])


if __name__ == '__main__':
    unittest.main()
