"""Pin which transcript lines validate_sample_data.py treats as a caught database error.

The --run step reads the tool's transcript and reports any line matching
CAUGHT_ERROR_RE as an error, because a count taken from a run in which an
artifact swallowed a database error describes the tool rather than the
evidence. The vocabulary is SQLite's: "no such table", "no such column",
"file is not a database", "database disk image is malformed" and "malformed
database schema". An artifact that skips an input it read and understood to be
incomplete says so in its own words, and the bare word "malformed" in such a
line is not a database error; a run of the Chromium HTTP cache artifact on a
corpus holding a half-written entry file was reported as one.

Every line below is a literal, in the shape the tool's transcript carries it.
"""
import importlib.util
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / 'admin' / 'scripts' / 'validate_sample_data.py'


def _load():
    spec = importlib.util.spec_from_file_location('validate_sample_data', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestCaughtErrorVocabulary(unittest.TestCase):
    """SQLite's own messages are caught; an artifact's own skip line is not."""

    DATABASE_ERRORS = (
        # The second line of the two-line "Error with <path>:" message an artifact logs.
        ' - no such column: zAddAssetAttr.ZSOMETHING',
        'Unable to query routine_history (unsupported schema version?): no such table: routine_history',
        'Facebook: query failed on prefs_db: no such table: preferences',
        'sqlite3.DatabaseError: database disk image is malformed',
        'Error reading knowledgeC.db: file is not a database',
        'sqlite3.DatabaseError: malformed database schema (sqlite_autoindex_x)',
    )

    ARTIFACT_SKIPS = (
        'Chromium HTTP cache: 1 entry files were skipped as malformed or truncated',
        'Chromium HTTP cache: 70d96111b776ba72_0 has no stream 0 EOF record',
        'Malformed binarycookies file Library/Cookies/Cookies.binarycookies: bad magic',
        'Error: Malformed JSON in file cache.json: Expecting value',
        'Kijiji: skipping malformed conversation: missing id',
        'Found 1,311 records for Chromium Browsers - HTTP Cache Entries',
    )

    def setUp(self):
        self.pattern = _load().CAUGHT_ERROR_RE

    def test_sqlite_messages_are_caught(self):
        for line in self.DATABASE_ERRORS:
            self.assertIsNotNone(self.pattern.search(line), line)

    def test_an_artifacts_own_skip_line_is_not(self):
        for line in self.ARTIFACT_SKIPS:
            self.assertIsNone(self.pattern.search(line), line)


if __name__ == '__main__':
    unittest.main()
