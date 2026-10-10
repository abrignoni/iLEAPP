"""The logarchive report artifacts hand the wrapper a datetime, and LAVA keeps its epoch."""
import ast
import pathlib
import sqlite3
import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import lavafuncs  # pylint: disable=wrong-import-position
from scripts.artifacts import logarchive  # pylint: disable=wrong-import-position
from scripts.ilapfuncs import check_output_types  # pylint: disable=wrong-import-position

# The producers stream the tables the others read; they never see these rows.
PRODUCERS = ('logarchive', 'logarchive_artifacts')
EPOCH = 1704308775.927575
EXPECTED = datetime(2024, 1, 3, 19, 6, 15, 927575, tzinfo=timezone.utc)
STORED_ROW = (EPOCH, 7, '/usr/libexec/test', 12, 'subsystem', 'category', 'message', '0')


def stored_rows(_path, _query):
    """One row of the table as get_sqlite_db_records returns it, readable by column name."""
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    db.execute('CREATE TABLE logarchive_artifacts(timestamp REAL, row_number INTEGER, '
               'process_image_path TEXT, process_id INTEGER, subsystem TEXT, category TEXT, '
               'event_message TEXT, trace_id TEXT)')
    db.execute('INSERT INTO logarchive_artifacts VALUES(?,?,?,?,?,?,?,?)', STORED_ROW)
    rows = db.execute('SELECT * FROM logarchive_artifacts').fetchall()
    db.close()
    return rows


class ReportTimeTests(unittest.TestCase):
    def test_epoch_seconds_become_an_aware_utc_datetime(self):
        self.assertEqual(logarchive._report_time(EPOCH), EXPECTED)  # pylint: disable=protected-access
        self.assertEqual(logarchive._report_time(1700000000),  # pylint: disable=protected-access
                         datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc))

    def test_anything_else_is_returned_as_stored(self):
        for value in ('2026-08-14 00:00:00', '', None, 1e300):
            self.assertEqual(logarchive._report_time(value), value)  # pylint: disable=protected-access

    def test_lava_stores_the_same_epoch(self):
        # lavafuncs turns an aware datetime back into seconds; microsecond values survive.
        for micro in (0, 1, 485265, 927575, 999999):
            value = 1704308775 + micro / 1_000_000
            converted = logarchive._report_time(value)  # pylint: disable=protected-access
            stored = lavafuncs._prepare_datetime_value(converted)  # pylint: disable=protected-access
            self.assertEqual(round(stored * 1_000_000), round(value * 1_000_000))

    def test_every_report_artifact_converts_and_every_lava_only_one_does_not(self):
        source = pathlib.Path(logarchive.__file__).read_text(encoding='utf-8')
        declared = {node.name for node in ast.parse(source).body
                    if isinstance(node, ast.FunctionDef)}
        context = Mock()
        context.get_files_found.return_value = ['_lava_artifacts.db']
        checked = 0
        with patch.object(logarchive, 'get_sqlite_db_records', stored_rows):
            for name, info in logarchive.__artifacts_v2__.items():
                if name in PRODUCERS:
                    continue
                self.assertIn(name, declared)
                headers, rows, _source = getattr(logarchive, name).__wrapped__(context)
                self.assertEqual(headers[0][1], 'datetime', name)
                checked += 1
                first = rows[0][0]
                if check_output_types('html', info['output_types']):
                    self.assertEqual(first, EXPECTED, name)
                    self.assertEqual(first.utcoffset().total_seconds(), 0, name)
                    if headers == logarchive.DATA_HEADERS:
                        self.assertEqual(tuple(rows[0][1:]), STORED_ROW[1:], name)
                else:
                    self.assertEqual(tuple(rows[0]), STORED_ROW, name)
        self.assertEqual(checked, len(logarchive.__artifacts_v2__) - len(PRODUCERS))


if __name__ == '__main__':
    unittest.main()
