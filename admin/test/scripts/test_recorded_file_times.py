"""Pin how these artifacts pick a file's time: the seeker's record, never the staged copy.

A FAT, exFAT or DOS-only zip reading has no zone, and the seekers stamp the staged copy with it
in the examiner's zone, so a report that read the copy's mtime would change with the machine.
Each module keeps its own _file_times, so every copy runs through the same cases here.
"""
import importlib
import os
import pathlib
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.search_files import FileInfo, StagedTimes  # pylint: disable=wrong-import-position

MODULES = ('draftmessage', 'fsCachedData', 'offlinePages', 'spotlightIndex')
UTC = 1717261200  # 2024-06-01 17:00:00 UTC
READING = '2024-06-01 12:00:00'


def file_times(name):
    module = importlib.import_module(f'scripts.artifacts.{name}')
    return module._file_times  # pylint: disable=protected-access


class RecordedFileTimes(unittest.TestCase):
    def check(self, info, expected):
        for name in MODULES:
            with self.subTest(module=name):
                seeker = SimpleNamespace(file_infos={'/staged/f': info})
                self.assertEqual(file_times(name)(seeker, '/staged/f'), expected)

    def test_a_recorded_utc_time_is_used_and_the_reading_is_not(self):
        self.check(FileInfo('f', 0, UTC, times=StagedTimes(modified=UTC, modified_no_zone=READING)), (UTC, ''))

    def test_a_seeker_that_records_no_times_object_gives_its_modification_date(self):
        self.check(FileInfo('f', 0, UTC), (UTC, ''))

    def test_a_reading_with_no_zone_stays_text(self):
        self.check(FileInfo('f', 0, 0, times=StagedTimes(modified_no_zone=READING)), (None, READING))

    def test_a_time_before_1970_is_kept(self):
        self.check(FileInfo('f', 0, -1, times=StagedTimes(modified=-1)), (-1, ''))

    def test_a_recorded_zero_is_no_time(self):
        self.check(FileInfo('f', 0, 0, times=StagedTimes(modified=0, modified_no_zone=READING)), (None, READING))
        self.check(FileInfo('f', 0, 0), (None, ''))

    def test_a_shown_time_rounds_down_and_is_not_rescaled(self):
        for name in MODULES:
            module = importlib.import_module(f'scripts.artifacts.{name}')
            convert = getattr(module, '_utc', None) or getattr(module, '_sec_to_utc', None)
            if convert is None:
                continue
            with self.subTest(module=name):
                self.assertEqual(convert(-0.5), datetime(1969, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
                self.assertEqual(convert(10_000_000_000), datetime(2286, 11, 20, 17, 46, 40, tzinfo=timezone.utc))
                self.assertEqual(convert(1e20), '')
                self.assertEqual(convert(None), '')

    def test_no_record_gives_no_time(self):
        for name in MODULES:
            with self.subTest(module=name):
                self.assertEqual(file_times(name)(SimpleNamespace(file_infos={}), '/staged/f'), (None, ''))
                self.assertEqual(file_times(name)(None, '/staged/f'), (None, ''))

    def test_every_spelling_of_a_windows_path_finds_the_record(self):
        info = FileInfo('f', 0, UTC)
        stored = '\\\\?\\C:\\out\\data\\f'
        for name in MODULES:
            for asked in ('C:/out/data/f', 'C:\\out\\data\\f', stored):
                with self.subTest(module=name, asked=asked):
                    self.assertEqual(file_times(name)(SimpleNamespace(file_infos={stored: info}), asked), (UTC, ''))

    @unittest.skipUnless(hasattr(time, 'tzset'), 'needs time.tzset')
    def test_the_staged_copy_and_the_examiners_zone_change_nothing(self):
        before = os.environ.get('TZ')

        def restore():
            if before is None:
                os.environ.pop('TZ', None)
            else:
                os.environ['TZ'] = before
            time.tzset()

        self.addCleanup(restore)
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'staged')
            with open(path, 'wb') as handle:
                handle.write(b'x')
            os.utime(path, (5, 5))
            seeker = SimpleNamespace(file_infos={path: FileInfo('f', 0, 0, times=StagedTimes(modified_no_zone=READING))})
            for zone in ('UTC', 'America/New_York', 'Asia/Tokyo'):
                os.environ['TZ'] = zone
                time.tzset()
                for name in MODULES:
                    with self.subTest(module=name, zone=zone):
                        self.assertEqual(file_times(name)(seeker, path), (None, READING))


if __name__ == '__main__':
    unittest.main()
