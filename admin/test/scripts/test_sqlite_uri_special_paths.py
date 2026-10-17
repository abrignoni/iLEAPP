"""SQLite URIs built from a path keep working when the path holds '#' or '?'.

A URI such as f"file:{path}?mode=ro" ends the path at the first '#' (fragment) or
'?' (query). For a folder named "case #12" SQLite then opens "case " instead and the
tables read as absent. Each reader below must percent-quote the path, so it reads
the synthetic database it was given and leaves no stray file next to the folder.
"""
# pylint: disable=protected-access

import os
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import fileSystemEvents  # pylint: disable=wrong-import-position
from scripts.artifacts import kakaoTalk  # pylint: disable=wrong-import-position
from scripts.artifacts import pinterest  # pylint: disable=wrong-import-position


class _Results:
    def __init__(self):
        self.rows = []

    def add_row(self, row):
        self.rows.append(row)

    def set_source_path(self, _path):
        pass


class _Context:
    def get_files_found(self):
        return []

    def create_artifact_result(self, headers=None):  # pylint: disable=unused-argument
        return _Results()


class SpecialCharacterPathTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        # "case " is where an unquoted URI for "case #1?x/..." lands.
        self.folder = os.path.join(self.root, 'case #1?x')
        os.makedirs(self.folder)
        self.stray = os.path.join(self.root, 'case ')

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def assert_no_stray(self):
        self.assertFalse(os.path.exists(self.stray), 'the URI was cut at # or ?')

    def test_kakaotalk_reads_tables_and_columns(self):
        path = os.path.join(self.folder, 'Message.sqlite')
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE ZMESSAGE (sentAt INTEGER, chatId INTEGER)')
        db.close()
        self.assertEqual(kakaoTalk._tables(path), {'ZMESSAGE'})
        self.assertEqual(kakaoTalk._columns(path, 'ZMESSAGE'), {'sentAt', 'chatId'})
        self.assert_no_stray()

    def test_pinterest_counts_autocomplete_rows(self):
        path = os.path.join(self.folder, 'autocomplete.db')
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE search_queries_content (docid INTEGER PRIMARY KEY, c0query TEXT)')
            db.executemany('INSERT INTO search_queries_content VALUES (?, ?)',
                           [(1, 'a'), (2, 'b'), (4, 'b')])
        db.close()
        self.assertEqual(pinterest._autocomplete_rows(path), (3, 1, 2))
        self.assert_no_stray()

    def test_file_system_events_reads_its_own_cache(self):
        # The cache is the module's own mkstemp file, so a '#' in the temp folder
        # is what puts the character in the path.
        try:
            with patch.object(tempfile, 'tempdir', self.folder):
                results = fileSystemEvents._report_rows(_Context())
        finally:
            fileSystemEvents._remove_cache()
        self.assertEqual(results.rows, [])
        self.assert_no_stray()


if __name__ == '__main__':
    unittest.main()
