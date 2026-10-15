"""A missing value must reach the timeline as a blank, not as the text None.

timeline() writes every cell as text. str(None) is 'None', so an artifact that
reports a missing date or field as None showed 'None' in the timeline while the
HTML and TSV showed a blank cell, and a row whose first column was None got the
key 'None'.
"""
import json
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ilapfuncs import timeline  # pylint: disable=wrong-import-position


class TestTimelineNone(unittest.TestCase):

    def _run(self, data_list, data_headers):
        with tempfile.TemporaryDirectory() as tmp:
            report_folder = pathlib.Path(tmp) / '_HTML' / 'Artifact'
            report_folder.mkdir(parents=True)
            timeline(str(report_folder), 'Artifact', data_list, data_headers)
            db = sqlite3.connect(pathlib.Path(tmp) / '_Timeline' / 'tl.db')
            try:
                return db.execute('SELECT key, activity, datalist FROM data').fetchall()
            finally:
                db.close()

    def test_none_is_written_blank(self):
        when = datetime(2026, 1, 2, 6, 5, tzinfo=timezone.utc)
        rows = self._run([(None, 'a', None), (when, None, 0)], ('Date', 'Name', 'Count'))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], '')
        self.assertEqual(json.loads(rows[0][2]), {'Date': '', 'Name': 'a', 'Count': ''})
        self.assertEqual(rows[1][0], str(when))
        self.assertEqual(json.loads(rows[1][2]), {'Date': str(when), 'Name': '', 'Count': '0'})

    def test_other_values_are_unchanged(self):
        """Only None changes: empty strings, zero and False keep their text."""
        rows = self._run([('', 0, False, 'None')], ('A', 'B', 'C', 'D'))
        self.assertEqual(rows[0][0], '')
        self.assertEqual(json.loads(rows[0][2]), {'A': '', 'B': '0', 'C': 'False', 'D': 'None'})


if __name__ == '__main__':
    unittest.main()
