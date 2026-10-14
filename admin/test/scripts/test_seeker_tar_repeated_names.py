"""Pin how the tar seeker stages a member name the archive stores more than once.

A tar can list one name more than once: appending to an archive adds a second
entry, and tar itself extracts the last one. The seeker used to iterate
getmembers(), which yields such a name once per entry, stage the first entry's
bytes and return that one path once per entry. So an artifact read one file
twice and its rows doubled, and the version staged was the one tar would have
discarded.

Now a search matches each distinct name once. Entries holding the same bytes
are staged once, from the last entry. Where the entries differ, the one
recording the latest modification time is staged under the name (the earlier
entry on a tie) and every other version beside it as <name>~tar-entry-<N><ext>,
N being the entry's position in the archive. Those other versions are on disk
and logged, and are not returned to artifacts.

The archives are built here with tarfile, plain and gzip compressed. Every
expected value is written out as a literal.
"""
import io
import os
import pathlib
import shutil
import sys
import tarfile
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.search_files import FileSeekerTar  # pylint: disable=wrong-import-position


class TestTarRepeatedMemberNames(unittest.TestCase):
    """One archive, several repeated names, one seeker; then the same archive gzipped."""

    # (name, content or None for a directory, mtime) in archive order; entry N is index N.
    ENTRIES = (
        ('a/same.db', b'IDENTICAL', 1000),
        ('b/log.db-wal', b'OLDER', 2000),
        ('c/prefs_db', b'SQLite format 3\x00populated', 3000),
        ('d/tie.xml', b'FIRST', 5000),
        ('e/dir', None, 1000),
        ('g/once.txt', b'ONCE', 6000),
        ('a/same.db', b'IDENTICAL', 1500),
        ('b/log.db-wal', b'NEWER-LONGER', 2600),
        ('c/prefs_db', b'', 2700),
        ('d/tie.xml', b'SECOND', 5000),
        ('e/dir', None, 1000),
    )

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='leapp_seeker_tar_repeats_')
        self.tar_path = os.path.join(self.tmp, 'repeats.tar')
        self.tgz_path = os.path.join(self.tmp, 'repeats.tar.gz')
        for path, mode in ((self.tar_path, 'w'), (self.tgz_path, 'w:gz')):
            with tarfile.open(path, mode) as archive:
                for name, content, mtime in self.ENTRIES:
                    info = tarfile.TarInfo(name)
                    info.mtime = mtime
                    if content is None:
                        info.type = tarfile.DIRTYPE
                        archive.addfile(info)
                    else:
                        info.size = len(content)
                        archive.addfile(info, io.BytesIO(content))
        self.data_folder = os.path.join(self.tmp, 'data')
        self.seeker = FileSeekerTar(self.tar_path, self.data_folder)

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
        self.assertFalse(os.path.exists(self._staged('a/same~tar-entry-6.db')))

    def test_an_identical_repeat_carries_the_last_entry_time(self):
        found = self.seeker.search('*/same.db')
        self.assertEqual(int(os.stat(found[0]).st_mtime), 1500)

    def test_a_differing_repeat_stages_the_latest_entry_under_the_name(self):
        found = self.seeker.search('*/log.db-wal')
        self.assertEqual(found, [self._staged('b/log.db-wal')])
        self.assertEqual(self._read(found[0]), b'NEWER-LONGER')

    def test_the_other_version_is_staged_beside_the_name_and_not_returned(self):
        found = self.seeker.search('*/log.db-wal')
        other = self._staged('b/log~tar-entry-1.db-wal')
        self.assertEqual(self._read(other), b'OLDER')
        self.assertNotIn(other, found)

    def test_a_populated_earlier_entry_beats_an_empty_later_one(self):
        found = self.seeker.search('*/prefs_db')
        self.assertEqual(found, [self._staged('c/prefs_db')])
        self.assertEqual(self._read(found[0]), b'SQLite format 3\x00populated')
        self.assertEqual(self._read(self._staged('c/prefs_db~tar-entry-8')), b'')

    def test_equal_recorded_times_keep_the_earlier_entry(self):
        found = self.seeker.search('*/tie.xml')
        self.assertEqual(found, [self._staged('d/tie.xml')])
        self.assertEqual(self._read(found[0]), b'FIRST')
        self.assertEqual(self._read(self._staged('d/tie~tar-entry-9.xml')), b'SECOND')

    def test_a_repeated_directory_entry_is_returned_once(self):
        found = self.seeker.search('*/e/dir')
        self.assertEqual(len(found), 1)

    def test_a_name_stored_once_is_unaffected(self):
        found = self.seeker.search('*/once.txt')
        self.assertEqual(found, [self._staged('g/once.txt')])
        self.assertEqual(self._read(found[0]), b'ONCE')

    def test_a_broad_pattern_lists_each_name_once_and_no_other_version(self):
        found = self.seeker.search('*')
        names = sorted(os.path.relpath(path, self.data_folder).replace(os.sep, '/') for path in found)
        self.assertEqual(names, ['a/same.db', 'b/log.db-wal', 'c/prefs_db', 'd/tie.xml',
                                 'e/dir', 'g/once.txt'])

    def test_the_recorded_source_path_is_the_member_name_as_stored(self):
        for pattern, member in (('*/same.db', 'a/same.db'), ('*/log.db-wal', 'b/log.db-wal'),
                                ('*/prefs_db', 'c/prefs_db')):
            found = self.seeker.search(pattern)
            self.assertEqual(self.seeker.file_infos[found[0]].source_path, member)

    def test_a_repeated_search_returns_the_same_paths(self):
        first = self.seeker.search('*/log.db-wal')
        self.assertEqual(self.seeker.search('*/log.db-wal'), first)
        self.assertEqual(self.seeker.search('*/log.db-wal', return_on_first_hit=True), first[0])

    def test_a_gzip_compressed_archive_behaves_the_same(self):
        data_folder = os.path.join(self.tmp, 'data_gz')
        seeker = FileSeekerTar(self.tgz_path, data_folder)
        try:
            found = seeker.search('*/log.db-wal')
            self.assertEqual(found, [os.path.join(data_folder, 'b', 'log.db-wal')])
            self.assertEqual(self._read(found[0]), b'NEWER-LONGER')
            self.assertEqual(self._read(os.path.join(data_folder, 'b', 'log~tar-entry-1.db-wal')), b'OLDER')
            self.assertEqual(seeker.search('*/same.db'), [os.path.join(data_folder, 'a', 'same.db')])
        finally:
            seeker.cleanup()


if __name__ == '__main__':
    unittest.main()
