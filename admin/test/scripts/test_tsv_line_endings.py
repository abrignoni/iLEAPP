"""TSV exports end every row with a single CRLF on every platform (issue #2609).

csv.writer ends each row with '\\r\\n'. tsv() opened the file in text mode without
newline='', so on Windows the '\\n' was translated again and rows ended '\\r\\r\\n'. A CSV
reader then saw an empty row after every row, and a newline inside a cell came back as
'\\r\\n'. On macOS and Linux text mode does not translate, so these tests only fail on
Windows without the fix.
"""
import csv
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs  # pylint: disable=wrong-import-position

HEADERS = ['Timestamp', 'Value', 'Note']
ROWS = [
    ['2026-10-30 10:00:00', 'one', 'line1\nline2'],
    ['2026-10-30 10:01:00', 'two', 'tab\there'],
]


class TsvLineEndingTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.report_folder = os.path.join(self.tmpdir, '_HTML', 'Messages') + os.sep
        os.makedirs(self.report_folder)
        self.path = os.path.join(self.tmpdir, '_TSV Exports', 'Test Table.tsv')

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_rows_end_with_one_crlf(self):
        ilapfuncs.tsv(self.report_folder, HEADERS, ROWS, 'Test Table')
        raw = pathlib.Path(self.path).read_bytes()
        self.assertNotIn(b'\r\r\n', raw)
        self.assertTrue(raw.endswith(b'\r\n'))

    def test_reader_gets_the_rows_back(self):
        ilapfuncs.tsv(self.report_folder, HEADERS, ROWS, 'Test Table')
        with open(self.path, encoding='utf-8-sig', newline='') as fh:
            parsed = list(csv.reader(fh, delimiter='\t'))
        self.assertEqual(parsed, [HEADERS] + ROWS)


if __name__ == '__main__':
    unittest.main()
