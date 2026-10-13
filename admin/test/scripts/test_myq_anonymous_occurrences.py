"""Actual NSURLCache SQLite/JSON bodies with anonymous event occurrences."""
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts import myq  # pylint: disable=wrong-import-position


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def event(label, identity='missing', suffix=''):
    value = {'event_timestamp': '2026-01-02T03:04:05Z', 'event_type': label + suffix,
             'event': {'device_event': 'recorded-' + label, 'device_name': 'door-' + suffix,
                       'device_type': 'opener', 'device_serial_number': 'serial-' + suffix},
             'event_by': {'name': 'name-' + label, 'source': 'service', 'user_id': 'u-' + label}}
    if identity != 'missing':
        value['id'] = identity
    return value


def fixture_responses(anonymous=True, suffix=''):
    responses = [
        [event('A', 'A', suffix), event('M1', suffix=suffix), event('N1', None, suffix),
         event('zero', 0, suffix), event('false', False, suffix), event('empty', '', suffix),
         event('M2', suffix=suffix)],
        [event('A-conflict', 'A', suffix), event('M3', suffix=suffix), event('N2', None, suffix),
         event('zero-conflict', 0, suffix), event('empty-conflict', '', suffix), event('B', 'B', suffix)],
        [event('M4', suffix=suffix), event('N3', None, suffix), event('B-conflict', 'B', suffix),
         event('C', 'C', suffix)],
    ]
    if not anonymous:
        responses = [[e for e in body if e.get('id') is not None] for body in responses]
    return responses + [responses[2]]


def create_cache(root, tenant='', anonymous=True, wal=False, suffix=''):
    """Copy a complete live SQLite state, including WAL, before closing the writer."""
    target = Path(root) / tenant / 'Library/Caches/com.myliftmaster.myq'
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        source = Path(work) / 'Cache.db'
        connection = sqlite3.connect(source)
        if wal:
            connection.execute('pragma journal_mode=wal')
            connection.execute('pragma wal_autocheckpoint=0')
        connection.executescript('''
            CREATE TABLE cfurl_cache_response(entry_ID INTEGER PRIMARY KEY, request_key TEXT, time_stamp INTEGER);
            CREATE TABLE cfurl_cache_receiver_data(entry_ID INTEGER, isDataOnFS INTEGER, receiver_data BLOB);
        ''')
        if wal:
            connection.execute('pragma wal_checkpoint(truncate)')
        responses = fixture_responses(anonymous, suffix)
        for index, events in enumerate(responses):
            payload = json.dumps({'device_history': events}).encode()
            on_fs = int(index >= 2)
            if index == 1:
                payload = gzip.compress(payload)
            if on_fs:
                folder = target / 'fsCachedData'
                folder.mkdir(exist_ok=True)
                (folder / 'body').write_bytes(payload)
                payload = b'body'
            connection.execute('insert into cfurl_cache_response values(?,?,?)',
                               (index + 1, 'https://accounthistory.myq-cloud.com/deviceHistory', index + 1))
            connection.execute('insert into cfurl_cache_receiver_data values(?,?,?)',
                               (index + 1, on_fs, payload))
        siblings = [('devices.myq-cloud.com/Devices', {'items': [{'id': 'device', 'name': suffix, 'created_date': '2026-01-01T00:00:00', 'state': {'online': False}}]}),
                    ('guestaccess.myq-cloud.com/users', {'account_users': [{'user_id': 'user', 'role': 'stored', 'created_date': '2026-01-01T00:00:00Z'}]}),
                    ('profiles.myq-cloud.com/my/profile', {'email': 'fixture@example.invalid', 'diagnostics_opt_in': False})]
        for index, (url, body) in enumerate(siblings, 5):
            connection.execute('insert into cfurl_cache_response values(?,?,?)', (index, 'https://' + url, index))
            connection.execute('insert into cfurl_cache_receiver_data values(?,?,?)', (index, 0, json.dumps(body).encode()))
        connection.commit()
        for item in Path(work).glob('Cache.db*'):
            shutil.copyfile(item, target / item.name)
        connection.close()
    for item in target.rglob('*'):
        if item.is_file():
            item.chmod(0o444)
    return target / 'Cache.db'


def independent_rows(database, root, anonymous=True):
    """Direct SQL + JSON oracle, with independent timestamp and explicit11cell projection."""
    connection = sqlite3.connect('file:' + str(database) + '?mode=ro', uri=True)
    records = connection.execute('SELECT r.request_key,r.time_stamp,d.isDataOnFS,d.receiver_data FROM cfurl_cache_response r LEFT JOIN cfurl_cache_receiver_data d ON d.entry_ID=r.entry_ID ORDER BY r.time_stamp').fetchall()
    connection.close()
    rows, seen = [], set()
    for key, _, external, payload in records:
        if 'accounthistory.myq-cloud.com' not in key or 'deviceHistory' not in key:
            continue
        if external:
            payload = (Path(database).parent / 'fsCachedData' / payload.decode()).read_bytes()
        if payload[:2] == b'\x1f\x8b':
            payload = gzip.decompress(payload)
        for value in json.loads(payload)['device_history']:
            identity = value.get('id')
            if identity is not None or not anonymous:
                if identity in seen:
                    continue
                seen.add(identity)
            detail, actor = value['event'], value['event_by']
            rows.append((datetime.fromisoformat(value['event_timestamp'].replace('Z', '+00:00')).astimezone(timezone.utc),
                         detail['device_event'], detail['device_name'], detail['device_type'], value['event_type'],
                         actor['name'], actor['source'], detail['device_serial_number'], actor['user_id'],
                         '' if identity is None else identity, str(Path(database).relative_to(root))))
    return rows


class TestAnonymousOccurrences(unittest.TestCase):
    def test_inline_gzip_external_repeated_occurrences(self):
        with tempfile.TemporaryDirectory() as root:
            database = create_cache(root)
            headers, rows, sources = myq.myqDeviceHistory.__wrapped__(Context(root, [database]))
            self.assertEqual(rows, independent_rows(database, root))
            self.assertEqual(len(headers), 11)
            self.assertEqual(len(rows), 14)
            self.assertEqual([r[4] for r in rows], ['A', 'M1', 'N1', 'zero', 'empty', 'M2', 'M3', 'N2', 'B', 'M4', 'N3', 'C', 'M4', 'N3'])
            self.assertEqual(sum(r[9] == '' for r in rows), 10)  #9 anonymous + existing empty-stringID
            self.assertIs(type(rows[3][9]), int)
            self.assertEqual(sources, str(database))
            self.assertEqual(len(independent_rows(database, root, False)), 6)

    def test_wal_and_two_containers_keep_own_external_bodies(self):
        with tempfile.TemporaryDirectory() as root:
            a = create_cache(root, 'a', wal=True, suffix='A')
            b = create_cache(root, 'b', wal=True, suffix='B')
            self.assertGreater(Path(str(a) + '-wal').stat().st_size, 0)
            _, rows, sources = myq.myqDeviceHistory.__wrapped__(Context(root, [b, a]))
            self.assertEqual(rows, independent_rows(b, root) + independent_rows(a, root))
            self.assertEqual(len(rows), 28)
            self.assertEqual(sources, str(b) + '\n' + str(a))
            self.assertTrue(all(r[2] == 'door-B' for r in rows[:14]))
            self.assertTrue(all(r[2] == 'door-A' for r in rows[14:]))

    def test_known_only_and_sibling_projection(self):
        with tempfile.TemporaryDirectory() as root:
            database = create_cache(root, anonymous=False)
            _, rows, _ = myq.myqDeviceHistory.__wrapped__(Context(root, [database]))
            self.assertEqual(len(rows), 5)
            self.assertEqual(rows, independent_rows(database, root, False))
            for function, fields in [(myq.myqDevices, 18), (myq.myqAccountUsers, 7), (myq.myqProfile, 8)]:
                headers, values, sources = function.__wrapped__(Context(root, [database]))
                self.assertEqual(len(headers), fields)
                self.assertEqual(len(values), 1)
                self.assertEqual(len(values[0]), fields)
                self.assertEqual(sources, str(database))

    def test_native_nonnull_id_collisions_remain(self):
        with tempfile.TemporaryDirectory() as root:
            database = create_cache(root)
            database.chmod(0o644)
            connection = sqlite3.connect(database)
            events = [event('one', 1), event('true', True), event('zero', 0), event('false', False),
                      event('string-one', '1'), event('empty', ''), event('empty-again', ''),
                      event('missing'), event('null', None)]
            connection.execute('delete from cfurl_cache_response')
            connection.execute('delete from cfurl_cache_receiver_data')
            connection.execute('insert into cfurl_cache_response values(1,?,1)', ('https://accounthistory.myq-cloud.com/deviceHistory',))
            connection.execute('insert into cfurl_cache_receiver_data values(1,0,?)', (json.dumps({'device_history': events}).encode(),))
            connection.commit()
            connection.close()
            database.chmod(0o444)
            _, rows, _ = myq.myqDeviceHistory.__wrapped__(Context(root, [database]))
            self.assertEqual(rows, independent_rows(database, root))
            self.assertEqual([r[4] for r in rows], ['one', 'zero', 'string-one', 'empty', 'missing', 'null'])
            self.assertEqual([type(r[9]) for r in rows[:4]], [int, int, str, str])


if __name__ == '__main__':
    unittest.main()
