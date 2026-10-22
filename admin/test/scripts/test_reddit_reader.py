"""Regression tests for safe grouping and the optional offline report reader."""
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from admin.scripts import build_reddit_reader as reader


class DiscussionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_reader_respects_chat_configuration_and_escapes_script_end(self):
        tables = {}
        dbpath = self.root/'_lava_artifacts.db'
        with sqlite3.connect(dbpath) as db:
            for table in ['reddit_chats','reddit_chat_messages']:
                db.execute('CREATE TABLE '+table+' (body,room,author,stamp,direction,account)')
                for text, room in [('</script><script>alert(1)</script>', 'same-id'), ('synthetic second','')]:
                    db.execute('INSERT INTO '+table+' VALUES (?,?,?,?,?,?)',
                               (text,room,'Synthetic',1700000000,'','alpha'))
                tables[table] = {'tablename':table, 'column_map':{'account':'Account ID'},
                    'source_path':'synthetic/source.sqlite','data_views':{'conversation':{
                        'textColumn':'body','conversationDiscriminatorColumn':'room',
                        'senderColumn':'author','timeColumn':'stamp','directionColumn':'direction',
                        'directionSentValue':'Outgoing'}}}
        manifest = {'artifacts':{'Reddit':list(tables.values())}}
        (self.root/'_lava_data.lava').write_text(json.dumps(manifest))
        before = hashlib.sha256(dbpath.read_bytes()).digest()
        rows = reader.load_records(self.root)
        self.assertEqual(len(rows),4)
        self.assertEqual(len({r['group'] for r in rows}),4)
        self.assertTrue(all(r['direction']=='' for r in rows))
        self.assertEqual(reader.build(self.root),4)
        page = (self.root/'Reddit_Reader.html').read_text()
        self.assertNotIn('</script><script>alert(1)</script>',page)
        self.assertIn(r'\u003c/script>',page)
        self.assertEqual(before,hashlib.sha256(dbpath.read_bytes()).digest())
        self.assertIn("node.textContent=String(text)",page)
        self.assertIn("connect-src 'none'",page)

    def test_reader_keeps_account_and_source_in_discussion_group(self):
        table = 'reddit_cached_comments'
        with sqlite3.connect(self.root/'_lava_artifacts.db') as db:
            db.execute('CREATE TABLE '+table+' (post,account,source,text)')
            db.executemany('INSERT INTO '+table+' VALUES (?,?,?,?)',[
                ('t3_same','alpha','container-a/cache','first'),
                ('t3_same','beta','container-a/cache','second'),
                ('t3_same','alpha','container-b/cache','third')])
        manifest = {'artifacts':{'Reddit':[{'tablename':table,'column_map':{
            'post':'Post ID (from permalink)','account':'Account','source':'Source File','text':'Text'}}]}}
        (self.root/'_lava_data.lava').write_text(json.dumps(manifest))
        rows = reader.load_records(self.root)
        self.assertEqual(len({r['group'] for r in rows}),3)
        self.assertTrue(all(r['postId']=='t3_same' for r in rows))

    def test_unlinked_post_and_comment_with_equal_table_rowids_stay_separate(self):
        artifacts = []
        with sqlite3.connect(self.root/'_lava_artifacts.db') as db:
            for table in ('reddit_cached_posts', 'reddit_cached_comments'):
                db.execute('CREATE TABLE '+table+' (object_id,post_id,account,source,title,text)')
                db.execute('INSERT INTO '+table+" VALUES ('','','alpha','same/cache','Unlinked','Synthetic')")
                artifacts.append({'tablename': table, 'column_map': {
                    'object_id': 'Object ID', 'post_id': 'Post ID (from permalink)',
                    'account': 'Account', 'source': 'Source File', 'title': 'Title', 'text': 'Text'}})
        (self.root/'_lava_data.lava').write_text(json.dumps({'artifacts': {'Reddit': artifacts}}))
        rows = reader.load_records(self.root)
        self.assertEqual([r['rowid'] for r in rows], [1, 1])
        self.assertEqual(len({r['group'] for r in rows}), 2)

    def test_established_post_link_still_groups_across_tables(self):
        artifacts = []
        with sqlite3.connect(self.root/'_lava_artifacts.db') as db:
            for table in ('reddit_cached_posts', 'reddit_cached_comments'):
                db.execute('CREATE TABLE '+table+' (object_id,post_id,account,source)')
                db.execute('INSERT INTO '+table+" VALUES ('t3_demo','t3_demo','alpha','same/cache')")
                artifacts.append({'tablename': table, 'column_map': {
                    'object_id': 'Object ID', 'post_id': 'Post ID (from permalink)',
                    'account': 'Account', 'source': 'Source File'}})
        (self.root/'_lava_data.lava').write_text(json.dumps({'artifacts': {'Reddit': artifacts}}))
        rows = reader.load_records(self.root)
        self.assertEqual(len({r['group'] for r in rows}), 1)


class WriterContractTests(unittest.TestCase):
    def test_reader_accepts_real_lava_column_map(self):
        from scripts import lavafuncs  # pylint: disable=import-outside-toplevel
        from scripts.context import Context  # pylint: disable=import-outside-toplevel
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            try:
                lavafuncs.initialize_lava(temp, temp, 'fs')
                Context.set_artifact_info({'name':'Synthetic posts','description':'Fabricated'})
                Context.set_module_file_path('scripts/artifacts/redditCache.py')
                headers = ('Account','Object ID','Title','Text','Source File')
                table, objects, column_map = lavafuncs.lava_process_artifact(
                    'Reddit','redditCache','Synthetic posts',headers,record_count=1,
                    func_name='reddit_cached_posts')
                lavafuncs.lava_insert_sqlite_data(table,
                    [('alpha','t3_demo','Synthetic title','Fabricated text','container-a/cache')],
                    objects,headers,column_map)
                lavafuncs.lava_db.commit()
                (root/'_lava_data.lava').write_text(json.dumps(lavafuncs.lava_data))
                rows = reader.load_records(root)
                self.assertEqual(rows[0]['title'],'Synthetic title')
                self.assertEqual(rows[0]['text'],'Fabricated text')
                self.assertEqual(rows[0]['postId'],'t3_demo')
            finally:
                if lavafuncs.lava_db is not None:
                    lavafuncs.lava_db.close()
                    lavafuncs.lava_db = None
                lavafuncs.lava_data = None
                Context.clear()


if __name__ == '__main__':
    unittest.main()
