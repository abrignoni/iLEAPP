"""Only the unsupported message date loses conversion; track end dates retain it."""
import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.artifacts import WithingsHealthMate as healthmate  # pylint: disable=wrong-import-position
from scripts.ilapfuncs import convert_cocoa_core_data_ts_to_utc  # pylint: disable=wrong-import-position


class Context:
    def get_files_found(self):
        return ['activity.sqlite']


class TestTrackedDates(unittest.TestCase):
    def test_cocoa_end_date_stays_a_converted_instant(self):
        row = [1] * 33
        row[4], row[5] = 699999000.0, 700000000.0
        with mock.patch.object(healthmate, 'get_sqlite_db_records', return_value=[row]):
            headers, rows, _ = healthmate.get_healthmate_tracked_activities.__wrapped__(Context())
        self.assertEqual(headers[1], ('End Date', 'datetime'))
        self.assertEqual(rows[0][1], convert_cocoa_core_data_ts_to_utc(700000000.0))
        self.assertEqual(len(headers), len(rows[0]))


if __name__ == '__main__':
    unittest.main()
