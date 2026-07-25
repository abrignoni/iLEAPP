"""Guard the LAVA writer against artifact names that are hostile to SQL or to the filesystem.

The LAVA writer turns each artifact's data_headers into SQLite column names. Those
identifiers used to be interpolated into CREATE TABLE and INSERT statements unquoted, so
any header that sanitizes down to a reserved word ('From', 'To', 'Order', ...) killed the
artifact at report time with `near "from": syntax error`. The parser itself ran fine, so
the only symptom was a LAVA table that silently never appeared, and
admin/test/scripts/test_module.py mocks the LAVA database connection, so module-level
testing passes either way. Module authors hit this three times in one day and worked
around it by renaming columns.

The same class of trap exists for a '/' in an artifact name or category: those become
HTML/TSV/KML filenames and _HTML folder names, and os.path.join() reads the '/' as a path
separator, so the artifact either fails to write its report or lands somewhere unintended.
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
from scripts.ilapfuncs import sanitize_report_name  # pylint: disable=wrong-import-position

# Reserved words an artifact could plausibly want as a column heading. 'From' and 'To' are
# the ones that actually bit (mastodon notifications, Apple Mail); the rest are the same
# hazard waiting for the next module.
RESERVED_HEADERS = [
    'From', 'To', 'Order', 'Group', 'Index', 'Select', 'Where', 'Table',
    'Values', 'Default', 'Check', 'References', 'Limit', 'Join', 'Set', 'Action',
]


class TestLavaReservedWordIdentifiers(unittest.TestCase):
    """The LAVA SQLite writer must quote identifiers so reserved words are usable."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')

    def tearDown(self):
        if lavafuncs.lava_db is not None:
            lavafuncs.lava_db.close()
            lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _fetch_rows(self, table_name):
        cursor = lavafuncs.lava_db.cursor()
        return cursor.execute(f'SELECT * FROM "{table_name}"').fetchall()

    def test_reserved_words_are_hostile_unquoted(self):
        """Documents why RESERVED_HEADERS is the corpus: unquoted, these really do fail."""
        db = sqlite3.connect(':memory:')
        offenders = []
        for header in RESERVED_HEADERS:
            column = lavafuncs.sanitize_sql_name(header)
            try:
                db.execute(f'CREATE TABLE t_{column} ({column} TEXT)')
            except sqlite3.OperationalError:
                offenders.append(header)
        db.close()
        self.assertIn('From', offenders)
        self.assertIn('Order', offenders)
        self.assertGreaterEqual(
            len(offenders), 5,
            'Test corpus no longer exercises the bug; add headers SQLite rejects unquoted.')

    def test_create_table_accepts_reserved_word_headers(self):
        table_name, column_map, object_columns = lavafuncs.lava_create_sqlite_table(
            'reserved_word_artifact', RESERVED_HEADERS)

        self.assertEqual(table_name, 'reserved_word_artifact')
        self.assertEqual(object_columns, {})
        self.assertEqual(
            [column_map[lavafuncs.sanitize_sql_name(h)] for h in RESERVED_HEADERS],
            RESERVED_HEADERS)

        cursor = lavafuncs.lava_db.cursor()
        columns = [row[1] for row in cursor.execute(f'PRAGMA table_info("{table_name}")')]
        self.assertEqual(columns, [lavafuncs.sanitize_sql_name(h) for h in RESERVED_HEADERS])

    def test_insert_populates_reserved_word_columns(self):
        table_name, column_map, object_columns = lavafuncs.lava_create_sqlite_table(
            'reserved_word_artifact', RESERVED_HEADERS)
        rows = [
            tuple(f'{header}-row1' for header in RESERVED_HEADERS),
            tuple(f'{header}-row2' for header in RESERVED_HEADERS),
        ]

        lavafuncs.lava_insert_sqlite_data(
            table_name, rows, object_columns, RESERVED_HEADERS, column_map)

        self.assertEqual(self._fetch_rows(table_name), rows)

        # Values must land in the column they were written for, not just somewhere.
        cursor = lavafuncs.lava_db.cursor()
        self.assertEqual(
            cursor.execute(f'SELECT "from", "order" FROM "{table_name}"').fetchall(),
            [('From-row1', 'Order-row1'), ('From-row2', 'Order-row2')])

    def test_reserved_word_table_name(self):
        """A module function named e.g. order() makes the table name reserved too."""
        table_name, column_map, object_columns = lavafuncs.lava_create_sqlite_table(
            'Order', ['From', 'Timestamp'])

        self.assertEqual(table_name, 'order')
        lavafuncs.lava_insert_sqlite_data(
            table_name, [('sender', 'ts')], object_columns, ['From', 'Timestamp'], column_map)
        self.assertEqual(self._fetch_rows(table_name), [('sender', 'ts')])

    def test_typed_headers_with_reserved_words(self):
        """Tuple headers take the typed CREATE TABLE branch, which needs quoting too."""
        headers = [('From', 'datetime'), ('Order', 'datetime'), 'Group']
        table_name, column_map, object_columns = lavafuncs.lava_create_sqlite_table(
            'typed_reserved_artifact', headers)

        self.assertEqual(object_columns, {'from': 'datetime', 'order': 'datetime'})

        timestamp = datetime.datetime(2026, 7, 25, 12, 0, tzinfo=datetime.timezone.utc)
        lavafuncs.lava_insert_sqlite_data(
            table_name, [(timestamp, timestamp, 'a group')], object_columns, headers, column_map)

        self.assertEqual(
            self._fetch_rows(table_name),
            [(int(timestamp.timestamp()), int(timestamp.timestamp()), 'a group')])

    def test_process_artifact_end_to_end(self):
        """The path artifact_processor actually takes, headers and all."""
        Context.set_artifact_info({'name': 'Reserved Words', 'description': 'test artifact'})
        # Only the basename is read, so this path never has to exist. Keeping it synthetic
        # lets the same test file be shared across the LEAPP tools unchanged.
        Context.set_module_file_path(str(REPO_ROOT / 'scripts' / 'artifacts' / 'reserved_words.py'))

        table_name, object_columns, column_map = lavafuncs.lava_process_artifact(
            'Testing', 'reserved_words_module', 'Reserved Words', RESERVED_HEADERS,
            record_count=1, func_name='reserved_words')
        lavafuncs.lava_insert_sqlite_data(
            table_name,
            [tuple(f'{header}-value' for header in RESERVED_HEADERS)],
            object_columns, RESERVED_HEADERS, column_map)

        self.assertEqual(table_name, 'reserved_words')
        self.assertEqual(len(self._fetch_rows(table_name)), 1)
        artifact = lavafuncs.lava_data['artifacts']['Testing'][0]
        self.assertEqual(artifact['tablename'], 'reserved_words')
        self.assertEqual(artifact['record_count'], 1)


class TestQuoteSqlName(unittest.TestCase):
    """quote_sql_name() must not be escapable by whatever ends up in a header."""

    def test_wraps_in_double_quotes(self):
        self.assertEqual(lavafuncs.quote_sql_name('from'), '"from"')

    def test_doubles_embedded_quotes(self):
        self.assertEqual(lavafuncs.quote_sql_name('a"b'), '"a""b"')

    def test_embedded_quote_is_a_usable_identifier(self):
        # sanitize_sql_name() strips quotes today, so this only guards quote_sql_name()
        # itself against a future caller that skips sanitizing.
        db = sqlite3.connect(':memory:')
        column = lavafuncs.quote_sql_name('odd"name')
        db.execute(f'CREATE TABLE t ({column} TEXT)')
        db.execute(f'INSERT INTO t ({column}) VALUES (?)', ('value',))
        self.assertEqual(db.execute('SELECT * FROM t').fetchall(), [('value',)])
        db.close()


class TestSanitizeReportName(unittest.TestCase):
    """Artifact names and categories become file and folder names."""

    def test_leaves_ordinary_names_alone(self):
        # Existing artifact names must keep producing byte-identical output paths.
        for name in ['SMS & iMessage', "Apple Maps", 'Twitter X - Direct Messages']:
            self.assertEqual(sanitize_report_name(name), name)

    def test_replaces_path_separators(self):
        self.assertEqual(sanitize_report_name('Twitter/X'), 'Twitter_X')
        self.assertEqual(sanitize_report_name('Foo\\Bar'), 'Foo_Bar')

    def test_result_is_a_single_path_component(self):
        import os
        safe_name = sanitize_report_name('Twitter/X - Cached Posts')
        self.assertEqual(os.path.basename(safe_name), safe_name)
        self.assertEqual(os.path.dirname(safe_name), '')

    def test_no_shipped_artifact_needs_sanitizing(self):
        """Nothing in scripts/artifacts should rely on the fallback."""
        import re
        offenders = []
        pattern = re.compile(r"^\s*'(name|category)':\s*(['\"])(.*?)\2", re.MULTILINE)
        for py_file in sorted((REPO_ROOT / 'scripts' / 'artifacts').glob('*.py')):
            source = py_file.read_text(encoding='utf-8', errors='replace')
            for _, _, value in pattern.findall(source):
                if '/' in value or '\\' in value:
                    offenders.append(f'{py_file.name}: {value}')
        self.assertEqual(
            offenders, [],
            'Artifact name/category contains a path separator; the report file name will '
            'not match the displayed name:\n' + '\n'.join(offenders))


if __name__ == '__main__':
    unittest.main()
