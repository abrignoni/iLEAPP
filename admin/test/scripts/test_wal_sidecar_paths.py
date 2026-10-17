"""The Viber Settings.data pattern stages the database's -wal beside it.

Settings.data is WAL-mode SQLite. A pattern that names the database alone leaves the
write-ahead log in the evidence, so the database is read without the records committed
only to the log. This test pins that the pattern also matches the -wal.
"""
import fnmatch
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position
from scripts.artifacts import viber
# pylint: enable=wrong-import-position

SETTINGS = ("/case/private/var/mobile/Containers/Shared/AppGroup/0000-UUID/"
            "com.viber/settings/Settings.data")


class WalSidecarPaths(unittest.TestCase):
    def test_viber_settings_pattern_stages_the_log(self):
        paths = viber.__artifacts_v2__["viber_settings"]["paths"]
        for candidate in (SETTINGS, SETTINGS + "-wal"):
            with self.subTest(candidate=candidate):
                self.assertTrue(any(fnmatch.fnmatchcase(candidate, p) for p in paths))


if __name__ == "__main__":
    unittest.main()
