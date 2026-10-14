"""Pin how the Safari history artifacts read History.db's tag tables.

history_tags holds one row per tag and history_items_to_tags links a tag to a history item.
Safari Browser - History shows an item's tags on each of its visits, and Safari Browser -
History Tags lists one row per link plus one row for a tag no link names. A database
without the two tables (iOS 12.4 has neither) still reports its visits. Item and tag ids
repeat between the main database and a profile's, so each file is read on its own.
Profile Name is the title SafariTabs.db stores for the profile directory a History.db is in.

Every value here is written for the test. The two tag tables use the CREATE TABLE text
Safari wrote on the tested images; the expected rows are written out, never read back from
the module.
"""
import fnmatch
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs  # pylint: disable=wrong-import-position
from scripts.artifacts import safariHistory  # pylint: disable=wrong-import-position

MAIN = 'private/var/mobile/Library/Safari/History.db'
PROFILE = 'private/var/mobile/Library/Safari/Profiles/WORK/History.db'
# The layout of the one tested image that holds a named profile: the profile directory is in
# the Safari app's data container and SafariTabs.db is under mobile/Library/Safari.
APP_PROFILE = ('private/var/mobile/Containers/Data/Application/APP-GUID/Library/Safari/Profiles/'
               '7B994837-CA41-466F-9280-21E7A8BF000B/History.db')
TABS = 'private/var/mobile/Library/Safari/SafariTabs.db'
# bookmarks as far as the name lookup reads it: (title, server_id, external_uuid).
PROFILE_ROWS = (('', 'DefaultProfile', 'DefaultProfile'),
                ('Pro', 'F548B279-8127-4504-82FF-B4EC2B0A2389',
                 '7B994837-CA41-466F-9280-21E7A8BF000B'))

BASE_TABLES = (
    'CREATE TABLE history_items (id INTEGER PRIMARY KEY, url TEXT NOT NULL UNIQUE, '
    'visit_count INTEGER NOT NULL)',
    'CREATE TABLE history_visits (id INTEGER PRIMARY KEY, history_item INTEGER NOT NULL, '
    'visit_time REAL NOT NULL, title TEXT NULL, redirect_source INTEGER NULL, '
    'redirect_destination INTEGER NULL, origin INTEGER NOT NULL DEFAULT 0)',
)
TAG_TABLES = (
    'CREATE TABLE history_tags (id INTEGER PRIMARY KEY,type INTEGER NOT NULL,level INTEGER NOT NULL,'
    'identifier TEXT NOT NULL,title TEXT NOT NULL,modification_timestamp REAL NOT NULL,'
    'item_count INTEGER NOT NULL DEFAULT 0)',
    'CREATE TABLE history_items_to_tags (history_item INTEGER NOT NULL,tag_id INTEGER NOT NULL,'
    'timestamp REAL NOT NULL,FOREIGN KEY(tag_id) REFERENCES history_tags(id) ON DELETE CASCADE,'
    'FOREIGN KEY(history_item) REFERENCES history_items(id) ON DELETE CASCADE,'
    'UNIQUE(history_item, tag_id) ON CONFLICT REPLACE)',
)

ITEMS = ((1, 'https://one.example/', 2), (2, 'https://two.example/', 1),
         (3, 'https://three.example/', 1))
# 700000000 seconds after 2001-01-01 is 2023-03-08 20:26:40 UTC.
VISITS = ((1, 1, 700000000.0, 'One'), (2, 1, 700000100.0, 'One again'),
          (3, 2, 700000200.0, 'Two'), (4, 3, 700000300.0, 'Three'))
# The stored item count of the first tag is higher than its links, and the third tag has a
# stored count above zero and no link at all.
TAGS = ((1, 1, 200, 'Q1001', 'Alpha', 700000205.5, 3), (2, 1, 200, 'Q1002', 'Beta', 700000110.0, 1),
        (3, 1, 200, 'Q1003', 'Gamma', 690000000.0, 2))
LINKS = ((1, 1, 700000010.0), (2, 1, 700000205.5), (1, 2, 700000110.0))

# A profile's database reuses item id 1 and tag id 1 for a different page and tag.
PROFILE_ITEMS = ((1, 'https://work.example/', 1),)
PROFILE_VISITS = ((1, 1, 700000500.0, 'Work'),)
PROFILE_TAGS = ((1, 1, 200, 'Q2001', 'Delta', 700000510.0, 1),)
PROFILE_LINKS = ((1, 1, 700000510.0),)


class SafariHistoryTagsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.files = []
        self.logged = []

    def tearDown(self):
        self._tmp.cleanup()

    def _store(self, relative, items=ITEMS, visits=VISITS, tags=TAGS, links=LINKS):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        database = sqlite3.connect(path)
        for statement in BASE_TABLES + (TAG_TABLES if tags is not None else ()):
            database.execute(statement)
        database.executemany('INSERT INTO history_items VALUES (?,?,?)', items)
        database.executemany(
            'INSERT INTO history_visits (id, history_item, visit_time, title) VALUES (?,?,?,?)', visits)
        if tags is not None:
            database.executemany('INSERT INTO history_tags VALUES (?,?,?,?,?,?,?)', tags)
            database.executemany('INSERT INTO history_items_to_tags VALUES (?,?,?)', links)
        database.commit()
        database.close()
        self.files.append(str(path))

    def _run(self, processor):
        context = SimpleNamespace(
            get_files_found=lambda: list(self.files),
            get_relative_path=lambda p: pathlib.Path(p).relative_to(self.root).as_posix())
        with mock.patch.object(ilapfuncs, 'logfunc') as log:
            headers, rows, source = processor.__wrapped__(context)
        self.logged = [call.args[0] for call in log.call_args_list]
        return headers, [tuple(row) for row in rows], source

    def test_a_visit_shows_the_tags_of_its_item_in_link_order(self):
        self._store(MAIN)
        headers, rows, source = self._run(safariHistory.safariHistory)
        self.assertEqual(headers[-4:], ('Tags', 'Tag Identifiers', 'Profile', 'Profile Name'))
        self.assertEqual({row[11] for row in rows}, {''})
        self.assertEqual(
            [(row[0], row[2], row[8], row[9], row[10]) for row in rows],
            [('2023-03-08 20:26:40', 'https://one.example/', 'Alpha; Beta', 'Q1001; Q1002', 'Default'),
             ('2023-03-08 20:28:20', 'https://one.example/', 'Alpha; Beta', 'Q1001; Q1002', 'Default'),
             ('2023-03-08 20:30:00', 'https://two.example/', 'Alpha', 'Q1001', 'Default'),
             ('2023-03-08 20:31:40', 'https://three.example/', '', '', 'Default')])
        self.assertEqual(source, MAIN)

    def test_tags_are_listed_per_link_and_once_when_no_link_names_them(self):
        self._store(MAIN)
        headers, rows, source = self._run(safariHistory.safariHistoryTags)
        self.assertEqual(
            headers,
            (('Tag Modified', 'datetime'), ('Item Tagged', 'datetime'), 'Tag', 'Identifier', 'URL',
             'Item Count', 'Linked Items', 'Type', 'Level', 'Profile', 'Profile Name'))
        self.assertEqual(rows, [
            ('2022-11-13 02:40:00', None, 'Gamma', 'Q1003', '', 2, 0, 1, 200, 'Default', ''),
            ('2023-03-08 20:28:30', '2023-03-08 20:28:30', 'Beta', 'Q1002', 'https://one.example/',
             1, 1, 1, 200, 'Default', ''),
            ('2023-03-08 20:30:05', '2023-03-08 20:26:50', 'Alpha', 'Q1001', 'https://one.example/',
             3, 2, 1, 200, 'Default', ''),
            ('2023-03-08 20:30:05', '2023-03-08 20:30:05', 'Alpha', 'Q1001', 'https://two.example/',
             3, 2, 1, 200, 'Default', '')])
        self.assertEqual(source, MAIN)

    def test_a_database_without_the_tag_tables_still_reports_its_visits(self):
        self._store(MAIN, tags=None)
        _headers, rows, source = self._run(safariHistory.safariHistory)
        self.assertEqual([(row[2], row[8], row[9]) for row in rows],
                         [('https://one.example/', '', ''), ('https://one.example/', '', ''),
                          ('https://two.example/', '', ''), ('https://three.example/', '', '')])
        self.assertEqual(source, MAIN)
        # The missing tables are not queried, so the run log carries no SQLite error for them.
        self.assertEqual(self.logged, [])
        _headers, rows, source = self._run(safariHistory.safariHistoryTags)
        self.assertEqual(rows, [])
        self.assertEqual(source, MAIN)
        self.assertEqual(self.logged, [])

    def test_a_profile_database_keeps_its_own_tags(self):
        self._store(MAIN)
        self._store(PROFILE, items=PROFILE_ITEMS, visits=PROFILE_VISITS, tags=PROFILE_TAGS,
                    links=PROFILE_LINKS)
        _headers, rows, source = self._run(safariHistory.safariHistory)
        self.assertEqual(
            [(row[2], row[8], row[9], row[10]) for row in rows],
            [('https://one.example/', 'Alpha; Beta', 'Q1001; Q1002', 'Default'),
             ('https://one.example/', 'Alpha; Beta', 'Q1001; Q1002', 'Default'),
             ('https://two.example/', 'Alpha', 'Q1001', 'Default'),
             ('https://three.example/', '', '', 'Default'),
             ('https://work.example/', 'Delta', 'Q2001', 'WORK')])
        self.assertEqual(source, f'{MAIN}\n{PROFILE}')
        _headers, rows, _source = self._run(safariHistory.safariHistoryTags)
        self.assertEqual([(row[2], row[4], row[9]) for row in rows],
                         [('Gamma', '', 'Default'), ('Beta', 'https://one.example/', 'Default'),
                          ('Alpha', 'https://one.example/', 'Default'),
                          ('Alpha', 'https://two.example/', 'Default'),
                          ('Delta', 'https://work.example/', 'WORK')])

    def _tabs(self, relative, rows=PROFILE_ROWS, columns='title TEXT, server_id TEXT, external_uuid TEXT'):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        database = sqlite3.connect(path)
        database.execute(f'CREATE TABLE bookmarks (id INTEGER PRIMARY KEY, {columns})')
        if 'external_uuid' in columns:
            database.executemany(
                'INSERT INTO bookmarks (title, server_id, external_uuid) VALUES (?,?,?)', rows)
        database.commit()
        database.close()
        self.files.append(str(path))

    def _profile(self, relative=APP_PROFILE):
        self._store(relative, items=PROFILE_ITEMS, visits=PROFILE_VISITS, tags=PROFILE_TAGS,
                    links=PROFILE_LINKS)

    def test_the_declared_paths_match_the_tabs_database_and_its_sidecars(self):
        for artifact in ('safariHistory', 'safariHistoryTags'):
            paths = safariHistory.__artifacts_v2__[artifact]['paths']
            for name in (MAIN, PROFILE, APP_PROFILE, TABS, TABS + '-wal', TABS + '-shm'):
                self.assertTrue(any(fnmatch.fnmatchcase(name, pattern) for pattern in paths),
                                (artifact, name))

    def test_a_profile_is_named_from_the_tabs_database(self):
        self._store(MAIN)
        self._profile()
        self._tabs(TABS)
        _headers, rows, source = self._run(safariHistory.safariHistory)
        self.assertEqual(
            sorted({(row[10], row[11]) for row in rows}),
            [('7B994837-CA41-466F-9280-21E7A8BF000B', 'Pro'), ('Default', '')])
        # SafariTabs.db is read for the names and is not a source of rows.
        self.assertEqual(source, f'{MAIN}\n{APP_PROFILE}')
        _headers, rows, _source = self._run(safariHistory.safariHistoryTags)
        self.assertEqual(
            sorted({(row[9], row[10]) for row in rows}),
            [('7B994837-CA41-466F-9280-21E7A8BF000B', 'Pro'), ('Default', '')])

    def test_a_directory_named_in_server_id_is_named_as_well(self):
        self._profile(APP_PROFILE.replace('7B994837-CA41-466F-9280-21E7A8BF000B',
                                          'F548B279-8127-4504-82FF-B4EC2B0A2389'))
        self._tabs(TABS)
        _headers, rows, _source = self._run(safariHistory.safariHistory)
        self.assertEqual({row[11] for row in rows}, {'Pro'})

    def test_two_extractions_each_name_their_own_profile(self):
        for folder, title in (('one', 'First'), ('two', 'Second')):
            self._profile(f'{folder}/{APP_PROFILE}')
            self._tabs(f'{folder}/{TABS}', rows=((title, 'OTHER', '7B994837-CA41-466F-9280-21E7A8BF000B'),))
        _headers, rows, _source = self._run(safariHistory.safariHistory)
        self.files.reverse()
        _headers, reversed_rows, _source = self._run(safariHistory.safariHistory)
        for found in (rows, reversed_rows):
            self.assertEqual(sorted(row[11] for row in found), ['First', 'Second'])

    def test_a_profile_no_row_names_shows_no_name(self):
        self._profile()
        _headers, rows, _source = self._run(safariHistory.safariHistory)
        self.assertEqual({row[11] for row in rows}, {''})
        self._tabs(TABS, rows=PROFILE_ROWS[:1])
        _headers, rows, _source = self._run(safariHistory.safariHistory)
        self.assertEqual({row[11] for row in rows}, {''})

    def test_the_main_database_is_never_named(self):
        # The directory above the main History.db is Safari; a row naming it is not a profile.
        self._store(MAIN)
        self._tabs(TABS, rows=(('Not a profile', 'Safari', 'Library'),))
        _headers, rows, _source = self._run(safariHistory.safariHistory)
        self.assertEqual({(row[10], row[11]) for row in rows}, {('Default', '')})

    def test_a_tabs_database_without_the_columns_is_not_queried(self):
        self._profile()
        self._tabs(TABS, columns='title TEXT')
        _headers, rows, _source = self._run(safariHistory.safariHistory)
        self.assertEqual({row[11] for row in rows}, {''})
        self.assertEqual(self.logged, [])


if __name__ == '__main__':
    unittest.main()
