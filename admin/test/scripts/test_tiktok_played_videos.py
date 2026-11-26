"""TikTok friends feed and follow feed played-id stores: every account table, both schema versions, TikTok containers only (SYNTHETIC)."""
import datetime
import fnmatch
import os
import shutil
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


class WalOnlyRowsTest(unittest.TestCase):
    """Rows that exist only in the -wal are read, through the artifact's own path patterns (issue 2878)."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = temp.name

    def wal_store(self, relative, ddl, rows):
        """Write a store in WAL mode and copy the main file and -wal before any checkpoint."""
        build = os.path.join(self.root, 'build', os.path.basename(relative))
        os.makedirs(os.path.dirname(build), exist_ok=True)
        db = sqlite3.connect(build)
        self.assertEqual(db.execute('PRAGMA journal_mode=WAL').fetchone()[0], 'wal')
        db.execute('PRAGMA wal_autocheckpoint=0')
        db.execute(ddl)
        db.executemany(f'INSERT INTO playedItemIds_555 VALUES ({",".join("?" * len(rows[0]))})', rows)
        db.commit()
        target = os.path.join(self.root, 'private/var/mobile/Containers/Data/Application/A', relative)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(build, target)
        shutil.copyfile(build + '-wal', target + '-wal')
        db.close()
        return target

    def collect(self, artifact):
        """Every file under the tree that one of the artifact's declared path patterns matches."""
        patterns = module.__artifacts_v2__[artifact]['paths']
        found = []
        for folder, _dirs, files in os.walk(self.root):
            for name in files:
                path = os.path.join(folder, name).replace('\\', '/')
                if any(fnmatch.fnmatch(path, pattern) for pattern in patterns):
                    found.append(path)
        return found

    def run_artifact(self, artifact):
        meta = os.path.join(self.root, 'private/var/mobile/Containers/Data/Application/A',
                            '.com.apple.mobile_container_manager.metadata.plist')
        with open(meta, 'wb') as handle:
            plistlib.dump({'MCMMetadataIdentifier': 'com.zhiliaoapp.musically'}, handle)
        found = self.collect(artifact)
        context = SimpleNamespace(get_files_found=lambda: found, get_relative_path=os.path.basename)
        with mock.patch.object(module, 'logfunc'), mock.patch('scripts.artifacts.tikTok.logfunc'):
            return getattr(module, artifact).__wrapped__(context), found

    def check(self, artifact, relative, ddl, rows):
        store = self.wal_store(relative, ddl, rows)
        main_only = sqlite3.connect(f'file:{store}?mode=ro&immutable=1', uri=True)
        tables = main_only.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table'").fetchone()[0]
        main_only.close()
        self.assertEqual(tables, 0, 'the fixture keeps the table and rows in the -wal only')
        (_headers, result, _source), found = self.run_artifact(artifact)
        wal = store.replace('\\', '/') + '-wal'
        self.assertTrue(wal in found, 'the declared paths collect the -wal')
        self.assertEqual(len(result), len(rows))
        return result

    def test_friends_feed_rows_only_in_the_wal(self):
        rows = self.check('tiktok_friends_feed_played', 'Library/Caches/com.friends.feed.deduplicate/record.db',
                          f'CREATE TABLE playedItemIds_555({OLD})',
                          [('w1', 1, 1700000000.0, 1, 1700000060.0), ('w2', 1, 1700000100.0, 1, 1700000100.0)])
        self.assertEqual(sorted(r[2] for r in rows), ['w1', 'w2'])

    def test_follow_feed_rows_only_in_the_wal(self):
        rows = self.check('tiktok_follow_feed_played', 'Documents/follow_feed/played_videos_recorder.db',
                          'CREATE TABLE playedItemIds_555(gid TEXT PRIMARY KEY, createTime REAL)',
                          [('g1', 1700000300.0), ('g2', 1700000400.0)])
        self.assertEqual(sorted(r[1] for r in rows), ['g1', 'g2'])


if __name__ == '__main__':
    unittest.main()
