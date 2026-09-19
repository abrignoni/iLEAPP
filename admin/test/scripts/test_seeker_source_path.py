"""Pin what the directory and single-file seekers record in file_infos.

The zip, tar, raw image and iTunes seekers record where a file sits in the
evidence. The directory seeker used to record the absolute path on the
examiner's machine and the single-file seeker its absolute input path, so the
LAVA file list, every media source path and any artifact that reads file_infos
carried the examiner's folder layout whenever the input was a directory or a
single file (iLEAPP issue #2057).

The directory seeker also built each staged path by slicing the input path off
the front of the match and dropping one more character. An input ending in a
separator lost the first letter of every staged path ('rivate/var/...') and an
input of '.' removed every dot from every staged path ('Cachedb').

These tests build a small evidence tree and run the real seekers against it,
with the input given as an absolute path, that path with a trailing separator,
a relative path and '.'. On Windows the absolute form is also tried with the
extended-length prefix the entry points add for a directory input.
"""
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.search_files import FileSeekerDir, FileSeekerFile  # pylint: disable=wrong-import-position

REL = 'private/var/mobile/Library/Preferences/com.apple.MobileSMS.plist'
CONTENT = b'stand-in plist bytes'
PATTERN = '*/mobile/Library/Preferences/com.apple.MobileSMS.plist'


class TestDirectoryAndSingleFileSourcePaths(unittest.TestCase):
    """The recorded source path and the staged path, per input form."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='leapp_seeker_src_')
        self.root = os.path.join(self.tmp, 'extraction')
        self.evidence_file = os.path.join(self.root, *REL.split('/'))
        os.makedirs(os.path.dirname(self.evidence_file))
        with open(self.evidence_file, 'wb') as fout:
            fout.write(CONTENT)
        self.cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _data_folder(self, label):
        folder = os.path.join(self.tmp, 'data_' + label)
        os.makedirs(folder)
        return folder

    def _check_directory_input(self, label, directory):
        data_folder = self._data_folder(label)
        seeker = FileSeekerDir(directory, data_folder)
        found = seeker.search(PATTERN)
        self.assertEqual(len(found), 1, (label, found))
        staged = found[0]
        self.assertEqual(seeker.file_infos[staged].source_path, REL, label)
        self.assertEqual(os.path.relpath(staged, data_folder).replace(os.sep, '/'), REL, label)
        with open(staged, 'rb') as fin:
            self.assertEqual(fin.read(), CONTENT, label)

    def test_absolute_directory_input(self):
        self._check_directory_input('absolute', self.root)

    def test_directory_input_with_a_trailing_separator(self):
        self._check_directory_input('trailing', self.root + os.sep)

    def test_relative_directory_input(self):
        os.chdir(self.tmp)
        self._check_directory_input('relative', 'extraction')

    def test_dot_as_the_directory_input(self):
        os.chdir(self.root)
        self._check_directory_input('dot', '.')

    @unittest.skipUnless(os.name == 'nt', 'the extended-length prefix is a Windows path form')
    def test_extended_length_prefix_on_windows(self):
        prefixed = '\\\\?\\' + self.root.replace('/', '\\')
        self._check_directory_input('prefixed', prefixed)
        self._check_directory_input('prefixed_trailing', prefixed + '\\')

    def test_single_file_input_records_the_file_name(self):
        data_folder = self._data_folder('file')
        seeker = FileSeekerFile(self.evidence_file, data_folder)
        found = seeker.search(PATTERN)
        self.assertEqual(len(found), 1, found)
        self.assertEqual(seeker.file_infos[found[0]].source_path, 'com.apple.MobileSMS.plist')
        self.assertEqual(os.path.basename(found[0]), 'com.apple.MobileSMS.plist')
        with open(found[0], 'rb') as fin:
            self.assertEqual(fin.read(), CONTENT)


if __name__ == '__main__':
    unittest.main()
