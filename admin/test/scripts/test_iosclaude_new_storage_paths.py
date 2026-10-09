"""The Claude artifacts find the storage layout app version 1.261005.20 introduced.

Issue #2411 reports that the app moved its bootstrap JSON from Library/Caches/bootstrap/
to Library/Application Support/accounts/<account>/claude.ai/orgs/<org>/<locale>/, and its
database from Library/Application Support/ClaudeCache/cache_<id>.sqlite to
Library/Application Support/accounts/<account>/claude.ai/orgs/<org>/chat.sqlite. The
paths only matched the old layout, and _cache_databases only kept files named
cache_*.sqlite, so even a matched chat.sqlite was discarded and every artifact stayed
empty.

These tests match the artifact paths with fnmatch against both layouts the way the
seekers do, and run the messages artifact over a chat.sqlite at the new location. The
database here is constructed with the schema the existing queries read; whether the
real chat.sqlite keeps that schema is not established by these tests.
"""
import fnmatch
from pathlib import Path
import sqlite3
import tempfile
import unittest

from scripts.artifacts import iOSclaude as module

CONTAINER = 'root/private/var/mobile/Containers/Data/Application/5E2A1C4B-0F3D-4A8B-9C1E-7D6F2A3B4C5D'
ACCOUNT = CONTAINER + '/Library/Application Support/accounts/8a1f2c3d/claude.ai/orgs/0b9e8d7c'
OLD_BOOTSTRAP = CONTAINER + '/Library/Caches/bootstrap/bootstrap.json'
NEW_BOOTSTRAP = ACCOUNT + '/en-US/bootstrap.json'
OLD_DATABASE = CONTAINER + '/Library/Application Support/ClaudeCache/cache_1234.sqlite'
NEW_DATABASE = ACCOUNT + '/chat.sqlite'


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def matches(artifact, path):
    patterns = module.__artifacts_v2__[artifact]['paths']
    return [p for p in patterns if fnmatch.fnmatchcase(path, p)]


class IOSClaudeNewStoragePathsTest(unittest.TestCase):

    def test_the_bootstrap_paths_match_both_layouts(self):
        self.assertEqual(len(matches('iOSclaudeAccountInfo', OLD_BOOTSTRAP)), 1)
        self.assertEqual(len(matches('iOSclaudeAccountInfo', NEW_BOOTSTRAP)), 1)

    def test_the_database_paths_match_both_layouts_once_each(self):
        for artifact in ('iOSclaudeConversations', 'iOSclaudeMessages', 'iOSclaudeProjects'):
            for path in (OLD_DATABASE, NEW_DATABASE):
                for suffix in ('', '-wal', '-shm'):
                    self.assertEqual(len(matches(artifact, path + suffix)), 1, (artifact, path + suffix))

    def test_the_database_filter_keeps_a_chat_sqlite_once(self):
        files = [NEW_DATABASE + '-wal', NEW_DATABASE, NEW_DATABASE + '-shm',
                 OLD_DATABASE, OLD_DATABASE + '-wal']
        self.assertEqual(module._cache_databases(files), sorted([NEW_DATABASE, OLD_DATABASE]))  # pylint: disable=protected-access

    def test_messages_are_read_from_a_chat_sqlite_at_the_new_location(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / NEW_DATABASE
            path.parent.mkdir(parents=True)
            db = sqlite3.connect(path)
            db.execute('CREATE TABLE messages(createdAT TEXT, content TEXT, files, sender, conversationId)')
            db.execute('CREATE TABLE conversations(id TEXT, name TEXT)')
            db.execute('INSERT INTO conversations VALUES (?,?)', ('c1', 'constructed'))
            db.execute('INSERT INTO messages VALUES (?,?,?,?,?)',
                       ('2026-10-05 12:00:00', '[{"type":"text","text":"hello"}]', '[]', 'human', 'c1'))
            db.commit()
            db.close()

            _, rows, source = module.iOSclaudeMessages.__wrapped__(
                Context(folder, [str(path) + '-wal', str(path)]))

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][1:4], ('human', 'constructed', 'hello'))
            self.assertEqual(rows[0][-1], NEW_DATABASE)
            self.assertEqual(source, str(path))


if __name__ == '__main__':
    unittest.main()
