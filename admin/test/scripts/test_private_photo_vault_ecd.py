"""Fabricated ECD and Crashlytics records; no private values or media."""
import fnmatch
import hashlib
import inspect
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.artifacts import privatePhotoVaultEcd as parser


class Context:
    def __init__(self, root, name):
        self.root = root
        self.files = [str(p) for p in root.rglob('*') if p.is_file() and any(
            fnmatch.fnmatchcase(str(p), pat) for pat in parser.__artifacts_v2__[name]['paths'])]

    def get_files_found(self):
        return self.files + self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def run(root, name):
    headers, rows, _ = inspect.unwrap(getattr(parser, name))(Context(root, name))
    assert all(len(row) == len(headers) for row in rows)
    return [dict(zip([h[0] if isinstance(h, tuple) else h for h in headers], r)) for r in rows]


def store(root, container='alpha'):
    p = root / 'private/var/mobile/Containers/Data/Application' / container / 'Library/PPV.ecd.decrypted'
    p.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(p) as db:
        db.execute('CREATE TABLE ecdPersistentMediaItem (__objectid INTEGER,syncId,albumSyncId,createdDate,modifiedDate,l_viewCount,encryptionKey)')
        db.executemany('INSERT INTO ecdPersistentMediaItem VALUES (?,?,?,?,?,?,?)', [
            (1, 'media-a', 'album-a', 1700000000.25, 1700000001.5, 0, 'synthetic-secret'),
            (2, 'media-b', 'album-a', 1700000000, None, None, None),
            (3, 'media-c', 'album-a', 'bad', 1700000001, 5, None)])
        db.execute('CREATE TABLE ecdPersistentAlbum (__objectid,title,createdDate,syncId,password)')
        db.execute('INSERT INTO ecdPersistentAlbum VALUES (1,\'Synthetic album\',1700000000,\'album-a\',\'synthetic-password\')')
    return p


class ParserTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_counts_nulls_fractional_epochs_and_secrets(self):
        tmp_path = self.root
        p = store(tmp_path)
        before = hashlib.sha256(p.read_bytes()).digest()
        rows = run(tmp_path, 'ppv_ecd_media')
        assert [r['View Count'] for r in rows] == [0, None, 5]
        assert rows[0]['Created'].year == 2023
        assert rows[0]['Created'].microsecond == 250000
        assert rows[2]['Created'] == ''
        assert 'synthetic-secret' not in str(rows)
        albums = run(tmp_path, 'ppv_ecd_albums')
        assert len(albums) == 1
        assert 'synthetic-password' not in str(albums)
        assert hashlib.sha256(p.read_bytes()).digest() == before

    def test_partial_read_reports_rows_emitted_and_keeps_good_prefix(self):
        def damaged_rows():
            yield (1,'synthetic')
            raise sqlite3.DatabaseError('synthetic failure after first row')
        with patch.object(parser,'open_sqlite_db_readonly') as opener, patch.object(parser,'logfunc') as log:
            cursor = opener.return_value.cursor.return_value
            cursor.description = [('id',),('value',)]
            cursor.__iter__.side_effect = damaged_rows
            opener.return_value.execute.side_effect = [opener.return_value,cursor]
            opener.return_value.fetchone.return_value = (1,)
            rows = list(parser._rows('synthetic.db','synthetic','synthetic/store'))  # pylint: disable=protected-access
        self.assertEqual(rows,[{'id':1,'value':'synthetic'}])
        self.assertIn('read incomplete; rows emitted=1',log.call_args.args[0])
        opener.return_value.close.assert_called_once()

    def test_multiple_containers_keep_identical_syncids(self):
        tmp_path = self.root
        store(tmp_path, 'alpha')
        store(tmp_path, 'beta')
        assert len(run(tmp_path, 'ppv_ecd_media')) == 6

    def test_encrypted_store_not_opened_as_sqlite(self):
        tmp_path = self.root
        p = tmp_path / 'Library/PPV.ecd'
        p.parent.mkdir()
        p.write_bytes(b'not sqlite, synthetic encrypted stand-in')
        assert run(tmp_path, 'ppv_ecd_media') == []

    def test_wal_store_rows_are_visible_without_changing_source(self):
        tmp_path = self.root
        p = store(tmp_path)
        db = sqlite3.connect(p)
        try:
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('PRAGMA wal_autocheckpoint=0')
            db.execute('UPDATE ecdPersistentMediaItem SET l_viewCount=9 WHERE __objectid=1')
            db.commit()
            wal = Path(str(p) + '-wal')
            before = [hashlib.sha256(x.read_bytes()).digest() for x in [p, wal]]
            assert run(tmp_path, 'ppv_ecd_media')[0]['View Count'] == 9
            assert before == [hashlib.sha256(x.read_bytes()).digest() for x in [p, wal]]
        finally:
            db.close()

    def test_nonfinite_epochs_do_not_raise(self):
        for value in (True, float('nan'), float('inf'), 1e99):
            assert parser._seconds(value) == ''  # pylint: disable=protected-access

    @unittest.skipUnless(os.environ.get("ILEAPP_LOCAL_IMAGE"), "private corpus not supplied")
    def test_local_corpus_shapes(self):
        root = Path(os.environ["ILEAPP_LOCAL_IMAGE"])
        if not root.is_dir():
            self.skipTest("this check expects a reconstructed filesystem directory")
        for name in parser.__artifacts_v2__:
            context = Context(root, name)
            headers, rows, _ = inspect.unwrap(getattr(parser, name))(context)
            self.assertTrue(all(len(row) == len(headers) for row in rows), "row shape mismatch")

    def test_diagnostic_hex_utf8_and_bad_lines(self):
        path = self.root / 'Library/Caches/com.crashlytics.data/com.enchantedcloud.photovault/v5/report/log_a.clsrecord'
        path.parent.mkdir(parents=True)
        text = 'Synthetic unlock: ✓'
        path.write_text(json.dumps({'log': {'msg': text.encode().hex(), 'time': 1700000000125}})
                        + '\n{\n' + json.dumps({'log': {'msg': 'not hex', 'time': 1700000001000}}))
        rows = run(self.root, 'ppv_diagnostic_log')
        assert len(rows) == 2
        assert rows[0]['Message'] == text
        assert rows[0]['Log Time'].microsecond == 125000
        assert rows[1]['Line Number'] == 3
        assert rows[1]['Message Hex'] == 'not hex'
        assert rows[1]['Message'] == ''

    def test_foreign_diagnostic_directory_not_selected(self):
        path = self.root / 'Library/Caches/com.crashlytics.data/com.example.other/v5/report/log_a.clsrecord'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'log': {'msg': '74657374', 'time': 1700000000000}}))
        assert run(self.root, 'ppv_diagnostic_log') == []

    def test_oversized_diagnostic_time_and_shape_errors_are_isolated(self):
        huge = 10**399
        path = self.root/'Library/Caches/com.crashlytics.data/com.enchantedcloud.photovault/v5/report/log_a.clsrecord'
        path.parent.mkdir(parents=True)
        entries = [{'log': {'msg': '74657374', 'time': stamp}} for stamp in (1700000000000, huge, 1700000001000)]
        entries += [{'log': []}, {'log': {'msg': 12}}]
        path.write_text('\n'.join(json.dumps(e) for e in entries))
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root, 'ppv_diagnostic_log')
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1]['Log Time'], '')
        self.assertEqual(rows[1]['Raw Time (Unix milliseconds)'], str(huge))
        messages = [c.args[0] for c in log.call_args_list]
        self.assertTrue(all(path.relative_to(self.root).as_posix() in msg for msg in messages))
        self.assertTrue(all(str(self.root) not in msg for msg in messages))
        for line in (2, 4, 5):
            self.assertTrue(any(f'line={line}' in msg for msg in messages))

    def test_seconds_handles_huge_integers_for_both_units(self):
        for value in (10**399, -(10**399), True, float('nan'), float('inf')):
            for divisor in (1, 1000):
                with self.subTest(value_type=type(value).__name__, divisor=divisor):
                    self.assertEqual(parser._seconds(value, divisor), '')  # pylint: disable=protected-access

    def test_unverified_schema_does_not_claim_signatures_are_absent(self):
        path = store(self.root)
        with sqlite3.connect(path) as db:
            for table in parser.ECD_SIGNATURES:
                db.execute('DROP TABLE "'+table+'"')
            db.execute('CREATE VIEW ecdPersistentMediaItem AS SELECT * FROM missing_source')
        with patch.object(parser, 'logfunc') as log:
            self.assertEqual(run(self.root,'ppv_ecd_albums'),[])
        messages = [c.args[0] for c in log.call_args_list]
        self.assertTrue(any('could not verify ECD schema' in m for m in messages))
        self.assertFalse(any('no supported ECD table signature' in m for m in messages))

    def test_zero_dates_blank_without_converting_zero_counters_to_null(self):
        path = store(self.root)
        with sqlite3.connect(path) as db:
            db.execute('UPDATE ecdPersistentMediaItem SET createdDate=0,modifiedDate=0 WHERE __objectid=1')
            db.execute('UPDATE ecdPersistentAlbum SET createdDate=0')
        row = run(self.root, 'ppv_ecd_media')[0]
        self.assertEqual(row['Created'], '')
        self.assertEqual(row['Modified'], '')
        self.assertEqual(row['View Count'], 0)
        self.assertEqual(json.loads(row['Metadata JSON'])['createdDate'], 0)
        self.assertEqual(run(self.root, 'ppv_ecd_albums')[0]['Created'], '')

    def test_readable_headers_and_opaque_codes(self):
        store(self.root)
        media = run(self.root, 'ppv_ecd_media')[0]
        albums = run(self.root, 'ppv_ecd_albums')[0]
        for label in ['Created', 'Media ID', 'Album ID', 'View Count', 'File Extension']:
            self.assertIn(label, media)
        for label in ['Created', 'Album ID', 'Title', 'Parent Album ID']:
            self.assertIn(label, albums)
        self.assertIn('File Type (as stored)', media)
        self.assertIn('Album Type (as stored)', albums)
        self.assertNotIn('Album ID (as stored)', albums)
        self.assertEqual(set(parser.__artifacts_v2__), {'ppv_ecd_albums', 'ppv_ecd_media', 'ppv_diagnostic_log'})

    def test_absent_optional_album_table_is_distinct_from_read_failure(self):
        path = store(self.root)
        with sqlite3.connect(path) as db:
            db.execute('DROP TABLE ecdPersistentAlbum')
        with patch.object(parser, 'logfunc') as log:
            self.assertEqual(run(self.root, 'ppv_ecd_albums'), [])
        messages = [c.args[0] for c in log.call_args_list]
        self.assertTrue(any('table not present; table=ecdPersistentAlbum' in m for m in messages))
        self.assertFalse(any('unreadable' in m for m in messages))

    def test_unreadable_media_signature_does_not_hide_good_album(self):
        path = store(self.root)
        with sqlite3.connect(path) as db:
            db.execute('DROP TABLE ecdPersistentMediaItem')
            db.execute('CREATE VIEW ecdPersistentMediaItem AS SELECT * FROM missing_source')
        with patch.object(parser, 'logfunc') as log:
            self.assertEqual(len(run(self.root, 'ppv_ecd_albums')), 1)
        self.assertTrue(any('unreadable ECD schema' in c.args[0] for c in log.call_args_list))
        self.assertFalse(any('no supported ECD table signature' in c.args[0] for c in log.call_args_list))

    def test_zero_diagnostic_time_blank_and_raw_zero_retained(self):
        path = self.root / 'Library/Caches/com.crashlytics.data/com.enchantedcloud.photovault/v5/report/log_a.clsrecord'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'log': {'msg': '74657374', 'time': 0}}))
        with patch.object(parser, 'logfunc') as log:
            row = run(self.root, 'ppv_diagnostic_log')[0]
        self.assertEqual(row['Log Time'], '')
        self.assertEqual(row['Raw Time (Unix milliseconds)'], 0)
        self.assertFalse(log.called)

    def test_removed_tables_alone_do_not_qualify_as_supported_ecd(self):
        path = self.root / 'Library/PPV.ecd.decrypted'
        path.parent.mkdir()
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE ecdPersistentMediaItemPart (__objectid,syncId,mediaItemSyncId)')
        with patch.object(parser, 'logfunc'):
            self.assertEqual(run(self.root, 'ppv_ecd_media'), [])
