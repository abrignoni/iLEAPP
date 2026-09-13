"""convert_plist_date_to_utc and convert_plist_date_to_timezone_offset on Python 3.10.

Regression test for a defect in both helpers. Each formatted its argument into an ISO
string ending in Z and parsed that string back with datetime.fromisoformat:

    str_date = '%04d-%02d-%02dT%02d:%02d:%02dZ' % (...)
    return datetime.fromisoformat(str_date)

datetime.fromisoformat did not accept a trailing Z until Python 3.11, so on 3.10 both
raised ValueError for every input. README.md lists 3.10 as a supported version and the
runtime contract job runs it, but that job imports the artifact modules rather than
calling into them, so a break inside a helper body was invisible to it. Fourteen artifact
modules call convert_plist_date_to_utc.

The helpers now attach the timezone to the value directly instead of going through a
string. A plist date is naive and already UTC. The sub-second part is still dropped, as
the '%02d' seconds field did before, so the output is unchanged on the versions where the
old code ran at all; the cases below pin that rather than assume it.

None of these datetimes come from an evidence file.
"""
import pathlib
import sys
import unittest
from datetime import datetime, timezone

# admin/test/scripts/<this file>, so the repository root is three levels up.
ROOT_DIR = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.ilapfuncs import (convert_plist_date_to_utc,
                               convert_plist_date_to_timezone_offset)


class ConvertPlistDateToUtc(unittest.TestCase):
    """The conversion must run on every supported Python, not only 3.11 and later."""

    def test_returns_an_aware_utc_datetime(self):
        self.assertEqual(convert_plist_date_to_utc(datetime(2024, 5, 1, 12, 0, 0)),
                         datetime(2024, 5, 1, 12, 0, 0, tzinfo=timezone.utc))

    def test_drops_the_sub_second_part_as_before(self):
        self.assertEqual(convert_plist_date_to_utc(datetime(2024, 5, 1, 12, 0, 0, 123456)),
                         datetime(2024, 5, 1, 12, 0, 0, tzinfo=timezone.utc))

    def test_handles_a_date_before_the_unix_epoch(self):
        self.assertEqual(convert_plist_date_to_utc(datetime(1904, 6, 15, 8, 30, 15)),
                         datetime(1904, 6, 15, 8, 30, 15, tzinfo=timezone.utc))

    def test_second_and_year_boundaries(self):
        for value in (datetime(1999, 12, 31, 23, 59, 59, 999999),
                      datetime(2001, 1, 1, 0, 0, 0)):
            with self.subTest(value=value):
                self.assertEqual(convert_plist_date_to_utc(value),
                                 value.replace(microsecond=0, tzinfo=timezone.utc))

    def test_falsy_input_is_returned_unchanged(self):
        for value in (None, ''):
            with self.subTest(value=value):
                self.assertEqual(convert_plist_date_to_utc(value), value)


class ConvertPlistDateToTimezoneOffset(unittest.TestCase):
    """The offset variant shared the same string round trip and the same break."""

    def test_runs_and_applies_the_offset(self):
        result = convert_plist_date_to_timezone_offset(
            datetime(2024, 5, 1, 12, 0, 0), 'UTC')
        self.assertIn('2024-05-01', str(result))

    def test_falsy_input_is_returned_unchanged(self):
        self.assertIsNone(convert_plist_date_to_timezone_offset(None, 'UTC'))


if __name__ == '__main__':
    unittest.main()
