"""Edge cases in shared conversion helpers in scripts/ilapfuncs.py and three local converters.

* convert_cocoa_core_data_ts_to_utc added the epoch offset in seconds before the value was
  scaled from ms, us or ns, so those came out about 31 years early. It and webkit_timestampsconv
  report the exact NSDate.distantPast and distantFuture values blank.
* webkit_timestampsconv now adds to the epoch before 1970 instead of relying on
  datetime.fromtimestamp, which is platform dependent there.
* get_birthdate and get_birthdate_from_unix_ts raised on an empty value or a sentinel.
* convert_bytes_to_unit stopped at GB and returned a bare number from 1 TiB up.
* homeKit, textReplacements and widgetEngagements each added the offset themselves.
"""
# pylint: disable=protected-access
import pathlib
import sys
import unittest
from datetime import datetime, timezone

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.ilapfuncs import (  # pylint: disable=wrong-import-position
    convert_bytes_to_unit,
    convert_cocoa_core_data_ts_to_utc,
    convert_unix_ts_to_utc,
    get_birthdate,
    get_birthdate_from_unix_ts,
    webkit_timestampsconv,
)

COCOA_SECONDS = 700000000
EXPECTED = datetime(2023, 3, 8, 20, 26, 40, tzinfo=timezone.utc)


class CocoaUnitScaling(unittest.TestCase):
    def test_every_unit_gives_the_same_instant(self):
        for factor in (1, 10**3, 10**6, 10**9):
            with self.subTest(factor=factor):
                self.assertEqual(
                    convert_cocoa_core_data_ts_to_utc(COCOA_SECONDS * factor), EXPECTED)

    def test_seconds_path_unchanged(self):
        self.assertEqual(
            convert_cocoa_core_data_ts_to_utc(COCOA_SECONDS + 0.75), EXPECTED)
        self.assertEqual(
            convert_cocoa_core_data_ts_to_utc(-978307200 + 86400),
            datetime(1970, 1, 2, tzinfo=timezone.utc))

    def test_empty_values_pass_through(self):
        for value in (None, 0, ''):
            with self.subTest(value=value):
                self.assertEqual(convert_cocoa_core_data_ts_to_utc(value), value)

    def test_distant_past_and_future_are_blank(self):
        # Values read from Foundation: NSDate.distantPast and distantFuture.
        for value in (-63114076800, -63114076800.0, 63113904000):
            with self.subTest(value=value):
                self.assertEqual(convert_cocoa_core_data_ts_to_utc(value), '')

    def test_distant_past_no_longer_reads_as_1968(self):
        result = convert_cocoa_core_data_ts_to_utc(-63114076800)
        self.assertNotIsInstance(result, datetime)

    def test_genuine_pre_1970_dates_still_convert(self):
        self.assertEqual(convert_cocoa_core_data_ts_to_utc(-1009843200),
                         datetime(1969, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(convert_cocoa_core_data_ts_to_utc(-63114076799),
                         convert_unix_ts_to_utc(-63114076799 + 978307200))

    def test_unit_boundary(self):
        # 10**11 is the first value scaled from milliseconds; one below stays seconds.
        self.assertEqual(convert_cocoa_core_data_ts_to_utc(10**11),
                         datetime(2004, 3, 3, 9, 46, 40, tzinfo=timezone.utc))
        self.assertEqual(convert_cocoa_core_data_ts_to_utc(10**11 - 1),
                         convert_unix_ts_to_utc(10**11 - 1 + 978307200))

    def test_malformed_values_still_raise(self):
        with self.assertRaises(TypeError):
            convert_cocoa_core_data_ts_to_utc('not a number')


class SentinelInReportOutputs(unittest.TestCase):
    def test_lava_stores_the_blank_as_blank(self):
        from scripts.lavafuncs import _prepare_datetime_value  # pylint: disable=import-outside-toplevel
        self.assertEqual(_prepare_datetime_value(convert_cocoa_core_data_ts_to_utc(-63114076800)), '')


class WebkitTimestampsconv(unittest.TestCase):
    def test_sentinels_are_blank_like_the_cocoa_converter(self):
        for value in (-63114076800, -63114076800.0, 63113904000, 63113904000.0):
            with self.subTest(value=value):
                self.assertEqual(webkit_timestampsconv(value), '')
                self.assertEqual(webkit_timestampsconv(value),
                                 convert_cocoa_core_data_ts_to_utc(value))

    def test_year_4001_that_is_not_the_sentinel_converts(self):
        self.assertEqual(webkit_timestampsconv(63113904001),
                         datetime(4001, 1, 1, 0, 0, 1, tzinfo=timezone.utc))

    def test_epoch_fraction_and_modern_values(self):
        self.assertEqual(webkit_timestampsconv(0), datetime(2001, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(webkit_timestampsconv(700000000), EXPECTED)
        self.assertEqual(webkit_timestampsconv(700000000.5),
                         EXPECTED.replace(microsecond=500000))

    def test_pre_1970_and_unix_epoch(self):
        self.assertEqual(webkit_timestampsconv(-978307200), datetime(1970, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(webkit_timestampsconv(-978307201), datetime(1969, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
        self.assertEqual(webkit_timestampsconv(-1009843200), datetime(1969, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(webkit_timestampsconv(-63113904000), datetime(1, 1, 1, tzinfo=timezone.utc))

    def test_out_of_range_stays_a_value_error(self):
        for value in (-63114076799, -63113904001, -1e30, 1e12):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    webkit_timestampsconv(value)


class LocalCocoaConverters(unittest.TestCase):
    """homeKit, textReplacements and widgetEngagements each had their own converter."""

    def converters(self):
        from scripts.artifacts import homeKit, textReplacements, widgetEngagements  # pylint: disable=import-outside-toplevel
        return (('homeKit', homeKit._cocoa), ('textReplacements', textReplacements._cocoa),
                ('widgetEngagements', widgetEngagements._cocoa))

    def test_sentinels_are_blank(self):
        for name, convert in self.converters():
            for value in (-63114076800, 63113904000):
                with self.subTest(module=name, value=value):
                    self.assertEqual(convert(value), '')

    def test_seconds_zero_units_and_truncated_fractions(self):
        for name, convert in self.converters():
            with self.subTest(module=name):
                self.assertEqual(convert(COCOA_SECONDS), EXPECTED)
                # the shared converter drops sub-second parts, as these converters always did
                self.assertEqual(convert(COCOA_SECONDS + 0.5), EXPECTED)
                self.assertEqual(convert(0), datetime(2001, 1, 1, tzinfo=timezone.utc))
                self.assertEqual(convert(COCOA_SECONDS * 1000), EXPECTED)
                self.assertEqual(convert(-1009843200 - 978307200), convert_unix_ts_to_utc(-1009843200))

    def test_empty_inputs(self):
        for name, convert in self.converters():
            for value in (None, ''):
                with self.subTest(module=name, value=value):
                    self.assertEqual(convert(value), '')


class TwitterCocoa(unittest.TestCase):
    def test_guard_and_helper_together(self):
        from scripts.artifacts.twitterX import _cocoa  # pylint: disable=import-outside-toplevel
        for value in (-63114076800, -63114076800.0, None, True, 'x'):
            with self.subTest(value=value):
                self.assertEqual(_cocoa(value), '')
        self.assertEqual(_cocoa(700000000), EXPECTED)


class Birthdate(unittest.TestCase):
    def test_absent_and_sentinels_are_blank(self):
        for value in (None, -63114076800, 63113904000):
            with self.subTest(value=value):
                self.assertEqual(get_birthdate(value), '')

    def test_valid_dates_and_the_no_year_convention(self):
        self.assertEqual(get_birthdate(0), '01 January 2001')
        self.assertEqual(get_birthdate(-978307200), '01 January 1970')
        # Apple stores a birthday without a year in 1604; the year is left out
        self.assertEqual(get_birthdate((datetime(1604, 7, 9) - datetime(2001, 1, 1)).total_seconds()), '09 July')

    def test_other_malformed_values_still_raise(self):
        with self.assertRaises(TypeError):
            get_birthdate('x')


class BirthdateFromUnix(unittest.TestCase):
    def test_empty_values_pass_through(self):
        for value in (None, 0, ''):
            with self.subTest(value=value):
                self.assertEqual(get_birthdate_from_unix_ts(value), value)

    def test_date(self):
        self.assertEqual(get_birthdate_from_unix_ts(0.5 * 86400 + 86400 * 365),
                         '01 January 1971')


class BytesToUnit(unittest.TestCase):
    def test_terabytes_and_up_carry_a_unit(self):
        self.assertEqual(convert_bytes_to_unit(2 * 1024**4), '2.0 TB')
        self.assertEqual(convert_bytes_to_unit(3 * 1024**5), '3.0 PB')

    def test_smaller_sizes_unchanged(self):
        self.assertEqual(convert_bytes_to_unit(512), '512.0 bytes')
        self.assertEqual(convert_bytes_to_unit(1536), '1.5 KB')
        self.assertEqual(convert_bytes_to_unit(5 * 1024**3), '5.0 GB')
        self.assertEqual(convert_bytes_to_unit(0), 0)


if __name__ == '__main__':
    unittest.main()
