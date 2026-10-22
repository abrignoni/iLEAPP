"""Fabricated PPV ECD and analytics stores; no private values or binaries."""
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
        db.execute('CREATE TABLE ecdPersistentMediaItemPart (__objectid,syncId,mediaItemSyncId,size,contentHash)')
        db.execute('INSERT INTO ecdPersistentMediaItemPart VALUES (1,\'part-a\',\'media-a\',0,\'synthetic-hash\')')
        db.execute('CREATE TABLE ecdPersistentTresspassRecord (__objectid,date,loginType,fileName)')
        db.execute('INSERT INTO ecdPersistentTresspassRecord VALUES (1,1700000000.5,7,\'synthetic.enc\')')
    return p


def analytics(root, events, container='alpha'):
    p = root / 'private/var/mobile/Containers/Data/Application' / container / 'Library/demo_MPDB.sqlite'
    p.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(p) as db:
        db.execute('CREATE TABLE mixpanel_demo_events (id INTEGER PRIMARY KEY,data,time)')
        for event in events:
            db.execute('INSERT INTO mixpanel_demo_events(data,time) VALUES (?,?)', (json.dumps(event), 99))
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
        assert [r['l_viewCount (as stored)'] for r in rows] == [0, None, 5]
        assert rows[0]['createdDate'].year == 2023
        assert rows[0]['createdDate'].microsecond == 250000
        assert rows[2]['createdDate'] == ''
        assert 'synthetic-secret' not in str(rows)
        albums = run(tmp_path, 'ppv_ecd_albums')
        assert len(albums) == 1
        assert 'synthetic-password' not in str(albums)
        assert hashlib.sha256(p.read_bytes()).digest() == before


    def test_absent_optional_table_is_distinct_from_sqlite_read_failure(self):
        path = store(self.root)
        with sqlite3.connect(path) as db:
            db.execute('DROP TABLE ecdPersistentMediaItemPart')
        with patch.object(parser, 'logfunc') as log:
            self.assertEqual(run(self.root, 'ppv_ecd_parts'), [])
        messages = [call.args[0] for call in log.call_args_list]
        self.assertTrue(any('table not present; table=ecdPersistentMediaItemPart' in m for m in messages))
        self.assertFalse(any('unreadable' in m for m in messages))
        with patch.object(parser, 'open_sqlite_db_readonly') as opener, patch.object(parser, 'logfunc') as log:
            opener.return_value.execute.side_effect = sqlite3.DatabaseError('synthetic failure')
            self.assertEqual(list(parser._rows(path, 'ecdPersistentMediaItemPart', 'synthetic/store')), [])  # pylint: disable=protected-access
        self.assertIn('unsupported or unreadable', log.call_args.args[0])
        opener.return_value.close.assert_called_once()

    def test_multiple_containers_keep_identical_syncids(self):
        tmp_path = self.root
        store(tmp_path, 'alpha')
        store(tmp_path, 'beta')
        assert len(run(tmp_path, 'ppv_ecd_media')) == 6


    def test_part_and_trespass_synthetic_only(self):
        tmp_path = self.root
        store(tmp_path)
        assert run(tmp_path, 'ppv_ecd_parts')[0]['size (as stored)'] == 0
        row = run(tmp_path, 'ppv_ecd_trespass')[0]
        assert row['loginType (as stored)'] == 7
        assert row['date'].microsecond == 500000


    def test_mixed_units_and_session_metrics_are_separate(self):
        tmp_path = self.root
        store(tmp_path)
        analytics(tmp_path, [
            {'event': 'app_unlock', 'properties': {'time': 1700000000.125,
                                                 'bundleId': 'com.enchantedcloud.photovault'}},
            {'event': '$ae_session', 'properties': {'time': 1700000000125,
                '$ae_session_length': 12, 'sessionParams': {'bundleId': 'com.enchantedcloud.photovault',
                'itemsViewed': 8, 'albumsViewed': 0, 'timeSpent': {'gallery': 0, 'thumbnails': 4.5}}}},
        ])
        rows = run(tmp_path, 'ppv_activity_events')
        assert [r['Time Divisor'] for r in rows] == [1, 1000]
        assert rows[0]['Event Time'] == rows[1]['Event Time']
        assert rows[0]['SQL Queue Time Raw'] == 99
        assert rows[0]['itemsViewed (as stored)'] is None
        assert rows[1]['itemsViewed (as stored)'] == 8
        assert rows[1]['timeSpent.gallery (as stored)'] == 0


    def test_foreign_and_unattributed_events_excluded(self):
        tmp_path = self.root
        store(tmp_path)
        analytics(tmp_path, [{'event': 'other', 'properties': {'bundleId': 'com.example.other'}},
                             {'event': 'sibling', 'properties': {'time': 1700000000}}])
        analytics(tmp_path, [{'event': 'unknown', 'properties': {'time': 1700000000}}], 'other')
        rows = run(tmp_path, 'ppv_activity_events')
        assert [r['Event Name (as stored)'] for r in rows] == ['sibling']


    def test_bundle_identity_without_ecd_and_invalid_time_retained(self):
        tmp_path = self.root
        analytics(tmp_path, [{'event': 'app_unlock', 'properties': {
            'bundleId': 'com.enchantedcloud.photovault', 'time': 'invalid'}}])
        row = run(tmp_path, 'ppv_activity_events')[0]
        assert row['Event Time'] == ''
        assert row['properties.time Raw'] == 'invalid'


    def test_encrypted_store_not_opened_as_sqlite(self):
        tmp_path = self.root
        p = tmp_path / 'Library/PPV.ecd'
        p.parent.mkdir()
        p.write_bytes(b'not sqlite, synthetic encrypted stand-in')
        assert run(tmp_path, 'ppv_ecd_media') == []


    def test_malformed_events_do_not_abort_following_rows(self):
        tmp_path = self.root
        p = analytics(tmp_path, [{'event': 'ok', 'properties': {'bundleId': 'com.enchantedcloud.photovault'}}])
        with sqlite3.connect(p) as db:
            db.execute('INSERT INTO mixpanel_demo_events(data,time) VALUES (\'{\',0)')
            db.execute('INSERT INTO mixpanel_demo_events(data,time) VALUES (\'[]\',0)')
        assert len(run(tmp_path, 'ppv_activity_events')) == 1


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
            assert run(tmp_path, 'ppv_ecd_media')[0]['l_viewCount (as stored)'] == 9
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


class AuditRegressionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_bad_table_first_does_not_hide_later_valid_table(self):
        path = self.root/'private/var/mobile/Containers/Data/Application/alpha/Library/demo_MPDB.sqlite'
        path.parent.mkdir(parents=True)
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE mixpanel_aaa_events (id, payload)')
            db.execute('CREATE TABLE mixpanel_bbb_events (id, data, time)')
            for n in range(6):
                db.execute('INSERT INTO mixpanel_bbb_events VALUES (?,?,?)', (n, json.dumps({
                    'event': f'good-{n}', 'properties': {'bundleId': parser.BUNDLE_ID, 'time': 1700000000}}), 99))
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root, 'ppv_activity_events')
        self.assertEqual(len(rows), 6)
        self.assertEqual([r['Event Row ID'] for r in rows], list(range(6)))
        self.assertTrue(any(path.relative_to(self.root).as_posix() in c.args[0] and 'mixpanel_aaa_events' in c.args[0] for c in log.call_args_list))

    def test_identity_matrix_rejects_any_explicit_foreign_id(self):
        store(self.root)
        events = []
        accepted = set()
        for outer in (None, '', parser.BUNDLE_ID, 'com.example.other'):
            for inner in (None, '', parser.BUNDLE_ID, 'com.example.other'):
                name = str(len(events))
                events.append({'event': name, 'properties': {'time': 1700000000,
                    'bundleId': outer, 'sessionParams': {'bundleId': inner}}})
                if outer != 'com.example.other' and inner != 'com.example.other':
                    accepted.add(name)
        analytics(self.root, events)
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root, 'ppv_activity_events')
        self.assertEqual({r['Event Name (as stored)'] for r in rows}, accepted)
        self.assertEqual(len([c for c in log.call_args_list if 'foreign/conflicting' in c.args[0]]), 7)
        self.assertTrue(all('Outer Bundle ID (as stored)' in r and 'Session Bundle ID (as stored)' in r for r in rows))

    def test_oversized_event_time_retains_raw_and_good_neighbors(self):
        huge = 10**399
        analytics(self.root, [{'event': str(n), 'properties': {'bundleId': parser.BUNDLE_ID, 'time': stamp}}
                             for n, stamp in enumerate((1700000000, huge, 1700000001))])
        with patch.object(parser, 'logfunc'):
            rows = run(self.root, 'ppv_activity_events')
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1]['Event Time'], '')
        self.assertEqual(rows[1]['properties.time Raw'], str(huge))
        self.assertEqual(rows[1]['Time Divisor'], 1000)
        self.assertNotEqual(rows[0]['Event Time'], '')
        self.assertNotEqual(rows[2]['Event Time'], '')

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
        self.assertEqual(rows[1]['Time Raw (Unix milliseconds)'], str(huge))
        messages = [c.args[0] for c in log.call_args_list]
        self.assertTrue(all(path.relative_to(self.root).as_posix() in msg for msg in messages))
        self.assertTrue(all(str(self.root) not in msg for msg in messages))
        for line in (2, 4, 5):
            self.assertTrue(any(f'line={line}' in msg for msg in messages))

    def test_unrelated_sqlite_named_ecd_is_not_an_app_marker(self):
        path = self.root/'private/var/mobile/Containers/Data/Application/alpha/Library/PPV.ecd.decrypted'
        path.parent.mkdir(parents=True)
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE unrelated (x)')
        analytics(self.root, [{'event': 'unknown', 'properties': {'time': 1700000000}}])
        with patch.object(parser, 'logfunc') as log:
            self.assertEqual(run(self.root, 'ppv_activity_events'), [])
            self.assertEqual(run(self.root, 'ppv_ecd_media'), [])
        self.assertTrue(any('no supported ECD table signature' in c.args[0] and path.relative_to(self.root).as_posix() in c.args[0] for c in log.call_args_list))

    def test_nonplaintext_store_requires_independent_container_identity(self):
        # This tests identity policy, not a claim to decode genuine ciphertext.
        base = self.root/'private/var/mobile/Containers/Data/Application/alpha'
        (base/'Library').mkdir(parents=True)
        (base/'Library/PPV.ecd').write_bytes(b'synthetic non-SQLite stand-in')
        analytics(self.root, [{'event': 'unlabelled', 'properties': {'time': 1700000000}}])
        with patch.object(parser, 'logfunc'):
            self.assertEqual(run(self.root, 'ppv_activity_events'), [])
        marker = base/'.com.apple.mobile_container_manager.metadata.plist'
        marker.write_bytes(plistlib.dumps({'MCMMetadataIdentifier': parser.BUNDLE_ID}))
        with patch.object(parser, 'logfunc'):
            rows = run(self.root, 'ppv_activity_events')
            self.assertEqual(run(self.root, 'ppv_ecd_media'), [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['App Association'], 'Container metadata bundle ID')
        marker.write_bytes(plistlib.dumps({'MCMMetadataIdentifier': 'com.example.other'}))
        with patch.object(parser, 'logfunc'):
            self.assertEqual(run(self.root, 'ppv_activity_events'), [])
        marker.unlink()
        nested = base/'Library/.com.apple.mobile_container_manager.metadata.plist'
        nested.write_bytes(plistlib.dumps({'MCMMetadataIdentifier': parser.BUNDLE_ID}))
        with patch.object(parser, 'logfunc'):
            self.assertEqual(run(self.root, 'ppv_activity_events'), [])

    def test_seconds_handles_huge_integers_for_both_units(self):
        for value in (10**399, -(10**399), True, float('nan'), float('inf')):
            for divisor in (1, 1000):
                with self.subTest(value_type=type(value).__name__, divisor=divisor):
                    self.assertEqual(parser._seconds(value, divisor), '')  # pylint: disable=protected-access


class ContainerMetadataTests(unittest.TestCase):
    def test_malformed_metadata_does_not_hide_explicitly_identified_events(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = analytics(root, [{'event': 'good', 'properties': {
                'bundleId': parser.BUNDLE_ID, 'time': 1700000000}}])
            marker = path.parent.parent/'.com.apple.mobile_container_manager.metadata.plist'
            marker.write_bytes(b'<?xml version="1.0"?><plist><dict>')
            with patch.object(parser, 'logfunc') as log:
                rows = run(root, 'ppv_activity_events')
            self.assertEqual(len(rows), 1)
            self.assertTrue(any(marker.relative_to(root).as_posix() in c.args[0] for c in log.call_args_list))


class WriterContractTests(unittest.TestCase):
    def test_oversized_raw_fields_survive_real_lava_writer(self):
        from scripts import lavafuncs  # pylint: disable=import-outside-toplevel
        from scripts.context import Context as ReportContext  # pylint: disable=import-outside-toplevel
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            huge = 10**399
            analytics(root, [{'event': str(n), 'properties': {'bundleId': parser.BUNDLE_ID,
                'time': stamp}} for n, stamp in enumerate((1700000000, huge, 1700000001))])
            log = root/'Library/Caches/com.crashlytics.data/com.enchantedcloud.photovault/v5/report/log_a.clsrecord'
            log.parent.mkdir(parents=True)
            log.write_text('\n'.join(json.dumps({'log': {'msg': '74657374', 'time': stamp}})
                                     for stamp in (1700000000000, huge, 1700000001000)))
            try:
                lavafuncs.initialize_lava(str(root), str(root), 'fs')
                for name, raw_column in (('ppv_activity_events', 'properties.time Raw'),
                                         ('ppv_diagnostic_log', 'Time Raw (Unix milliseconds)')):
                    headers, rows, _ = inspect.unwrap(getattr(parser, name))(Context(root, name))
                    ReportContext.set_artifact_info(parser.__artifacts_v2__[name])
                    ReportContext.set_module_file_path('scripts/artifacts/privatePhotoVaultEcd.py')
                    table, objects, column_map = lavafuncs.lava_process_artifact(
                        'Private Photo Vault', 'privatePhotoVaultEcd', name, headers,
                        record_count=len(rows), func_name=name)
                    lavafuncs.lava_insert_sqlite_data(table, rows, objects, headers, column_map)
                    lavafuncs.lava_db.commit()
                    raw_sql = next(sql for sql, label in column_map.items() if label == raw_column)
                    values = lavafuncs.lava_db.execute(f'SELECT "{raw_sql}" FROM "{table}"').fetchall()
                    self.assertEqual(len(values), 3)
                    self.assertEqual(values[1][0], str(huge))
            finally:
                if lavafuncs.lava_db is not None:
                    lavafuncs.lava_db.close()
                    lavafuncs.lava_db = None
                lavafuncs.lava_data = None
                ReportContext.clear()


class ContainerIdentityTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def metadata(self, bundle):
        path = self.root/'private/var/mobile/Containers/Data/Application/alpha/.com.apple.mobile_container_manager.metadata.plist'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(plistlib.dumps({'MCMMetadataIdentifier': bundle}))

    def test_matching_metadata_and_store_keep_all_supporting_bases(self):
        store(self.root)
        self.metadata(parser.BUNDLE_ID)
        analytics(self.root, [
            {'event': 'labelled', 'properties': {'bundleId': parser.BUNDLE_ID, 'time': 1700000000}},
            {'event': 'unlabelled', 'properties': {'bundleId': None, 'time': 1700000001}}])
        rows = run(self.root, 'ppv_activity_events')
        expected = 'Verified ECD schema in same container; Container metadata bundle ID'
        self.assertEqual(rows[0]['App Association'], 'Event bundle ID; '+expected)
        self.assertEqual(rows[1]['App Association'], expected)
        self.assertTrue(all(r['Container Bundle ID (as stored)'] == parser.BUNDLE_ID for r in rows))
        self.assertTrue(all(r['Container Identity Status'] == 'Container metadata matches' for r in rows))

    def test_labelled_event_in_foreign_container_is_kept_and_flagged(self):
        self.metadata('com.example.other')
        path = analytics(self.root, [
            {'event': 'labelled', 'properties': {'bundleId': parser.BUNDLE_ID, 'time': 1700000000}},
            {'event': 'unknown', 'properties': {'time': 1700000001}}])
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root, 'ppv_activity_events')
        self.assertEqual([r['Event Name (as stored)'] for r in rows], ['labelled'])
        self.assertEqual(rows[0]['Container Bundle ID (as stored)'], 'com.example.other')
        self.assertEqual(rows[0]['Container Identity Status'], 'Conflict: container metadata names another app')
        self.assertEqual(rows[0]['App Association'], 'Event bundle ID')
        messages = [c.args[0] for c in log.call_args_list]
        self.assertTrue(any('conflicts with container metadata' in msg for msg in messages))
        self.assertTrue(all(str(self.root) not in msg for msg in messages))
        self.assertTrue(all(path.relative_to(self.root).as_posix() in msg for msg in messages))

    def test_verified_store_with_foreign_metadata_retains_the_contradiction(self):
        store(self.root)
        self.metadata('com.example.other')
        analytics(self.root, [{'event': 'unlabelled', 'properties': {'time': 1700000000}}])
        with patch.object(parser, 'logfunc'):
            row = run(self.root, 'ppv_activity_events')[0]
        self.assertEqual(row['App Association'], 'Verified ECD schema in same container')
        self.assertEqual(row['Container Identity Status'], 'Conflict: container metadata names another app')

    def test_absent_metadata_is_not_reported_as_agreement(self):
        analytics(self.root, [{'event': 'labelled', 'properties': {'bundleId': parser.BUNDLE_ID, 'time': 1700000000}}])
        row = run(self.root, 'ppv_activity_events')[0]
        self.assertEqual(row['Container Identity Status'], 'Container metadata unavailable')
        self.assertIsNone(row['Container Bundle ID (as stored)'])
