"""Fabricated join boundaries for the examiner workspace; no case data is required."""
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from admin.scripts import build_reddit_reader as reader


class LinkedWorkspaceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.artifacts = []
        self.app = 'private/var/mobile/Containers/Data/Application/SYNTHETIC-A/'
        self.account = self.app+'Documents/release02/accountData/alpha/'

    def table(self, name, rows, source='', view=None):
        labels = list(dict.fromkeys(label for row in rows for label in row))
        with sqlite3.connect(self.root/'_lava_artifacts.db') as db:
            db.execute('CREATE TABLE "'+name+'" ('+','.join('c'+str(i) for i in range(len(labels)))+')')
            db.executemany('INSERT INTO "'+name+'" VALUES ('+','.join('?' for _ in labels)+')',
                           [[row.get(label) for label in labels] for row in rows])
        item = {'tablename': name, 'column_map': {'c'+str(i): label for i,label in enumerate(labels)},
                'source_path': source}
        if view:
            item['data_views'] = {'conversation': {key:'c'+str(labels.index(value)) if key!='directionSentValue' else value for key,value in view.items()}}
        self.artifacts.append(item)

    def load(self):
        (self.root/'_lava_data.lava').write_text(json.dumps({'artifacts': {'Reddit': self.artifacts}}))
        return reader.load_records(self.root)

    def history(self, ids=('t3_demo',), path=None):
        self.table('reddit_post_history', [{'Account':'alpha','Post ID':ident,
                   'List Position (zero-based)':i,'Source File':path or self.account+'PostHistory'}
                  for i,ident in enumerate(ids)])

    def posts(self, paths=None):
        self.table('reddit_cached_posts', [{'Account':'alpha','Object ID':'t3_demo',
                   'Title':'Fabricated post','Community ID':'t5_demo','Author ID':'t2_demo',
                   'Source File':path} for path in (paths or [self.account+'sqlNormalizedCache'])])

    def test_history_links_to_post_without_rewriting_history_and_retains_duplicates(self):
        self.history(('t3_demo','t3_demo','t3_missing'))
        self.posts()
        records = self.load()
        history = [r for r in records if r['kind']=='post_history']
        self.assertEqual([r['matchCount'] for r in history],[1,1,0])
        self.assertEqual(len({r['group'] for r in history}),3)
        self.assertNotIn('Title',history[0]['fields'])
        self.assertEqual(history[0]['title'],'')
        self.assertEqual(history[0]['fields']['Post ID'],'t3_demo')

    def test_identical_ids_do_not_cross_accounts_containers_or_mismatched_paths(self):
        self.history()
        other = self.account.replace('alpha/','beta/')
        self.posts([other+'sqlNormalizedCache',
                    self.account.replace('SYNTHETIC-A','SYNTHETIC-B')+'sqlNormalizedCache'])
        records=self.load()
        self.assertFalse(next(r for r in records if r['kind']=='post_history')['links'])

    def test_multiple_cache_candidates_are_retained_without_selecting_a_winner(self):
        self.history()
        self.posts([self.account+'sqlNormalizedCache',self.account+'snapshot/sqlNormalizedCache'])
        records=self.load()
        history=next(r for r in records if r['kind']=='post_history')
        self.assertEqual(history['matchCount'],2)
        self.assertEqual(len(history['links']),2)
        self.assertEqual(len({r['group'] for r in records if r['kind']=='post'}),2)

    def test_subreddit_headers_link_with_unchanged_legacy_subscription_headers(self):
        cache = self.account+'sqlNormalizedCache'
        self.table('reddit_cached_posts',[{'Account':'alpha','Object ID':'t3_demo',
                   'Subreddit':'Synthetic','Subreddit ID':'t5_demo','Source File':cache}])
        self.table('reddit_cached_comments',[{'Account':'alpha','Object ID':'t1_demo',
                   'Post ID (from permalink)':'t3_demo','Subreddit (from permalink)':'Synthetic','Source File':cache}])
        self.table('reddit_cached_communities',[{'Account':'alpha','Subreddit ID':'t5_demo',
                   'Subreddit':'Synthetic','Source File':cache}])
        self.table('reddit_subreddit_subscriptions',[{'Account':'alpha','Community ID':'t5_demo',
                   'Community':'Synthetic','Source File':self.account+'SubredditSubscriptions'}])
        self.table('reddit_community_history',[{'Account':'alpha','Entry':'t5_demo',
                   'Source File':self.account+'SubredditHistory'}])
        records = self.load()
        history = next(r for r in records if r['kind']=='community_history')
        self.assertEqual(history['matchCount'],1)
        for row in records:
            if row['kind'] in ('post','comment'):
                self.assertEqual(row['community'],'Synthetic')
                expected = {'reddit_cached_communities'}
                if row['kind']=='post':
                    expected.add('reddit_subreddit_subscriptions')
                self.assertEqual({link['ref'].split(':')[0] for link in row['links']}, expected)
        self.assertEqual(next(r for r in records if r['kind']=='post')['fields']['Subreddit ID'],'t5_demo')
        self.assertTrue(all(r['communityId']=='t5_demo' for r in records if r['kind']=='community'))

    def test_old_subscriptions_and_new_cache_combine_but_preserve_conflicting_states(self):
        self.table('reddit_community_history',[
            {'Account':'alpha','Entry':'t5_demo','Source File':self.account+'SubredditHistory'},
            {'Account':'alpha','Entry':'t5_older','Source File':self.account+'SubredditHistory'}])
        self.table('reddit_cached_communities',[{'Account':'alpha','Community ID':'t5_demo',
                   'Community':'SyntheticCommunity','Is Subscribed (as stored)':False,
                   'Source File':self.account+'sqlNormalizedCache'}])
        self.table('reddit_subreddit_subscriptions',[
            {'Account':'alpha','Community ID':'t5_demo','Community':'SyntheticCommunity','Subscribed':'YES','Source File':self.account+'SubredditSubscriptions'},
            {'Account':'alpha','Community ID':'t5_older','Community':'OlderOnly','Subscribed':'NO','Source File':self.account+'SubredditSubscriptions'}])
        self.posts()
        records=self.load()
        history=[r for r in records if r['kind']=='community_history']
        self.assertEqual([r['matchCount'] for r in history],[1,1])
        matches=[r for r in records if r['kind']=='community' and r['id']=='t5_demo']
        self.assertEqual(len({r['group'] for r in matches}),1)
        self.assertEqual(matches[0]['fields']['Is Subscribed (as stored)'],0)
        self.assertEqual(matches[1]['fields']['Subscribed'],'YES')
        post=next(r for r in records if r['kind']=='post')
        self.assertTrue(any(link['ref'].startswith('reddit_subreddit_subscriptions:') for link in post['links']))

    def test_existing_profiles_add_exact_id_context_without_name_or_account_state_merging(self):
        self.posts()
        self.table('reddit_cached_profiles',[{'Account':'alpha','Profile ID':'t2_demo','Display Name':'Cache name',
                   'Is Blocked (as stored)':False,'Source File':self.account+'sqlNormalizedCache'}])
        self.table('reddit_users',[
            {'Reddit ID':'t2_demo','Display Name':'Older name','Is Blocked':'YES',
             'Source File':self.app+'Library/Caches/MatrixChat/redditAccount/hash/RedditUsersStore.db'},
            {'Reddit ID':'t2_demo','Display Name':'Foreign container','Source File':self.app.replace('SYNTHETIC-A','SYNTHETIC-B')+'store.db'},
            {'Reddit ID':'t2_other','Display Name':'Cache name','Source File':self.app+'store.db'}])
        records=self.load()
        post=next(r for r in records if r['kind']=='post')
        references={link['ref'] for link in post['links']}
        self.assertIn('reddit_users:1',references)
        self.assertNotIn('reddit_users:2',references)
        self.assertNotIn('reddit_users:3',references)
        profiles=[r for r in records if r['kind']=='profile' and r['container']==self.app.rstrip('/') and r['id']=='t2_demo']
        self.assertEqual(len({r['group'] for r in profiles}),1)
        self.assertEqual({r['author'] for r in profiles},{'Cache name','Older name'})

    def test_ambiguous_manifest_source_does_not_create_contact_identity_join(self):
        self.posts()
        self.table('reddit_chat_contacts',[{'User ID':'t2_demo','Username':'Synthetic','Account ID':'alpha'}],
                   source=self.app+'one.db\n'+self.app+'two.db')
        records=self.load()
        contact=next(r for r in records if r['kind']=='contact')
        self.assertFalse(contact['container'])
        self.assertFalse(contact['links'])

    def test_matrix_contacts_use_sender_id_and_do_not_guess_from_display_name(self):
        self.table('reddit_chats',[{'Message':'Synthetic','Sender ID':'@synthetic:example.invalid',
                   'Sender Display Name':'Same name','Room ID':'!room:example.invalid','Direction':'',
                   'Server Timestamp':1700000000}], source=self.app+'matrix.db', view={
                       'textColumn':'Message','senderColumn':'Sender Display Name',
                       'conversationDiscriminatorColumn':'Room ID','timeColumn':'Server Timestamp',
                       'directionColumn':'Direction','directionSentValue':'Outgoing'})
        self.table('reddit_chat_users',[
            {'Matrix User ID':'@synthetic:example.invalid','Display Name':'Other label','Source File':self.app+'users.db'},
            {'Matrix User ID':'@different:example.invalid','Display Name':'Same name','Source File':self.app+'users.db'}])
        records=self.load()
        chat=next(r for r in records if r['kind']=='chat')
        self.assertEqual([link['ref'] for link in chat['links']],['reddit_chat_users:1'])

    def test_permalink_community_names_link_only_to_unique_same_cache_observations(self):
        cache=self.account+'sqlNormalizedCache'
        self.table('reddit_cached_comments',[{'Account':'alpha','Object ID':'t1_demo',
                   'Post ID (from permalink)':'t3_demo','Community (from permalink)':'Synthetic',
                   'Source File':cache}])
        self.table('reddit_cached_communities',[
            {'Account':'alpha','Community ID':'t5_one','Community':'Synthetic','Source File':cache},
            {'Account':'alpha','Community ID':'t5_two','Community':'Synthetic','Source File':cache}])
        self.assertFalse(next(r for r in self.load() if r['kind']=='comment')['links'])

    def test_missing_history_account_scope_never_joins_by_id_alone(self):
        self.history(path='unattributed/PostHistory')
        self.posts()
        self.assertFalse(next(r for r in self.load() if r['kind']=='post_history')['links'])

    def test_existing_exports_work_without_cache_history_contribution(self):
        self.table('reddit_users',[{'Reddit ID':'t2_demo','Display Name':'Synthetic','Source File':self.app+'users.db'}])
        self.table('reddit_subreddit_subscriptions',[{'Account':'alpha','Community ID':'t5_demo','Community':'Synthetic','Source File':self.account+'SubredditSubscriptions'}])
        records=self.load()
        self.assertEqual({r['kind'] for r in records},{'profile','community'})
        before=hashlib.sha256((self.root/'_lava_artifacts.db').read_bytes()).digest()
        self.assertEqual(reader.build(self.root),2)
        self.assertEqual(before,hashlib.sha256((self.root/'_lava_artifacts.db').read_bytes()).digest())

    def test_wrapping_is_opt_in_idempotent_and_preserves_original_cell_text(self):
        self.posts()
        self.load()
        folder=self.root/'_HTML/Reddit'
        folder.mkdir(parents=True)
        page=folder/'Reddit - Cached Posts.html'
        original='<html><head></head><body><td>&lt;synthetic&gt;'+('x'*1000)+'</td></body></html>'
        page.write_text(original)
        reader.build(self.root)
        self.assertEqual(page.read_text(),original)
        reader.build(self.root,format_tables=True)
        formatted=page.read_text()
        self.assertEqual(formatted.replace(reader.TABLE_STYLE+'\n',''),original)
        self.assertEqual(reader.wrap_tables(self.root),0)

    def test_wrapping_applies_to_current_flat_report_layout_and_leaves_other_apps_alone(self):
        folder=self.root/'_HTML'
        folder.mkdir()
        original='<html><head></head><body>Fabricated text</body></html>'
        (folder/'Reddit_-_Cached_Posts.html').write_text(original)
        (folder/'Other_App.html').write_text(original)
        self.assertEqual(reader.wrap_tables(self.root),1)
        self.assertIn(reader.TABLE_STYLE,(folder/'Reddit_-_Cached_Posts.html').read_text())
        self.assertEqual((folder/'Other_App.html').read_text(),original)


if __name__=='__main__':
    unittest.main()
