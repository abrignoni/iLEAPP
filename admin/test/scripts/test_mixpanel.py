"""Fabricated multi-app Mixpanel queues; no case data or identifiers."""
import fnmatch
import hashlib
import inspect
import json
import plistlib
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.artifacts import mixpanel as parser


class Context:
    def __init__(self, root):
        self.root = root
        self.files = [str(p) for p in root.rglob('*') if p.is_file() and any(
            fnmatch.fnmatchcase(str(p), pat) for pat in parser.__artifacts_v2__['mixpanel_events']['paths'])]

    def get_files_found(self):
        return self.files + self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def run(root):
    headers, rows, _ = inspect.unwrap(parser.mixpanel_events)(Context(root))
    assert all(len(row) == len(headers) for row in rows)
    return [dict(zip([h[0] if isinstance(h, tuple) else h for h in headers], r)) for r in rows]


def analytics(root, events, container='alpha'):
    p = root / 'private/var/mobile/Containers/Data/Application' / container / 'Library/demo_MPDB.sqlite'
    p.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(p) as db:
        db.execute('CREATE TABLE mixpanel_demo_events (id INTEGER PRIMARY KEY,data,time)')
        for event in events:
            db.execute('INSERT INTO mixpanel_demo_events(data,time) VALUES (?,?)', (json.dumps(event), 99))
    return p


def metadata(root, bundle, container='alpha', nested=False):
    path = root / 'private/var/mobile/Containers/Data/Application' / container
    if nested:
        path /= 'Library'
    path /= '.com.apple.mobile_container_manager.metadata.plist'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(plistlib.dumps({'MCMMetadataIdentifier': bundle}))
    return path


class MixpanelTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_multiple_apps_and_unknown_apps_retained_without_log_noise(self):
        for n, bundle in enumerate(['com.example.alpha', 'com.example.beta', None]):
            analytics(self.root, [{'event': 'synthetic', 'properties': {'time': 1700000000, 'bundleId': bundle}}], str(n))
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root)
        self.assertEqual(len(rows), 3)
        self.assertEqual({r['Bundle ID'] for r in rows}, {'com.example.alpha', 'com.example.beta', None})
        self.assertFalse(log.called)

    def test_unlabelled_event_uses_only_direct_container_metadata(self):
        analytics(self.root, [{'event': 'synthetic', 'properties': {'time': 1700000000}}])
        metadata(self.root, 'com.example.nested', nested=True)
        self.assertIsNone(run(self.root)[0]['Bundle ID'])
        metadata(self.root, 'com.example.alpha')
        row = run(self.root)[0]
        self.assertEqual(row['Bundle ID'], 'com.example.alpha')
        self.assertEqual(row['Bundle ID Source'], 'Container metadata')

    def test_identity_matrix_retains_all_rows_and_exposes_conflicts(self):
        values = [None, '', 'com.example.alpha', 'com.example.beta', 7, False, {'invalid': True}]
        events = [{'event': str(n), 'properties': {'time': 1700000000, 'bundleId': outer,
                   'sessionParams': {'bundleId': inner}}}
                  for n, (outer, inner) in enumerate((o, i) for o in values for i in values)]
        analytics(self.root, events)
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root)
        self.assertEqual(len(rows), 49)
        self.assertFalse(log.called)
        for row, event in zip(rows, events):
            props = event['properties']
            outer, inner = props['bundleId'], props['sessionParams']['bundleId']
            candidates = {v for v in (outer, inner) if isinstance(v, str) and v}
            if len(candidates) > 1:
                self.assertIsNone(row['Bundle ID'])
                self.assertIn('Conflict', row['Bundle ID Status'])
            elif candidates:
                self.assertEqual(row['Bundle ID'], next(iter(candidates)))
            else:
                self.assertIsNone(row['Bundle ID'])
            self.assertEqual(json.loads(row['Event JSON']), event)

    def test_event_and_container_conflict_is_visible_without_rejecting_row(self):
        metadata(self.root, 'com.example.container')
        analytics(self.root, [{'event': 'synthetic', 'properties': {'time': 1700000000, 'bundleId': 'com.example.event'}}])
        with patch.object(parser, 'logfunc') as log:
            row = run(self.root)[0]
        self.assertEqual(row['Bundle ID'], 'com.example.event')
        self.assertEqual(row['Container Bundle ID'], 'com.example.container')
        self.assertIn('Conflict', row['Bundle ID Status'])
        self.assertFalse(log.called)

    def test_mixed_units_metrics_and_sdk_fields_are_preserved(self):
        analytics(self.root, [
            {'event': 'one', 'properties': {'time': 1700000000.125, 'bundleId': 'com.example.alpha'}},
            {'event': 'two', 'properties': {'time': 1700000000125, '$ae_session_length': 12,
             'mp_lib': 'iphone', '$lib_version': 'synthetic', 'sessionParams': {
                 'bundleId': 'com.example.beta', 'itemsViewed': 8, 'albumsViewed': 0,
                 'timeSpent': {'gallery': 0, 'thumbnails': 4.5}}}}])
        rows = run(self.root)
        self.assertEqual([r['Time Divisor'] for r in rows], [1, 1000])
        self.assertEqual(rows[0]['Event Time'], rows[1]['Event Time'])
        self.assertEqual(rows[0]['Raw Queue Time'], 99)
        session = json.loads(rows[1]['Event JSON'])['properties']['sessionParams']
        self.assertEqual(session['itemsViewed'], 8)
        self.assertEqual(session['albumsViewed'], 0)
        self.assertEqual(session['timeSpent']['gallery'], 0)
        self.assertEqual(session['bundleId'], 'com.example.beta')
        for label in ['Items Viewed', 'Albums Viewed', 'Thumbnail Time', 'Gallery Time', 'Session Bundle ID']:
            self.assertNotIn(label, rows[1])
        self.assertEqual(rows[1]['SDK Library'], 'iphone')

    def test_zero_date_is_blank_raw_zero_and_zero_metrics_retained(self):
        analytics(self.root, [{'event': 'zero', 'properties': {'time': 0, 'sessionParams': {'itemsViewed': 0}}}])
        with patch.object(parser, 'logfunc') as log:
            row = run(self.root)[0]
        self.assertEqual(row['Event Time'], '')
        self.assertEqual(row['Raw Event Time'], 0)
        self.assertEqual(json.loads(row['Event JSON'])['properties']['sessionParams']['itemsViewed'], 0)
        self.assertFalse(log.called)

    def test_oversized_time_does_not_hide_good_neighbors(self):
        huge = 10**399
        analytics(self.root, [{'event': str(n), 'properties': {'time': t}} for n, t in enumerate((1700000000, huge, 1700000001))])
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1]['Event Time'], '')
        self.assertEqual(rows[1]['Raw Event Time'], str(huge))
        self.assertEqual(rows[1]['Time Divisor'], 1000)
        self.assertEqual(len(log.call_args_list), 1)

    def test_invalid_json_and_shapes_do_not_hide_later_valid_events(self):
        path = analytics(self.root, [])
        entries = ['{', '[]', json.dumps({'event': 'bad', 'properties': []}),
                   json.dumps({'event': 'valid', 'properties': {'time': 1700000000}})]
        with sqlite3.connect(path) as db:
            db.executemany('INSERT INTO mixpanel_demo_events(data,time) VALUES (?,0)', [(s,) for s in entries])
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root)
        self.assertEqual([r['Event'] for r in rows], ['valid'])
        self.assertTrue(all('table=mixpanel_demo_events' in c.args[0] and 'row=' in c.args[0]
                            and str(self.root) not in c.args[0] for c in log.call_args_list))

    def test_bad_table_before_valid_table_does_not_stop_database(self):
        path = analytics(self.root, [{'event': 'valid', 'properties': {'time': 1700000000}}])
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE mixpanel_aaa_events (id, payload)')
            db.execute('CREATE TABLE unrelated (id,data,time)')
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root)
        self.assertEqual([r['Event'] for r in rows], ['valid'])
        self.assertTrue(any('table=mixpanel_aaa_events' in c.args[0] for c in log.call_args_list))

    def test_malformed_metadata_does_not_hide_events(self):
        path = analytics(self.root, [{'event': 'valid', 'properties': {'time': 1700000000}}])
        marker = path.parent.parent / '.com.apple.mobile_container_manager.metadata.plist'
        marker.write_bytes(b'<?xml version="1.0"?><plist><dict>')
        with patch.object(parser, 'logfunc') as log:
            self.assertEqual(len(run(self.root)), 1)
        self.assertTrue(any('unreadable container metadata' in c.args[0] for c in log.call_args_list))

    def test_identical_event_ids_in_different_containers_are_not_merged(self):
        for container in ['alpha', 'beta']:
            analytics(self.root, [{'event': 'same', 'properties': {'time': 1700000000}}], container)
        rows = run(self.root)
        self.assertEqual([r['Event Row ID'] for r in rows], [1, 1])
        self.assertEqual(len({r['Source File'] for r in rows}), 2)

    def test_source_and_wal_bytes_unchanged(self):
        path = analytics(self.root, [{'event': 'first', 'properties': {'time': 1700000000}}])
        db = sqlite3.connect(path)
        try:
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('PRAGMA wal_autocheckpoint=0')
            db.execute('INSERT INTO mixpanel_demo_events(data,time) VALUES (?,0)', (json.dumps({'event': 'wal', 'properties': {'time': 1700000001}}),))
            db.commit()
            sources = [path, Path(str(path) + '-wal')]
            before = [hashlib.sha256(p.read_bytes()).digest() for p in sources]
            self.assertEqual([r['Event'] for r in run(self.root)], ['first', 'wal'])
            self.assertEqual(before, [hashlib.sha256(p.read_bytes()).digest() for p in sources])
        finally:
            db.close()

    def test_seconds_reject_nonfinite_huge_boolean_and_zero(self):
        for v in [10**399, -(10**399), True, False, 0, float('nan'), float('inf')]:
            for divisor in [1, 1000]:
                self.assertEqual(parser._seconds(v, divisor), '')  # pylint: disable=protected-access


class WriterTests(unittest.TestCase):
    def test_oversized_event_and_diagnostic_raw_values_survive_lava(self):
        from scripts import lavafuncs  # pylint: disable=import-outside-toplevel
        from scripts.context import Context as ReportContext  # pylint: disable=import-outside-toplevel
        from scripts.artifacts import crashlytics as crash  # pylint: disable=import-outside-toplevel
        from admin.test.scripts.test_crashlytics import Context as CrashContext  # pylint: disable=import-outside-toplevel
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            huge = 10**399
            analytics(root, [{'event': str(n), 'properties': {'time': t}} for n, t in enumerate((1700000000, huge, 1700000001))])
            log = root/'Library/Caches/com.crashlytics.data/com.enchantedcloud.photovault/v5/report/log_a.clsrecord'
            log.parent.mkdir(parents=True)
            msg = '$A$:{"name":"test","parameters":{}}'.encode().hex()
            log.write_text('\n'.join(json.dumps({'log': {'msg': msg, 'time': t}}) for t in (1700000000000, huge, 1700000001000)))
            try:
                lavafuncs.initialize_lava(str(root), str(root), 'fs')
                for module, name, context, raw_column in [
                    (parser, 'mixpanel_events', Context(root), 'Raw Event Time'),
                    (crash, 'crashlytics_logs', CrashContext(root), 'Raw Time (Unix milliseconds)')]:
                    headers, rows, _ = inspect.unwrap(getattr(module, name))(context)
                    module_name = module.__name__.rsplit('.', 1)[-1]
                    ReportContext.set_artifact_info(module.__artifacts_v2__[name])
                    ReportContext.set_module_file_path('scripts/artifacts/' + module_name + '.py')
                    table, objects, column_map = lavafuncs.lava_process_artifact(
                        module.__artifacts_v2__[name]['category'], module_name, name, headers,
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
