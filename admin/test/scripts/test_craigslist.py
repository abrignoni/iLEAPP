"""Craigslist artifacts against the synthetic fixture, and against the shapes a real container can lack.

The fixture (synthetic_craigslist.py) is fabricated; no value here comes from a device.
"""
import fnmatch
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import tempfile
import types
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from scripts.artifacts import craigslist
from scripts.context import Context
from scripts.search_files import FileInfo

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('synthetic_craigslist', HERE / 'synthetic_craigslist.py')
FIXTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURE)

ARTIFACTS = {
    'recent_searches': craigslist.craigslist_recent_searches,
    'visited_postings': craigslist.craigslist_visited_postings,
    'saved_items': craigslist.craigslist_saved_items,
    'account_state': craigslist.craigslist_account_state,
    'startup_log': craigslist.craigslist_startup_log,
    'cached_searches': craigslist.craigslist_cached_searches,
    'cached_postings': craigslist.craigslist_cached_postings,
}
UTC = timezone.utc


class CraigslistBase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)
        patcher = mock.patch.object(craigslist, 'logfunc')
        self.log = patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(Context.clear)

    def extract(self, zip_path):
        root = os.path.join(self.tmpdir, 'extraction')
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(root)
        return root

    def run_artifact(self, name, root):
        """Run an artifact on the files its own paths glob matches under root."""
        function = ARTIFACTS[name]
        patterns = craigslist.__artifacts_v2__[function.__name__]['paths']
        found = []
        for base, _dirs, files in os.walk(root):
            for filename in files:
                full = os.path.join(base, filename)
                relative = 'root/' + os.path.relpath(full, root).replace(os.sep, '/')
                if any(fnmatch.fnmatchcase(relative, pattern) for pattern in patterns):
                    found.append(full)
        Context.clear()
        Context.set_data_folder(root)
        Context.set_report_folder(self.tmpdir)
        Context.set_files_found(found)
        Context.set_seeker(types.SimpleNamespace(
            directory=root, file_infos={p: FileInfo(os.path.relpath(p, root), 0, 0) for p in found}))
        return function.__wrapped__(Context)


class CraigslistFixtureTests(CraigslistBase):
    def setUp(self):
        super().setUp()
        zip_path = os.path.join(self.tmpdir, 'fixture.zip')
        self.expected = FIXTURE.build(zip_path)
        self.root = self.extract(zip_path)

    def rows(self, name):
        headers, rows, source = self.run_artifact(name, self.root)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        for row in rows:
            self.assertEqual(len(row), len(names), name)
        return names, [dict(zip(names, row)) for row in rows], source

    def test_every_artifact_matches_the_expected_count(self):
        for name in ('recent_searches', 'visited_postings', 'saved_items', 'startup_log', 'cached_searches',
                     'cached_postings'):
            _names, rows, source = self.rows(name)
            self.assertEqual(len(rows), self.expected[name], name)
            self.assertTrue(source, name)

    def test_recent_searches_decode_milliseconds_filters_and_missing_location(self):
        _names, rows, _source = self.rows('recent_searches')
        first = rows[0]
        self.assertEqual(first['Search Time'], datetime(2026, 3, 1, 12, 1, 0, tzinfo=UTC))
        self.assertEqual(first['Search Text'], 'synthetic desk')
        self.assertEqual(first['Filters'], 'search_distance=25')
        self.assertEqual(first['City'], 'Exampleville')
        self.assertEqual(rows[1]['Category Labels'], 'services > household')
        self.assertIsNone(rows[2]['City'])
        self.assertEqual(rows[2]['Filters'], '')

    def test_viewed_postings_pick_up_cached_titles_only_when_cached(self):
        _names, rows, _source = self.rows('visited_postings')
        titled = {r['Posting ID']: r['Cached Title'] for r in rows}
        self.assertEqual(titled['9000000001'], 'Synthetic desk')
        self.assertEqual(titled['9000000002'], 'Synthetic chair')
        self.assertIsNone(titled['9000000003'])   # response kept on disk
        self.assertIsNone(titled['9000000099'])   # not cached at all
        self.assertEqual(sum(1 for r in rows if r['Cached Title']), self.expected['visited_with_cached_title'])
        self.assertEqual(rows[0]['Viewed Time'], datetime(2026, 3, 1, 12, 5, 0, tzinfo=UTC))

    def test_saved_items_cover_favorite_hidden_and_saved_search(self):
        _names, rows, _source = self.rows('saved_items')
        by_list = {r['List']: r for r in rows}
        self.assertEqual(set(by_list), {'Favorite', 'Hidden', 'Saved search'})
        favorite = by_list['Favorite']
        self.assertEqual(favorite['Title'], 'Synthetic desk')
        self.assertEqual(favorite['Sync State'], 'unsynched')
        self.assertEqual(favorite['Posted'], datetime(2026, 3, 1, 11, 0, 0, tzinfo=UTC))
        self.assertEqual(favorite['Stored Entry'], '')
        self.assertIn('synthetic saved search', by_list['Saved search']['Stored Entry'])

    def test_account_state_never_exports_token_values(self):
        _names, rows, _source = self.rows('account_state')
        items = {r['Item']: r['Value'] for r in rows}
        self.assertEqual(items['Is Logged In'], True)
        self.assertEqual(items['Login (as stored)'], 'owner@example.invalid')
        self.assertEqual(items['Access Token Present'], 'Yes')
        self.assertEqual(items['Push Token Present'], 'No')
        self.assertEqual(items['Device UID (as stored)'], 'SYNTHETIC-DEVICE-UID-0001')
        self.assertEqual(items['Permission: location'], 'blocked')
        dump = json.dumps([r for r in rows], default=str)
        self.assertNotIn('SYNTHETIC-NOT-A-TOKEN', dump)
        self.assertNotIn('SYNTHETIC-NOT-A-COOKIE', dump)
        timed = [r for r in rows if r['Time'] is not None]
        self.assertTrue(timed)

    def test_startup_log_splits_tab_separated_entries(self):
        _names, rows, _source = self.rows('startup_log')
        self.assertEqual(rows[0]['Event'], 'Init Log File')
        self.assertEqual(rows[-1]['Event'], 'STARTUP COMPLETE')
        self.assertEqual(rows[-1]['Detail'], 'AppReadyListener')
        self.assertEqual(rows[0]['Log Time'], datetime(2026, 3, 1, 12, 10, 0, tzinfo=UTC))

    def test_cached_searches_split_request_parameters(self):
        _names, rows, _source = self.rows('cached_searches')
        kinds = sorted(r['Request Type'] for r in rows)
        self.assertEqual(kinds, ['Category counts', 'Search results', 'Search suggestions', 'Search suggestions'])
        count = next(r for r in rows if r['Request Type'] == 'Category counts')
        self.assertEqual(count['Search Text'], 'synthetic desk')
        self.assertEqual(count['Search Distance (as stored)'], 25.0)
        results = next(r for r in rows if r['Request Type'] == 'Search results')
        self.assertEqual(results['Category'], 'sss')
        self.assertEqual(results['Batch Size'], '20')
        self.assertEqual(results['Cache Time'], datetime(2026, 3, 1, 12, 1, 15, tzinfo=UTC))

    def test_cached_postings_read_database_bodies_and_count_disk_bodies(self):
        _names, rows, _source = self.rows('cached_postings')
        titles = sorted(r['Title'] for r in rows)
        self.assertEqual(titles, ['Synthetic chair', 'Synthetic desk'])
        desk = next(r for r in rows if r['Title'] == 'Synthetic desk')
        self.assertEqual(desk['Price'], '$10')
        self.assertEqual(desk['Image Count'], 2)
        self.assertEqual(desk['Posted'], datetime(2026, 3, 1, 10, 0, 0, tzinfo=UTC))
        chair = next(r for r in rows if r['Title'] == 'Synthetic chair')
        self.assertIsNone(chair['Price'])
        self.assertTrue(any('fsCachedData' in str(c.args[0]) for c in self.log.call_args_list))

    def test_every_artifact_pattern_matches_the_fixture_once(self):
        for name in ARTIFACTS:
            _names, rows, _source = self.rows(name)
            self.assertTrue(rows, name)


class CraigslistRobustnessTests(CraigslistBase):
    """Missing or reshaped stores give no rows and no exception."""

    def container(self):
        root = os.path.join(self.tmpdir, 'bare')
        folder = os.path.join(root, FIXTURE.CONTAINER, 'Library', 'Application Support', FIXTURE.BUNDLE,
                              'RCTAsyncLocalStorage_V1')
        os.makedirs(folder)
        return root, folder

    def test_empty_manifest_and_missing_hashed_files(self):
        root, folder = self.container()
        Path(folder, 'manifest.json').write_text(json.dumps({'persist:search': None, 'persist:root': None}), encoding='utf-8')
        for name in ('recent_searches', 'visited_postings', 'saved_items', 'account_state', 'startup_log'):
            _headers, rows, _source = self.run_artifact(name, root)
            self.assertEqual(list(rows), [], name)

    def test_manifest_that_is_not_json_or_not_an_object(self):
        root, folder = self.container()
        for text in ('not json', '[1, 2]', ''):
            Path(folder, 'manifest.json').write_text(text, encoding='utf-8')
            _headers, rows, _source = self.run_artifact('recent_searches', root)
            self.assertEqual(list(rows), [], text)

    def test_inline_value_is_read(self):
        root, folder = self.container()
        state = {'recentSearches': [{'params': {'query': 'inline form'}, 'timestamp': 1772366400000}]}
        # a value small enough to stay inline in manifest.json, as JSON text
        Path(folder, 'manifest.json').write_text(json.dumps({'persist:search': json.dumps(state)}), encoding='utf-8')
        _headers, rows, _source = self.run_artifact('recent_searches', root)
        self.assertEqual(rows[0][1], 'inline form')

    def test_unexpected_value_types_do_not_raise(self):
        root, folder = self.container()
        odd = {'recentSearches': ['x', 7, {'timestamp': 'soon', 'location': 'here', 'humanReadableParams': 'y'}],
               'visitedPostings': {'1': 'not a time', '2': None, '3': 10 ** 30}}
        Path(folder, 'manifest.json').write_text(json.dumps({'persist:search': None}), encoding='utf-8')
        Path(folder, hashlib.md5(b'persist:search').hexdigest()).write_text(json.dumps(odd), encoding='utf-8')
        _headers, rows, _source = self.run_artifact('recent_searches', root)
        self.assertEqual(len(rows), 1)
        _headers, rows, _source = self.run_artifact('visited_postings', root)
        self.assertEqual(len(rows), 3)

    def test_cache_db_without_the_cfurl_tables(self):
        root = os.path.join(self.tmpdir, 'bare_cache')
        folder = os.path.join(root, FIXTURE.CONTAINER, 'Library', 'Caches', FIXTURE.BUNDLE)
        os.makedirs(folder)
        db = sqlite3.connect(os.path.join(folder, 'Cache.db'))
        db.execute('CREATE TABLE unrelated (x)')
        db.commit()
        db.close()
        for name in ('cached_searches', 'cached_postings', 'visited_postings'):
            _headers, rows, _source = self.run_artifact(name, root)
            self.assertEqual(list(rows), [], name)

    def test_cache_response_that_is_not_json(self):
        root = os.path.join(self.tmpdir, 'badbody')
        folder = os.path.join(root, FIXTURE.CONTAINER, 'Library', 'Caches', FIXTURE.BUNDLE)
        os.makedirs(folder)
        FIXTURE.cache_db(os.path.join(folder, 'Cache.db'))
        db = sqlite3.connect(os.path.join(folder, 'Cache.db'))
        db.execute('UPDATE cfurl_cache_receiver_data SET receiver_data = ? WHERE isDataOnFS = 0', (b'<html>',))
        db.commit()
        db.close()
        _headers, rows, _source = self.run_artifact('cached_postings', root)
        self.assertEqual(list(rows), [])
        _headers, rows, _source = self.run_artifact('cached_searches', root)
        self.assertEqual(len(rows), 4)


if __name__ == '__main__':
    unittest.main()
