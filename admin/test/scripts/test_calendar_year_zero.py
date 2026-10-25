"""calendarEvents keeps its rows when SQLite renders a stored time as year 0000 (SYNTHETIC values)."""
# pylint: disable=protected-access
import sqlite3
import unittest

from scripts.artifacts import calendarAll


class YearZeroTest(unittest.TestCase):
    def test_sqlite_year_zero_text_is_blank_not_an_error(self):
        db = sqlite3.connect(':memory:')
        text = db.execute("SELECT datetime('2001-01-01', ? || ' seconds')", (-63114076800,)).fetchone()[0]
        self.assertTrue(text.startswith('0000'))
        self.assertEqual(calendarAll._utc_or_blank(text), '')

    def test_ordinary_and_missing_values(self):
        self.assertEqual(str(calendarAll._utc_or_blank('2026-03-01 12:00:00')), '2026-03-01 12:00:00+00:00')
        self.assertEqual(str(calendarAll._utc_or_blank('2026-03-01 12:00:00.250')), '2026-03-01 12:00:00+00:00')
        self.assertEqual(calendarAll._utc_or_blank(None), '')
        self.assertEqual(calendarAll._utc_or_blank('not a date'), '')


if __name__ == '__main__':
    unittest.main()
