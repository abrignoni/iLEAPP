r"""get_relative_path names a staged file as the evidence names it.

The seeker stages a file whose evidence name holds a character Windows cannot
write (':', '|', '?', a control character) under that name with the character
replaced, on every platform, and records the evidence name in its FileInfo. A
report used to give the staged name, which is not in the extraction. These tests
pin which paths get the evidence name back and which keep the staged spelling.
The Windows spellings are plain strings, so they run on every platform.
"""
import pathlib
import sys
import unittest
from types import SimpleNamespace

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.search_files import FileInfo  # pylint: disable=wrong-import-position

DATA = '/case/report/data'
WIN_DATA = '\\\\?\\C:\\case\\report\\data'


class EvidenceNameTests(unittest.TestCase):

    def setUp(self):
        self.saved = (Context._data_folder, Context._output_folder_base, Context._seeker)
        Context._data_folder = DATA
        Context._output_folder_base = '/case/report'
        self.infos = {}
        Context._seeker = SimpleNamespace(file_infos=self.infos)

    def tearDown(self):
        Context._data_folder, Context._output_folder_base, Context._seeker = self.saved

    def stage(self, staged, evidence, folder=DATA, sep='/'):
        path = folder + sep + staged.replace('/', sep)
        self.infos[path] = FileInfo(evidence, 0, 0)
        return path

    def test_a_renamed_file_is_reported_by_its_evidence_name(self):
        path = self.stage('db/Battery/BDC/BDC_2000-01-01_00_00_00.csv',
                          'db/Battery/BDC/BDC_2000-01-01_00:00:00.csv')
        self.assertEqual(Context.get_relative_path(path), 'db/Battery/BDC/BDC_2000-01-01_00:00:00.csv')

    def test_a_renamed_folder_is_reported_by_its_evidence_name(self):
        path = self.stage('a/x_y/f.db', 'a/x|y/f.db')
        self.assertEqual(Context.get_relative_path(path), 'a/x|y/f.db')

    def test_a_control_character_comes_back(self):
        path = self.stage('a/icon_.png', 'a/icon\x01.png')
        self.assertEqual(Context.get_relative_path(path), 'a/icon\x01.png')

    def test_a_name_holding_a_line_break_keeps_the_staged_name(self):
        path = self.stage('a/one_two.txt', 'a/one\ntwo.txt')
        self.assertEqual(Context.get_relative_path(path), 'a/one_two.txt')
        path = self.stage('a/three_four.txt', 'a/three\rfour.txt')
        self.assertEqual(Context.get_relative_path(path), 'a/three_four.txt')

    def test_an_unchanged_name_is_reported_as_before(self):
        path = self.stage('private/var/mobile/a.db', 'private/var/mobile/a.db')
        self.assertEqual(Context.get_relative_path(path), 'private/var/mobile/a.db')

    def test_an_evidence_name_with_a_leading_slash_keeps_the_report_spelling(self):
        path = self.stage('private/var/mobile/a.db', '/private/var/mobile/a.db')
        self.assertEqual(Context.get_relative_path(path), 'private/var/mobile/a.db')
        path = self.stage('private/var/b_c.db', '/private/var/b:c.db')
        self.assertEqual(Context.get_relative_path(path), 'private/var/b:c.db')

    def test_a_folder_entry_keeps_the_report_spelling(self):
        path = self.stage('private/var/cache', 'private/var/cache/')
        self.assertEqual(Context.get_relative_path(path), 'private/var/cache')

    def test_a_case_variant_copy_keeps_its_staged_name(self):
        path = self.stage('a/Photo~case-0123abcd.jpg', 'a/photo.jpg')
        self.assertEqual(Context.get_relative_path(path), 'a/Photo~case-0123abcd.jpg')

    def test_a_name_the_seeker_did_not_produce_is_not_replaced(self):
        path = self.stage('a/other.db', 'a/b:c.db')
        self.assertEqual(Context.get_relative_path(path), 'a/other.db')

    def test_an_evidence_name_holding_a_backslash_keeps_the_staged_name(self):
        path = self.stage('a/b/c_d', 'a/b\\c:d')
        self.assertEqual(Context.get_relative_path(path), 'a/b/c_d')

    def test_a_path_built_from_a_staged_one_keeps_the_staged_spelling(self):
        path = self.stage('a/x_y/f.db', 'a/x|y/f.db')
        folder = path.rsplit('/', 1)[0]
        self.assertEqual(Context.get_relative_path(folder), 'a/x_y')
        self.assertEqual(Context.get_relative_path(path + '-wal'), 'a/x_y/f.db-wal')
        self.assertEqual(Context.get_relative_path(path + ', ' + path), 'a/x_y/f.db, a/x_y/f.db')

    def test_without_a_seeker_the_staged_name_is_reported(self):
        path = self.stage('a/b_c.db', 'a/b:c.db')
        Context._seeker = None
        self.assertEqual(Context.get_relative_path(path), 'a/b_c.db')

    def test_a_windows_path_keeps_its_separators(self):
        Context._data_folder = WIN_DATA
        Context._output_folder_base = '\\\\?\\C:\\case\\report'
        path = self.stage('a/b_c.db', 'a/b:c.db', folder=WIN_DATA, sep='\\')
        self.assertEqual(Context.get_relative_path(path), 'a\\b:c.db')

    def test_a_windows_path_respelled_by_the_artifact_is_still_found(self):
        Context._data_folder = WIN_DATA
        Context._output_folder_base = '\\\\?\\C:\\case\\report'
        path = self.stage('a/b_c.db', 'a/b:c.db', folder=WIN_DATA, sep='\\')
        bare = path.removeprefix('\\\\?\\')
        self.assertEqual(Context.get_relative_path(bare), 'a\\b:c.db')
        self.assertEqual(Context.get_relative_path(bare.replace('\\', '/')), 'a/b:c.db')


if __name__ == '__main__':
    unittest.main()
