"""Actual SQLite/JSON coverage for cached row grouping and source choice."""
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from scripts.artifacts.netflix import netflix_continue_watching


class TestContinueWatchingNative(unittest.TestCase):
    """Exercise stored JSON, first-winner grouping and an actual live WAL."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def database(self, directory, values, wal=False, blob=False):
        """Create a complete SQLite state and keep its connection alive for WAL."""
        path = self.root / directory / 'Library/gqlData/ABC-1.2-gql1.3.db'
        path.parent.mkdir(parents=True)
        connection = sqlite3.connect(path)
        if wal:
            connection.execute('PRAGMA journal_mode=WAL')
            connection.execute('PRAGMA wal_autocheckpoint=0')
        connection.execute('CREATE TABLE records(key TEXT, record BLOB)')
        connection.commit()
        if wal:
            connection.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        for index, value in enumerate(values):
            serialized = json.dumps(value)
            connection.execute('INSERT INTO records VALUES (?, ?)',
                               (str(index), serialized.encode() if blob else serialized))
        connection.commit()
        self.addCleanup(connection.close)
        return path

    def rows(self, files):
        """Call the native wrapper with explicit encountered paths."""
        context = SimpleNamespace(
            get_files_found=lambda: [str(p) for p in files],
            get_relative_path=lambda p: str(Path(p).relative_to(self.root)))
        return netflix_continue_watching.__wrapped__(context)[1:]

    @staticmethod
    def entry(value):
        """Build an admitted cached JSON entry."""
        return {'__typename': 'PinotContinueWatchingEntityTreatment',
                'displayString': value, 'unifiedEntity': {'$reference': 'Video:7'}}

    def test_falsey_equality_retains_first_native_class_and_occurrences(self):
        """Native equality groups zero types and preserves the first winner."""
        path = self.database('A', [self.entry(v) for v in [0, False, 0.0, None, '']])
        rows, _ = self.rows([path])
        self.assertEqual([r[5] for r in rows], [3, 2])
        self.assertIs(type(rows[0][0]), int)
        self.assertEqual(rows[0][:5], (0, '7', '', '', 'ABC'))
        self.assertEqual(rows[1][0], '')

    def test_first_title_and_first_source_with_duplicate_records(self):
        """Title lookup and source winner stay independent from displayString."""
        values = [{'title': 'Cached', 'videoId': 7, '__typename': 'Video'},
                  {'title': 'Later', 'videoId': 7}, self.entry('Independent')]
        first = self.database('A', values)
        second = self.database('B', values)
        rows, source = self.rows([second, first, second])
        self.assertEqual(rows, [('Independent', '7', 'Cached', 'Video', 'ABC', 2,
                                 str(second.relative_to(self.root)))])
        self.assertEqual(source, '\n'.join(sorted([str(first), str(second)])))

    def test_nonobject_and_wrong_typename_skip_reference_zero_retained(self):
        """Decode JSON BLOB inputs and skip nonobject or wrong-type records."""
        values = [0, [], {'__typename': 'other'},
                  {'__typename': 'PinotContinueWatchingEntityTreatment',
                   'displayString': True, 'unifiedEntity': {'$reference': 0}}]
        path = self.database('A', values, blob=True)
        rows, _ = self.rows([path])
        self.assertEqual(rows[0][:6], (True, '', '', '', 'ABC', 1))
        self.assertIs(type(rows[0][0]), bool)

    def test_own_live_wal_contains_rows_absent_from_main_only(self):
        """Live WAL belongs to this main and contributes selected rows."""
        live = self.database('A', [self.entry('WAL row')], wal=True)
        other = self.root / 'B/Library/gqlData/ABC-1.2-gql1.3.db'
        other.parent.mkdir(parents=True)
        shutil.copyfile(live, other)
        self.assertEqual(len(self.rows([live])[0]), 1)
        self.assertEqual(self.rows([other])[0], [])


if __name__ == '__main__':
    unittest.main()
