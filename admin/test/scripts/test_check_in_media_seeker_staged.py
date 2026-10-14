"""check_in_media checks in a file the seeker staged, even when files_found does not list it.

An artifact can stage a file with its own seeker search while it runs, the way iLEAPP's
Google Chat finds an attachment under '<container>/tmp/<name>' from a name its database
stores. That file is not in the artifact's files_found, and check_in_media used to resolve
only through files_found by file name, so:

- with no other file of that name found, it logged 'No matching file found' and returned
  None, and the row's media cell was left blank;
- with another found file of that name, the media item was identified by that other
  file's evidence path, so the two collapsed onto one media item.

These tests stage files with a real FileSeekerDir over a synthetic folder, set files_found
to what the artifact's own paths would find, and check the searched file in. The file is the
same in all five LEAPP cores.
"""
import hashlib
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import types
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs, lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.search_files import FileSeekerDir  # pylint: disable=wrong-import-position

CONTAINER = 'private/var/mobile/Containers/Data/Application/0A1B2C3D-4E5F-4A6B-8C7D-8E9F0A1B2C3D'
DATABASE = f'{CONTAINER}/Documents/user_accounts/111111111111/dynamite.db'
ATTACHMENT = f'{CONTAINER}/tmp/attachment.jpg'
SAME_NAME = f'{CONTAINER}/Documents/user_accounts/111111111111/tmp/attachment.jpg'
JPEG = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00' + b'\x00' * 64


class CheckInMediaSeekerStagedTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        root = pathlib.Path(self.tmpdir)
        self.input = root / 'input'
        report = root / 'report'
        data_folder = report / 'data'
        media_folder = report / 'media'
        html_media_folder = report / '_HTML' / 'media'
        for folder in (self.input, data_folder, media_folder, html_media_folder):
            folder.mkdir(parents=True, exist_ok=True)
        for rel_path, content in ((DATABASE, b'SQLite format 3\x00'),
                                  (ATTACHMENT, JPEG + b'searched'),
                                  (SAME_NAME, JPEG + b'same name')):
            path = self.input / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        lavafuncs.initialize_lava(str(report), str(report), 'fs')
        Context.clear()
        Context.set_output_params(types.SimpleNamespace(
            media_folder=str(media_folder), html_media_folder=str(html_media_folder),
            data_folder=str(data_folder), output_folder_base=str(report)))
        Context.set_module_name('test_module')
        Context.set_artifact_name('Test Artifact')
        self.seeker = FileSeekerDir(str(self.input), str(data_folder))
        Context.set_seeker(self.seeker)

    def tearDown(self):
        if lavafuncs.lava_db is not None:
            try:
                lavafuncs.lava_db.close()
            except sqlite3.ProgrammingError:
                pass
            lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        Context.clear()
        Context.set_output_params(None)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _find(self, *patterns):
        """Stage files the way the artifact's paths do and make them its files_found."""
        found = [path for pattern in patterns for path in self.seeker.search(pattern)]
        Context.set_files_found(found)
        return found

    @staticmethod
    def _media_item(rel_path):
        return lavafuncs.lava_db.execute(
            'SELECT source_path, extraction_path FROM _lava_media_items WHERE id = ?',
            (hashlib.sha1(rel_path.encode()).hexdigest(),)).fetchone()

    def _checked_in_bytes(self, rel_path):
        _, extraction_path = self._media_item(rel_path)
        report = pathlib.Path(Context.get_output_params().media_folder).parent
        return (report / extraction_path).read_bytes()

    def test_a_searched_file_files_found_does_not_list_is_checked_in(self):
        self._find('*/Documents/user_accounts/*/dynamite.db*')
        staged = self.seeker.search(f'*/{CONTAINER.rsplit("/", 1)[1]}/tmp/attachment.jpg',
                                    return_on_first_hit=True)
        self.assertTrue(staged, 'the search staged nothing, so the test proves nothing')
        self.assertNotIn(staged, Context.get_files_found())

        self.assertIsNotNone(ilapfuncs.check_in_media(staged, name='attachment.jpg'))

        self.assertEqual(self._media_item(ATTACHMENT)[0], ATTACHMENT)
        self.assertEqual(self._checked_in_bytes(ATTACHMENT), JPEG + b'searched')

    def test_a_searched_file_is_not_identified_by_a_found_file_of_the_same_name(self):
        found = self._find('*/Documents/user_accounts/*/dynamite.db*',
                           '*/Documents/user_accounts/*/tmp/*')
        self.assertEqual(sum(path.endswith('attachment.jpg') for path in found), 1)
        staged = self.seeker.search(f'*/{CONTAINER.rsplit("/", 1)[1]}/tmp/attachment.jpg',
                                    return_on_first_hit=True)
        same_name = next(path for path in found if path.endswith('attachment.jpg'))

        searched_ref = ilapfuncs.check_in_media(staged, name='attachment.jpg')
        same_name_ref = ilapfuncs.check_in_media(same_name, name='attachment.jpg')

        self.assertIsNotNone(searched_ref)
        self.assertIsNotNone(same_name_ref)
        self.assertEqual(self._media_item(ATTACHMENT)[0], ATTACHMENT)
        self.assertEqual(self._media_item(SAME_NAME)[0], SAME_NAME)
        self.assertEqual(self._checked_in_bytes(ATTACHMENT), JPEG + b'searched')
        self.assertEqual(self._checked_in_bytes(SAME_NAME), JPEG + b'same name')

    def test_a_found_file_named_by_a_partial_path_is_checked_in_as_before(self):
        self._find('*/Documents/user_accounts/*/tmp/*')

        self.assertIsNotNone(ilapfuncs.check_in_media('111111111111/tmp/attachment.jpg'))

        self.assertEqual(self._media_item(SAME_NAME)[0], SAME_NAME)

    def test_a_name_nothing_staged_still_returns_none(self):
        self._find('*/Documents/user_accounts/*/dynamite.db*')

        self.assertIsNone(ilapfuncs.check_in_media('not_staged.jpg'))


if __name__ == '__main__':
    unittest.main()
