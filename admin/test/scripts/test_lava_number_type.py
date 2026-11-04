"""The 'number' header type: a NUMERIC column, so LAVA sorts it as numbers.

Untyped headers are TEXT, so a column of row numbers or process ids sorts 1, 10, 100, 2.
A header declared ('Count', 'number') gets NUMERIC affinity: values that read as numbers
are stored as INTEGER or REAL and anything else stays as written text. NUMERIC also
rewrites the written form of what it converts ('007' is stored as 7), so the type belongs
on columns that are numbers by nature, not on identifiers or codes.
"""
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position


class TestLavaNumberType(unittest.TestCase):

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

    def _write(self, rows):
        headers = [('Count', 'number'), 'Note']
        table_name, column_map, object_columns = lavafuncs.lava_create_sqlite_table('number_artifact', headers)
        lavafuncs.lava_insert_sqlite_data(table_name, rows, object_columns, headers, column_map)
        return table_name, object_columns

    def test_number_maps_to_numeric(self):
        self.assertEqual(lavafuncs.get_sql_type('number'), 'NUMERIC')
        self.assertEqual(lavafuncs.get_sql_type('datetime'), 'INTEGER')
        self.assertEqual(lavafuncs.get_sql_type('date'), 'TEXT')
        self.assertEqual(lavafuncs.get_sql_type('phonenumber'), 'TEXT')

    def test_column_is_declared_numeric_and_listed_as_typed(self):
        table_name, object_columns = self._write([('1', 'a')])
        declared = {row[1]: row[2] for row in lavafuncs.lava_db.execute(f'PRAGMA table_info("{table_name}")')}
        self.assertEqual(declared['count'], 'NUMERIC')
        self.assertEqual(declared['note'], 'TEXT')
        self.assertEqual(object_columns, {'count': 'number'})

    def test_numbers_sort_as_numbers(self):
        table_name, _ = self._write([('10', 'a'), ('2', 'b'), (100, 'c'), (2.5, 'd'), ('-5', 'e'), ('1', 'f')])
        ordered = [row[0] for row in lavafuncs.lava_db.execute(f'SELECT "count" FROM "{table_name}" ORDER BY "count"')]
        self.assertEqual(ordered, [-5, 1, 2, 2.5, 10, 100])

    def test_what_numeric_storage_keeps_and_rewrites(self):
        rows = [('007', 'leading zeros'), ('1,234', 'thousands separator'), ('0x1F', 'hex'),
                ('12abc', 'text'), ('', 'empty'), (None, 'null')]
        table_name, _ = self._write(rows)
        stored = lavafuncs.lava_db.execute(
            f'SELECT "count", typeof("count") FROM "{table_name}" ORDER BY rowid').fetchall()
        self.assertEqual(stored, [(7, 'integer'), ('1,234', 'text'), ('0x1F', 'text'),
                                  ('12abc', 'text'), ('', 'text'), (None, 'null')])


if __name__ == '__main__':
    unittest.main()
