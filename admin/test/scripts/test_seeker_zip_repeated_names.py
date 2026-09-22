"""Pin how the zip seeker stages a member name the archive stores more than once.

A zip's central directory can list one name more than once. The seeker used to
iterate namelist(), which lists such a name once per entry, and extract by
name, which zipfile resolves to the last entry. So one staged file was returned
once per entry, an artifact read it that many times and its rows doubled, and
no earlier entry was ever staged: for a name whose last entry was empty the
populated entry before it was unreachable.

Now a search matches each distinct name once. Entries repeating the same
content (same CRC-32 and size) are staged once. Where the entries differ, the
one recording the latest modification time is staged under the name (the
earlier entry on a tie) and every other version beside it as
<name>~zip-entry-<N><ext>, N being the entry's position in the archive. Those
other versions are on disk and logged, and are not returned to artifacts.

The archive is built here with zipfile, which warns on a duplicate name and
writes it anyway. Every expected value is written out as a literal.
"""
import os
import pathlib
import shutil
import struct
import sys
import tempfile
import unittest
import warnings
import zipfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.search_files import FileSeekerZip  # pylint: disable=wrong-import-position


def _unix_mtime(seconds):
    """An extended-timestamp extra field (0x5455) carrying only a modification time."""
    return struct.pack('<HHBI', 0x5455, 5, 1, seconds)


class TestZipRepeatedMemberNames(unittest.TestCase):
    """One archive, several repeated names, one seeker."""

    # (name, content, DOS date_time, extra) in archive order; entry N is index N.
    ENTRIES = (
        ('a/same.db', b'IDENTICAL', (2024, 1, 1, 9, 0, 0), _unix_mtime(1000)),
        ('b/log.db-wal', b'OLDER', (2024, 1, 1, 10, 0, 0), _unix_mtime(2000)),
        ('c/prefs_db', b'SQLite format 3\x00populated', (2024, 1, 1, 11, 48, 0), _unix_mtime(3000)),
        ('d/tie.xml', b'FIRST', (2024, 1, 1, 12, 0, 0), _unix_mtime(5000)),
        ('e/dir/', b'', (2024, 1, 1, 13, 0, 0), b''),
        ('f/mixed.txt', b'ENTRY1', (2020, 1, 1, 0, 0, 0), _unix_mtime(4000000000)),
        ('g/once.txt', b'ONCE', (2024, 1, 1, 14, 0, 0), _unix_mtime(6000)),
        ('a/same.db', b'IDENTICAL', (2024, 1, 1, 9, 0, 0), _unix_mtime(1000)),
        ('b/log.db-wal', b'NEWER-LONGER', (2024, 1, 1, 10, 10, 0), _unix_mtime(2600)),
        ('c/prefs_db', b'', (2024, 1, 1, 11, 44, 0), _unix_mtime(2700)),
        ('d/tie.xml', b'SECOND', (2024, 1, 1, 12, 0, 0), _unix_mtime(5000)),
        ('e/dir/', b'', (2024, 1, 1, 13, 0, 0), b''),
        ('f/mixed.txt', b'ENTRY2', (2024, 6, 1, 0, 0, 0), b''),
    )

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='leapp_seeker_zip_repeats_')
        self.zip_path = os.path.join(self.tmp, 'repeats.zip')
        self.data_folder = os.path.join(self.tmp, 'data')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            with zipfile.ZipFile(self.zip_path, 'w') as archive:
                for name, content, date_time, extra in self.ENTRIES:
                    info = zipfile.ZipInfo(name, date_time=date_time)
                    info.extra = extra
                    archive.writestr(info, content)
        self.seeker = FileSeekerZip(self.zip_path, self.data_folder)

    def tearDown(self):
        self.seeker.cleanup()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _staged(self, relative):
        return os.path.join(self.data_folder, *relative.split('/'))

    def _read(self, path):
        with open(path, 'rb') as fin:
            return fin.read()

    def test_an_identical_repeat_is_returned_once_and_staged_once(self):
        found = self.seeker.search('*/same.db')
        self.assertEqual(found, [self._staged('a/same.db')])
        self.assertEqual(self._read(found[0]), b'IDENTICAL')
        self.assertFalse(os.path.exists(self._staged('a/same~zip-entry-7.db')))

    def test_a_differing_repeat_stages_the_latest_entry_under_the_name(self):
        found = self.seeker.search('*/log.db-wal')
        self.assertEqual(found, [self._staged('b/log.db-wal')])
        self.assertEqual(self._read(found[0]), b'NEWER-LONGER')

    def test_the_other_version_is_staged_beside_the_name_and_not_returned(self):
        found = self.seeker.search('*/log.db-wal')
        other = self._staged('b/log~zip-entry-1.db-wal')
        self.assertEqual(self._read(other), b'OLDER')
        self.assertNotIn(other, found)

    def test_a_populated_earlier_entry_beats_an_empty_later_one(self):
        found = self.seeker.search('*/prefs_db')
        self.assertEqual(found, [self._staged('c/prefs_db')])
        self.assertEqual(self._read(found[0]), b'SQLite format 3\x00populated')
        self.assertEqual(self._read(self._staged('c/prefs_db~zip-entry-9')), b'')

    def test_equal_recorded_times_keep_the_earlier_entry(self):
        found = self.seeker.search('*/tie.xml')
        self.assertEqual(found, [self._staged('d/tie.xml')])
        self.assertEqual(self._read(found[0]), b'FIRST')
        self.assertEqual(self._read(self._staged('d/tie~zip-entry-10.xml')), b'SECOND')

    def test_entries_without_a_shared_clock_compare_on_dos_time(self):
        found = self.seeker.search('*/mixed.txt')
        self.assertEqual(found, [self._staged('f/mixed.txt')])
        self.assertEqual(self._read(found[0]), b'ENTRY2')

    def test_a_repeated_directory_entry_is_returned_once(self):
        found = self.seeker.search('*/e/dir/')
        self.assertEqual(len(found), 1)

    def test_a_name_stored_once_is_unaffected(self):
        found = self.seeker.search('*/once.txt')
        self.assertEqual(found, [self._staged('g/once.txt')])
        self.assertEqual(self._read(found[0]), b'ONCE')

    def test_a_broad_pattern_lists_each_name_once_and_no_other_version(self):
        found = self.seeker.search('*')
        names = sorted(os.path.relpath(path, self.data_folder).replace(os.sep, '/') for path in found)
        self.assertEqual(names, ['a/same.db', 'b/log.db-wal', 'c/prefs_db', 'd/tie.xml',
                                 'e/dir', 'f/mixed.txt', 'g/once.txt'])

    def test_the_recorded_source_path_is_the_member_name_as_stored(self):
        for pattern, member in (('*/same.db', 'a/same.db'), ('*/log.db-wal', 'b/log.db-wal'),
                                ('*/prefs_db', 'c/prefs_db')):
            found = self.seeker.search(pattern)
            self.assertEqual(self.seeker.file_infos[found[0]].source_path, member)

    def test_a_repeated_search_returns_the_same_paths(self):
        first = self.seeker.search('*/log.db-wal')
        self.assertEqual(self.seeker.search('*/log.db-wal'), first)
        self.assertEqual(self.seeker.search('*/log.db-wal', return_on_first_hit=True), first[0])


class TestZipWithoutRepeatedMemberNames(unittest.TestCase):
    """The ordinary archive: every name distinct, so the seeker need not walk the members.

    Every real extraction is this case. The seeker used to group all 630,560 members of
    one to find out, which measured 138 MB. ZipFile has already keyed its own dict on the
    member name by then, so a short dict means a repeat and an equal one means none.
    """

    ENTRIES = (
        ('a/first.db', b'ONE', (2024, 1, 1, 9, 0, 0)),
        ('b/second.db-wal', b'TWO', (2024, 1, 1, 10, 0, 0)),
        ('c/dir/', b'', (2024, 1, 1, 11, 0, 0)),
        ('d/third.xml', b'THREE', (2024, 1, 1, 12, 0, 0)),
    )

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='leapp_seeker_zip_distinct_')
        self.zip_path = os.path.join(self.tmp, 'distinct.zip')
        self.data_folder = os.path.join(self.tmp, 'data')
        with zipfile.ZipFile(self.zip_path, 'w') as archive:
            for name, content, date_time in self.ENTRIES:
                archive.writestr(zipfile.ZipInfo(name, date_time=date_time), content)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_every_name_is_listed_once_and_nothing_is_flagged_as_repeated(self):
        seeker = FileSeekerZip(self.zip_path, self.data_folder)
        self.addCleanup(seeker.cleanup)
        self.assertEqual(seeker._search_names,  # pylint: disable=protected-access
                         ['a/first.db', 'b/second.db-wal', 'c/dir/', 'd/third.xml'])
        self.assertEqual(seeker._chosen, {})  # pylint: disable=protected-access
        self.assertEqual(seeker._other_versions, {})  # pylint: disable=protected-access

    def test_searching_still_finds_and_stages_each_member(self):
        seeker = FileSeekerZip(self.zip_path, self.data_folder)
        self.addCleanup(seeker.cleanup)
        found = seeker.search('*/second.db-wal')
        self.assertEqual(len(found), 1)
        with open(found[0], 'rb') as fin:
            self.assertEqual(fin.read(), b'TWO')
        self.assertEqual(seeker.file_infos[found[0]].source_path, 'b/second.db-wal')

    def test_the_members_are_never_walked_when_no_name_repeats(self):
        """The one infolist() call in the class is the walk. It must not run here.

        Without this the cheap path could be dropped and every test above would still
        pass, because the walk returns the same answer. It just costs 138 MB on a real
        archive to do so.
        """
        original = zipfile.ZipFile.infolist

        def refuse(self):
            raise AssertionError('the member walk ran on an archive with no repeated names')

        zipfile.ZipFile.infolist = refuse
        self.addCleanup(setattr, zipfile.ZipFile, 'infolist', original)
        seeker = FileSeekerZip(self.zip_path, self.data_folder)
        self.addCleanup(seeker.cleanup)
        self.assertEqual(len(seeker._search_names), 4)  # pylint: disable=protected-access

    def test_the_walk_still_runs_when_a_name_does_repeat(self):
        """The control for the test above: the same probe must fire on a repeated name."""
        repeated = os.path.join(self.tmp, 'repeats.zip')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            with zipfile.ZipFile(repeated, 'w') as archive:
                archive.writestr('a/first.db', b'ONE')
                archive.writestr('a/first.db', b'ONE AGAIN')
        original = zipfile.ZipFile.infolist

        def refuse(self):
            raise AssertionError('walk ran')

        zipfile.ZipFile.infolist = refuse
        self.addCleanup(setattr, zipfile.ZipFile, 'infolist', original)
        with self.assertRaises(AssertionError):
            FileSeekerZip(repeated, os.path.join(self.tmp, 'data2'))


if __name__ == '__main__':
    unittest.main()
