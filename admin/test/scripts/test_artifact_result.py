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
from scripts.ilapfuncs import artifact_processor, OutputParameters  # pylint: disable=wrong-import-position

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

class TestDiscardAfterRows(ArtifactResultTestCase):
    """A result discarded after writing rows leaves no table and no manifest entry."""

    def setUp(self):
        super().setUp()
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')

    def _table_names(self):
        cursor = lavafuncs.lava_db.cursor()
        return [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                if not r[0].startswith('_')]

    def test_discard_drops_the_table_and_the_manifest_entry(self):
        result = Context.create_artifact_result(headers=HEADERS, batch_size=2)
        for row in ROWS:
            result.add_row(row)
        # Rows were flushed: the table exists and the manifest names the artifact.
        self.assertTrue(result.is_lava_backed)
        self.assertIn(result.table_name, self._table_names())
        self.assertEqual(len(lavafuncs.lava_data['artifacts'].get('Unit Category', [])), 1)

        result.discard()

        self.assertNotIn(result.table_name, self._table_names())
        self.assertNotIn('Unit Category', lavafuncs.lava_data['artifacts'])
        self.assertFalse(result.is_lava_backed)
        self.assertEqual(result.row_count, 0)
        self.assertEqual(len(result), 0)
        # A discarded result is closed: nothing more can be added to it.
        with self.assertRaises(ValueError):
            result.add_row(ROWS[0])

    def test_discard_before_any_row_is_harmless(self):
        result = Context.create_artifact_result(headers=HEADERS)
        result.discard()
        self.assertEqual(self._table_names(), [])
        self.assertNotIn('Unit Category', lavafuncs.lava_data['artifacts'])

    def test_the_context_hands_back_the_result_it_created(self):
        result = Context.create_artifact_result(headers=HEADERS)
        self.assertIs(Context.get_artifact_result(), result)
        Context.clear()
        self.assertIsNone(Context.get_artifact_result())

# artifact_processor reads the artifact's metadata from the module globals of the function
# it wraps, so the two probe modules below are registered here.
__artifacts_v2__ = {
    'streaming_module_that_raises': {
        'name': 'Streaming Raises', 'category': 'Probe Category', 'description': 'probe',
        'author': '@unit', 'creation_date': '2026-09-20', 'last_update_date': '2026-09-20',
        'notes': '', 'paths': ('*/nothing',), 'output_types': 'lava_only',
    },
    'list_module_that_raises': {
        'name': 'List Raises', 'category': 'Probe Category', 'description': 'probe',
        'author': '@unit', 'creation_date': '2026-09-20', 'last_update_date': '2026-09-20',
        'notes': '', 'paths': ('*/nothing',), 'output_types': 'lava_only',
    },
}


@artifact_processor
def streaming_module_that_raises(context):
    result = context.create_artifact_result(headers=HEADERS, source_path='probe.db', batch_size=2)
    for row in ROWS:
        result.add_row(row)
    raise RuntimeError('probe: failed after streaming rows')


@artifact_processor
def list_module_that_raises(context):  # pylint: disable=unused-argument
    raise RuntimeError('probe: failed after building a list')


class TestARaisingModuleLeavesNothingBehind(ArtifactResultTestCase):
    """Through artifact_processor, a module that raises after streaming leaves no table and no
    manifest entry, exactly like a list-returning module that raises."""

    def setUp(self):
        super().setUp()
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        # OutputParameters() points the class-level log paths logfunc() writes to at this
        # tmpdir; put them back afterwards or a later test logs into a deleted folder.
        self._saved_log_paths = {name: getattr(OutputParameters, name) for name in vars(OutputParameters)
                                 if name.startswith('screen_output_file_path')}
        self.output_params = OutputParameters(self.tmpdir)
        Context.set_output_params(self.output_params)

    def tearDown(self):
        for name, value in self._saved_log_paths.items():
            setattr(OutputParameters, name, value)
        super().tearDown()

    def _artifact_tables(self):
        cursor = lavafuncs.lava_db.cursor()
        return [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                if not r[0].startswith('_')]

    def test_streaming_module_that_raises_leaves_no_table_and_no_manifest_entry(self):
        with self.assertRaises(RuntimeError):
            streaming_module_that_raises([], self.tmpdir, None, True, 'UTC')
        self.assertEqual(self._artifact_tables(), [])
        self.assertNotIn('Probe Category', lavafuncs.lava_data['artifacts'])

    def test_list_module_that_raises_leaves_the_same_nothing(self):
        with self.assertRaises(RuntimeError):
            list_module_that_raises([], self.tmpdir, None, True, 'UTC')
        self.assertEqual(self._artifact_tables(), [])
        self.assertNotIn('Probe Category', lavafuncs.lava_data['artifacts'])

class TestReplayKeepsPythonText(ArtifactResultTestCase):
    """Floats and booleans in untyped columns replay exactly as the list path prints them,
    while the list path's own stored values are unchanged."""

    def setUp(self):
        super().setUp()
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')

    def test_streamed_rows_replay_as_the_original_values(self):
        headers = ('Latitude', 'Flag', 'Count', 'Text', 'Looks Numeric')
        rows = [(35.65956623101914, True, 7, 'plain', '1.5e3'),
                (-78.87282251025944, False, 0, '', '007')]
        result = Context.create_artifact_result(headers=headers)
        for row in rows:
            result.add_row(row)
        result.close()
        replayed = list(lavafuncs.lava_iter_artifact_rows(
            result.table_name, headers, result.object_columns, result.row_count))
        self.assertEqual(replayed, rows)
        # The stored text is Python's own rendering, not SQLite's 15-digit one.
        stored = lavafuncs.lava_db.execute(
            f'SELECT latitude, flag FROM {lavafuncs.quote_sql_name(result.table_name)} ORDER BY rowid').fetchall()
        self.assertEqual(stored, [('35.65956623101914', 'True'), ('-78.87282251025944', 'False')])

    def test_list_path_storage_is_unchanged(self):
        headers = ('Latitude', 'Flag', 'When')
        table, object_columns, column_map = lavafuncs.lava_process_artifact(
            'Unit Category', 'unit_module', 'List Artifact', (headers[0], headers[1], (headers[2], 'datetime')),
            1, func_name='list_artifact')
        lavafuncs.lava_insert_sqlite_data(
            table, [(35.65956623101914, True, '2024-07-21T15:16:47.357843+00:00')],
            object_columns, (headers[0], headers[1], (headers[2], 'datetime')), column_map)
        stored = lavafuncs.lava_db.execute(
            f'SELECT latitude, flag, "when" FROM {lavafuncs.quote_sql_name(table)}').fetchone()
        # SQLite's rendering of a bound float and boolean into TEXT columns, and a whole-second
        # int epoch for an ISO string: what the list path stored before this change.
        self.assertEqual(stored, ('35.6595662310191', '1', 1721575007))

    def test_python_text_restore_is_exact_and_leaves_other_text_alone(self):
        restore = lavafuncs._restore_lava_value  # pylint: disable=protected-access
        self.assertIs(restore('True'), True)
        self.assertIs(restore('False'), False)
        self.assertEqual(restore('35.65956623101914'), 35.65956623101914)
        self.assertEqual(restore('7'), 7)
        self.assertEqual(restore('-3'), -3)
        self.assertEqual(restore('1.5e3'), '1.5e3')      # not a repr, stays text
        self.assertEqual(restore('007'), '007')          # not the decimal form of 7
        self.assertEqual(restore('-0'), '-0')
        self.assertEqual(restore('nan'), 'nan')          # non-finite never converts
        self.assertEqual(restore('["a", "b"]', 'media'), ['a', 'b'])
        self.assertEqual(restore('single-ref', 'media'), 'single-ref')
