"""Cocoa times between NSDate.distantPast and Python's datetime.min are blank, not a failed artifact.

NSDate.distantPast is -63114076800 Cocoa seconds; datetime.min (0001-01-01 00:00:00 UTC) is
-63113904000. Foundation shows the 172,800 seconds between them as 0001-01-01 and 0001-01-02
(NSDateFormatter, Gregorian calendar, UTC, on macOS); datetime cannot hold them. Before this
change webkit_timestampsconv raised ValueError and get_birthdate OverflowError for them, which
ended an artifact that does not catch it (notificationsDuet, calendarBirthdays) and dropped the
record in one that does (biomeDKInfocus). Every other input keeps its earlier behavior.

All inputs are constructed. A by-name scan of the SQLite stores in three images (otto_ios17,
iphone11_ios17, wilkerson_iphone16_ios26) found no value in this range; SEGB and protobuf streams
and plists, where most webkit_timestampsconv callers read their times, were not scanned.
"""
import math
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import scripts.ilapfuncs as ilapfuncs  # pylint: disable=wrong-import-position
from scripts.ilapfuncs import get_birthdate, webkit_timestampsconv  # pylint: disable=wrong-import-position
from scripts.artifacts import biomeDKInfocus, calendarAll, notificationsDuet  # pylint: disable=wrong-import-position
import test_webkit_sentinel_callers as callers  # pylint: disable=wrong-import-position

DISTANT_PAST = -63114076800
DISTANT_FUTURE = 63113904000
DATETIME_MIN = -63113904000  # 0001-01-01 00:00:00 UTC as Cocoa seconds
YEAR_ONE = datetime(1, 1, 1, tzinfo=timezone.utc)
COCOA_SECONDS = 700000000
EXPECTED = datetime(2023, 3, 8, 20, 26, 40, tzinfo=timezone.utc)
INSIDE = (math.nextafter(float(DISTANT_PAST), math.inf), DISTANT_PAST + 1, DISTANT_PAST + 0.5,
          DISTANT_PAST + 18000, (DISTANT_PAST + DATETIME_MIN) // 2, DATETIME_MIN - 1,
          math.nextafter(float(DATETIME_MIN), -math.inf))


class QuietLog(unittest.TestCase):
    """Capture logfunc and start each test with an empty diagnostic record."""

    def setUp(self):
        logged = getattr(ilapfuncs, '_unrepresentable_cocoa_logged', set())
        logged.clear()
        patcher = mock.patch('scripts.ilapfuncs.logfunc')
        self.log = patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(logged.clear)


class Boundaries(QuietLog):
    def test_constant_is_datetime_min(self):
        self.assertEqual(ilapfuncs.COCOA_DATETIME_MIN, DATETIME_MIN)
        self.assertEqual((YEAR_ONE - datetime(2001, 1, 1, tzinfo=timezone.utc)).total_seconds(),
                         DATETIME_MIN)

    def test_inside_the_window_is_blank(self):
        for value in INSIDE:
            with self.subTest(value=value):
                self.assertEqual(webkit_timestampsconv(value), '')
                self.assertEqual(get_birthdate(value), '')

    def test_window_edges_keep_their_meaning(self):
        for value in (DISTANT_PAST, float(DISTANT_PAST), DISTANT_FUTURE):
            with self.subTest(value=value):
                self.assertEqual(webkit_timestampsconv(value), '')
                self.assertEqual(get_birthdate(value), '')
        for value in (DATETIME_MIN, float(DATETIME_MIN)):
            with self.subTest(value=value):
                self.assertEqual(webkit_timestampsconv(value), YEAR_ONE)
                # converted, not blank; strftime renders year 1 as '0001' or '1' by platform and Python version
                self.assertEqual(get_birthdate(value), YEAR_ONE.strftime('%d %B %Y'))
        self.assertEqual(webkit_timestampsconv(DATETIME_MIN + 0.5),
                         YEAR_ONE.replace(microsecond=500000))
        self.log.assert_not_called()

    def test_normal_dates_and_types(self):
        self.assertEqual(webkit_timestampsconv(COCOA_SECONDS), EXPECTED)
        self.assertEqual(webkit_timestampsconv(float(COCOA_SECONDS) + 0.25), EXPECTED.replace(microsecond=250000))
        self.assertEqual(webkit_timestampsconv(True), datetime(2001, 1, 1, 0, 0, 1, tzinfo=timezone.utc))
        self.assertEqual(get_birthdate(COCOA_SECONDS), '08 March 2023')
        self.assertEqual(webkit_timestampsconv(COCOA_SECONDS).tzinfo, timezone.utc)

    def test_other_invalid_input_unchanged(self):
        below = math.nextafter(float(DISTANT_PAST), -math.inf)
        for value in (below, DISTANT_PAST - 1, -1e11, 1e12, float('inf'), float('-inf'), float('nan')):
            with self.subTest(helper='webkit', value=value):
                with self.assertRaises(ValueError):
                    webkit_timestampsconv(value)
        for value in (below, DISTANT_PAST - 1, -1e11, 1e12, float('-inf')):
            with self.subTest(helper='birthdate', value=value):
                with self.assertRaises(OverflowError):
                    get_birthdate(value)
        for value in (None, '700000000', b'x'):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    webkit_timestampsconv(value)
        with self.assertRaises(TypeError):
            get_birthdate('x')
        self.log.assert_not_called()


class Diagnostic(QuietLog):
    def test_each_value_is_logged_once_up_to_a_limit(self):
        webkit_timestampsconv(DISTANT_PAST + 1)
        webkit_timestampsconv(DISTANT_PAST + 1)
        get_birthdate(DISTANT_PAST + 1)
        self.assertEqual(self.log.call_count, 1)
        self.assertIn(repr(DISTANT_PAST + 1), self.log.call_args.args[0])
        for offset in range(2, 20):
            webkit_timestampsconv(DISTANT_PAST + offset)
        limit = ilapfuncs._UNREPRESENTABLE_COCOA_LOG_LIMIT  # pylint: disable=protected-access
        self.assertEqual(self.log.call_count, limit + 1)
        self.assertIn('not logging the rest', self.log.call_args.args[0])


class RecordsAreKept(QuietLog):
    def test_unguarded_caller_keeps_every_record(self):
        duet = callers.NotificationsDuet()
        entries = [(callers.WRITTEN, duet.record(COCOA_SECONDS, COCOA_SECONDS)),
                   (callers.WRITTEN, duet.record(DISTANT_PAST + 18000, COCOA_SECONDS))]
        for rows in map(callers.rows_of, callers.run_segb(notificationsDuet.get_notificationsDuet, entries)):
            self.assertEqual([(r[1], r[2]) for r in rows], [(EXPECTED, EXPECTED), (None, EXPECTED)])
            self.assertEqual([r[5] for r in rows], ['title', 'title'])

    def test_try_wrapped_caller_keeps_the_record(self):
        infocus = callers.BiomeDKInfocusRetention()
        entries = [(callers.WRITTEN, infocus.record(COCOA_SECONDS, COCOA_SECONDS, COCOA_SECONDS)),
                   (callers.WRITTEN, infocus.record(COCOA_SECONDS, COCOA_SECONDS, DATETIME_MIN - 1))]
        for rows in map(callers.rows_of, callers.run_segb(biomeDKInfocus.get_biomeDKInfocus, entries)):
            self.assertEqual([r[1:4] for r in rows], [(EXPECTED, EXPECTED, EXPECTED),
                                                       (EXPECTED, EXPECTED, None)])

    def test_calendar_birthdays_keeps_every_row(self):
        # calendarBirthdays leaves its read-only connection open, and Windows will not delete an
        # open file, so the temporary folder may outlive the test there.
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            path = pathlib.Path(folder) / 'Calendar.sqlitedb'
            db = sqlite3.connect(path)
            db.executescript('''
                CREATE TABLE Store (ROWID INTEGER PRIMARY KEY, name TEXT);
                CREATE TABLE Calendar (ROWID INTEGER PRIMARY KEY, title TEXT, color TEXT, store_id INTEGER);
                CREATE TABLE CalendarItem (ROWID INTEGER PRIMARY KEY, summary TEXT, start_date REAL,
                                           calendar_id INTEGER, calendar_scale TEXT);
                INSERT INTO Store VALUES (1, 'Account');
                INSERT INTO Calendar VALUES (1, 'Birthdays', NULL, 1);''')
            db.executemany('INSERT INTO CalendarItem VALUES (?, ?, ?, 1, ?)',
                           [(1, 'Person A', COCOA_SECONDS, 'gregorian'),
                            (2, 'Person B', DISTANT_PAST + 86400, 'gregorian'),
                            (3, 'Person C', None, 'gregorian')])
            db.commit()
            db.close()
            ctx = SimpleNamespace(get_files_found=lambda: [str(path)], get_relative_path=lambda p: 'Calendar.sqlitedb')
            _headers, (rows, _html), _source = calendarAll.calendarBirthdays.__wrapped__(ctx)
        self.assertEqual([(r[0], r[1]) for r in rows],
                         [('08 March 2023', 'Person A'), ('', 'Person B'), ('', 'Person C')])


if __name__ == '__main__':
    unittest.main()
