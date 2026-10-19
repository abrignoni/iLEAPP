"""groupMe: every GroupMe.sqlite is read, so an empty copy cannot hide the populated one.

The iOS 17.3 corpus image holds the store under Library/Application Support with rows
and an empty copy under Documents. Before this test the artifacts read only the first
match, so file order decided whether they reported anything.
"""
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from scripts.artifacts.groupMe import groupMeChats  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

SCHEMA = (
    'CREATE TABLE ZGMCHAT (Z_PK INTEGER PRIMARY KEY, ZCREATEDAT TIMESTAMP, ZUPDATEDAT TIMESTAMP, '
    'ZLASTMESSAGEDATE TIMESTAMP, ZLASTVIEWED TIMESTAMP, ZNAME VARCHAR, ZCHATID VARCHAR, '
    'ZCHATTYPE VARCHAR, ZGROUPTYPE VARCHAR, ZGROUPDESCRIPTION VARCHAR, ZUSERID VARCHAR, '
    'ZCREATORID VARCHAR, ZUNREADCOUNT INTEGER, ZMUTED INTEGER, ZHIDDEN INTEGER, '
    'ZSHAREURL VARCHAR, ZAVATARURL VARCHAR)',
    'CREATE TABLE ZGMMESSAGE (Z_PK INTEGER PRIMARY KEY, ZGROUP INTEGER, ZUSER INTEGER)',
)


def _store(folder, rows):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, 'GroupMe.sqlite')
    con = sqlite3.connect(path)
    for statement in SCHEMA:
        con.execute(statement)
    for pk, name in rows:
        con.execute('INSERT INTO ZGMCHAT (Z_PK, ZCREATEDAT, ZNAME, ZCHATID, ZCHATTYPE) '
                    "VALUES (?, 700000000, ?, ?, 'group')", (pk, name, f'chat{pk}'))
    con.commit()
    con.close()
    return path


class GroupMeStoresTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Context.clear()
        Context.set_report_folder(self.tmpdir)
        app = os.path.join(self.tmpdir, 'mobile', 'Containers', 'Data', 'Application', 'UUID')
        self.empty = _store(os.path.join(app, 'Documents'), [])
        self.populated = _store(os.path.join(app, 'Library', 'Application Support'),
                                [(1, 'Synthetic Group'), (2, 'Synthetic Direct')])

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run(self, files):
        Context.set_files_found(files)
        return groupMeChats.__wrapped__(Context)

    def test_file_order_does_not_decide_the_output(self):
        empty_first = self._run([self.empty, self.populated])
        populated_first = self._run([self.populated, self.empty])
        self.assertEqual(len(empty_first[1]), 2)
        self.assertEqual(empty_first[1], populated_first[1])

    def test_each_row_names_its_store_and_every_store_is_listed(self):
        headers, rows, source = self._run([self.empty, self.populated])
        self.assertEqual(headers[-1], 'Source File')
        self.assertTrue(all(row[-1].endswith(os.path.join('Application Support', 'GroupMe.sqlite'))
                            for row in rows))
        self.assertEqual(sorted(source.split('\n')), sorted([self.empty, self.populated]))

    def test_sidecars_and_appledouble_files_are_not_stores(self):
        folder = os.path.dirname(self.populated)
        extra = [os.path.join(folder, name) for name in ('GroupMe.sqlite-wal', '._GroupMe.sqlite')]
        _, rows, source = self._run([self.populated] + extra)
        self.assertEqual(len(rows), 2)
        self.assertEqual(source, self.populated)


if __name__ == '__main__':
    unittest.main()
