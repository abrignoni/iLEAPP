"""convert_unix_ts_to_utc: pre-1970 epochs, and sub-second units outside 2001-2286.

Regression test for two defects in convert_unix_ts_in_seconds, which normalises a Unix
timestamp to seconds before conversion.

It used to size its input with int(math.log10(ts))+1 and, when that came to more than ten
digits, trim the value down to ten digits. Two consequences:

  * math.log10 raises ValueError for any value at or below zero, so a timestamp before
    1970 crashed the artifact reading it. Birth dates are the field that reaches this in
    practice, and -1 is a common stored sentinel.
  * Trimming to ten digits assumes the value in seconds is itself ten digits, which only
    holds from 2001-09-09 to 2286. A millisecond value outside that window was divided by
    a power of ten that was not a power of a thousand, so it decoded to a plausible but
    wrong date rather than failing: a 1990 date read as 2170 and a 1995 date as 2220.

The unit is now taken from the value's magnitude and divided by the matching power of a
thousand. Conversion also adds a timedelta to the epoch instead of calling
datetime.fromtimestamp, which the Python documentation notes may raise OSError for a
timestamp the platform C gmtime() cannot represent. windows_smoke.yml runs this file so
the pre-1970 cases are exercised on Windows rather than assumed.

The timestamps here are chosen to cover the unit and epoch boundaries. None of them come
from an evidence file.
"""
import pathlib
import sys
import unittest
from datetime import datetime, timezone

# admin/test/scripts/<this file>, so the repository root is three levels up from the
# directory holding it. windows_smoke.yml runs this file directly rather than through
# unittest discovery, so the path cannot be assumed to already be set.
ROOT_DIR = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.ilapfuncs import (convert_ts_int_to_utc, convert_unix_ts_in_seconds,
                                convert_unix_ts_to_str, convert_unix_ts_to_utc)

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Chosen for coverage, not taken from any capture: two comfortably pre-1970 dates, one
# just outside the near-epoch band where units stop being separable, one just after the
# epoch, then the pre-2001 range the digit sizing got wrong, then modern dates.
DATES = [
    (1930, 1, 1), (1965, 3, 8), (1969, 6, 1), (1970, 7, 1),
    (1975, 1, 1), (1985, 6, 15), (1990, 1, 1), (1995, 1, 1), (2000, 1, 1),
    (2001, 9, 9), (2015, 6, 1), (2025, 8, 12), (2100, 1, 1),
]

UNITS = (('seconds', 1), ('milliseconds', 10 ** 3),
         ('microseconds', 10 ** 6), ('nanoseconds', 10 ** 9))


def as_epoch(year, month, day, multiplier=1):
    """The given UTC date as a Unix timestamp in the unit given by multiplier."""
    return int((datetime(year, month, day, tzinfo=timezone.utc) - EPOCH).total_seconds()) * multiplier


class TestUnixTimestampConversion(unittest.TestCase):

    def test_pre_1970_does_not_raise(self):
        """The reported crash: any value at or below zero went into math.log10."""
        for value in (-1, -1000, as_epoch(1930, 1, 1), as_epoch(1965, 3, 8, 10 ** 3)):
            with self.subTest(value=value):
                self.assertIsInstance(convert_unix_ts_to_utc(value), datetime)

    def test_pre_1970_decodes_to_the_right_date(self):
        """Not crashing is not enough: the date itself has to be right."""
        for year, month, day in ((1930, 1, 1), (1965, 3, 8), (1969, 6, 1)):
            for unit, multiplier in UNITS:
                with self.subTest(date=(year, month, day), unit=unit):
                    got = convert_unix_ts_to_utc(as_epoch(year, month, day, multiplier))
                    self.assertEqual(got, datetime(year, month, day, tzinfo=timezone.utc))

    def test_sentinel_minus_one(self):
        """-1 is a common stored 'unset' value and used to crash."""
        self.assertEqual(convert_unix_ts_to_utc(-1),
                         datetime(1969, 12, 31, 23, 59, 59, tzinfo=timezone.utc))

    def test_every_unit_round_trips(self):
        """Seconds, milliseconds, microseconds and nanoseconds all reach the same date.

        The near-epoch dates are excluded: magnitude cannot separate the units there, and
        test_near_epoch_units_are_not_separable pins that behaviour deliberately.
        """
        for year, month, day in DATES:
            if abs(as_epoch(year, month, day)) < 10 ** 7:
                continue
            for unit, multiplier in UNITS:
                with self.subTest(date=(year, month, day), unit=unit):
                    got = convert_unix_ts_to_utc(as_epoch(year, month, day, multiplier))
                    self.assertEqual(got, datetime(year, month, day, tzinfo=timezone.utc))

    def test_pre_2001_milliseconds_are_not_mis_scaled(self):
        """The silent half of the defect: these decoded to a wrong year, without raising."""
        for year, month, day in ((1975, 1, 1), (1985, 6, 15), (1990, 1, 1),
                                 (1995, 1, 1), (2000, 1, 1)):
            with self.subTest(date=(year, month, day)):
                got = convert_unix_ts_to_utc(as_epoch(year, month, day, 10 ** 3))
                self.assertEqual(got, datetime(year, month, day, tzinfo=timezone.utc))

    def test_seconds_are_passed_through(self):
        """A value already in seconds must not be rescaled."""
        for year, month, day in DATES:
            with self.subTest(date=(year, month, day)):
                seconds = as_epoch(year, month, day)
                self.assertEqual(convert_unix_ts_in_seconds(seconds), seconds)

    def test_near_epoch_units_are_not_separable(self):
        """Documented limit, pinned so a change to it is visible rather than silent.

        Within about four months of the epoch a sub-second value is indistinguishable
        from a coarser unit, so it is read as the coarser one. A caller that knows its
        unit should convert it itself.
        """
        near = as_epoch(1969, 12, 1, 10 ** 3)          # milliseconds, inside the band
        self.assertEqual(convert_unix_ts_in_seconds(near), near)

    def test_falsy_values_are_returned_unchanged(self):
        """Long-standing behaviour of the wrapper, kept so callers testing it still work."""
        for value in (0, None, ''):
            with self.subTest(value=value):
                self.assertEqual(convert_unix_ts_to_utc(value), value)

    def test_float_seconds_accepted(self):
        """Several artifacts divide a millisecond column by 1000 before calling."""
        got = convert_unix_ts_to_utc(as_epoch(1965, 3, 8, 10 ** 3) / 1000)
        self.assertEqual(got, datetime(1965, 3, 8, tzinfo=timezone.utc))

    def test_sub_second_remainder_floors_toward_the_past(self):
        """A partial second belongs to the second containing it, on both sides of zero.

        Both values sit above the millisecond threshold, so they are read as milliseconds
        and carry a half-second remainder that has to floor rather than truncate.
        """
        self.assertEqual(convert_unix_ts_in_seconds(10 ** 10 + 1_500), 10 ** 7 + 1)
        self.assertEqual(convert_unix_ts_in_seconds(-(10 ** 10) - 1_500), -(10 ** 7) - 2)

    def test_str_converter_matches_the_datetime_converter(self):
        """convert_unix_ts_to_str shares the sizing helper and must agree with it."""
        for year, month, day in ((1930, 1, 1), (1965, 3, 8), (1990, 1, 1), (2025, 8, 12)):
            for multiplier in (1, 10 ** 3):
                with self.subTest(date=(year, month, day), multiplier=multiplier):
                    value = as_epoch(year, month, day, multiplier)
                    self.assertEqual(convert_unix_ts_to_str(value),
                                     f'{year:04d}-{month:02d}-{day:02d} 00:00:00')

    def test_int_converter_handles_pre_1970(self):
        """convert_ts_int_to_utc is reached from the timezone path, which can pass a
        negative once the sizing helper stops rejecting one."""
        self.assertEqual(convert_ts_int_to_utc(as_epoch(1965, 3, 8)),
                         datetime(1965, 3, 8, tzinfo=timezone.utc))

    def test_int_converter_keeps_sub_second_precision(self):
        """convert_ts_int_to_utc is handed float seconds by Biome artifacts, and the
        fraction is part of the record. Truncating it silently drops precision."""
        value = 1_784_568_258.951650
        self.assertEqual(convert_ts_int_to_utc(value),
                         datetime(2026, 7, 20, 17, 24, 18, 951650, tzinfo=timezone.utc))


if __name__ == '__main__':
    unittest.main()
