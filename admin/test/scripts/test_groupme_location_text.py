"""GroupMe location columns read the same on every SQLite version, in attachment order.

groupMeMessages joined each message's location latitudes, longitudes and venue names with
three GROUP_CONCAT subqueries. SQLite turned each float into text itself, and that text
depends on the library: 15 significant digits through 3.51, 17 from 3.52. GROUP_CONCAT
also promises no order, so the nth latitude and the nth venue need not have belonged to
one attachment. These tests read a constructed store with two location attachments on one
message.
"""
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import groupMe  # pylint: disable=wrong-import-position


class GroupMeLocationTextTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = str(pathlib.Path(self.tmpdir, 'GroupMe.sqlite'))
        db = sqlite3.connect(self.path)
        db.execute('CREATE TABLE ZGMATTACHMENT (Z_PK INTEGER PRIMARY KEY, ZMESSAGE INTEGER, '
                   'ZTYPE TEXT, ZLAT REAL, ZLNG REAL, ZVENUENAME TEXT)')
        db.executemany('INSERT INTO ZGMATTACHMENT VALUES (?,?,?,?,?,?)', [
            (12, 7, 'location', 38.778645041716885, -77.21797596106694, 'Second'),
            (11, 7, 'location', 35.661225944880535, -78.87916778107541, 'First'),
            (13, 7, 'image', 0.0, 0.0, None),
            (14, 8, 'location', 35.66298937679041, -78.88271144766435, None),
        ])
        db.commit()
        db.close()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_coordinates_are_python_text_in_attachment_order(self):
        locations = groupMe._locations_by_message(self.path)  # pylint: disable=protected-access

        self.assertEqual(locations[7], ('35.661225944880535, 38.778645041716885',
                                        '-78.87916778107541, -77.21797596106694',
                                        'First, Second'))
        self.assertEqual(locations[8], ('35.66298937679041', '-78.88271144766435', None))
        self.assertEqual(set(locations), {7, 8})


if __name__ == '__main__':
    unittest.main()
