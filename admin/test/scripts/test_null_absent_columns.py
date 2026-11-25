"""null_absent_columns rewriting inside function calls, subqueries, and top-level select items.

When a missing column appears as a non-final argument to a function call such
as COALESCE(t.ZMISSING, t.B), the trailing comma must not trigger a
"NULL AS <name>" alias inside parentheses, which SQLite rejects as a syntax
error. Bare select items at parenthesis depth zero or directly inside a
subquery (such as a derived table or CTE body whose innermost unclosed "("
begins with SELECT) still receive "NULL AS <name>" so callers reading
sqlite3.Row by column name keep working.
"""
import contextlib
import os
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs  # pylint: disable=wrong-import-position


class TestNullAbsentColumns(unittest.TestCase):
    """null_absent_columns emits NULL AS for top-level and subquery select items."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(self._remove_tmpdir)
        self.db_path = os.path.join(self.tmpdir, 'sample.sqlite')
        with contextlib.closing(sqlite3.connect(self.db_path)) as con:
            con.execute('CREATE TABLE T(B TEXT)')
            con.execute("INSERT INTO T(B) VALUES ('present')")
            con.commit()

    def _remove_tmpdir(self):
        if self.tmpdir is None or not os.path.exists(self.tmpdir):
            self.tmpdir = None
            return
        try:
            shutil.rmtree(self.tmpdir)
        except OSError as exc:
            raise RuntimeError(
                f'Failed to clean up temporary directory {self.tmpdir}: {exc}'
            ) from exc
        self.tmpdir = None

    def _rewrite_and_fetch(self, query):
        rewritten = ilapfuncs.null_absent_columns(self.db_path, query)
        with contextlib.closing(sqlite3.connect(self.db_path)) as con:
            con.row_factory = sqlite3.Row
            row = con.execute(rewritten).fetchone()
        return rewritten, row

    def test_coalesce_non_final_argument(self):
        query = 'SELECT COALESCE(t.ZMISSING, t.B) AS X FROM T t'
        rewritten, row = self._rewrite_and_fetch(query)
        self.assertEqual(rewritten, 'SELECT COALESCE(NULL, t.B) AS X FROM T t')
        self.assertEqual(row['X'], 'present')

    def test_top_level_select_items_keep_alias(self):
        rewritten, row = self._rewrite_and_fetch('SELECT t.ZMISSING, t.B FROM T t')
        self.assertEqual(rewritten, 'SELECT NULL AS ZMISSING, t.B FROM T t')
        self.assertIsNone(row['ZMISSING'])
        self.assertEqual(row['B'], 'present')

        rewritten, row = self._rewrite_and_fetch('SELECT t.ZMISSING FROM T t')
        self.assertEqual(rewritten, 'SELECT NULL AS ZMISSING FROM T t')
        self.assertIsNone(row['ZMISSING'])

    def test_last_argument_nested_and_mixed_depths(self):
        rewritten, row = self._rewrite_and_fetch(
            'SELECT COALESCE(t.B, t.ZMISSING) AS X FROM T t')
        self.assertEqual(rewritten, 'SELECT COALESCE(t.B, NULL) AS X FROM T t')
        self.assertEqual(row['X'], 'present')

        rewritten, row = self._rewrite_and_fetch(
            'SELECT IFNULL(COALESCE(t.ZMISSING, t.B), t.B) AS X FROM T t')
        self.assertEqual(
            rewritten, 'SELECT IFNULL(COALESCE(NULL, t.B), t.B) AS X FROM T t')
        self.assertEqual(row['X'], 'present')

        rewritten, row = self._rewrite_and_fetch(
            'SELECT COALESCE(t.ZMISSING, t.B) AS X, t.ZMISSING FROM T t')
        self.assertEqual(
            rewritten, 'SELECT COALESCE(NULL, t.B) AS X, NULL AS ZMISSING FROM T t')
        self.assertEqual(row['X'], 'present')
        self.assertIsNone(row['ZMISSING'])

    def test_quotes_and_comments_do_not_change_depth(self):
        rewritten, row = self._rewrite_and_fetch(
            "SELECT COALESCE(t.ZMISSING, ')'), t.B FROM T t")
        self.assertEqual(
            rewritten, "SELECT COALESCE(NULL, ')'), t.B FROM T t")
        self.assertEqual(row[0], ')')
        self.assertEqual(row['B'], 'present')

        rewritten, row = self._rewrite_and_fetch(
            "SELECT COALESCE(')', t.ZMISSING, t.B) AS X FROM T t")
        self.assertEqual(
            rewritten, "SELECT COALESCE(')', NULL, t.B) AS X FROM T t")
        self.assertEqual(row['X'], ')')

        rewritten, row = self._rewrite_and_fetch(
            "SELECT 'it''s (' AS S, t.ZMISSING, t.B FROM T t")
        self.assertEqual(
            rewritten, "SELECT 'it''s (' AS S, NULL AS ZMISSING, t.B FROM T t")
        self.assertEqual(row['S'], "it's (")
        self.assertIsNone(row['ZMISSING'])
        self.assertEqual(row['B'], 'present')

        rewritten, row = self._rewrite_and_fetch(
            'SELECT t.B AS "col""(", t.ZMISSING FROM T t')
        self.assertEqual(
            rewritten, 'SELECT t.B AS "col""(", NULL AS ZMISSING FROM T t')
        self.assertEqual(row['col"('], 'present')
        self.assertIsNone(row['ZMISSING'])

        rewritten, row = self._rewrite_and_fetch(
            'SELECT -- (\n t.ZMISSING, t.B FROM T t')
        self.assertEqual(
            rewritten, 'SELECT -- (\n NULL AS ZMISSING, t.B FROM T t')
        self.assertIsNone(row['ZMISSING'])
        self.assertEqual(row['B'], 'present')

        rewritten, row = self._rewrite_and_fetch(
            'SELECT /* ( */ t.ZMISSING, t.B FROM T t')
        self.assertEqual(
            rewritten, 'SELECT /* ( */ NULL AS ZMISSING, t.B FROM T t')
        self.assertIsNone(row['ZMISSING'])
        self.assertEqual(row['B'], 'present')

    def test_longer_identifier_not_rewritten(self):
        with contextlib.closing(sqlite3.connect(self.db_path)) as con:
            con.execute('CREATE TABLE T2(B TEXT, ZMISSING_EXTRA TEXT)')
            con.execute("INSERT INTO T2(B, ZMISSING_EXTRA) VALUES ('present', 'kept')")
            con.commit()

        rewritten, row = self._rewrite_and_fetch(
            'SELECT COALESCE(t.ZMISSING, t.ZMISSING_EXTRA) AS X, t.ZMISSING_EXTRA FROM T2 t')
        self.assertEqual(
            rewritten,
            'SELECT COALESCE(NULL, t.ZMISSING_EXTRA) AS X, t.ZMISSING_EXTRA FROM T2 t')
        self.assertEqual(row['X'], 'kept')
        self.assertEqual(row['ZMISSING_EXTRA'], 'kept')

    def test_subquery_and_cte_select_items_keep_alias(self):
        rewritten, row = self._rewrite_and_fetch(
            'SELECT s.* FROM (SELECT t.ZMISSING FROM T t) s')
        self.assertEqual(
            rewritten, 'SELECT s.* FROM (SELECT NULL AS ZMISSING FROM T t) s')
        self.assertIsNone(row['ZMISSING'])

        rewritten, row = self._rewrite_and_fetch(
            'SELECT s.* FROM (SELECT t.ZMISSING, t.B FROM T t) s')
        self.assertEqual(
            rewritten,
            'SELECT s.* FROM (SELECT NULL AS ZMISSING, t.B FROM T t) s')
        self.assertIsNone(row['ZMISSING'])
        self.assertEqual(row['B'], 'present')

        rewritten, row = self._rewrite_and_fetch(
            'WITH c AS (SELECT t.ZMISSING FROM T t) SELECT * FROM c')
        self.assertEqual(
            rewritten,
            'WITH c AS (SELECT NULL AS ZMISSING FROM T t) SELECT * FROM c')
        self.assertIsNone(row['ZMISSING'])

        rewritten, row = self._rewrite_and_fetch(
            'SELECT s.* FROM (select t.ZMISSING FROM T t) s')
        self.assertEqual(
            rewritten, 'SELECT s.* FROM (select NULL AS ZMISSING FROM T t) s')
        self.assertIsNone(row['ZMISSING'])

        rewritten, row = self._rewrite_and_fetch(
            'SELECT s.* FROM (/* sub */ -- note\n SELECT t.ZMISSING FROM T t) s')
        self.assertEqual(
            rewritten,
            'SELECT s.* FROM (/* sub */ -- note\n SELECT NULL AS ZMISSING FROM T t) s')
        self.assertIsNone(row['ZMISSING'])

    def test_function_inside_subquery_stays_plain_null(self):
        rewritten, row = self._rewrite_and_fetch(
            'SELECT s.X FROM (SELECT COALESCE(t.ZMISSING, t.B) AS X FROM T t) s')
        self.assertEqual(
            rewritten,
            'SELECT s.X FROM (SELECT COALESCE(NULL, t.B) AS X FROM T t) s')
        self.assertEqual(row['X'], 'present')

    def test_error_paths_return_query_unchanged(self):
        missing = os.path.join(self.tmpdir, 'unreadable.sqlite')
        query = 'SELECT t.ZMISSING FROM T t'
        self.assertEqual(ilapfuncs.null_absent_columns(missing, query), query)

        other_error = 'SELECT t.ZMISSING FROM NO_SUCH_TABLE t'
        self.assertEqual(
            ilapfuncs.null_absent_columns(self.db_path, other_error), other_error)


if __name__ == '__main__':
    unittest.main()
