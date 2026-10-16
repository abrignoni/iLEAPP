"""Pin that a staged path rewritten to '/' still loses the examiner's folders.

On Windows the data folder is spelled with backslashes and the long-path prefix,
'\\\\?\\C:\\...\\data'. An artifact can rewrite a seeker path to forward slashes,
'//?/C:/.../data/...', and then pass it to `Context.get_relative_path` or return it as the
source path. The strip used to be a plain match on the backslash spelling, so the
rewritten path came back whole and the examiner's own folders reached the report's
Source File cells, the "located at" line and the LAVA manifest's `source_path`. A code read
of ALEAPP on 2026-10-16 found 59 artifact modules doing this.

The function is plain string work, so these tests set Windows-spelled folders directly
and run on every platform. They fail on the unfixed function.
"""
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.context import Context  # pylint: disable=wrong-import-position

# The folders a Windows run sets: the report folder with the long-path prefix, and the
# data folder inside it.
REPORT = '\\\\?\\C:\\Users\\examiner\\Cases\\LEAPP_Output_2026'
DATA = REPORT + '\\data'
REPORT_SLASHED = '//?/C:/Users/examiner/Cases/LEAPP_Output_2026'
DATA_SLASHED = REPORT_SLASHED + '/data'


class WindowsFoldersTestCase(unittest.TestCase):
    """Both folders set the way a Windows run sets them."""

    def setUp(self):
        Context.clear()
        Context._data_folder = DATA            # pylint: disable=protected-access
        Context._output_folder_base = REPORT   # pylint: disable=protected-access

    def tearDown(self):
        Context._data_folder = None            # pylint: disable=protected-access
        Context._output_folder_base = None     # pylint: disable=protected-access
        Context.clear()


class TestARewrittenStagedPathIsReduced(WindowsFoldersTestCase):

    def test_a_staged_path_rewritten_to_forward_slashes_loses_the_data_folder(self):
        staged = DATA_SLASHED + '/data/data/com.example/files/store.json'
        self.assertEqual(Context.get_relative_path(staged),
                         'data/data/com.example/files/store.json')

    def test_no_part_of_the_examiners_folders_survives(self):
        got = Context.get_relative_path(DATA_SLASHED + '/data/data/com.example/a.db')
        self.assertNotIn('examiner', got)
        self.assertFalse(got.startswith(('/', '\\', '//?/')), f'still absolute: {got!r}')

    def test_the_data_folder_still_wins_over_the_report_folder(self):
        got = Context.get_relative_path(DATA_SLASHED + '/data/data/com.example/a.db')
        self.assertFalse(got.startswith('data/data/data'), f'data prefix survived: {got!r}')

    def test_several_rewritten_paths_in_one_source_string_are_all_reduced(self):
        joined = ', '.join([DATA_SLASHED + '/a/one.db', DATA_SLASHED + '/b/two.db'])
        self.assertEqual(Context.get_relative_path(joined), 'a/one.db, b/two.db')

    def test_a_string_holding_both_spellings_is_reduced_in_both(self):
        joined = '\n'.join([DATA + '\\a\\one.db', DATA_SLASHED + '/b/two.db'])
        self.assertEqual(Context.get_relative_path(joined), 'a\\one.db\nb/two.db')

    def test_a_rewritten_report_file_loses_the_report_folder(self):
        self.assertEqual(Context.get_relative_path(REPORT_SLASHED + '/_lava_artifacts.db'),
                         '_lava_artifacts.db')


class TestTheNativeSpellingIsUnchanged(WindowsFoldersTestCase):

    def test_a_backslash_staged_path_reduces_as_before(self):
        self.assertEqual(Context.get_relative_path(DATA + '\\data\\data\\com.example\\a.db'),
                         'data\\data\\com.example\\a.db')

    def test_a_path_outside_both_folders_is_unchanged(self):
        other = 'C:/Users/examiner/Desktop/notes.txt'
        self.assertEqual(Context.get_relative_path(other), other)


if __name__ == '__main__':
    unittest.main()
