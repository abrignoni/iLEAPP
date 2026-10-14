"""The LAVA writer commits once per artifact, not once per staged file.

Every media item, media reference, search pattern, file path and pattern-to-file
link used to commit as it was inserted, so a run paid a durable commit per
staged file: four per media file, tens of thousands on a large chat store, and
each one a disk flush on a platform that syncs on commit. The per-row inserts
now leave their rows in the open transaction and the main loop calls
lava_commit() once after each artifact. These tests pin that, and pin that the
rows still reach disk: once per artifact and once more before the database is
closed.
"""
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import types
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position


class CountingConnection(sqlite3.Connection):
    """A connection that counts its commits."""
    commits = 0

    def commit(self):
        CountingConnection.commits += 1
        super().commit()


def _media_item(item_id):
    return types.SimpleNamespace(id=item_id, source_path='a/b.jpg', extraction_path='media/x.jpg',
                                 mimetype='image/jpeg', metadata='', created_at=0, updated_at=0,
                                 is_embedded=0)


def _media_reference(ref_id, item_id):
    return types.SimpleNamespace(id=ref_id, media_item_id=item_id, module_name='m',
                                 artifact_name='a', name='b.jpg')


class LavaCommitBatchingTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        CountingConnection.commits = 0
        real_connect = sqlite3.connect
        self._real_connect = real_connect
        lavafuncs.sqlite3.connect = lambda path, *a, **k: real_connect(path, *a, factory=CountingConnection, **k)
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        self.db_path = str(pathlib.Path(self.tmpdir) / lavafuncs.lava_db_name)
        CountingConnection.commits = 0

    def tearDown(self):
        lavafuncs.sqlite3.connect = self._real_connect
        if lavafuncs.lava_db is not None:
            try:
                lavafuncs.lava_db.close()
            except sqlite3.ProgrammingError:
                pass
            lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _insert_one_of_each(self):
        lavafuncs.lava_insert_sqlite_artifact_search_pattern(1, 'mod', 'art', '*/x')
        lavafuncs.lava_insert_sqlite_file_path(7, 'a/b.jpg')
        lavafuncs.lava_insert_sqlite_artifact_link_pattern_to_file(1, 7)
        lavafuncs.lava_insert_sqlite_media_item(_media_item('item1'))
        lavafuncs.lava_insert_sqlite_media_references(_media_reference('ref1', 'item1'))

    def _rows_seen_by_a_second_connection(self):
        other = self._real_connect(f'file:{self.db_path}?mode=ro', uri=True)
        try:
            return [other.execute(f'select count(*) from {t}').fetchone()[0]
                    for t in ('_artifact_search_patterns', '_file_path_list',
                              '_artifact_pattern_to_file', '_lava_media_items',
                              '_lava_media_references')]
        finally:
            other.close()

    def test_per_row_inserts_do_not_commit(self):
        self._insert_one_of_each()
        self.assertEqual(CountingConnection.commits, 0)
        self.assertEqual(self._rows_seen_by_a_second_connection(), [0, 0, 0, 0, 0])

    def test_lava_commit_makes_the_rows_durable_in_one_commit(self):
        self._insert_one_of_each()
        lavafuncs.lava_commit()
        self.assertEqual(CountingConnection.commits, 1)
        self.assertEqual(self._rows_seen_by_a_second_connection(), [1, 1, 1, 1, 1])

    def test_finalize_commits_what_the_last_artifact_left_open(self):
        self._insert_one_of_each()
        lavafuncs.lava_finalize_output(self.tmpdir)
        self.assertEqual(CountingConnection.commits, 1)
        self.assertEqual(self._rows_seen_by_a_second_connection(), [1, 1, 1, 1, 1])

    def test_lava_commit_with_no_database_is_a_no_op(self):
        lavafuncs.lava_db.close()
        lavafuncs.lava_db = None
        lavafuncs.lava_commit()


if __name__ == '__main__':
    unittest.main()
