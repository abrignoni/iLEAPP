"""snapchatFriendingBadges joins badges to names within one app container (SYNTHETIC stores)."""
import datetime
import os
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from scripts.artifacts import snapchatFriending as module

UNIX = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
BADGE_DDL = ('CREATE TABLE friending_badge_data (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, userID TEXT, '
             'timestamp INTEGER NOT NULL, source TEXT NOT NULL)')
NOTE_DDL = ('CREATE TABLE friending_notification_snapchatter (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, '
            'userId TEXT NOT NULL, mutableName TEXT NOT NULL, displayName TEXT NOT NULL, notificationType INTEGER '
            'NOT NULL, suggestReason TEXT, processingTimestamp REAL NOT NULL)')


class FriendingTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = temp.name

    def container(self, uuid, badges=(), notes=()):
        docs = os.path.join(self.root, 'private/var/mobile/Containers/Data/Application', uuid, 'Documents')
        os.makedirs(os.path.join(docs, 'user_scoped/h/DocObjects'))
        paths = []
        if badges:
            path = os.path.join(docs, 'friending_badge_data.db')
            db = sqlite3.connect(path)
            db.execute(BADGE_DDL)
            db.executemany('INSERT INTO friending_badge_data (userID, timestamp, source) VALUES (?, ?, ?)', badges)
            db.commit()
            db.close()
            paths.append(path)
        if notes:
            path = os.path.join(docs, 'friending_notification_snapchatter.db')
            db = sqlite3.connect(path)
            db.execute(NOTE_DDL)
            db.executemany('INSERT INTO friending_notification_snapchatter (userId, mutableName, displayName, '
                           'notificationType, suggestReason, processingTimestamp) VALUES (?, ?, ?, 0, ?, -1)', notes)
            db.commit()
            db.close()
            paths.append(path)
        doc_store = os.path.join(docs, 'user_scoped/h/DocObjects/primary.docobjects')
        open(doc_store, 'wb').close()
        return paths + [doc_store]

    def run_module(self, paths, snapchatters):
        context = SimpleNamespace(get_files_found=lambda: paths, get_relative_path=os.path.basename)
        lookup = lambda path: snapchatters.get(
            path.replace('\\', '/').split('/Application/')[1].split('/')[0], {})
        with mock.patch.object(module, '_friend_records', side_effect=lookup), mock.patch.object(module, 'logfunc'):
            return module.snapchatFriendingBadges.__wrapped__(context)

    def test_badges_named_from_both_stores_and_a_notification_without_a_badge(self):
        paths = self.container('A', badges=[('u1', 1700000000, 'INCOMING_FRIEND_REQUEST'),
                                            ('u2', 1700000100, 'AVAILABLE_FRIEND_SUGGESTIONS')],
                               notes=[('u2', 'm2', 'Two', 'reason'), ('u3', 'm3', 'Three', None)])
        headers, rows, _ = self.run_module(paths, {'A': {'u1': ('name1', 'One')}})
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0], (UNIX + datetime.timedelta(seconds=1700000000), 'INCOMING_FRIEND_REQUEST', 'u1',
                                   'name1', 'One', '', '', ''))
        self.assertEqual(rows[1][2:], ('u2', '', '', 'Two', 'm2', 'reason'))
        self.assertEqual(rows[2], ('', '', 'u3', '', '', 'Three', 'm3', ''))

    def test_the_doc_store_is_a_source_only_when_it_names_someone(self):
        paths = self.container('A', badges=[('u1', 1700000000, 'INCOMING_FRIEND_REQUEST')])
        doc_store = paths[-1]
        _, _, named = self.run_module(paths, {'A': {'u1': ('name1', 'One')}})
        _, _, unnamed = self.run_module(paths, {})
        self.assertIn(doc_store, named.split('\n'))
        self.assertNotIn(doc_store, unnamed.split('\n'))

    def test_containers_do_not_lend_names_to_each_other(self):
        paths = (self.container('A', badges=[('u1', 1700000000, 'INCOMING_FRIEND_REQUEST')])
                 + self.container('B', notes=[('u1', 'other', 'Other', None)]))
        rows = self.run_module(paths, {'B': {'u1': ('b-name', 'B Display')}})[1]
        a_row = next(r for r in rows if r[1])
        self.assertEqual(a_row[3:], ('', '', '', '', ''))
        self.assertEqual(len(rows), 2)

    def test_a_bad_store_keeps_the_other_container(self):
        good = self.container('A', badges=[('u1', 1700000000, 'INCOMING_FRIEND_REQUEST')])
        bad_dir = os.path.join(self.root, 'private/var/mobile/Containers/Data/Application/C/Documents')
        os.makedirs(bad_dir)
        bad = os.path.join(bad_dir, 'friending_badge_data.db')
        sqlite3.connect(bad).close()
        _, rows, source = self.run_module([bad] + good, {})
        self.assertEqual([r[2] for r in rows], ['u1'])
        self.assertNotIn(bad, source.split('\n'))


if __name__ == '__main__':
    unittest.main()
