r"""Windows: get_sqlite_db_path makes a relative path absolute before adding \\?\.

The extended-length prefix \\?\ turns off Windows path parsing, so it is only
valid in front of a full path with a drive. get_sqlite_db_path used to put it in
front of whatever it was given, so a relative path such as admin\test\temp\x.db
became \\?\admin\test\temp\x.db and SQLite reported "unable to open database
file". The test harness hit this until it staged into an absolute folder.

The URI tests run on every platform with the Windows branch forced on. The open
test runs only on Windows, where windows_smoke.yml runs it.
"""
import ntpath
import os
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs  # pylint: disable=wrong-import-position

PREFIX = '%5C%5C%3F%5C'


class TestRelativePathUri(unittest.TestCase):
    """The Windows branch, forced on, with a fixed current directory.

    On Windows ntpath.abspath asks the OS and ignores os.getcwd, so the stand-in
    below resolves against C:\\work the way Windows does. The real resolution is
    exercised by TestRelativePathOpens.
    """

    @staticmethod
    def _abspath(path):
        return ntpath.normpath(ntpath.join('C:\\work', path))

    def uri(self, path):
        with mock.patch.object(ilapfuncs, 'is_platform_windows', return_value=True), \
                mock.patch('ntpath.abspath', side_effect=self._abspath):
            return ilapfuncs.get_sqlite_db_path(path)

    def test_relative_path_is_made_absolute(self):
        self.assertEqual(self.uri('admin\\test\\temp\\x.db'),
                         PREFIX + 'C:%5Cwork%5Cadmin%5Ctest%5Ctemp%5Cx.db')

    def test_forward_slashed_relative_path_is_made_absolute(self):
        self.assertEqual(self.uri('admin/test/temp/x.db'),
                         PREFIX + 'C:%5Cwork%5Cadmin%5Ctest%5Ctemp%5Cx.db')

    def test_drive_relative_path_is_made_absolute(self):
        self.assertEqual(self.uri('C:x.db'), PREFIX + 'C:%5Cwork%5Cx.db')

    def test_rooted_path_without_drive_gets_the_drive(self):
        self.assertEqual(self.uri('\\data\\x.db'), PREFIX + 'C:%5Cdata%5Cx.db')

    def test_absolute_path_is_unchanged(self):
        self.assertEqual(self.uri('D:\\case\\x.db'), PREFIX + 'D:%5Ccase%5Cx.db')

    def test_absolute_path_is_not_normalised(self):
        # Only relative paths are resolved. A full path keeps its exact spelling,
        # so a name the seeker staged with a trailing dot or space still matches.
        self.assertEqual(self.uri('D:\\case\\name. \\x.db'),
                         PREFIX + 'D:%5Ccase%5Cname.%20%5Cx.db')

    def test_extended_and_unc_paths_are_unchanged(self):
        self.assertEqual(self.uri('\\\\?\\D:\\case\\x.db'), PREFIX + 'D:%5Ccase%5Cx.db')
        self.assertEqual(self.uri('\\\\server\\share\\x.db'),
                         PREFIX + '%5CUNC%5Cserver%5Cshare%5Cx.db')


@unittest.skipUnless(ilapfuncs.is_platform_windows(),
                     r'extended-length (\\?\) paths are a Windows-only concept')
class TestRelativePathOpens(unittest.TestCase):
    """A database named by a relative path opens on Windows."""

    def setUp(self):
        self.base = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.makedirs(os.path.join(self.base, 'sub'))
        con = sqlite3.connect(os.path.join(self.base, 'sub', 'x.db'))
        con.execute('CREATE TABLE t (v TEXT)')
        con.execute("INSERT INTO t VALUES ('relative')")
        con.commit()
        con.close()
        os.chdir(self.base)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.base, ignore_errors=True)

    def test_relative_path_opens(self):
        db = ilapfuncs.open_sqlite_db_readonly('sub\\x.db')
        self.assertIsNotNone(db, 'open_sqlite_db_readonly returned None on a relative path')
        try:
            self.assertEqual(db.execute('SELECT v FROM t').fetchone()[0], 'relative')
        finally:
            db.close()


if __name__ == '__main__':
    unittest.main()
