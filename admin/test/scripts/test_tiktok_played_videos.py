"""TikTok friends feed and follow feed played-id stores: every account table, both schema versions, TikTok containers only (SYNTHETIC)."""
import datetime
import os
import plistlib
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from scripts.artifacts import tikTokPlayedVideos as module

UNIX = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
OLD = 'awemeId TEXT PRIMARY KEY,scene INTEGER,recordTimeStamp REAL,latestPlayedScene INTEGER,latestPlayedTimeStamp REAL'
NEW = OLD + ',isStory INTEGER,pageType INTEGER,userID TEXT'


class PlayedVideosTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = temp.name

    def container(self, uuid, bundle):
        base = os.path.join(self.root, 'private/var/mobile/Containers/Data/Application', uuid)
        os.makedirs(base)
        meta = os.path.join(base, '.com.apple.mobile_container_manager.metadata.plist')
        with open(meta, 'wb') as handle:
            plistlib.dump({'MCMMetadataIdentifier': bundle}, handle)
        return base, meta

    def friends(self, base, tables):
        path = os.path.join(base, 'Library/Caches/com.friends.feed.deduplicate/record.db')
        os.makedirs(os.path.dirname(path))
        db = sqlite3.connect(path)
        for account, columns, rows in tables:
            db.execute(f'CREATE TABLE playedItemIds_{account}({columns})')
            for row in rows:
                db.execute(f'INSERT INTO playedItemIds_{account} VALUES ({",".join("?" * len(row))})', row)
        db.commit()
        db.close()
        return path

    def run_artifact(self, function, paths):
        context = SimpleNamespace(get_files_found=lambda: paths, get_relative_path=os.path.basename)
        with mock.patch.object(module, 'logfunc'), mock.patch('scripts.artifacts.tikTok.logfunc'):
            return function.__wrapped__(context)

    def test_every_account_table_and_both_schema_versions(self):
        base, meta = self.container('A', 'com.zhiliaoapp.musically')
        store = self.friends(base, [('111', OLD, [('v1', 1, 1700000000.5, 1, 1700000100.0)]),
                                    ('222', NEW, [('v2', 1, 1700000200.0, 1, 1700000200.0, 0, 101, 'u9')])])
        headers, rows, source = self.run_artifact(module.tiktok_friends_feed_played, [meta, store])
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(sorted((r[2], r[3], r[4]) for r in rows), [('v1', '', '111'), ('v2', 'u9', '222')])
        v1 = next(r for r in rows if r[2] == 'v1')
        self.assertEqual(v1[0], UNIX + datetime.timedelta(seconds=1700000100.0))
        self.assertEqual(v1[1], UNIX + datetime.timedelta(seconds=1700000000.5))
        self.assertEqual(source, store)

    def test_another_apps_container_is_not_read(self):
        base, meta = self.container('B', 'com.example.other')
        store = self.friends(base, [('111', OLD, [('v1', 1, 1700000000.0, 1, 1700000000.0)])])
        self.assertEqual(self.run_artifact(module.tiktok_friends_feed_played, [meta, store])[1], [])

    def test_follow_feed_store(self):
        base, meta = self.container('A', 'com.zhiliaoapp.musically')
        path = os.path.join(base, 'Documents/follow_feed/played_videos_recorder.db')
        os.makedirs(os.path.dirname(path))
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE playedItemIds_333(gid TEXT PRIMARY KEY, createTime REAL)')
        db.execute('INSERT INTO playedItemIds_333 VALUES (?, ?)', ('g1', 1700000300.0))
        db.commit()
        db.close()
        _, rows, _ = self.run_artifact(module.tiktok_follow_feed_played, [meta, path, path + '-wal'])
        self.assertEqual(rows, [(UNIX + datetime.timedelta(seconds=1700000300.0), 'g1', '333')])


if __name__ == '__main__':
    unittest.main()
