"""The test harness stages a case member under the name a real run gives it.

FileSeekerZip replaces the characters Windows cannot hold in a file name on
every platform. The harness used ZipFile.extract, which replaces fewer of them,
and only on Windows. So on macOS and Linux a case saw a member stored as
BDC_2000-01-01_00:00:00.csv under that name, where a run stages it as
BDC_2000-01-01_00_00_00.csv, and the recorded results held a path no run
produces.
"""
import pathlib
import sys
import tempfile
import unittest
import zipfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / 'admin' / 'test' / 'scripts'))

# pylint: disable=wrong-import-position
import test_module  # noqa: E402
from scripts.search_files import FileSeekerZip  # noqa: E402

MEMBERS = {
    'db/Battery/BDC_2000-01-01_00:00:00.csv': b'colon',
    "Media/it's here.txt": b'apostrophe',
    'plain/name.txt': b'plain',
}


class HarnessStagesLikeTheSeeker(unittest.TestCase):

    def setUp(self):
        self._folder = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        root = pathlib.Path(self._folder.name)
        self.zip_path = root / 'case.zip'
        with zipfile.ZipFile(self.zip_path, 'w') as archive:
            for name, data in MEMBERS.items():
                archive.writestr(name, data)
        self.harness_dir = root / 'harness'
        self.seeker_dir = root / 'seeker'
        self.harness_dir.mkdir()
        self.seeker_dir.mkdir()

    def tearDown(self):
        self._folder.cleanup()

    def staged_by_harness(self):
        file_infos = {}
        with zipfile.ZipFile(self.zip_path) as archive:
            test_module.stage_case_members(archive, self.harness_dir, file_infos)
        return {info.source_path: pathlib.Path(path).relative_to(self.harness_dir).as_posix()
                for path, info in file_infos.items()}

    def staged_by_seeker(self):
        seeker = FileSeekerZip(str(self.zip_path), str(self.seeker_dir))
        try:
            seeker.search('*')
            # copied maps each member name to the path the seeker staged it at.
            staged = {name: pathlib.Path(path).relative_to(self.seeker_dir).as_posix()
                      for name, path in seeker.copied.items()}
            self.assertEqual(set(staged), set(MEMBERS))
            return staged
        finally:
            seeker.cleanup()

    def test_every_member_is_staged_under_the_seekers_name(self):
        self.assertEqual(self.staged_by_harness(), self.staged_by_seeker())

    def test_colon_becomes_underscore_on_every_platform(self):
        staged = self.staged_by_harness()
        self.assertEqual(staged['db/Battery/BDC_2000-01-01_00:00:00.csv'],
                         'db/Battery/BDC_2000-01-01_00_00_00.csv')
        self.assertEqual(staged['plain/name.txt'], 'plain/name.txt')

    def test_staged_content_is_the_members(self):
        file_infos = {}
        with zipfile.ZipFile(self.zip_path) as archive:
            test_module.stage_case_members(archive, self.harness_dir, file_infos)
        for path, info in file_infos.items():
            self.assertEqual(pathlib.Path(path).read_bytes(), MEMBERS[info.source_path])


if __name__ == '__main__':
    unittest.main()
