"""The compiled gate must never remove a row accepted by SQLite."""
import ast
import pathlib
import random
import sqlite3
import sys
import unittest
from unittest.mock import patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from scripts import log_filter  # pylint: disable=wrong-import-position


class FilterTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.execute('CREATE TABLE logarchive(timestamp, row_number, process_image_path, '
                        'process_id, subsystem, category, event_message, trace_id)')

    def compare(self, query):
        accelerated, mode = log_filter.accelerate_query(self.db, query)
        self.assertIn('compiled multi-pattern', mode)
        self.assertNotEqual(accelerated, query)
        expected = self.db.execute(query + ' ORDER BY rowid').fetchall()
        actual = self.db.execute(accelerated + ' ORDER BY rowid').fetchall()
        self.assertEqual(actual, expected)
        return expected

    def insert(self, message, category=None, subsystem=None, path=None):
        self.db.execute('INSERT INTO logarchive VALUES(NULL,NULL,?,NULL,?,?,?,NULL)',
                        (path, subsystem, category, message))

    @unittest.skipIf(log_filter.ahocorasick is None, 'compiled matcher unavailable')
    def test_like_semantics_nulls_types_duplicates_and_boolean_branches(self):
        values = [None, '', 'FOO', 'foo', 'FoO', 'xfooy', 'foo\x00bar', 'foo_bar',
                  'fooXbar', 'foo--bar', "it's foo", 'éfoo', 'İfoo', 'Kfoo',
                  'ßfoo', b'foo', 123, 123.0, '123', 'BAR', 'bar', 'baz', 'foo']
        for value in values:
            self.insert(value, 'exact', 'engine', '/system/path')
        for value in ('bar', 'baz', 'other'):
            self.insert(value, 'alternate', 'engine', '/other/path')
        for query in [
                "event_message LIKE '%foo%'",
                "event_message LIKE '%foo_bar%' OR event_message = '123'",
                "event_message LIKE '%foo--bar%' OR event_message LIKE '%it''s%'",
                "(event_message LIKE '%foo%' AND category = 'exact') OR category = 'alternate'",
                "event_message LIKE '%foo%' AND (category = 'missing' OR subsystem LIKE 'eng%')",
                "process_image_path LIKE '%/system/%' AND event_message LIKE '%bar%'",
                "event_message LIKE '%foo%' -- final comment with LIKE 'fake'\n",
                "event_message LIKE '%foo%' /* OR event_message LIKE '%' */"]:
            with self.subTest(query=query):
                self.compare('SELECT * FROM logarchive WHERE (' + query + '\n)')
        self.db.execute('PRAGMA case_sensitive_like=ON')
        self.compare("SELECT * FROM logarchive WHERE (event_message LIKE '%FOO%')")

    def test_missing_library_preserves_original_sql(self):
        query = "SELECT * FROM logarchive WHERE (event_message LIKE '%foo%')"
        with patch.object(log_filter, 'ahocorasick', None):
            actual, mode = log_filter.accelerate_query(self.db, query)
        self.assertEqual(actual, query)
        self.assertIn('unavailable', mode)

    @unittest.skipIf(log_filter.ahocorasick is None, 'compiled matcher unavailable')
    def test_unsupported_or_unanchored_expressions_fall_back(self):
        expressions = ["event_message LIKE '%'", "event_message LIKE '___'",
                       "event_message = ''", "event_message LIKE '%é%'",
                       "event_message LIKE 'foo\x00bar'", "NOT event_message LIKE '%foo%'",
                       "event_message NOT LIKE '%foo%'", "event_message IS NULL",
                       "event_message LIKE '%foo%' ESCAPE '_'", '1',
                       "lower(event_message) = 'foo'", "event_message GLOB '*foo*'",
                       "event_message = 'foo' COLLATE NOCASE", "missing = 'foo'",
                       "event_message = 'foo' OR 1", "event_message = 'foo') OR ('a'='a'",
                       "event_message = 'foo';", "event_message = 'foo' UNION SELECT * FROM logarchive",
                       "event_message = 'foo' AND", "()", "event_message = 'foo' (category = 'a')"]
        for expression in expressions:
            query = 'SELECT * FROM logarchive WHERE (' + expression + ')'
            with self.subTest(expression=expression):
                actual, mode = log_filter.accelerate_query(self.db, query)
                self.assertEqual(actual, query)
                self.assertIn('unsupported', mode)
        query = "SELECT event_message FROM logarchive WHERE event_message = 'foo'"
        self.assertEqual(log_filter.accelerate_query(self.db, query)[0], query)

    @unittest.skipIf(log_filter.ahocorasick is None, 'compiled matcher unavailable')
    def test_current_collection_query_against_sqlite_oracle(self):
        tree = ast.parse((REPO_ROOT / 'scripts/artifacts/logarchive.py').read_text(encoding='utf-8'))
        function = next(node for node in tree.body
                        if isinstance(node, ast.FunctionDef) and node.name == 'logarchive_artifacts')
        query = next(node.value.value for node in function.body if isinstance(node, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == 'query' for t in node.targets))
        # Witnesses for every real pattern, plus combinations for AND branches.
        prefix = log_filter._SELECT.match(query)  # pylint: disable=protected-access
        tokens = [m.group() for m in log_filter._TOKEN.finditer(query[prefix.end():])]  # pylint: disable=protected-access
        tokens = [t for t in tokens if not (t.isspace() or t.startswith(('--', '/*')))]
        witnesses = {'event_message': [], 'category': [], 'subsystem': [], 'process_image_path': []}
        for index, token in enumerate(tokens[:-2]):
            if token in witnesses and tokens[index + 1].upper() in ('LIKE', '='):
                literal = tokens[index + 2][1:-1].replace("''", "'")
                if tokens[index + 1].upper() == 'LIKE':
                    literal = literal.replace('%', '').replace('_', 'X')
                witnesses[token].append(literal)
        rng = random.Random(2261)
        for message in witnesses['event_message']:
            for category in witnesses['category'] + [None]:
                for subsystem in witnesses['subsystem'] + [None]:
                    self.insert(message, category, subsystem, '/system/path')
        for _ in range(2000):
            self.insert(rng.choice(witnesses['event_message'] + ['unrelated', '', None]),
                        rng.choice(witnesses['category'] + [None]),
                        rng.choice(witnesses['subsystem'] + [None]),
                        rng.choice(witnesses['process_image_path'] + [None]))
        self.assertGreater(len(self.compare(query)), 0)


if __name__ == '__main__':
    unittest.main()
