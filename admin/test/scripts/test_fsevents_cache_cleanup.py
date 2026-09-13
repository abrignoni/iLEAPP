"""Cover the temporary cache the FSEvents artifacts share, and how it gets cleaned up.

The module parses every FSEvents record in the extraction once into a temporary SQLite
database so its twenty-odd artifacts can query it instead of re-parsing. On a full file
system extraction that file reaches gigabytes, and it lives in the system temp directory
under a random mkstemp name, so a copy left behind is invisible: no later run can recognise
it, and nothing reports it. Three orphans totalling 2.7 GB were found on one machine, the
largest 1.72 GB.

Two separate failures put them there, and they need different fixes:

  * an exit from the build that is not a successful build. The atexit handler deletes
    _CACHE["path"], and that slot used to stay empty until after the parse finished, so an
    exception the build's own handler does not catch, or Ctrl-C, unwound to an atexit that
    knew nothing about the file. Covered by the registration tests below.
  * a killed interpreter. atexit does not run at all on SIGKILL or SIGTERM, so nothing
    in-process can help; the next run has to reap what the last one abandoned. Covered by
    the sweep tests below.

A clean run has always cleaned up after itself, which is why this went unnoticed.
"""
import os
import pathlib
import sqlite3
import sys
import tempfile
import time
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import fileSystemEvents  # pylint: disable=wrong-import-position


class _Context:
    """The slice of Context that _build_cache touches."""

    def __init__(self, files_found, relative_path_error=None):
        self._files_found = files_found
        self._relative_path_error = relative_path_error

    def get_files_found(self):
        return self._files_found

    def get_relative_path(self, file_found):
        if self._relative_path_error:
            raise self._relative_path_error
        return file_found


class CacheRegistrationTests(unittest.TestCase):
    """The cache path must be known to the cleanup handler for the whole build.

    Registering it only after a successful parse leaves the entire parse - the part that
    takes minutes and writes the gigabytes - as a window in which the file exists and
    nothing but a local variable knows its name.
    """

    def setUp(self):
        self.original = dict(fileSystemEvents._CACHE)  # pylint: disable=protected-access
        fileSystemEvents._CACHE.update({"key": None, "path": None})  # pylint: disable=protected-access

    def tearDown(self):
        fileSystemEvents._remove_cache()  # pylint: disable=protected-access
        fileSystemEvents._CACHE.update(self.original)  # pylint: disable=protected-access

    def test_uncaught_exception_leaves_the_path_registered_for_atexit(self):
        # ValueError is not in the build's own (OSError, sqlite3.Error) handler, so it
        # propagates exactly like a zlib.error on a corrupt member or a Ctrl-C would.
        context = _Context(['/nonexistent/0000000000000001'],
                           relative_path_error=ValueError('parse blew up'))
        with self.assertRaises(ValueError):
            fileSystemEvents._build_cache(context)  # pylint: disable=protected-access

        registered = fileSystemEvents._CACHE['path']  # pylint: disable=protected-access
        self.assertIsNotNone(registered, 'cache path was not registered, atexit cannot clean it')
        self.assertTrue(os.path.exists(registered))

        # atexit calls exactly this, and it has to be enough to remove the file.
        fileSystemEvents._remove_cache()  # pylint: disable=protected-access
        self.assertFalse(os.path.exists(registered), 'cache file survived the cleanup handler')

    def test_failed_build_is_never_returned_as_a_cache_hit(self):
        # Registering the path early must not make a half-written database look usable.
        context = _Context(['/nonexistent/0000000000000001'],
                           relative_path_error=ValueError('parse blew up'))
        with self.assertRaises(ValueError):
            fileSystemEvents._build_cache(context)  # pylint: disable=protected-access
        self.assertIsNone(fileSystemEvents._CACHE['key'],  # pylint: disable=protected-access
                          'a failed build left a key behind, so the next call would query it')

    def test_successful_build_registers_key_and_path(self):
        context = _Context([])
        cache_path = fileSystemEvents._build_cache(context)  # pylint: disable=protected-access
        self.addCleanup(fileSystemEvents._remove_cache)  # pylint: disable=protected-access

        self.assertTrue(os.path.exists(cache_path))
        self.assertEqual(fileSystemEvents._CACHE['path'], cache_path)  # pylint: disable=protected-access
        self.assertIsNotNone(fileSystemEvents._CACHE['key'])  # pylint: disable=protected-access
        with sqlite3.connect(cache_path) as database:
            self.assertEqual(database.execute('SELECT COUNT(*) FROM events').fetchone()[0], 0)

    def test_second_call_with_the_same_files_reuses_the_cache(self):
        context = _Context([])
        first = fileSystemEvents._build_cache(context)  # pylint: disable=protected-access
        self.addCleanup(fileSystemEvents._remove_cache)  # pylint: disable=protected-access
        second = fileSystemEvents._build_cache(context)  # pylint: disable=protected-access
        self.assertEqual(first, second, 'the shared cache was rebuilt for the second artifact')


class StaleCacheSweepTests(unittest.TestCase):
    """What a killed run leaves behind, and what must be left alone.

    The sweep runs against a directory shared with every other program on the machine, and
    possibly with a second iLEAPP running right now, so being conservative matters more
    than reclaiming every byte.
    """

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        patcher = mock.patch.object(fileSystemEvents.tempfile, 'gettempdir',
                                    return_value=self.tempdir.name)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _make(self, name, age_seconds):
        path = os.path.join(self.tempdir.name, name)
        with open(path, 'wb') as handle:
            handle.write(b'not really a database')
        stamp = time.time() - age_seconds
        os.utime(path, (stamp, stamp))
        return path

    def test_abandoned_cache_is_removed(self):
        stale = self._make('ileapp_fsevents_abcd1234.sqlite',
                           fileSystemEvents._STALE_CACHE_AGE_SECONDS + 60)  # pylint: disable=protected-access
        fileSystemEvents._remove_stale_caches()  # pylint: disable=protected-access
        self.assertFalse(os.path.exists(stale))

    def test_a_cache_still_in_use_is_left_alone(self):
        # A concurrent iLEAPP writes its cache at the start of its run. Reaping it would
        # cost that run a rebuild of everything it has parsed so far.
        fresh = self._make('ileapp_fsevents_efgh5678.sqlite', 60)
        fileSystemEvents._remove_stale_caches()  # pylint: disable=protected-access
        self.assertTrue(os.path.exists(fresh))

    def test_other_peoples_temp_files_are_left_alone(self):
        others = [
            self._make('ileapp_logarchive_cache.sqlite', 30 * 24 * 60 * 60),
            self._make('ileapp_fsevents_notours.txt', 30 * 24 * 60 * 60),
            self._make('some_other_tool.sqlite', 30 * 24 * 60 * 60),
        ]
        fileSystemEvents._remove_stale_caches()  # pylint: disable=protected-access
        for path in others:
            self.assertTrue(os.path.exists(path), f'swept a file it does not own: {path}')

    def test_a_missing_file_does_not_raise(self):
        # Two runs sweeping at once, or a temp cleaner working the same directory.
        stale = self._make('ileapp_fsevents_racing.sqlite',
                           fileSystemEvents._STALE_CACHE_AGE_SECONDS + 60)  # pylint: disable=protected-access
        real_getmtime = os.path.getmtime

        def vanishing(path):
            os.unlink(path)
            return real_getmtime(path)

        with mock.patch.object(fileSystemEvents.os.path, 'getmtime', side_effect=vanishing):
            fileSystemEvents._remove_stale_caches()  # pylint: disable=protected-access
        self.assertFalse(os.path.exists(stale))


if __name__ == '__main__':
    unittest.main()
