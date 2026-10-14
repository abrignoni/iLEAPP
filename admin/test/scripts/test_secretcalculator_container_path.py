"""Secret Calculator finds its container from the path inside the extraction.

The artifact took the container from the staged path of its metadata plist, split at the
first '/private/'. When the report sat under a folder of that name, as it does under macOS
/private/tmp and /private/var/folders, the split landed in the examiner's own folders, the
database was looked for in a container that does not exist, and the artifact reported
nothing.

These tests stage a constructed container with a real FileSeekerDir, once with the report
under a folder named private and once without, and run the artifact over it.
"""
import pathlib
import plistlib
import shutil
import sqlite3
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import secretCalculator as module  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.search_files import FileSeekerDir  # pylint: disable=wrong-import-position

CONTAINER = 'private/var/mobile/Containers/Data/Application/1A2B3C4D-5E6F-4A7B-8C9D-0E1F2A3B4C5D'
JPEG = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00' + b'\x00' * 64


class SecretCalculatorContainerPathTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.input = pathlib.Path(self.tmpdir) / 'input'
        app = self.input / CONTAINER
        (app / 'Library' / 'Data').mkdir(parents=True)
        with open(app / '.com.apple.mobile_container_manager.metadata.plist', 'wb') as handle:
            plistlib.dump({'MCMMetadataIdentifier': 'xyz.hypertornado.calculator'}, handle)
        (app / 'Library' / 'Data' / 'photo_one.jpg').write_bytes(JPEG)
        db = sqlite3.connect(app / 'Library' / 'data.sqlite')
        db.executescript("CREATE TABLE Photos(date INTEGER, path TEXT, video INTEGER);"
                         "INSERT INTO Photos VALUES(1700000000, 'photo_one.jpg', 0),"
                         "(1700000100, 'missing.jpg', 0);")
        db.commit()
        db.close()
        checkin = patch.object(module, 'check_in_media', side_effect=lambda path: path)
        checkin.start()
        self.addCleanup(checkin.stop)

    def tearDown(self):
        Context.clear()
        Context.set_output_params(None)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run(self, report_parent):
        data_folder = pathlib.Path(self.tmpdir) / report_parent / 'report' / 'data'
        data_folder.mkdir(parents=True)
        Context.clear()
        Context.set_output_params(types.SimpleNamespace(
            data_folder=str(data_folder), output_folder_base=str(data_folder.parent)))
        seeker = FileSeekerDir(str(self.input), str(data_folder))
        Context.set_seeker(seeker)
        Context.set_files_found(seeker.search(
            '*mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'))
        _, data_list, source = module.secretCalculatorPhotoAlbum.__wrapped__(Context)
        return data_list, source

    def assert_rows(self, data_list, source):
        self.assertEqual(len(data_list), 2)
        media = [row[1] for row in data_list]
        self.assertTrue(media[0] and media[0].endswith(f'{CONTAINER}/Library/Data/photo_one.jpg'))
        self.assertIsNone(media[1])
        self.assertEqual(source, f'{CONTAINER}/.com.apple.mobile_container_manager.metadata.plist')

    def test_a_report_under_a_folder_named_private_finds_the_container(self):
        self.assert_rows(*self._run('private/tmp'))

    def test_a_report_elsewhere_finds_the_container(self):
        self.assert_rows(*self._run('cases'))


if __name__ == '__main__':
    unittest.main()
