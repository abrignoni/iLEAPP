"""Edge cases in three shared conversion helpers in scripts/ilapfuncs.py.

* convert_cocoa_core_data_ts_to_utc added the epoch offset in seconds before the
  value was scaled from milliseconds, microseconds or nanoseconds, so those
  values came out about 31 years early.
* get_birthdate_from_unix_ts called .year on the empty value that
  convert_unix_ts_to_utc passes back, raising AttributeError.
* convert_bytes_to_unit stopped at GB and returned a bare number, without a
  unit, for anything from 1 TiB up.
"""
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
    get_birthdate_from_unix_ts,
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

    def test_sentinels_keep_the_earlier_path(self):
        # NSDate.distantPast and distantFuture in Cocoa seconds. A Notes attachment on a
        # registered iOS 17 corpus stores distantPast; these must not be rescaled here.
        for value in (-63114076800, 63113904000):
            with self.subTest(value=value):
                self.assertEqual(convert_cocoa_core_data_ts_to_utc(value),
                                 convert_unix_ts_to_utc(value + 978307200))


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
