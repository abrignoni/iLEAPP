"""Controls use fabricated timestamps/exports; Node checks are optional off this host."""
import hashlib
import json
import shutil
import sqlite3
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from admin.scripts import build_reddit_reader as reader
from admin.test.scripts import test_reddit_reader_links as links_tests


CONTROL_JS = Path(reader.__file__).with_name('reddit_reader_controls.js')


@unittest.skipUnless(shutil.which('node'), 'Node.js is needed to execute the actual reader controls')
class ControlTests(unittest.TestCase):
    def check_js(self, assertions):
        code = 'const assert=require("node:assert/strict");const C=require(process.argv[1]);\n'+assertions
        result = subprocess.run([shutil.which('node'), '-e', code, str(CONTROL_JS)],
                                text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_zero_negative_missing_and_invalid_epochs(self):
        self.check_js(r"""
for(const value of ['',null,undefined,' ',false,true,'bad','9'.repeat(400)])assert.equal(C.epoch(value),null);
assert.equal(C.epoch(0),0);assert.equal(C.epoch(-1),-1);
assert.equal(C.day(0),'1970-01-01');assert.equal(C.day(-1),'1969-12-31');
""")

    def test_display_formats_clock_and_no_epoch_mutation(self):
        self.check_js(r"""
const value=Date.parse('2024-02-03T13:04:05.125Z')/1000;
assert.equal(C.stamp(value,{timeZone:'UTC'}),'2024-02-03 13:04:05.125 [UTC UTC+00:00]');
assert.equal(C.stamp(value,{timeZone:'UTC',dateFormat:'mdy',clock:'12'}),'02/03/2024 01:04:05.125 PM [UTC UTC+00:00]');
assert.equal(C.stamp(value,{timeZone:'UTC',dateFormat:'dmy'}),'03/02/2024 13:04:05.125 [UTC UTC+00:00]');
assert.equal(C.stamp(0,{clock:'12'}),'1970-01-01 12:00:00 AM [UTC UTC+00:00]');
assert.equal(value,1706965445.125);assert.throws(()=>C.zone('Invalid/Zone'));
""")

    def test_date_details_omit_only_absent_raw_values(self):
        self.check_js(r"""
for(const value of ['',null,undefined,' '])assert.equal(C.dateDetail(value),'Date not retained');
assert.ok(C.dateDetail(0).endsWith('Raw UTC epoch: 0'));
assert.ok(C.dateDetail('invalid').endsWith('Raw UTC epoch: invalid'));
assert.ok(C.dateDetail('1706965445.123456').endsWith('Raw UTC epoch: 1706965445.123456'));
""")

    def test_dst_repeated_hour_retains_distinct_offsets(self):
        self.check_js(r"""
const first=Date.parse('2024-11-03T05:30:00Z')/1000,second=Date.parse('2024-11-03T06:30:00Z')/1000;
assert.equal(C.stamp(first,{timeZone:'America/New_York'}),'2024-11-03 01:30:00 [America/New_York UTC-04:00]');
assert.equal(C.stamp(second,{timeZone:'America/New_York'}),'2024-11-03 01:30:00 [America/New_York UTC-05:00]');
assert.equal(C.day(first,'America/New_York'),C.day(second,'America/New_York'));
""")

    def test_inclusive_local_date_bounds_cover_23_and_25_hour_days(self):
        self.check_js(r"""
for(const [day,start,end] of [['2024-03-10','2024-03-10T05:00:00Z','2024-03-11T04:00:00Z'],['2024-11-03','2024-11-03T04:00:00Z','2024-11-04T05:00:00Z']]){
 const a=Date.parse(start)/1000,b=Date.parse(end)/1000,opts={timeZone:'America/New_York',from:day,to:day,includeUndated:false};
 assert.equal(C.inRange({created:a-0.001},opts),false);assert.equal(C.inRange({created:a},opts),true);
 assert.equal(C.inRange({created:b-0.001},opts),true);assert.equal(C.inRange({created:b},opts),false);
 assert.equal(C.inRange({created:''},opts),false);assert.equal(C.inRange({created:''},{...opts,includeUndated:true}),true);
}
assert.equal(C.day(0,'Pacific/Honolulu'),'1969-12-31');
""")

    def test_row_and_group_sorts_keep_unknown_dates_last_and_posts_first(self):
        self.check_js(r"""
const rows=[{kind:'comment',created:'',table:'t',rowid:1},{kind:'comment',created:2,table:'t',rowid:2},{kind:'post',created:1,table:'t',rowid:3}];
assert.deepEqual([...rows].sort((a,b)=>C.compareRows(a,b,'newest')).map(r=>r.rowid),[3,2,1]);
const groups=rows.map(r=>({id:String(r.rowid),title:String(r.rowid),rows:[r],kind:'discussion',comments:0}));
assert.deepEqual([...groups].sort((a,b)=>C.compareGroups(a,b,'oldest')).map(g=>g.id),['3','2','1']);
assert.deepEqual([...groups].sort((a,b)=>C.compareGroups(a,b,'newest')).map(g=>g.id),['2','3','1']);
""")

    def test_csv_quoting_unicode_multiline_and_spreadsheet_formulas(self):
        self.check_js(r"""
assert.equal(C.csvCell('a,"b"\n雪'),'"a,""b""\n雪"');
for(const value of ['=1+1','+cmd','-formula','@formula','  =SUM(1)','\t=SUM(1)','\n=1'])assert.ok(C.csvCell(value).startsWith('"\''));
assert.equal(C.csvCell(0),'"0"');assert.equal(C.csvCell(false),'"false"');
""")

    def test_json_and_csv_exports_preserve_raw_fields_and_include_settings(self):
        self.check_js(r"""
const row={table:'synthetic',rowid:1,kind:'post',created:0,title:'=1+1',fields:{Text:'=1+1',Flag:false,Count:0},links:[]};
const before=JSON.stringify(row),bundle=C.exportBundle([row],{scope:'filtered',section:'discussion',exportedAtUTC:'2026-01-01T00:00:00Z',settings:{timeZone:'Pacific/Honolulu',dateFormat:'iso'}});
assert.equal(JSON.stringify(row),before);assert.deepEqual(bundle.records[0].fields,row.fields);
assert.equal(bundle.records[0].createdUTC,'1970-01-01T00:00:00.000Z');assert.ok(bundle.records[0].displayCreated.startsWith('1969-12-31'));
assert.equal(bundle.count,1);assert.ok(C.csv(bundle).includes('Raw fields JSON'));assert.ok(C.csv(bundle).includes('Pacific/Honolulu'));
""")


class GeneratedNavigationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        fixture = links_tests.LinkedWorkspaceTests()
        fixture.root = self.root
        fixture.artifacts = []
        fixture.app = 'private/var/mobile/Containers/Data/Application/SYNTHETIC-A/'
        fixture.account = fixture.app+'Documents/release02/accountData/alpha/'
        fixture.posts()
        fixture.load()
        self.original = reader.load_records(self.root)
        folder = self.root/'_HTML'
        folder.mkdir()
        self.original_page = '<html><head></head><body><nav>iLEAPP</nav><td>Synthetic cell</td></body></html>'
        (folder/'index.html').write_text(self.original_page)
        (folder/'Reddit_-_Cached_Posts.html').write_text(self.original_page)

    def test_default_build_preserves_database_manifest_and_page_bytes(self):
        files = [self.root/'_lava_artifacts.db',self.root/'_lava_data.lava',self.root/'_HTML/index.html']
        before = [hashlib.sha256(path.read_bytes()).digest() for path in files]
        reader.build(self.root)
        self.assertEqual(before,[hashlib.sha256(path.read_bytes()).digest() for path in files])
        page = (self.root/'Reddit_Reader.html').read_text()
        self.assertIn('function csvCell',page)
        self.assertIn('font-family:Roboto',page)
        self.assertNotIn('__REPORT_FONTS__',page)
        self.assertNotIn('__CONTROLS__',page)

    def test_explicit_navigation_is_idempotent_and_preserves_original_rows(self):
        reader.build(self.root,navigation=True)
        once = json.loads((self.root/'_lava_data.lava').read_text())
        reader.build(self.root,navigation=True)
        self.assertEqual(once,json.loads((self.root/'_lava_data.lava').read_text()))
        self.assertEqual(self.original,reader.load_records(self.root))
        with sqlite3.connect(self.root/'_lava_artifacts.db') as db:
            self.assertEqual(db.execute('SELECT count(*) FROM reddit_reader_navigation').fetchone()[0],1)
            item = db.execute("SELECT extraction_path,type,source_path FROM _lava_media_items").fetchone()
            self.assertEqual(item[0:2],('Reddit_Reader.html','text/html'))
            self.assertIn('Generated',item[2])
            self.assertTrue((self.root/'_HTML'/item[0]).is_file())
        page = (self.root/'_HTML/index.html').read_text()
        self.assertEqual(page.count('id="reddit-reader-link"'),1)
        self.assertIn('href="Reddit_Reader.html"',page)
        self.assertTrue((self.root/'_Reader_Originals/_lava_data.lava').is_file())
        with sqlite3.connect(self.root/'_Reader_Originals/_lava_artifacts.db') as backup:
            self.assertEqual(backup.execute('SELECT count(*) FROM reddit_cached_posts').fetchone()[0],1)

    def test_incomplete_backup_blocks_integration_without_changing_originals(self):
        backup = self.root/'_Reader_Originals'
        backup.mkdir()
        (backup/'_lava_data.lava').write_text('{}')
        database = self.root/'_lava_artifacts.db'
        before = database.read_bytes()
        with self.assertRaisesRegex(ValueError, 'Incomplete original report backup'):
            reader.add_navigation(self.root)
        self.assertEqual(database.read_bytes(), before)

    def test_backup_copy_failure_never_publishes_a_partial_backup(self):
        database = self.root/'_lava_artifacts.db'
        before = database.read_bytes()
        with mock.patch.object(reader.shutil, 'copy2', side_effect=OSError('fabricated copy error')):
            with self.assertRaisesRegex(OSError, 'fabricated copy error'):
                reader.add_navigation(self.root)
        self.assertFalse((self.root/'_Reader_Originals').exists())
        self.assertEqual(database.read_bytes(), before)

    def test_existing_media_reference_is_not_silently_overwritten(self):
        with sqlite3.connect(self.root/'_lava_artifacts.db') as db:
            db.execute('CREATE TABLE _lava_media_references (id TEXT PRIMARY KEY, media_item_id, module_name, artifact_name, name)')
            db.execute("INSERT INTO _lava_media_references VALUES ('reddit-reader-generated-reference-v1','foreign','Other','Other','Preserve')")
        with self.assertRaisesRegex(ValueError, 'reference is already in use'):
            reader.add_navigation(self.root)
        with sqlite3.connect(self.root/'_lava_artifacts.db') as db:
            self.assertEqual(db.execute('SELECT media_item_id FROM _lava_media_references').fetchone()[0], 'foreign')

    def test_navigation_rejects_an_unrelated_manifest_module(self):
        path = self.root/'_lava_data.lava'
        manifest = json.loads(path.read_text())
        manifest['meta'] = {'modules': [{'module_name':'RedditReader','module_filename':'unrelated.py'}]}
        path.write_text(json.dumps(manifest))
        original = path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'module name is already in use'):
            reader.add_navigation(self.root)
        self.assertEqual(path.read_bytes(), original)

    def test_navigation_rejects_a_nonstandard_destination(self):
        with self.assertRaisesRegex(ValueError, 'standard report-local'):
            reader.build(self.root, output=self.root/'other.html', navigation=True)
        self.assertFalse((self.root/'other.html').exists())

    def test_existing_navigation_table_is_not_silently_overwritten(self):
        with sqlite3.connect(self.root/'_lava_artifacts.db') as db:
            db.execute('CREATE TABLE reddit_reader_navigation (original TEXT)')
            db.execute("INSERT INTO reddit_reader_navigation VALUES ('Preserve')")
        with self.assertRaisesRegex(ValueError,'already in use'):
            reader.add_navigation(self.root)
        with sqlite3.connect(self.root/'_lava_artifacts.db') as db:
            self.assertEqual(db.execute('SELECT original FROM reddit_reader_navigation').fetchone()[0],'Preserve')


if __name__ == '__main__':
    unittest.main()
