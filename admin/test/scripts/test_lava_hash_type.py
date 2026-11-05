"""The 'hash' header type: a TEXT column LAVA sorts as text ignoring case.

Untyped text sorts in LAVA with the UINT collation, which reads the digit runs inside a
value as numbers, so hex digests and UUIDs come out in an order that looks random. A header
declared ('SHA-256', 'hash') is stored as TEXT exactly as written, and the type travels in
the manifest's object_columns, which is what LAVA reads to sort the column as text instead.
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


class TestLavaHashType(unittest.TestCase):

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
        headers = [('SHA-256', 'hash'), 'Note']
        table_name, column_map, object_columns = lavafuncs.lava_create_sqlite_table('hash_artifact', headers)
        lavafuncs.lava_insert_sqlite_data(table_name, rows, object_columns, headers, column_map)
        return table_name, object_columns

    def test_hash_maps_to_text(self):
        self.assertEqual(lavafuncs.get_sql_type('hash'), 'TEXT')

    def test_column_is_text_and_listed_as_typed(self):
        table_name, object_columns = self._write([('00ab', 'a')])
        declared = {row[1]: row[2] for row in lavafuncs.lava_db.execute(f'PRAGMA table_info("{table_name}")')}
        self.assertEqual(declared['sha256'], 'TEXT')
        self.assertEqual(declared['note'], 'TEXT')
        self.assertEqual(object_columns, {'sha256': 'hash'})

    def test_values_are_stored_as_written(self):
        rows = [('007E', 'leading zeros'), ('0A0B', 'upper case'), ('0a0b', 'lower case'),
                ('05AA9323-6731-4629-B9AF-E2AC66E4FB93', 'uuid'), ('123', 'digits only'), (None, 'null')]
        table_name, _ = self._write(rows)
        stored = lavafuncs.lava_db.execute(
            f'SELECT "sha256", typeof("sha256") FROM "{table_name}" ORDER BY rowid').fetchall()
        self.assertEqual(stored, [('007E', 'text'), ('0A0B', 'text'), ('0a0b', 'text'),
                                  ('05AA9323-6731-4629-B9AF-E2AC66E4FB93', 'text'), ('123', 'text'),
                                  (None, 'null')])


if __name__ == '__main__':
    unittest.main()
