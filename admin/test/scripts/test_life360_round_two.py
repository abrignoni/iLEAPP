"""Fabricated controls for Life360 cache responses and historical page-version recovery."""
# pylint: disable=protected-access
# Direct format controls deliberately exercise internal binary-decoding primitives.
from datetime import datetime, timezone
import fnmatch
import gzip
import hashlib
import inspect
import json
from pathlib import Path
import shutil
import sqlite3
import struct
import tempfile
import unittest
from unittest.mock import patch

from admin.test.fixtures.life360 import make_synthetic_round_two as fixture
from admin.test.fixtures.life360 import make_synthetic_life360 as base
from scripts import life360_common, life360_recovery as recovery
from scripts.artifacts import life360Cache as cache, life360Recovered as recovered


class Context:
    def __init__(self, root, patterns):
        self.root = Path(root)
        self.files = [str(p) for p in self.root.rglob('*') if p.is_file()
                      and any(fnmatch.fnmatchcase(p.as_posix(), pattern) for pattern in patterns)]

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return Path(path).relative_to(self.root).as_posix()


def run(module, name, root, context=None):
    context = context or Context(root, module.__artifacts_v2__[name]['paths'])
    headers, rows, sources = inspect.unwrap(getattr(module, name))(context)
    labels = [h[0] if isinstance(h, tuple) else h for h in headers]
    if any(len(r) != len(labels) for r in rows):
        raise AssertionError('Header/row width mismatch')
    return [dict(zip(labels, r)) for r in rows], sources


class RoundTwoTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.app = self.root / 'one'
        self.topic, self.locations, self.drives = fixture.build_container(self.app)
        self.cache = self.app / 'Library/Caches/com.life360.safetymap/Cache.db'
        self.logs = []
        for module in (cache, recovered, recovery, life360_common):
            mock = patch.object(module, 'logfunc', side_effect=self.logs.append)
            mock.start()
            self.addCleanup(mock.stop)

    def mutate_cache(self, sql, values=()):
        with sqlite3.connect(self.cache) as connection:
            connection.execute(sql, values)

    def test_all_round_two_artifacts_have_data_widths_and_timestamp_first_columns(self):
        for module in (cache, recovered):
            for name, info in module.__artifacts_v2__.items():
                with self.subTest(artifact=name):
                    context = Context(self.root, info['paths'])
                    headers, rows, sources = inspect.unwrap(getattr(module, name))(context)
                    self.assertTrue(rows)
                    self.assertTrue(sources)
                    non_time_seen = False
                    for header in headers:
                        is_time = isinstance(header, tuple) and header[1] == 'datetime'
                        self.assertFalse(non_time_seen and is_time)
                        non_time_seen = non_time_seen or not is_time
                    self.assertTrue(all(len(r) == len(headers) for r in rows))

    def test_cached_locations_keep_precision_zero_unknown_fields_and_separate_times(self):
        rows, _ = run(cache, 'life360CachedLocations', self.root)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['Location Time'], datetime(2026, 1, 15, 12, 0, 0, 125000, timezone.utc))
        self.assertEqual(row['Cached Time'], datetime(2026, 1, 15, 13, tzinfo=timezone.utc))
        self.assertEqual(row['Speed (as stored)'], 0)
        self.assertEqual(row['Battery Charging'], False)
        self.assertEqual(json.loads(row['Record JSON'])['unknownField'], 'retained')
        self.assertEqual(json.loads(row['Owner IDs']), [base.USER])

    def test_external_body_is_resolved_by_exact_cache_directory(self):
        rows, _ = run(cache, 'life360CachedCircles', self.root)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]['Body Source File'].endswith('fsCachedData/synthetic-4'))
        self.assertEqual(rows[0]['Created'], datetime.fromtimestamp(base.T0, timezone.utc))

    def test_missing_external_body_has_index_row_and_named_log(self):
        rows, _ = run(cache, 'life360CacheResponses', self.root)
        entry = next(r for r in rows if r['Cache Entry ID'] == 6)
        self.assertEqual(entry['Body Status'], 'Body unavailable or invalid')
        self.assertTrue(any('entry 6' in m and 'external body missing' in m for m in self.logs))
        self.assertEqual(len(rows), 6)

    def test_external_body_path_traversal_and_absolute_paths_are_rejected(self):
        for bad in ('../outside', '/outside', 'a/b', '..', '.'):
            with self.subTest(reference=bad):
                self.mutate_cache('update cfurl_cache_receiver_data set receiver_data=? where entry_ID=4', (bad,))
                rows, _ = run(cache, 'life360CachedCircles', self.root)
                self.assertEqual(rows, [])
                self.assertTrue(any('unsafe external-body reference' in m for m in self.logs))

    def test_caches_from_other_tenants_cannot_supply_a_missing_body(self):
        other = self.root / 'two'
        fixture.build_cache(other)
        (self.cache.parent / 'fsCachedData/synthetic-4').unlink()
        rows, _ = run(cache, 'life360CachedCircles', self.root)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]['Source File'].startswith('two/'))

    def test_other_host_and_sdk_cache_are_excluded_including_source_list(self):
        self.mutate_cache('update cfurl_cache_response set request_key=? where entry_ID=1',
                          ('https://api-cloudfront.life360.com.evil.invalid/v5/circles/devices/locations',))
        sdk = self.cache.parent / 'sdk/Cache.db'
        sdk.parent.mkdir()
        shutil.copyfile(self.cache, sdk)
        rows, sources = run(cache, 'life360CacheResponses', self.root)
        self.assertEqual(len(rows), 5)
        self.assertNotIn('sdk/Cache.db', sources.replace('\\', '/'))
        locations, _ = run(cache, 'life360CachedLocations', self.root)
        self.assertEqual(locations, [])

    def test_request_paths_omit_credentials_query_and_fragment(self):
        self.mutate_cache('update cfurl_cache_response set request_key=? where entry_ID=1',
                          ('https://user:password@api-cloudfront.life360.com/v5/circles/devices/locations?token=secret#hidden',))
        rows, _ = run(cache, 'life360CachedLocations', self.root)
        self.assertEqual(rows[0]['Request Path'], 'api-cloudfront.life360.com/v5/circles/devices/locations')

    def test_gzip_json_and_text_storage_are_both_supported(self):
        with sqlite3.connect(self.cache) as connection:
            body = connection.execute('select receiver_data from cfurl_cache_receiver_data where entry_ID=1').fetchone()[0]
        for value in (body.decode(), gzip.compress(body)):
            self.mutate_cache('update cfurl_cache_receiver_data set receiver_data=? where entry_ID=1', (value,))
            rows, _ = run(cache, 'life360CachedLocations', self.root)
            self.assertEqual(len(rows), 1)

    def test_malformed_json_and_nonfinite_numbers_are_logged_without_payload(self):
        for value in (b'{SYNTHETIC_FAILED_PAYLOAD', b'{"data":NaN}', b'{"data":1e9999}'):
            self.mutate_cache('update cfurl_cache_receiver_data set receiver_data=? where entry_ID=1', (value,))
            rows, _ = run(cache, 'life360CacheResponses', self.root)
            self.assertEqual(len(rows), 6)
            self.assertEqual(rows[0]['Body Status'], 'Body unavailable or invalid')
        self.assertTrue(all('SYNTHETIC_FAILED_PAYLOAD' not in m for m in self.logs))

    def test_profile_created_without_zone_stays_raw(self):
        rows, _ = run(cache, 'life360CachedAccount', self.root)
        self.assertEqual(rows[0]['Profile Created (as stored)'], '2026-01-15 12:00:00')
        self.assertEqual(json.loads(rows[0]['Record JSON'])['extraProfileField'], 'retained')

    def test_missing_zone_is_not_replaced_with_local_time(self):
        self.assertEqual(cache._time('2026-01-15T12:00:00', 'synthetic'), '')
        self.assertTrue(any('invalid synthetic' in m for m in self.logs))

    def test_non_object_list_items_do_not_suppress_good_items(self):
        with sqlite3.connect(self.cache) as connection:
            blob = connection.execute('select receiver_data from cfurl_cache_receiver_data where entry_ID=1').fetchone()[0]
        body = json.loads(blob)
        body['data']['items'].insert(0, 'unsupported')
        self.mutate_cache('update cfurl_cache_receiver_data set receiver_data=? where entry_ID=1', (json.dumps(body),))
        rows, _ = run(cache, 'life360CachedLocations', self.root)
        self.assertEqual(len(rows), 1)
        self.assertTrue(any('non-object item' in m for m in self.logs))

    def test_recovery_returns_known_nonlive_records_and_preserves_live_exclusion(self):
        rows, _ = run(recovered, 'life360RecoveredTopics', self.root)
        self.assertEqual(len(rows), 8)
        identities = {json.loads(r['Payload (as stored)'])['id'] for r in rows}
        self.assertEqual(identities, {base.uid(0xD000), base.uid(0xD001), base.uid(0xE000), base.uid(0xE001), base.uid(0xF000), base.uid(0xF001), base.uid(0xF004), base.uid(0xF005)})
        self.assertNotIn(base.uid(0xD002), identities)
        self.assertTrue(any('Main-file view' in r['Source States'] for r in rows))
        self.assertTrue(any('Committed WAL page' in r['Source States'] for r in rows))

    def test_wal_overflow_payload_is_complete_and_provenance_names_its_frames(self):
        rows, _ = run(recovered, 'life360RecoveredTopics', self.root)
        row = next(r for r in rows if json.loads(r['Payload (as stored)'])['id'] == base.uid(0xD001))
        self.assertEqual(json.loads(row['Payload (as stored)'])['padding'], 'overflow-control-' * 200)
        sources = json.loads(row['Recovery Sources JSON'])
        wal = [s for s in sources if s['frame']]
        self.assertTrue(wal)
        self.assertTrue(any(s['overflow'] for s in wal))
        self.assertTrue(all(s['frame'] <= s['commitFrame'] for s in wal))
        self.assertTrue(all(p['frame'] > 0 for s in wal for p in s['overflow']))

    def test_source_cell_offsets_resolve_to_physical_main_or_wal_bytes(self):
        rows = list(recovery.recover_rows(self.topic, 'ZENTRY', 'synthetic'))
        main = self.topic.read_bytes()
        wal = Path(str(self.topic) + '-wal').read_bytes()
        size = int.from_bytes(main[16:18], 'big')
        self.assertTrue(rows)
        for record in rows:
            source = record['source']
            frame = source['frame']
            page_start = 32 + (frame - 1) * (size + 24) + 24 if frame else (source['page'] - 1) * size
            data = wal if frame else main
            page = data[page_start:page_start + size]
            count = int.from_bytes(page[3:5], 'big')
            pointers = [int.from_bytes(page[8 + 2 * i:10 + 2 * i], 'big') for i in range(count)]
            self.assertIn(source['cellOffset'], pointers)
            self.assertEqual(source['fileOffset'], page_start + source['cellOffset'])
            self.assertTrue(data[source['fileOffset']:source['fileOffset'] + 1])

    def test_recovered_event_waypoint_and_incident_epochs_are_independent(self):
        for name in ('life360RecoveredMovement', 'life360RecoveredWaypoints', 'life360RecoveredIncidents', 'life360RecoveredBreaches', 'life360RecoveredDwells'):
            rows, _ = run(recovered, name, self.root)
            self.assertEqual(len(rows), 2)
            first = next(iter(rows[0].values()))
            self.assertEqual(first.year, 2026)
            self.assertEqual(first.tzinfo, timezone.utc)
        locations, _ = run(recovered, 'life360RecoveredLocations', self.root)
        self.assertEqual(len(locations), 2)
        self.assertTrue(all(r['Location Time'].year == 2026 for r in locations))

    def test_recovered_drives_use_no_current_circle_join(self):
        rows, _ = run(recovered, 'life360RecoveredDrives', self.root)
        self.assertEqual(len(rows), 1)
        self.assertNotIn('Circle IDs', rows[0])
        self.assertEqual(rows[0]['Start Time'].year, 2026)

    def test_bad_wal_checksum_is_excluded_and_good_files_continue(self):
        path = Path(str(self.topic) + '-wal')
        data = bytearray(path.read_bytes())
        data[32 + 24 + 100] ^= 1
        path.write_bytes(data)
        rows = list(recovery.recover_rows(self.topic, 'ZENTRY', 'synthetic-topic'))
        # SQLite also ignores the invalid WAL prefix, so the main row is now the live comparison.
        self.assertEqual(rows, [])
        good, _ = run(recovered, 'life360RecoveredTopics', self.root)
        self.assertEqual(len(good), 6)  # Other topics' valid historical records survive.
        self.assertTrue(any('checksum mismatch' in m for m in self.logs))

    def test_truncated_and_old_salt_tail_are_excluded(self):
        path = Path(str(self.topic) + '-wal')
        original = path.read_bytes()
        for suffix in (b'short-tail', original[32:32 + 1048]):
            path.write_bytes(original + suffix)
            rows = list(recovery.recover_rows(self.topic, 'ZENTRY', 'synthetic-topic'))
            self.assertEqual(len({r['fingerprint'] for r in rows}), 2)
        self.assertTrue(any('truncated' in m or 'checksum mismatch' in m for m in self.logs))

    def test_incomplete_transaction_after_valid_commits_is_not_recovered(self):
        path = Path(str(self.topic) + '-wal')
        original = path.read_bytes()
        magic, _, size, _, salt1, salt2, _, _ = struct.unpack('>8I', original[:32])
        frame_size = size + 24
        last = original[-frame_size:]
        page = struct.unpack('>I', last[:4])[0]
        seed = struct.unpack('>2I', last[16:24])
        prefix = struct.pack('>2I', page, 0)
        checksum = recovery._checksum(prefix + last[24:], '<' if magic == 0x377f0682 else '>', seed)
        tail = prefix + struct.pack('>4I', salt1, salt2, *checksum) + last[24:]
        expected = list(recovery.wal_transactions(path, size, 'synthetic'))
        path.write_bytes(original + tail)
        actual = list(recovery.wal_transactions(path, size, 'synthetic'))
        self.assertEqual(len(actual), len(expected))
        self.assertTrue(any('uncommitted/incomplete' in m for m in self.logs))

    def test_wal_header_checksum_and_foreign_salts_are_rejected(self):
        path = Path(str(self.topic) + '-wal')
        original = path.read_bytes()
        for position in (24, 32 + 8):
            bad = bytearray(original)
            bad[position] ^= 1
            path.write_bytes(bad)
            self.assertEqual(list(recovery.wal_transactions(path, 1024, 'synthetic')), [])
        self.assertTrue(any('WAL read/validation failed' in m for m in self.logs))
        self.assertTrue(any('invalid page/salt' in m for m in self.logs))

    def test_record_versions_with_same_entry_identifier_stay_distinct(self):
        docs = [{'id': base.uid(0xF001), 'versionValue': value} for value in ('old-one', 'old-two', 'live')]
        path = self.root / 'same-id.sqlite'
        fixture._history(path, docs)
        rows = list(recovery.recover_rows(path, 'ZENTRY', 'synthetic'))
        values = {json.loads(r['values']['ZDATA'])['versionValue'] for r in rows}
        self.assertEqual(values, {'old-one', 'old-two'})

    def test_schema_and_historical_rows_can_exist_only_in_the_wal(self):
        path = self.root / 'schema-in-wal.sqlite'
        connection = sqlite3.connect(path)
        connection.execute('PRAGMA journal_mode=WAL')
        connection.execute('PRAGMA wal_autocheckpoint=0')
        connection.execute('CREATE TABLE ZENTRY(Z_PK INTEGER PRIMARY KEY,Z_ENT INTEGER,Z_OPT INTEGER,ZTIMESTAMP FLOAT,ZID BLOB,ZDATA BLOB)')
        connection.commit()
        connection.execute('INSERT INTO ZENTRY VALUES(1,1,1,?,NULL,?)', (float(base.T0), b'{"history":"old"}'))
        connection.commit()
        connection.execute('DELETE FROM ZENTRY')
        connection.commit()
        snapshot = {suffix: Path(str(path) + suffix).read_bytes() for suffix in ('', '-wal', '-shm')}
        connection.close()
        for suffix, content in snapshot.items():
            Path(str(path) + suffix).write_bytes(content)
        rows = list(recovery.recover_rows(path, 'ZENTRY', 'synthetic'))
        self.assertEqual({r['values']['ZDATA'] for r in rows}, {b'{"history":"old"}'})

    def test_damaged_gzip_is_logged_and_other_response_rows_survive(self):
        self.mutate_cache('update cfurl_cache_receiver_data set receiver_data=? where entry_ID=1',
                          (b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03bad-deflate',))
        rows, _ = run(cache, 'life360CachedLocations', self.root)
        self.assertEqual(rows, [])
        devices, _ = run(cache, 'life360CachedDevices', self.root)
        self.assertEqual(len(devices), 1)
        self.assertTrue(any('entry 1' in m and 'body unavailable/invalid' in m for m in self.logs))

    def test_invalid_coordinate_is_blank_with_its_original_value_in_json(self):
        with sqlite3.connect(self.cache) as connection:
            data = connection.execute('select receiver_data from cfurl_cache_receiver_data where entry_ID=1').fetchone()[0]
        body = json.loads(data)
        body['data']['items'][0]['latitude'] = 'synthetic-not-coordinate'
        self.mutate_cache('update cfurl_cache_receiver_data set receiver_data=? where entry_ID=1', (json.dumps(body),))
        rows, _ = run(cache, 'life360CachedLocations', self.root)
        self.assertEqual(rows[0]['Latitude'], '')
        self.assertEqual(json.loads(rows[0]['Record JSON'])['latitude'], 'synthetic-not-coordinate')
        self.assertTrue(any('coordinate was invalid' in m for m in self.logs))

    def test_bad_cell_does_not_remove_other_cells_on_the_page(self):
        page = bytearray(512)
        page[0] = 13
        page[3:5] = struct.pack('>H', 2)
        page[8:12] = struct.pack('>2H', 1, 500)  # First pointer is invalid; second is a complete cell.
        page[500:504] = bytes([2, 7, 2, 0])  # Payload size 2, rowid 7, one NULL column.
        errors = []
        cells = list(recovery._cells(bytes(page), 2, 512, lambda _: (None, 0), 'utf-8', errors.append))
        self.assertEqual(errors, [0])
        self.assertEqual(cells, [(7, [None], 500, [])])

    def test_old_wal_record_cannot_use_main_file_overflow_bytes(self):
        # The provider's unavailable WAL page must fail even if bytes exist elsewhere.
        page = bytearray(512)
        page[0] = 13
        page[3:5] = struct.pack('>H', 1)
        page[8:10] = struct.pack('>H', 100)
        size = 1000
        encoded = bytes([0x87, 0x68])  # varint 1000
        page[100:103] = encoded + b'\x01'
        minimum = (512 - 12) * 32 // 255 - 23
        local = minimum + (size - minimum) % (512 - 4)
        if local > 512 - 35:
            local = minimum
        page[103 + local:107 + local] = struct.pack('>I', 9)
        errors = []
        rows = list(recovery._cells(bytes(page), 2, 512, lambda _: (None, 0), 'utf-8', errors.append))
        self.assertEqual(rows, [])
        self.assertEqual(errors, [0])

    def test_physical_alias_is_read_once(self):
        alias = self.root / 'alias'
        try:
            alias.symlink_to(self.app, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('Directory symlinks unavailable')
        for module, name in ((cache, 'life360CacheResponses'), (recovered, 'life360RecoveredTopics')):
            context = Context(self.root, module.__artifacts_v2__[name]['paths'])
            expected, _ = run(module, name, self.root, context)
            context.files.extend(str(alias / Path(p).relative_to(self.app)) for p in list(context.files))
            actual, _ = run(module, name, self.root, context)
            self.assertEqual(actual, expected)

    def test_all_artifacts_double_for_separate_containers_without_merging_ids(self):
        before = {}
        for module in (cache, recovered):
            for name in module.__artifacts_v2__:
                before[name] = len(run(module, name, self.root)[0])
        fixture.build_container(self.root / 'two')
        for module in (cache, recovered):
            for name in module.__artifacts_v2__:
                with self.subTest(artifact=name):
                    rows, _ = run(module, name, self.root)
                    self.assertEqual(len(rows), 2 * before[name])

    def test_foreign_or_missing_marker_fails_closed(self):
        marker = self.app / '.com.apple.mobile_container_manager.metadata.plist'
        marker.unlink()
        rows, _ = run(recovered, 'life360RecoveredTopics', self.root)
        self.assertEqual(rows, [])
        rows, _ = run(cache, 'life360CacheResponses', self.root)
        self.assertEqual(rows, [])
        self.assertTrue(any('marker missing' in m for m in self.logs))

    def test_duplicate_file_lists_do_not_duplicate_records(self):
        for module, name in ((cache, 'life360CacheResponses'), (recovered, 'life360RecoveredTopics')):
            context = Context(self.root, module.__artifacts_v2__[name]['paths'])
            expected, _ = run(module, name, self.root, context)
            context.files *= 2
            actual, _ = run(module, name, self.root, context)
            self.assertEqual(actual, expected)

    def test_source_content_bytes_are_unchanged(self):
        paths = [p for p in self.root.rglob('*') if p.is_file() and not p.name.endswith('-shm')]
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        for module in (cache, recovered):
            for name in module.__artifacts_v2__:
                run(module, name, self.root)
        self.assertTrue(all(hashlib.sha256(p.read_bytes()).hexdigest() == digest for p, digest in before.items()))

    def test_varint_serial_types_and_checksum_endianness(self):
        self.assertEqual(recovery._varint(b'\x81\x00', 0), (128, 2))
        # SQLite record: NULL, integer -1, float .125, constant 0, constant 1, text, blob.
        payload = bytes([8, 0, 1, 7, 8, 9, 15, 14]) + b'\xff' + struct.pack('>d', .125) + b'x\x01'
        self.assertEqual(recovery._decode(payload, 'utf-8'), [None, -1, .125, 0, 1, 'x', b'\x01'])
        self.assertEqual(recovery._checksum(struct.pack('<4I', 1, 2, 3, 4), '<'), (7, 14))
        self.assertEqual(recovery._checksum(struct.pack('>4I', 1, 2, 3, 4), '>'), (7, 14))


if __name__ == '__main__':
    unittest.main()
