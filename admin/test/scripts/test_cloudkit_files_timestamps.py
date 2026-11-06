"""Timestamp handling in cloudkit_cache.cloudkit_files.

Modified, Field 8 and Field 10 are left empty when the value is below 1000 Unix seconds
or cannot be converted, and a negative raw protobuf value that lands after that limit
is still a date.
"""
import os
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from scripts import blackboxprotobuf  # pylint: disable=wrong-import-position
from scripts.artifacts.cloudkit_cache import (  # pylint: disable=wrong-import-position
    _file_field_times, _unix_seconds_to_utc)

_APPLE = 978307200
_TYPEDEF = {'8': {'type': 'int', 'name': ''}, '9': {'type': 'int', 'name': ''},
            '10': {'type': 'int', 'name': ''}}


def _blob(**fields):
    return bytes(blackboxprotobuf.encode_message(
        {k.lstrip('f'): v for k, v in fields.items()},
        {k.lstrip('f'): _TYPEDEF[k.lstrip('f')] for k in fields}))


class UnixSecondsTest(unittest.TestCase):
    def test_near_epoch_values_are_empty(self):
        for value in (0, 424, 427, 999, -5, -8589934091):
            self.assertEqual(_unix_seconds_to_utc(value), '', value)

    def test_limit_and_ordinary_values_convert(self):
        self.assertEqual(_unix_seconds_to_utc(1000),
                         datetime(1970, 1, 1, 0, 16, 40, tzinfo=timezone.utc))
        self.assertEqual(_unix_seconds_to_utc(1765388369),
                         datetime.fromtimestamp(1765388369, timezone.utc))

    def test_absent_and_unconvertible_values_are_empty(self):
        self.assertEqual(_unix_seconds_to_utc(None), '')
        self.assertEqual(_unix_seconds_to_utc('not a number'), '')
        self.assertEqual(_unix_seconds_to_utc(10**12 * 400), '')


class FileFieldTimesTest(unittest.TestCase):
    def test_fields_8_and_10_read_from_the_apple_epoch(self):
        f8, f10 = _file_field_times(_blob(f8=785347764, f9=785347764, f10=747236683))
        self.assertEqual(f8, datetime.fromtimestamp(785347764 + _APPLE, timezone.utc))
        self.assertEqual(f10, datetime.fromtimestamp(747236683 + _APPLE, timezone.utc))

    def test_negative_raw_value_before_2001_is_kept(self):
        f8, _ = _file_field_times(_blob(f8=-662774400, f10=747236683))
        self.assertEqual(f8, datetime(1980, 1, 1, tzinfo=timezone.utc))

    def test_near_epoch_field_values_are_empty(self):
        self.assertEqual(_file_field_times(_blob(f8=-978306773, f10=-978306776)), ('', ''))

    def test_missing_fields_and_missing_blob(self):
        self.assertEqual(_file_field_times(_blob(f9=785347764)), ('', ''))
        self.assertEqual(_file_field_times(None), ('', ''))
        self.assertEqual(_file_field_times(b''), ('', ''))

    def test_undecodable_blob_returns_none(self):
        self.assertIsNone(_file_field_times(b'\xff\xff\xff'))


if __name__ == '__main__':
    unittest.main()
