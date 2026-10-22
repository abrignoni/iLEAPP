"""Fabricated fixtures only; never load private case files in CI."""
import fnmatch
import hashlib
import inspect
import json
import plistlib
import sqlite3
import tempfile
import unittest
import os
from pathlib import Path
from unittest.mock import patch

from scripts.artifacts import redditCache as parser


class Context:
    def __init__(self, root, name):
        self.root = root
        self.files = [str(p) for p in root.rglob('*') if p.is_file() and any(
            fnmatch.fnmatchcase(str(p), pat) for pat in parser.__artifacts_v2__[name]['paths'])]

    def get_files_found(self):
        return self.files + self.files  # Duplicate seeker hits must not duplicate rows.

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def run(root, name):
    headers, rows, _ = inspect.unwrap(getattr(parser, name))(Context(root, name))
    assert all(len(row) == len(headers) for row in rows)
    labels = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(labels, row)) for row in rows]


def cache(root, account, records):
    p = root / 'Documents/release02/accountData' / account / 'sqlNormalizedCache'
    p.parent.mkdir(parents=True)
    with sqlite3.connect(p) as db:
        db.execute('CREATE TABLE records (_id INTEGER PRIMARY KEY,key TEXT,record TEXT)')
        for k, value in records.items():
            db.execute('INSERT INTO records(key,record) VALUES (?,?)', (k, json.dumps(value)))
    return p


class ParserTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_resolves_content_without_cross_account_merges(self):
        tmp_path = self.root
        for account, text in [('alpha', '<b>fabricated A</b>'), ('beta', 'fabricated B')]:
            cache(tmp_path, account, {
                'Comment:t1_demo': {'id': 't1_demo', 'content': {'$reference': 'Comment:t1_demo.content'},
                                    'authorInfo': {'$reference': 'Redditor:t2_demo'},
                                    'createdAt': '2024-01-02T03:04:05.125Z',
                                    'isOwnComment': False, 'isSaved': False, 'score': 0},
                'Comment:t1_demo.content': {'markdown': text},
                'Redditor:t2_demo': {'displayName': account, 'id': 't2_demo'},
            })
        rows = run(tmp_path, 'reddit_cached_comments')
        assert len(rows) == 2
        assert {r['Account']: r['Text'] for r in rows} == {'alpha': '<b>fabricated A</b>', 'beta': 'fabricated B'}
        assert all(r['Is Own (as stored)'] is False for r in rows)
        assert all(r['Content Created'].microsecond == 125000 for r in rows)
        assert all(r['Author Name'] == r['Account'] for r in rows)


    def test_missing_and_cyclic_references_preserved(self):
        tmp_path = self.root
        cache(tmp_path, 'alpha', {'SubredditPost:t3_demo': {'id': 't3_demo',
              'content': {'$reference': 'missing'}, 'subreddit': {'$reference': 'loop'}},
              'loop': {'$reference': 'loop'}})
        row = run(tmp_path, 'reddit_cached_posts')[0]
        assert row['Text'] == ''
        assert '$reference' in row['Resolved Content JSON']
        assert row['Is Own (as stored)'] is None


    def test_bad_json_does_not_hide_following_records(self):
        tmp_path = self.root
        p = cache(tmp_path, 'alpha', {'Subreddit:t5_demo': {'id': 't5_demo', 'isSubscribed': False}})
        with sqlite3.connect(p) as db:
            db.execute('INSERT INTO records(key,record) VALUES (?,?)', ('broken', '{'))
        before = hashlib.sha256(p.read_bytes()).digest()
        assert len(run(tmp_path, 'reddit_cached_communities')) == 1
        assert hashlib.sha256(p.read_bytes()).digest() == before


    def test_wal_only_row_is_read_without_checkpoint(self):
        tmp_path = self.root
        p = cache(tmp_path, 'alpha', {})
        db = sqlite3.connect(p)
        try:
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('PRAGMA wal_autocheckpoint=0')
            db.execute('INSERT INTO records(key,record) VALUES (?,?)',
                       ('Redditor:t2_wal', '{"id":"t2_wal","displayName":"Synthetic"}'))
            db.commit()
            wal = Path(str(p) + '-wal')
            before = [hashlib.sha256(x.read_bytes()).digest() for x in [p, wal]]
            assert len(run(tmp_path, 'reddit_cached_profiles')) == 1
            assert before == [hashlib.sha256(x.read_bytes()).digest() for x in [p, wal]]
        finally:
            db.close()


    def test_history_keeps_info_only_ids_and_duplicate_positions(self):
        tmp_path = self.root
        p = tmp_path / 'Documents/release02/accountData/alpha/PostHistory'
        p.parent.mkdir(parents=True)
        p.write_bytes(plistlib.dumps({'kPostIDDictionaryKey': ['t3_a', 't3_a'],
                                     'kInfoDictionaryKey': {'t3_a': {'kGlanceInfoKey': False},
                                                            't3_b': {'kGlanceInfoKey': True}}}))
        rows = run(tmp_path, 'reddit_post_history')
        assert [r['List Position (zero-based)'] for r in rows] == [0, 1, None]
        assert rows[-1]['Membership'] == 'Info dictionary only'
        assert rows[0]['kGlanceInfoKey (as stored)'] is False


    def test_nskeyed_community_history(self):
        tmp_path = self.root
        p = tmp_path / 'Documents/release02/accountData/alpha/SubredditHistory'
        p.parent.mkdir(parents=True)
        uid = plistlib.UID
        archive = {'$version': 100000, '$archiver': 'NSKeyedArchiver', '$top': {'root': uid(1)},
                   '$objects': ['$null', {'NS.objects': [uid(2)], '$class': uid(3)}, 't5_demo',
                                {'$classname': 'NSArray', '$classes': ['NSArray', 'NSObject']}]}
        p.write_bytes(plistlib.dumps(archive, fmt=plistlib.FMT_BINARY))  # pylint: disable=no-member
        assert run(tmp_path, 'reddit_community_history')[0]['Entry'] == 't5_demo'


    def test_draft_core_data_epoch(self):
        tmp_path = self.root
        p = tmp_path / 'Documents/release02/accountData/alpha/commentDrafts/CommentDraftEntity.sqlite'
        p.parent.mkdir(parents=True)
        with sqlite3.connect(p) as db:
            db.execute('CREATE TABLE ZCOMMENTDRAFTENTITY (Z_PK,ZMODIFIEDDATE,ZCONTENT,ZID,ZPARENTCOMMENTPK,ZPOSTPK,ZPOSTTITLE)')
            db.execute('INSERT INTO ZCOMMENTDRAFTENTITY VALUES (1,0,\'synthetic\',\'d\',NULL,\'t3_a\',\'title\')')
        row = run(tmp_path, 'reddit_comment_drafts')[0]
        assert row['Modified'].year == 2001
        assert row['Content'] == 'synthetic'


    def test_empty_wrong_schema_and_invalid_timestamp(self):
        tmp_path = self.root
        p = cache(tmp_path, 'alpha', {'Comment:t1_a': {'createdAt': 'bad'}})
        assert run(tmp_path, 'reddit_cached_comments')[0]['Content Created'] == ''
        with sqlite3.connect(p) as db:
            db.execute('DROP TABLE records')
        assert run(tmp_path, 'reddit_cached_comments') == []


    @unittest.skipUnless(os.environ.get("ILEAPP_LOCAL_IMAGE"), "private corpus not supplied")
    def test_local_corpus_shapes(self):
        root = Path(os.environ["ILEAPP_LOCAL_IMAGE"])
        if not root.is_dir():
            self.skipTest("this check expects a reconstructed filesystem directory")
        for name in parser.__artifacts_v2__:
            context = Context(root, name)
            headers, rows, _ = inspect.unwrap(getattr(parser, name))(context)
            self.assertTrue(all(len(row) == len(headers) for row in rows), "row shape mismatch")


class DiscussionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_permalink_requires_matching_comment_and_reddit_host(self):
        good = '/r/Synthetic/comments/abc123/title/def456/'
        self.assertEqual(parser._permalink_context(good, 't1_def456'), ('t3_abc123', 'Synthetic'))  # pylint: disable=protected-access
        self.assertEqual(parser._permalink_context(good.replace('/title/', '//'), 't1_def456'), ('t3_abc123', 'Synthetic'))  # pylint: disable=protected-access
        self.assertEqual(parser._permalink_context(good.replace('/r/Synthetic/', '/user/Synthetic/'), 't1_def456'), ('t3_abc123', ''))  # pylint: disable=protected-access
        for value in ['https://example.com'+good, 'javascript:'+good, good+'extra/',
                      good.replace('def456', 'unrelated'), 'not a URL', '//reddit.com.evil'+good]:
            self.assertEqual(parser._permalink_context(value, 't1_def456'), ('', ''))  # pylint: disable=protected-access
        self.assertEqual(parser._permalink_context('https://www.reddit.com'+good+'?x=1', 't1_def456'), ('t3_abc123', 'Synthetic'))  # pylint: disable=protected-access

    def test_same_database_title_join_preserves_separate_sources(self):
        for container,title in [('container-a','Fabricated A'), ('container-b','Fabricated B')]:
            cache(self.root/container, 'alpha', {
                'SubredditPost:t3_abc123': {'id':'t3_abc123','title':title},
                'Comment:t1_def456': {'id':'t1_def456', 'content':{'markdown':'Synthetic comment'},
                                      'permalink':'/r/Synthetic/comments/abc123/title/def456/'}})
        rows = run(self.root, 'reddit_cached_comments')
        self.assertEqual({r['Cached Post Title'] for r in rows}, {'Fabricated A','Fabricated B'})
        self.assertTrue(all(r['Post ID (from permalink)']=='t3_abc123' for r in rows))
        self.assertEqual(len({r['Source File'] for r in rows}), 2)

    def test_missing_parent_and_bad_link_do_not_hide_comment(self):
        cache(self.root, 'alpha', {
            'Comment:t1_def456': {'id':'t1_def456', 'permalink':'/r/Synthetic/comments/abc123/title/def456/'},
            'Comment:t1_bad': {'id':'t1_bad', 'permalink':'/r/Synthetic/comments/abc123/title/def456/'}})
        rows = {r['Object ID']:r for r in run(self.root, 'reddit_cached_comments')}
        self.assertEqual(rows['t1_def456']['Post ID (from permalink)'], 't3_abc123')
        self.assertEqual(rows['t1_def456']['Cached Post Title'], '')
        self.assertEqual(rows['t1_bad']['Post ID (from permalink)'], '')



class AuditRegressionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_observed_offsets_match_z_for_posts_and_comments(self):
        records = {}
        for n, stamp in enumerate(('2024-05-01T12:40:00.125000+0000',
                                   '2024-05-01T12:40:00.125000Z',
                                   '2024-05-01T18:10:00.125000+0530',
                                   '2024-05-01T18:10:00.125000+05:30',
                                   '2024-05-01T08:40:00.125000-0400')):
            for kind in ('SubredditPost', 'Comment'):
                records[f'{kind}:demo{n}'] = {'id': f'demo{n}', 'createdAt': stamp, 'editedAt': stamp}
        cache(self.root, 'alpha', records)
        for name in ('reddit_cached_posts', 'reddit_cached_comments'):
            with self.subTest(artifact=name):
                rows = run(self.root, name)
                expected = rows[0]['Content Created']
                self.assertNotEqual(expected, '')
                self.assertEqual(expected.microsecond, 125000)
                self.assertTrue(all(r['Content Created'] == expected == r['Content Edited'] for r in rows))

    def test_basic_calendar_and_hour_only_offsets_preserve_utc_and_microseconds(self):
        for value in ('2024-05-01T17:40:00.123456+05',
                      '2024-05-01T08:40:00.123456-04',
                      '20240501T124000.123456Z', '20240501T174000.123456+0500',
                      '20240501T174000.123456+05',
                      '20240501T1240.123456Z', '2024-05-01T124000.123456Z',
                      '2024-05-01T0840.123456-04'):
            with self.subTest(value=value):
                stamp = parser._iso(value, 'synthetic/cache')  # pylint: disable=protected-access
                self.assertNotEqual(stamp, '')
                self.assertEqual(stamp.isoformat(), '2024-05-01T12:40:00.123456+00:00')
        for value in ('20240501T124000Z', '2024-05-01T17:40:00+05',
                      '20240501T1240Z', '2024-05-01T124000Z', '2024-05-01T1240Z'):
            with self.subTest(value=value):
                self.assertEqual(parser._iso(value).isoformat(),  # pylint: disable=protected-access
                                 '2024-05-01T12:40:00+00:00')

    def test_bad_date_diagnostic_names_source_key_and_field(self):
        path = cache(self.root, 'alpha', {'Comment:bad': {'createdAt': 'bad',
                      'editedAt': '2024-05-01T12:40:00'}})
        with patch.object(parser, 'logfunc') as log:
            row = run(self.root, 'reddit_cached_comments')[0]
        self.assertEqual(row['Content Created'], '')
        self.assertEqual(row['Content Edited'], '')
        messages = [call.args[0] for call in log.call_args_list]
        self.assertEqual(len(messages), 2)
        self.assertTrue(all(path.relative_to(self.root).as_posix() in msg and 'Comment:bad' in msg for msg in messages))
        self.assertTrue(any('field=createdAt' in msg for msg in messages))
        self.assertTrue(any('field=editedAt' in msg for msg in messages))

    def test_comment_dates_lead_literal_headers(self):
        headers, _, _ = inspect.unwrap(parser.reddit_cached_comments)(Context(self.root, 'reddit_cached_comments'))
        self.assertEqual(headers[:2], (('Content Created', 'datetime'), ('Content Edited', 'datetime')))

    def test_malformed_cache_names_file_row_key_and_preserves_good_records(self):
        path = cache(self.root, 'alpha', {'Redditor:ok': {'id': 'ok'}})
        with sqlite3.connect(path) as db:
            db.execute("INSERT INTO records(key,record) VALUES ('broken','{')")
        with patch.object(parser, 'logfunc') as log:
            self.assertEqual(len(run(self.root, 'reddit_cached_profiles')), 1)
        msg = log.call_args.args[0]
        self.assertIn(path.relative_to(self.root).as_posix(), msg)
        self.assertNotIn(str(self.root), msg)
        self.assertIn('row=2', msg)
        self.assertIn('key=broken', msg)

    def test_wrong_history_shapes_are_reported_with_source(self):
        base = self.root/'Documents/release02/accountData/alpha'
        base.mkdir(parents=True)
        for filename, value, artifact in (
                ('PostHistory', ['unexpected'], 'reddit_post_history'),
                ('SubredditHistory', {'unexpected': True}, 'reddit_community_history')):
            path = base/filename
            path.write_bytes(plistlib.dumps(value))
            with self.subTest(source=filename), patch.object(parser, 'logfunc') as log:
                self.assertEqual(run(self.root, artifact), [])
                self.assertTrue(any(path.relative_to(self.root).as_posix() in c.args[0] for c in log.call_args_list))

    def test_draft_account_scope_and_bad_store_diagnostic(self):
        for account in ('alpha', 'beta'):
            path = self.root/f'Documents/release02/accountData/{account}/commentDrafts/CommentDraftEntity.sqlite'
            path.parent.mkdir(parents=True)
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE ZCOMMENTDRAFTENTITY (Z_PK,ZMODIFIEDDATE,ZCONTENT,ZID,ZPARENTCOMMENTPK,ZPOSTPK,ZPOSTTITLE)')
                db.execute("INSERT INTO ZCOMMENTDRAFTENTITY VALUES (1,0,'synthetic','draft',NULL,'post','title')")
        decoy = self.root/'OtherApp/Library/Application Support/CommentDraftEntity.sqlite'
        decoy.parent.mkdir(parents=True)
        with sqlite3.connect(decoy) as db:
            db.execute('CREATE TABLE unrelated (x)')
        rows = run(self.root, 'reddit_comment_drafts')
        self.assertEqual({r['Account'] for r in rows}, {'alpha', 'beta'})
        self.assertEqual(len(rows), 2)
        self.assertNotIn(str(decoy), Context(self.root, 'reddit_comment_drafts').files)
        bad = self.root/'Documents/release02/accountData/bad/commentDrafts/CommentDraftEntity.sqlite'
        bad.parent.mkdir(parents=True)
        with sqlite3.connect(bad) as db:
            db.execute('CREATE TABLE unrelated (x)')
        with patch.object(parser, 'logfunc') as log:
            self.assertEqual(len(run(self.root, 'reddit_comment_drafts')), 2)
        self.assertTrue(any(bad.relative_to(self.root).as_posix() in c.args[0] for c in log.call_args_list))


class FractionCompatibilityTests(unittest.TestCase):
    def test_all_fraction_lengths_have_the_same_microsecond_precision(self):
        expected = {'': 0, '1': 100000, '12': 120000, '123': 123000,
                    '1234': 123400, '12345': 123450, '123456': 123456,
                    '1234567': 123456, '123456789': 123456}
        for digits, microsecond in expected.items():
            for offset in ('Z', '+0000', '+00:00'):
                fraction = '.'+digits if digits else ''
                value = '2024-05-01T12:40:00'+fraction+offset
                with self.subTest(digits=digits, offset=offset):
                    stamp = parser._iso(value, 'synthetic/cache')  # pylint: disable=protected-access
                    self.assertNotEqual(stamp, '')
                    self.assertEqual(stamp.microsecond, microsecond)
                    self.assertEqual((stamp.year, stamp.month, stamp.day, stamp.hour, stamp.minute, stamp.second),
                                     (2024, 5, 1, 12, 40, 0))

    def test_parser_diagnostics_do_not_include_local_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = cache(root, 'alpha', {'Comment:bad': {'createdAt': 'invalid'}})
            with sqlite3.connect(path) as db:
                db.execute("INSERT INTO records(key,record) VALUES ('bad-json','{')")
            with patch.object(parser, 'logfunc') as log:
                run(root, 'reddit_cached_comments')
            messages = [call.args[0] for call in log.call_args_list]
            self.assertEqual(len(messages), 2)
            self.assertTrue(all(str(root) not in msg for msg in messages))
            self.assertTrue(all(path.relative_to(root).as_posix() in msg for msg in messages))
