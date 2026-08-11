"""Cover the temp directory PowerLog decompresses its rotated archives into.

A device keeps months of rotated `.PLSQL.gz` telemetry archives. The artifacts cannot
query a gzip file, so the module decompresses each one to a session temp directory and
reuses it across all of its artifacts. Those copies are the full uncompressed size, so an
extraction with a long history leaves hundreds of megabytes there.

Nothing removed them. 135 directories totalling 12 GB were found in the system temp
directory of one machine, from two days of ordinary runs, all of which had completed
normally. That is the difference from the FSEvents cache leak fixed alongside this: that
one only leaked when a run was interrupted, this one leaked every single time.

Both halves are needed and they cover different failures: atexit for a run that ends, a
sweep for a run that is killed and never gets to run atexit at all.
"""
import os
import pathlib
import sys
import tempfile
import time
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import powerlog  # pylint: disable=wrong-import-position


class GzTempRemovalTests(unittest.TestCase):
    """What a finished run must leave behind: nothing."""

    def setUp(self):
        self.original_cache = dict(powerlog._GZ_CACHE)  # pylint: disable=protected-access
        self.original_temp = dict(powerlog._GZ_TEMP)  # pylint: disable=protected-access
        powerlog._GZ_CACHE.clear()  # pylint: disable=protected-access
        powerlog._GZ_TEMP.clear()  # pylint: disable=protected-access

    def tearDown(self):
        powerlog._remove_gz_temp()  # pylint: disable=protected-access
        powerlog._GZ_CACHE.update(self.original_cache)  # pylint: disable=protected-access
        powerlog._GZ_TEMP.update(self.original_temp)  # pylint: disable=protected-access

    def _materialize_one(self):
        """Decompress a real gzip archive through the module's own code path."""
        import gzip  # pylint: disable=import-outside-toplevel

        source_dir = tempfile.TemporaryDirectory()
        self.addCleanup(source_dir.cleanup)
        gz_path = os.path.join(source_dir.name, 'powerlog_2026-01-01_ABCD1234.PLSQL.gz')
        with gzip.open(gz_path, 'wb') as handle:
            handle.write(b'SQLite format 3\x00' + b'\x00' * 512)
        return powerlog._materialize_gz(gz_path)  # pylint: disable=protected-access

    def test_decompressed_copies_are_removed_when_the_run_ends(self):
        materialized = self._materialize_one()
        self.assertIsNotNone(materialized, 'the archive did not decompress')
        temp_dir = powerlog._GZ_TEMP['dir']  # pylint: disable=protected-access
        self.assertTrue(os.path.exists(materialized))

        # atexit calls exactly this.
        powerlog._remove_gz_temp()  # pylint: disable=protected-access

        self.assertFalse(os.path.exists(temp_dir),
                         'the decompressed PowerLog databases survived the run')
        self.assertEqual(powerlog._GZ_CACHE, {})  # pylint: disable=protected-access
        self.assertEqual(powerlog._GZ_TEMP, {})  # pylint: disable=protected-access

    def test_cleanup_is_registered_with_atexit(self):
        # The whole fix is worthless if nothing calls it. atexit stores the callback in a
        # private registry, so assert against the module's own attribute instead.
        self.assertTrue(callable(powerlog._remove_gz_temp))  # pylint: disable=protected-access
        source = pathlib.Path(powerlog.__file__).read_text(encoding='utf-8')
        self.assertIn('atexit.register(_remove_gz_temp)', source)

    def test_cleanup_on_an_untouched_module_does_nothing(self):
        powerlog._remove_gz_temp()  # pylint: disable=protected-access
        powerlog._remove_gz_temp()  # pylint: disable=protected-access

    def test_a_second_archive_reuses_the_same_directory(self):
        first = self._materialize_one()
        directory = powerlog._GZ_TEMP['dir']  # pylint: disable=protected-access
        second = self._materialize_one()
        self.assertEqual(powerlog._GZ_TEMP['dir'], directory,  # pylint: disable=protected-access
                         'a second archive made a second temp directory')
        self.assertNotEqual(first, second, 'the two archives collided on one filename')


class StaleGzTempSweepTests(unittest.TestCase):
    """What a killed run leaves behind, and what must be left alone."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        patcher = mock.patch.object(powerlog.tempfile, 'gettempdir',
                                    return_value=self.tempdir.name)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _make_dir(self, name, age_seconds):
        path = os.path.join(self.tempdir.name, name)
        os.makedirs(path)
        with open(os.path.join(path, '0000_powerlog.PLSQL'), 'wb') as handle:
            handle.write(b'not really a database')
        stamp = time.time() - age_seconds
        os.utime(path, (stamp, stamp))
        return path

    def test_abandoned_directory_is_removed(self):
        stale = self._make_dir('ileapp_powerlog_gz_abcd1234',
                               powerlog._STALE_TEMP_AGE_SECONDS + 60)  # pylint: disable=protected-access
        powerlog._remove_stale_gz_temps()  # pylint: disable=protected-access
        self.assertFalse(os.path.exists(stale))

    def test_a_directory_still_in_use_is_left_alone(self):
        fresh = self._make_dir('ileapp_powerlog_gz_efgh5678', 60)
        powerlog._remove_stale_gz_temps()  # pylint: disable=protected-access
        self.assertTrue(os.path.exists(fresh))

    def test_other_peoples_temp_entries_are_left_alone(self):
        others = [
            self._make_dir('ileapp_fsevents_cache', 30 * 24 * 60 * 60),
            self._make_dir('some_other_tool', 30 * 24 * 60 * 60),
        ]
        stray_file = os.path.join(self.tempdir.name, 'ileapp_powerlog_gz_notadir')
        with open(stray_file, 'wb') as handle:
            handle.write(b'a file, not a directory')
        stamp = time.time() - 30 * 24 * 60 * 60
        os.utime(stray_file, (stamp, stamp))

        powerlog._remove_stale_gz_temps()  # pylint: disable=protected-access

        for path in others:
            self.assertTrue(os.path.exists(path), f'swept an entry it does not own: {path}')
        self.assertTrue(os.path.exists(stray_file), 'swept a file, and it only owns directories')


if __name__ == '__main__':
    unittest.main()
