"""Fabricated logs from several apps, including both Private Photo Vault bundle IDs."""
import fnmatch
import hashlib
import inspect
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.artifacts import crashlytics as parser


class Context:
    def __init__(self, root):
        self.root = root
        self.files = [str(p) for p in root.rglob('*') if p.is_file() and any(
            fnmatch.fnmatchcase(str(p), pattern)
            for pattern in parser.__artifacts_v2__['crashlytics_logs']['paths'])]

    def get_files_found(self):
        return self.files + self.files

    def get_relative_path(self, path):
        return Path(path).relative_to(self.root).as_posix()


def write_log(root, messages, bundle='com.example.alpha', container='alpha'):
    path = root / ('private/var/mobile/Containers/Data/Application/' + container +
                   '/Library/Caches/com.crashlytics.data/' + bundle + '/v5/report/log_a.clsrecord')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(json.dumps({'log': {'msg': text.encode().hex(), 'time': stamp}})
                             for text, stamp in messages), encoding='utf-8')
    return path


def run(root):
    headers, rows, _ = inspect.unwrap(parser.crashlytics_logs)(Context(root))
    assert all(len(row) == len(headers) for row in rows)
    labels = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(labels, row)) for row in rows]


def breadcrumb(name, parameters):
    return '$A$:' + json.dumps({'name': name, 'parameters': parameters}, ensure_ascii=False)


class CrashlyticsTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_multiple_apps_including_pro_and_identical_filenames_remain_separate(self):
        bundles = ['com.example.reader', 'com.enchantedcloud.photovault',
                   'com.enchantedcloud.photovaultpro']
        for n, bundle in enumerate(bundles):
            write_log(self.root, [(breadcrumb('synthetic', {}), 1700000000000)], bundle, str(n))
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root)
        self.assertEqual([r['Bundle ID'] for r in rows], bundles)
        self.assertEqual(len({r['Source File'] for r in rows}), 3)
        self.assertEqual([r['Line Number'] for r in rows], [1, 1, 1])
        self.assertFalse(log.called)

    def test_analytics_event_and_screen_columns_are_structured_and_message_is_preserved(self):
        texts = [breadcrumb('screen_view', {'firebase_screen': 'Home "é"',
                                           'firebase_screen_class': 'RootController'}),
                 breadcrumb('screen_view', {'screen_name': 'Library', 'screen_class': 'VaultController'}),
                 breadcrumb('select_content', {'item_id': 'synthetic', 'firebase_screen': 'Context only'}),
                 breadcrumb('screen_view', {'firebase_screen_class': 'ClassOnly'}),
                 breadcrumb('_vs', {'_sn': 'Compact Home', '_sc': 'CompactController', '_pn': 'Previous'})]
        write_log(self.root, [(text, 1700000000000) for text in texts])
        rows = run(self.root)
        self.assertEqual([r['Message'] for r in rows], texts)
        self.assertEqual([r['Event'] for r in rows], ['screen_view', 'screen_view', 'select_content', 'screen_view', '_vs'])
        self.assertEqual([r['Screen Name'] for r in rows], ['Home "é"', 'Library', '', '', 'Compact Home'])
        self.assertEqual([r['Screen Class'] for r in rows], ['RootController', 'VaultController', '', 'ClassOnly', 'CompactController'])
        self.assertTrue(all(r['Breadcrumb Status'] == 'Parsed analytics event' for r in rows))

    def test_plain_messages_and_embedded_prefix_are_not_reported(self):
        texts = ['screen_view: Home', 'Synthetic app unlock', 'Prefix ' + breadcrumb('event', {}),
                 breadcrumb('kept', {})]
        write_log(self.root, [(text, 1700000000000) for text in texts])
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root)
        self.assertEqual([r['Event'] for r in rows], ['kept'])
        self.assertEqual(rows[0]['Line Number'], 4)
        self.assertFalse(log.called)

    def test_malformed_breadcrumbs_are_retained_without_hiding_neighbors(self):
        texts = ['$A$:{', '$A$:[]', '$A$:{"name":12}', '$A$:{"name":"example","parameters":[]}',
                 breadcrumb('screen_view', {'firebase_screen': 12}), breadcrumb('last', {})]
        write_log(self.root, [(text, 1700000000000) for text in texts])
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root)
        self.assertEqual(len(rows), 6)
        self.assertEqual([r['Message'] for r in rows], texts)
        self.assertEqual(rows[0]['Breadcrumb Status'], 'Malformed analytics JSON')
        self.assertEqual(rows[1]['Breadcrumb Status'], 'Unsupported analytics shape')
        self.assertEqual(rows[3]['Event'], 'example')
        self.assertEqual(rows[3]['Breadcrumb Status'], 'Unsupported analytics parameters')
        self.assertEqual(rows[4]['Screen Name'], '')
        self.assertEqual(rows[-1]['Event'], 'last')
        self.assertFalse(log.called)

    def test_bad_json_shapes_and_non_string_messages_are_isolated_and_source_is_relative(self):
        path = write_log(self.root, [])
        text = breadcrumb('test', {})
        lines = ['{', '[]', '{"log":[]}', '{"log":{"msg":12}}',
                 json.dumps({'log': {'msg': text.encode().hex(), 'time': 1700000000125}})]
        path.write_text('\n'.join(lines), encoding='utf-8')
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Message'], text)
        self.assertEqual(rows[0]['Line Number'], 5)
        self.assertEqual(rows[0]['Log Time'].microsecond, 125000)
        self.assertEqual(len(log.call_args_list), 4)
        for n, call in enumerate(log.call_args_list, 1):
            self.assertIn(f'line={n}', call.args[0])
            self.assertIn(path.relative_to(self.root).as_posix(), call.args[0])
            self.assertNotIn(str(self.root), call.args[0])

    def test_undecodable_hex_is_skipped_and_counted_once_per_file(self):
        path = write_log(self.root, [])
        path.write_text('\n'.join(json.dumps({'log': {'msg': raw, 'time': 0}})
                                 for raw in ['not hex', 'ff', '', breadcrumb('kept', {}).encode().hex()]),
                        encoding='utf-8')
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root)
        self.assertEqual([r['Event'] for r in rows], ['kept'])
        self.assertEqual(len(log.call_args_list), 1)
        self.assertIn('skipped 2 message(s)', log.call_args.args[0])
        self.assertIn(path.relative_to(self.root).as_posix(), log.call_args.args[0])

    def test_zero_missing_and_oversized_times_preserve_raw_and_good_rows(self):
        huge = 10**399
        stamps = [0, None, 1700000000125, huge, -huge, 1700000001000]
        write_log(self.root, [(breadcrumb('synthetic', {}), stamp) for stamp in stamps])
        with patch.object(parser, 'logfunc') as log:
            rows = run(self.root)
        self.assertEqual(len(rows), len(stamps))
        self.assertEqual(rows[0]['Log Time'], '')
        self.assertEqual(rows[0]['Raw Time (Unix milliseconds)'], 0)
        self.assertIsNone(rows[1]['Raw Time (Unix milliseconds)'])
        self.assertEqual(rows[2]['Log Time'].microsecond, 125000)
        self.assertEqual(rows[3]['Raw Time (Unix milliseconds)'], str(huge))
        self.assertEqual(rows[4]['Raw Time (Unix milliseconds)'], str(-huge))
        self.assertEqual(len(log.call_args_list), 2)

    def test_source_bytes_are_unchanged_and_duplicate_found_files_not_duplicated(self):
        path = write_log(self.root, [(breadcrumb('synthetic', {}), 1700000000000)])
        before = hashlib.sha256(path.read_bytes()).digest()
        self.assertEqual(len(run(self.root)), 1)
        self.assertEqual(hashlib.sha256(path.read_bytes()).digest(), before)

    def test_only_crashlytics_log_paths_supply_bundle_ids(self):
        candidates = [('Caches/com.crashlytics.data/com.example.alpha/v5/report/log_a.clsrecord', 'com.example.alpha'),
                      ('Caches/com.crashlytics.data/com.example.beta/v6/log_b.clsrecord', 'com.example.beta'),
                      ('Caches/other/com.example.alpha/v5/log_a.clsrecord', ''),
                      ('Caches/com.crashlytics.data/com.example.alpha/v5/log_a.clsrecord-wal', '')]
        for path, expected in candidates:
            self.assertEqual(parser._bundle_id(path), expected)  # pylint: disable=protected-access
            self.assertEqual(parser._bundle_id(path.replace('/', '\\')), expected)  # pylint: disable=protected-access

    def test_invalid_times_do_not_raise(self):
        for value in [True, float('nan'), float('inf'), 10**399, {'invalid': True}]:
            self.assertEqual(parser._time(value), '')  # pylint: disable=protected-access

    def test_generator_creates_current_two_artifacts_with_expected_rows(self):
        from admin.test.fixtures.analytics import make_synthetic  # pylint: disable=import-outside-toplevel
        from admin.test.scripts.test_mixpanel import run as mixpanel_rows  # pylint: disable=import-outside-toplevel
        import zipfile  # pylint: disable=import-outside-toplevel
        destination = self.root/'generated'
        make_synthetic.main(destination)
        unpacked = self.root/'unpacked'
        for archive in destination.glob('admin/test/cases/data/*/*.zip'):
            with zipfile.ZipFile(archive) as handle:
                handle.extractall(unpacked)
        self.assertEqual(len(run(unpacked)), 4)
        self.assertEqual(len(mixpanel_rows(unpacked)), 7)
        self.assertFalse(list(destination.rglob('*ECD*')))
