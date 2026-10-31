"""The logarchive artifact reads a 'log show' json export without writing to it.

rows_from_json used to cut off anything after the last ']' by truncating the file in place.
That file is the staged copy the report keeps in its data folder and presents as the source,
so the run changed its size, bytes and hash. These tests check the export is read up to that
bracket, as before, and that the file is unchanged afterwards.
"""
import hashlib
import json
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import logarchive  # pylint: disable=wrong-import-position

RECORDS = [
    {'timestamp': '2026-03-14 10:00:00.100000-0500', 'processImagePath': '/usr/libexec/one',
     'processID': 11, 'subsystem': 'com.example.one', 'category': 'general',
     'eventMessage': 'first', 'traceID': 1},
    {'timestamp': '2026-03-14 10:00:01.250000-0500', 'processImagePath': '/usr/libexec/two',
     'processID': 22, 'subsystem': 'com.example.two', 'category': 'general',
     'eventMessage': 'second ] with a bracket', 'traceID': 2},
]


class LogarchiveJsonReadOnlyTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, 'logarchive.json')

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def write(self, data):
        with open(self.path, 'wb') as f:
            f.write(data)
        with open(self.path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def rows(self):
        return list(logarchive.rows_from_json(self.path))

    def test_text_after_the_array_is_ignored_and_the_file_is_unchanged(self):
        digest = self.write(json.dumps(RECORDS).encode() + b'\nlog: 2 entries shown\n')

        rows = self.rows()

        self.assertEqual([row[6] for row in rows], ['first', 'second ] with a bracket'])
        self.assertEqual([row[1] for row in rows], [1, 2])
        with open(self.path, 'rb') as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), digest)

    def test_a_clean_export_reads_whole_and_is_unchanged(self):
        digest = self.write(json.dumps(RECORDS).encode())

        self.assertEqual(len(self.rows()), 2)
        with open(self.path, 'rb') as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), digest)

    def test_trailing_text_longer_than_one_scan_chunk_is_found(self):
        self.write(json.dumps(RECORDS).encode() + b'x' * 200000)

        self.assertEqual(len(self.rows()), 2)
        self.assertEqual(os.path.getsize(self.path), len(json.dumps(RECORDS)) + 200000)


if __name__ == '__main__':
    unittest.main()
