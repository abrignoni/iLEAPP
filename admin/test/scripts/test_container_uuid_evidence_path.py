"""Google Chat and Waze read the app container identifier from the evidence path only.

Both modules find the container as .../Application/<UUID>/ and, when no component
qualifies, fall back to the UUID nearest the file. They read the staged path, which
starts with the examiner's output folder, so when the evidence held no container UUID
the fallback took one from the examiner's own folders. An iTunes backup is that case:
the seeker stages app files under .../Application/<bundle id>/. Google Chat then searched
for attachments in a container that does not exist, and Waze looked for its databases
under the wrong identifier instead of the bundle id.

These tests stage files under an output folder whose name is a version-4 UUID and check
which identifier each module takes.
"""
import pathlib
import shutil
import sys
import tempfile
import types
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import googleChat, waze  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

CASE_UUID = '0F8B2A6C-3D1E-4B7A-9C2D-5E6F7A8B9C0D'
CONTAINER_UUID = '1A2B3C4D-5E6F-4A7B-8C9D-0E1F2A3B4C5D'
APPLICATION = 'private/var/mobile/Containers/Data/Application'


class ContainerUuidEvidencePathTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        report = pathlib.Path(self.tmpdir) / CASE_UUID / 'iLEAPP_Output'
        self.data_folder = report / 'data'
        self.data_folder.mkdir(parents=True)
        Context.clear()
        Context.set_output_params(types.SimpleNamespace(
            data_folder=str(self.data_folder), output_folder_base=str(report)))

    def tearDown(self):
        Context.clear()
        Context.set_output_params(None)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _stage(self, rel_path):
        staged = self.data_folder / rel_path
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_bytes(b'')
        return str(staged)

    def _google_chat_guid(self, rel_path):
        return googleChat._container_guid(  # pylint: disable=protected-access
            Context.get_relative_path(self._stage(rel_path)))

    def test_google_chat_takes_no_guid_from_the_examiners_folders(self):
        rel_path = f'{APPLICATION}/com.google.Dynamite/Documents/user_accounts/1/dynamite.db'

        self.assertEqual(self._google_chat_guid(rel_path), '')

    def test_google_chat_still_takes_the_container_guid(self):
        rel_path = f'{APPLICATION}/{CONTAINER_UUID}/Documents/user_accounts/1/dynamite.db'

        self.assertEqual(self._google_chat_guid(rel_path), CONTAINER_UUID)

    def _waze_app_id(self, rel_path):
        Context.set_files_found([self._stage(rel_path)])
        return waze.get_app_id(waze.WAZE_PREFERENCES_PLIST, Context)

    def test_waze_takes_the_bundle_id_of_a_backup_not_the_examiners_uuid(self):
        rel_path = f'{APPLICATION}/com.waze.iphone/Library/Preferences/com.waze.iphone.plist'

        self.assertEqual(self._waze_app_id(rel_path), 'com.waze.iphone')

    def test_waze_still_takes_the_container_uuid(self):
        rel_path = f'{APPLICATION}/{CONTAINER_UUID}/Library/Preferences/com.waze.iphone.plist'

        self.assertEqual(self._waze_app_id(rel_path), CONTAINER_UUID)


if __name__ == '__main__':
    unittest.main()
