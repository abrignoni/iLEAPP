r"""Windows: open a SQLite database whose full path exceeds 260 characters.

Regression test for the case Mattia Epifani reported. On a Windows output path
over MAX_PATH (260), each core's main prepends the extended-length prefix \\?\
to the output, so the seeker hands artifacts a path like \\?\D:\...\telephony.db.
Many artifacts then normalise that path to forward slashes for their own matching
(str(path).replace('\\', '/')) and open the normalised string, which turns the
prefix into //?/. get_sqlite_db_path used to check the prefix with backslashes
only, so //?/... matched none of the checks, fell to the normal-path branch, and
had a second \\?\ prepended, producing \\?\//?/D:/... which SQLite cannot open.
The database then failed to open and every SQLite artifact on such a path lost
its rows.

This can only run on Windows: \\?\ extended-length paths are a Windows concept,
and on a POSIX host get_sqlite_db_path never takes the branch under test. The
ubuntu runtime-contract job discovers this file and skips it; windows_smoke.yml
runs it for real.

The database, its directory tree, and the cleanup all go through the \\?\ prefix
so the test does not depend on long-path support being enabled in the registry.
"""
import os
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from urllib.parse import quote

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs  # pylint: disable=wrong-import-position


def _legacy_get_sqlite_db_path(path):
    r"""Reproduce the pre-fix get_sqlite_db_path Windows branch.

    Kept as a negative control. It inspected the extended-length prefix with
    backslashes only, so a forward-slashed //?/... path fell through to the
    normal-path branch and had a second \\?\ prepended. The test uses it to
    prove that broken form really fails to open on this runner, which is what
    makes the positive assertion non-vacuous.
    """
    path_str = str(path)
    if path_str.startswith('\\\\?\\UNC\\'):
        remainder = path_str[4:]
    elif path_str.startswith('\\\\?\\'):
        remainder = path_str[4:]
    elif path_str.startswith('\\\\'):
        remainder = '\\UNC' + path_str[1:]
    else:
        remainder = path_str
    return "%5C%5C%3F%5C" + quote(remainder, safe=':/')


@unittest.skipUnless(ilapfuncs.is_platform_windows(),
                     r'extended-length (\\?\) paths are a Windows-only concept')
class TestSqliteLongPathUri(unittest.TestCase):
    """open_sqlite_db_readonly must open a database on a >260-character path."""

    def setUp(self):
        self.base = tempfile.mkdtemp()
        # Mirror the real com.android.providers.telephony layout, then pad until
        # the full path is comfortably past MAX_PATH.
        deep = pathlib.Path(self.base)
        for part in ('ALEAPP_Output_placeholder', 'data', 'Dump', 'data',
                     'user_de', '0', 'com.android.providers.telephony',
                     'databases'):
            deep = deep / part
        while len(str(deep)) < 300:
            deep = deep / ('x' * 40)
        self.long_dir = str(deep)
        self.db_path = os.path.join(self.long_dir, 'telephony.db')
        self.assertGreater(len(self.db_path), 260,
                           'the test path must exceed MAX_PATH to be meaningful')
        os.makedirs(self._ext(self.long_dir), exist_ok=True)
        con = sqlite3.connect(self._ext(self.db_path))
        con.execute('CREATE TABLE sim (id INTEGER, name TEXT)')
        con.execute("INSERT INTO sim VALUES (1, 'carrier')")
        con.commit()
        con.close()

    def tearDown(self):
        shutil.rmtree(self._ext(self.base), ignore_errors=True)

    @staticmethod
    def _ext(path):
        r"""Return the \\?\-prefixed absolute form, so create/open bypass MAX_PATH."""
        return '\\\\?\\' + os.path.abspath(path)

    def _read_carrier(self, db):
        try:
            row = db.execute('SELECT name FROM sim WHERE id = 1').fetchone()
        finally:
            db.close()
        return row[0] if row else None

    def test_forward_slashed_extended_path_opens(self):
        r"""The reported case: the seeker's \\?\ path normalised to //?/ by an artifact."""
        seeker_path = self._ext(self.db_path)              # \\?\C:\...\telephony.db
        artifact_path = seeker_path.replace('\\', '/')     # //?/C:/...  (this broke)
        self.assertTrue(artifact_path.startswith('//?/'))
        db = ilapfuncs.open_sqlite_db_readonly(artifact_path)
        self.assertIsNotNone(
            db, 'open_sqlite_db_readonly returned None on a forward-slashed long path')
        self.assertEqual(self._read_carrier(db), 'carrier')

    def test_backslash_extended_path_still_opens(self):
        """The form that already worked must keep working (no regression)."""
        db = ilapfuncs.open_sqlite_db_readonly(self._ext(self.db_path))
        self.assertIsNotNone(db)
        self.assertEqual(self._read_carrier(db), 'carrier')

    def test_legacy_uri_really_fails(self):
        """Negative control: the pre-fix URI must fail here, or the test proves nothing."""
        artifact_path = self._ext(self.db_path).replace('\\', '/')
        legacy_uri = f"file:{_legacy_get_sqlite_db_path(artifact_path)}?mode=ro"
        with self.assertRaises(sqlite3.OperationalError):
            con = sqlite3.connect(legacy_uri, uri=True)
            con.execute('SELECT 1 FROM sim')
            con.close()


if __name__ == '__main__':
    unittest.main()
