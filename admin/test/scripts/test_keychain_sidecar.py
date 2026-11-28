"""Pin how keychain.py finds the <UDID>_keychain.plist sidecar for a zip input.

The returned path must be the file's own name as stored, so the lookup works on a case-sensitive
file system whatever the case of the UDID in the sidecar's name."""
import pathlib
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position
from scripts.artifacts.keychain import _find_keychain_for_zip  # pylint: disable=protected-access
# pylint: enable=wrong-import-position

UDID_40 = '0123456789abcdef0123456789abcdef01234567'
UDID_8_16 = '00008030-001a2b3c4d5e6f70'


class KeychainSidecarTest(unittest.TestCase):

    def setUp(self):
        self.folder = pathlib.Path(tempfile.mkdtemp(prefix='leapp_keychain_sidecar_'))

    def tearDown(self):
        for path in sorted(self.folder.rglob('*'), reverse=True):
            if path.is_dir():
                path.rmdir()
            else:
                path.unlink()
        self.folder.rmdir()

    def touch(self, relative):
        path = self.folder / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'')
        return path

    def test_lowercase_sidecar_beside_the_zip(self):
        zip_path = self.touch(f'{UDID_40}_files_full.zip')
        sidecar = self.touch(f'{UDID_40}_keychain.plist')
        found = _find_keychain_for_zip(zip_path)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, sidecar.name)

    def test_uppercase_sidecar_beside_a_lowercase_zip(self):
        zip_path = self.touch(f'{UDID_40}_files_full.zip')
        sidecar = self.touch(f'{UDID_40.upper()}_keychain.plist')
        self.assertEqual(_find_keychain_for_zip(zip_path).name, sidecar.name)

    def test_lowercase_sidecar_in_the_udid_folder(self):
        zip_path = self.touch(f'{UDID_8_16}/fs/fs-partial-afu.zip')
        sidecar = self.touch(f'{UDID_8_16}/{UDID_8_16}_keychain.plist')
        self.assertEqual(_find_keychain_for_zip(zip_path), sidecar)

    def test_lowercase_sidecar_beside_the_udid_folder(self):
        zip_path = self.touch(f'{UDID_8_16}/fs/fs-partial-afu.zip')
        sidecar = self.touch(f'{UDID_8_16}_keychain.plist')
        self.assertEqual(_find_keychain_for_zip(zip_path), sidecar)

    def test_no_sidecar(self):
        zip_path = self.touch(f'{UDID_40}_files_full.zip')
        self.touch(f'{UDID_40}_passwords.txt')
        self.assertIsNone(_find_keychain_for_zip(zip_path))

    def test_other_udid_is_not_matched(self):
        zip_path = self.touch(f'{UDID_40}_files_full.zip')
        self.touch(f'{"f" * 40}_keychain.plist')
        self.assertIsNone(_find_keychain_for_zip(zip_path))


if __name__ == '__main__':
    unittest.main()
