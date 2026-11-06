"""offerup: OfferUp (com.offerup.iphone.consumer) container stores, SYNTHETIC input only."""
import importlib.util
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import offerup as module

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('synthetic_offerup', HERE / 'synthetic_offerup.py')
SYNTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNTH)


def _write(folder, files):
    out = []
    for name, data in files.items():
        path = Path(folder) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        out.append(str(path))
    return out


def _run(function, paths, base):
    context = SimpleNamespace(
        get_files_found=lambda: list(paths),
        get_relative_path=lambda value: os.path.relpath(value, base).replace('\\', '/'))
    return function.__wrapped__(context)


def _column(headers, rows, name):
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [row[names.index(name)] for row in rows]


class OfferUpTest(unittest.TestCase):
    def _run_all(self, files):
        with tempfile.TemporaryDirectory() as folder:
            paths = _write(folder, files)
            return {
                function.__name__: _run(function, paths, folder)
                for function in (module.offerup_app_state, module.offerup_locations,
                                 module.offerup_recent_searches, module.offerup_listing_affinity,
                                 module.offerup_chat_drafts, module.offerup_activity,
                                 module.offerup_network_cache)
            }

    def test_current_container_row_counts_and_widths(self):
        out = self._run_all(SYNTH.build_files('current'))
        counts = {name: len(result[1]) for name, result in out.items()}
        self.assertEqual(counts, {
            'offerup_app_state': 31, 'offerup_locations': 3, 'offerup_recent_searches': 3,
            'offerup_listing_affinity': 6, 'offerup_chat_drafts': 2, 'offerup_activity': 12,
            'offerup_network_cache': 4})
        for headers, rows, _ in out.values():
            self.assertTrue(all(len(row) == len(headers) for row in rows))

    def test_identifiers_come_from_the_offerup_container_only(self):
        out = self._run_all(SYNTH.build_files('current'))
        headers, rows, _ = out['offerup_app_state']
        values = dict(zip(_column(headers, rows, 'Item'), _column(headers, rows, 'Value')))
        self.assertEqual(values['Account ID (from storage key name)'], SYNTH.ACCOUNT_ID)
        self.assertEqual(values['Advertising ID'], SYNTH.ADVERTISING_ID)
        self.assertEqual(values['Statsig stable ID'], SYNTH.STABLE_ID)
        self.assertEqual(values['App version (current)'], '2026.9.0')
        self.assertNotIn('9.9.9', values.values())
        places = _column(*out['offerup_locations'][:2], 'Place')
        self.assertNotIn('Decoyville', places)

    def test_decoy_container_with_the_same_mmkv_names_yields_nothing(self):
        files = {name: data for name, data in SYNTH.build_files('current').items()
                 if SYNTH.container_uuid('decoy-current') in name}
        out = self._run_all(files)
        self.assertEqual({name: len(result[1]) for name, result in out.items()},
                         {name: 0 for name in out})

    def test_container_without_metadata_plist_is_found_by_its_bundle_named_files(self):
        files = {name: data for name, data in SYNTH.build_files('current').items()
                 if not name.endswith('.com.apple.mobile_container_manager.metadata.plist')}
        out = self._run_all(files)
        self.assertEqual(len(out['offerup_app_state'][1]), 31)

    def test_earlier_container_reads_the_overflow_file_and_reports_absent_stores_as_empty(self):
        out = self._run_all(SYNTH.build_files('earlier'))
        self.assertEqual(len(out['offerup_recent_searches'][1]), 3)
        for name in ('offerup_listing_affinity', 'offerup_chat_drafts', 'offerup_network_cache'):
            self.assertEqual(out[name][1], [], name)

    def test_latest_entry_wins_for_a_rewritten_key_and_a_rewritten_session(self):
        out = self._run_all(SYNTH.build_files('current'))
        headers, rows, _ = out['offerup_activity']
        events = _column(headers, rows, 'Event')
        beats = [row for row, event in zip(rows, events) if event == 'Realtime (Ably) heartbeat']
        self.assertEqual(len(beats), 1)
        self.assertEqual(beats[0][0].isoformat(), '2026-09-21T14:13:27+00:00')
        sessions = [row for row, event in zip(rows, events) if event == 'Statsig session']
        self.assertEqual(len(sessions), 2)
        first = next(row for row in sessions if row[3].endswith('a1'))
        self.assertEqual((first[1] - first[0]).total_seconds(), 300)

    def test_cache_lists_offerup_and_ably_hosts_only_and_never_reads_a_body_in_a_file(self):
        out = self._run_all(SYNTH.build_files('current'))
        headers, rows, _ = out['offerup_network_cache']
        hosts = _column(headers, rows, 'Host')
        self.assertFalse(any('doubleclick' in host for host in hosts))
        in_file = [row for row in rows if _column(headers, [row], 'Body In File')[0] == 'Yes']
        self.assertEqual(len(in_file), 1)
        self.assertEqual(_column(headers, in_file, 'Body Size'), [''])
        keys = dict(zip(_column(headers, rows, 'URL'), _column(headers, rows, 'Body Keys')))
        self.assertEqual(keys['https://offerup-rest.ably.io:443/comet/connect'],
                         'action, connectionId, connectionDetails')

    def test_cache_database_without_the_cache_tables_gives_no_rows_and_no_error(self):
        files = SYNTH.build_files('current')
        key = next(name for name in files if name.endswith('Cache.db'))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'Cache.db'
            connection = sqlite3.connect(path)
            connection.execute('CREATE TABLE unrelated (a INTEGER)')
            connection.commit()
            connection.close()
            files[key] = path.read_bytes()
        out = self._run_all(files)
        self.assertEqual(out['offerup_network_cache'][1], [])

    def test_unreadable_stores_give_no_rows_and_no_error(self):
        files = SYNTH.build_files('current')
        for name in list(files):
            if name.endswith(('/redux', '/statsig', '/manifest.json', 'consumer.plist', '/Cache.db')):
                files[name] = b'not a store'
        out = self._run_all(files)
        for name, (_, rows, _) in out.items():
            self.assertEqual(rows, [], name)

    def test_draft_text_is_reported_in_full_with_its_length(self):
        out = self._run_all(SYNTH.build_files('current'))
        headers, rows, _ = out['offerup_chat_drafts']
        by_id = dict(zip(_column(headers, rows, 'Conversation ID'), zip(_column(headers, rows, 'Draft'),
                                                                        _column(headers, rows, 'Length'))))
        self.assertEqual(by_id['7000000000000000001'], ('Synthetic draft text, not sent', 30))
        self.assertEqual(by_id['7000000000000000002'], ('ok', 2))


if __name__ == '__main__':
    unittest.main()
