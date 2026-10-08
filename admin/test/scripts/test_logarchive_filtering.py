"""Unified Log filtering stays bounded, observable and complete (issue #2261)."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import lavafuncs, unifiedlogs  # pylint: disable=wrong-import-position
from scripts.artifacts import logarchive  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position


class TrackedCursor(sqlite3.Cursor):
    def fetchall(self):
        rows = super().fetchall()
        self.connection.largest_result = max(self.connection.largest_result, len(rows))
        return rows


class TrackedConnection(sqlite3.Connection):
    closed = False
    largest_result = 0

    def execute(self, *args):
        return self.cursor(factory=TrackedCursor).execute(*args)

    def close(self):
        self.closed = True
        super().close()


class FilteringTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(pathlib.Path(self.tmp.name) / '_lava_artifacts.db')
        self.db = sqlite3.connect(self.path)
        self.db.execute('CREATE TABLE logarchive(timestamp INTEGER, row_number TEXT, '
                        'process_image_path TEXT, process_id TEXT, subsystem TEXT, category TEXT, '
                        'event_message TEXT, trace_id TEXT)')
        self.readers = []
        self.logs = []
        self.opener = patch.object(unifiedlogs, 'open_sqlite_db_readonly', self.open_readonly)
        self.opener.start()
        Context.clear()

    def tearDown(self):
        self.opener.stop()
        for reader in self.readers:
            if not reader.closed:
                reader.close()
        if lavafuncs.lava_db is not None:
            lavafuncs.lava_db.close()
        lavafuncs.lava_db = lavafuncs.lava_data = lavafuncs.lava_db_path = None
        self.db.close()
        Context.clear()
        self.tmp.cleanup()

    def open_readonly(self, path):
        reader = sqlite3.connect(f'file:{path}?mode=ro', uri=True, factory=TrackedConnection)
        self.readers.append(reader)
        return reader

    def insert(self, rowid, message, subsystem='synthetic', category='test'):
        self.db.execute('INSERT INTO logarchive VALUES(?,?,?,?,?,?,?,?)',
                        (1700000000, str(rowid), '/test', '12', subsystem, category, message, ''))

    def test_ranges_preserve_or_branches_duplicates_nulls_and_order(self):
        # Use explicit rowids to exercise gaps and a negative lower endpoint.
        for rowid, message in [(-3, 'first'), (1, 'last'), (4, None), (8, 'other'),
                               (10, 'first'), (11, 'last'), (14, 'last')]:
            self.db.execute('INSERT INTO logarchive(rowid, event_message) VALUES(?,?)',
                            (rowid, message))
        self.db.commit()
        query = "SELECT * FROM logarchive WHERE (event_message='first' OR event_message='last')"
        expected = self.db.execute(query + ' ORDER BY rowid').fetchall()
        actual = list(unifiedlogs.filtered_records(self.path, query, batch_size=3, log=self.logs.append))
        self.assertEqual(actual, expected)
        self.assertTrue(self.readers[-1].closed)
        self.assertLessEqual(self.readers[-1].largest_result, 3)

    def test_zero_matches_still_report_progress_without_a_second_count_scan(self):
        for index in range(11):
            self.insert(index, 'unrelated')
        self.db.commit()
        ticks = iter(range(0, 1000, 21))
        rows = list(unifiedlogs.filtered_records(
            self.path, "SELECT * FROM logarchive WHERE (event_message='missing')",
            batch_size=3, clock=lambda: next(ticks), log=self.logs.append))
        self.assertEqual(rows, [])
        updates = [line for line in self.logs if line.startswith('Unified Log filtering:')]
        self.assertGreater(len(updates), 1)
        self.assertTrue(all('0 selected' in line for line in updates))
        self.assertIn('100% of source range', self.logs[-1])

    def test_progress_is_time_throttled(self):
        for index in range(31):
            self.insert(index, 'unrelated')
        self.db.commit()
        ticks = iter(range(100))
        list(unifiedlogs.filtered_records(
            self.path, 'SELECT * FROM logarchive WHERE (1)', batch_size=1,
            clock=lambda: next(ticks), log=self.logs.append))
        updates = [line for line in self.logs if line.startswith('Unified Log filtering:')]
        self.assertEqual(len(updates), 1)
        self.assertIn('31 selected', self.logs[-1])

    def test_empty_source_and_failed_query_close_the_connection(self):
        self.assertEqual(list(unifiedlogs.filtered_records(
            self.path, 'SELECT * FROM logarchive WHERE (1)', log=self.logs.append)), [])
        self.assertTrue(self.readers[-1].closed)
        self.assertIn('empty source', self.logs[-1])
        self.insert(1, 'first')
        self.db.commit()
        self.logs.clear()
        with self.assertRaises(sqlite3.OperationalError):
            list(unifiedlogs.filtered_records(self.path,
                 'SELECT * FROM logarchive WHERE (missing_column=1)', log=self.logs.append))
        self.assertTrue(self.readers[-1].closed)
        self.assertFalse(any('finished' in line for line in self.logs))

    def test_abandoned_iterator_closes_reader(self):
        for index in range(10):
            self.insert(index, 'first')
        self.db.commit()
        rows = unifiedlogs.filtered_records(self.path, 'SELECT * FROM logarchive WHERE (1)',
                                           batch_size=2, log=self.logs.append)
        next(rows)
        rows.close()
        self.assertTrue(self.readers[-1].closed)
        self.assertFalse(any('finished' in line for line in self.logs))

    def run_artifact(self):
        # The decorator exposes the core's five-argument dispatcher signature.
        # pylint: disable=too-many-function-args
        return logarchive.logarchive_artifacts([self.path], self.tmp.name, None, False, 0)

    def test_actual_artifact_commits_multiple_batches_without_reader_locks(self):
        for index in range(25037):
            self.insert(index, 'Take screenshot é' if index % 2 else 'App state test',
                        'com.apple.CommCenter', 'ct.server')
        self.db.commit()
        expected = self.db.execute('SELECT * FROM logarchive ORDER BY rowid').fetchall()
        lavafuncs.initialize_lava(self.tmp.name, self.tmp.name, 'fs')
        self.run_artifact()
        actual = lavafuncs.lava_db.execute('SELECT * FROM logarchive_artifacts ORDER BY rowid').fetchall()
        self.assertEqual(actual, expected)
        self.assertLessEqual(self.readers[-1].largest_result, 10000)
        self.assertTrue(self.readers[-1].closed)
        artifact = lavafuncs.lava_data['artifacts']['Unified Logs'][0]
        self.assertEqual(artifact['record_count'], 25037)

    def test_failure_discards_already_written_collection_rows(self):
        for index in range(10001):
            self.insert(index, 'Take screenshot')
        self.db.commit()
        lavafuncs.initialize_lava(self.tmp.name, self.tmp.name, 'fs')
        original = unifiedlogs.filtered_records

        def fail_after_batch(*args):
            rows = original(*args, log=self.logs.append)
            try:
                for index, row in enumerate(rows):
                    if index == 10000:
                        raise sqlite3.OperationalError('injected read failure')
                    yield row
            finally:
                rows.close()

        with patch.object(unifiedlogs, 'filtered_records', fail_after_batch):
            with self.assertRaisesRegex(sqlite3.OperationalError, 'injected'):
                self.run_artifact()
        self.assertIsNone(lavafuncs.lava_db.execute(
            "SELECT name FROM sqlite_master WHERE name='logarchive_artifacts'").fetchone())
        self.assertEqual(lavafuncs.lava_db.execute('SELECT count(*) FROM logarchive').fetchone()[0], 10001)
        self.assertEqual(lavafuncs.lava_data['artifacts'].get('Unified Logs', []), [])
        self.assertTrue(self.readers[-1].closed)
        self.assertFalse(any('finished' in line for line in self.logs))

    def test_empty_selection_registers_no_collection_table(self):
        self.insert(1, 'unrelated')
        self.db.commit()
        lavafuncs.initialize_lava(self.tmp.name, self.tmp.name, 'fs')
        self.run_artifact()
        self.assertIsNone(lavafuncs.lava_db.execute(
            "SELECT name FROM sqlite_master WHERE name='logarchive_artifacts'").fetchone())


if __name__ == '__main__':
    unittest.main()
