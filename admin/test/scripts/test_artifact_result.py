"""ArtifactResult, the writer-style return for large artifacts.

Two paths exist. With a LAVA run active, add_row() streams rows into the artifact's LAVA
table and close() corrects the manifest with the count and the source path the module
knew only once its loop was over. With no LAVA run active, which is how the test harness
executes a module, the rows stay in memory and come back by iterating the result.
"""
import datetime
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from leapp_functions.app.artifact_result import ArtifactResult  # pylint: disable=wrong-import-position

UTC = datetime.timezone.utc
STAMP = datetime.datetime(2022, 3, 4, 12, 34, 56, tzinfo=UTC)
STAMP_EPOCH = 1646397296  # 2022-03-04 12:34:56 UTC, written out by hand
HEADERS = ['Label', 'Moment', ('Stamp', 'datetime')]
ROWS = [
    ('row 0', STAMP, STAMP),
    ('row 1', datetime.datetime(2022, 3, 4, 12, 34, 56), STAMP),
    ('row 2', '', STAMP),
]
# The text sqlite3 stores for the untyped Moment column: an aware datetime, a naive one, an empty string.
MOMENT_TEXT = ['2022-03-04 12:34:56+00:00', '2022-03-04 12:34:56', '']


class ArtifactResultTestCase(unittest.TestCase):
    """Shared Context setup: what artifact_processor gives a module before calling it."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Context.clear()
        Context.set_data_folder(self.tmpdir)
        Context.set_report_folder(self.tmpdir)
        Context.set_module_name('unit_module')
        Context.set_module_file_path(str(pathlib.Path(self.tmpdir, 'unit_module.py')))
        Context.set_artifact_name('Unit Artifact')
        Context.set_artifact_func_name('unit_artifact')
        Context.set_artifact_info({'category': 'Unit Category', 'description': 'unit description',
                                   'author': '@unit', 'creation_date': '2026-09-12',
                                   'last_update_date': '2026-09-12', 'notes': ''})

    def tearDown(self):
        if lavafuncs.lava_db is not None:
            lavafuncs.lava_db.close()
        lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        lavafuncs.lava_db_path = None
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)


class TestWriterModeWithLava(ArtifactResultTestCase):
    """Rows added through add_row() land in the LAVA table and the manifest is corrected on close()."""

    def setUp(self):
        super().setUp()
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')

    def test_rows_reach_lava_and_the_manifest_gets_count_and_late_source_path(self):
        result = Context.create_artifact_result(headers=HEADERS, estimated_row_count=len(ROWS))
        for row in ROWS:
            result.add_row(row)
        # A module that only knows its files once its loop is over sets the path last.
        result.set_source_path('cases/one.db\ncases/two.db')
        result.close()

        self.assertTrue(result.is_lava_backed)
        self.assertEqual(result.row_count, len(ROWS))
        self.assertTrue(result)
        self.assertEqual(len(result), len(ROWS))

        stored = lavafuncs.lava_db.execute(
            f'SELECT moment, typeof(moment), stamp FROM "{result.table_name}" ORDER BY rowid').fetchall()
        self.assertEqual([row[0] for row in stored], MOMENT_TEXT)
        self.assertEqual({row[1] for row in stored}, {'text'})
        self.assertEqual({row[2] for row in stored}, {STAMP_EPOCH})

        entries = lavafuncs.lava_data['artifacts']['Unit Category']
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['tablename'], result.table_name)
        self.assertEqual(entries[0]['record_count'], len(ROWS))
        self.assertEqual(entries[0]['source_path'], 'cases/one.db\ncases/two.db')

        replayed = list(lavafuncs.lava_iter_artifact_rows(
            result.table_name, HEADERS, result.object_columns, result.row_count))
        self.assertEqual(len(replayed), len(ROWS))
        self.assertEqual([row[0] for row in replayed], [row[0] for row in ROWS])
        self.assertEqual([row[1] for row in replayed], MOMENT_TEXT)
        self.assertEqual({row[2] for row in replayed}, {STAMP})

    def test_source_path_given_up_front_is_kept(self):
        result = Context.create_artifact_result(headers=HEADERS, source_path='cases/only.db')
        result.add_row(ROWS[0])
        result.close()
        entries = lavafuncs.lava_data['artifacts']['Unit Category']
        self.assertEqual(entries[0]['source_path'], 'cases/only.db')
        self.assertEqual(entries[0]['record_count'], 1)


class TestWriterModeWithoutLava(ArtifactResultTestCase):
    """With no LAVA run active the rows stay in memory and iterate back unchanged."""

    def test_rows_stay_in_memory_and_iterate_back(self):
        self.assertIsNone(lavafuncs.lava_data)
        result = Context.create_artifact_result(headers=HEADERS)
        self.assertFalse(result)
        for row in ROWS:
            result.add_row(row)
        self.assertFalse(result.is_lava_backed)
        self.assertIsNone(result.table_name)
        self.assertTrue(result)
        self.assertEqual(len(result), len(ROWS))
        self.assertEqual(list(result), ROWS)
        result.close()
        self.assertEqual(list(result), ROWS)

    def test_rows_iterable_still_refuses_add_row(self):
        result = ArtifactResult(headers=HEADERS, rows=list(ROWS))
        with self.assertRaises(ValueError):
            result.add_row(ROWS[0])
        self.assertEqual(list(result), ROWS)


class TestAsyncInsert(ArtifactResultTestCase):
    """The writer-thread insert returns its count and re-raises what the thread hit."""

    def setUp(self):
        super().setUp()
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        self.table, self.column_map, self.object_columns = lavafuncs.lava_create_sqlite_table('async_insert', HEADERS)

    def test_rows_are_written_on_the_writer_thread(self):
        inserted = lavafuncs.lava_insert_sqlite_data(
            self.table, list(ROWS), self.object_columns, HEADERS, self.column_map, batch_size=2, async_write=True)
        self.assertEqual(inserted, len(ROWS))
        stored = lavafuncs.lava_db.execute(f'SELECT label, moment, stamp FROM "{self.table}" ORDER BY rowid').fetchall()
        self.assertEqual([row[0] for row in stored], [row[0] for row in ROWS])
        self.assertEqual([row[1] for row in stored], MOMENT_TEXT)
        self.assertEqual({row[2] for row in stored}, {STAMP_EPOCH})

    def test_a_failure_on_the_writer_thread_reaches_the_caller(self):
        short_rows = [('only one value',)]  # three columns declared, one bound
        with self.assertRaises(sqlite3.Error):
            lavafuncs.lava_insert_sqlite_data(
                self.table, short_rows, self.object_columns, HEADERS, self.column_map, async_write=True)
        count = lavafuncs.lava_db.execute(f'SELECT COUNT(*) FROM "{self.table}"').fetchone()[0]
        self.assertEqual(count, 0)


if __name__ == '__main__':
    unittest.main()
