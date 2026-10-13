"""Actual Postbox bytes and SQLite/WAL presence projections."""
import hashlib
from pathlib import Path
import shutil
import sqlite3
import struct
import tempfile
import unittest

from scripts.artifacts import telegramAccounts as module
from scripts.artifacts.telegramAccounts import _decode_root
from admin.test.scripts.test_telegram_contact_read_diagnostics import encoded_peer

MISSING = object()


def encoded_value(value):
    if value is None:
        return b'\x0b'
    if isinstance(value, bool):
        return b'\x02' + bytes([value])
    if isinstance(value, int):
        return b'\x01' + struct.pack('<q', value)
    if isinstance(value, float):
        return b'\x03' + struct.pack('<d', value)
    if isinstance(value, str):
        raw = value.encode()
        return b'\x04' + struct.pack('<i', len(raw)) + raw
    if isinstance(value, list):
        return b'\x06' + struct.pack('<i', len(value)) + b''.join(
            struct.pack('<i', item) for item in value)
    if isinstance(value, dict):
        payload = encoded_record(value)
        return b'\x05' + struct.pack('<ii', 0, len(payload)) + payload
    return b'\x0a' + struct.pack('<i', len(value)) + value


def encoded_record(fields):
    return b''.join(bytes([len(key)]) + key.encode() + encoded_value(value)
                    for key, value in fields.items() if value is not MISSING)


def presence_cases():
    variants = [MISSING, None, 0, 1, 2, 3, 4, -1, 999, '0', '1', '', False,
                True, 0.0, 1.0, 2.0]
    flags = [MISSING, None, False, True, 0, 1, -1, 0.0, 0.5, '', '0', [],
             [0], {}, {'x': 0}, b'raw']
    times = [1700000000, 0, -1, 2147483646, 2147483647, MISSING, None, '1', True, False]
    activities = [1700000010, 0, -1, MISSING, None, '1', True, False]
    rows = []
    for i, variant in enumerate(variants):
        for j, flag in enumerate(flags):
            rows.append(encoded_record({'v': variant, 'h': flag,
                                        't': times[j % len(times)],
                                        'la': activities[i % len(activities)]}))
    return rows + rows[48:50]


def write_database(path, values=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE t2 (key,value)')
    db.execute('CREATE TABLE t20 (key,value)')
    db.execute('INSERT INTO t2 VALUES (?,?)', (struct.pack('>q', 7), encoded_peer(7)))
    values = presence_cases() if values is None else values
    db.executemany('INSERT INTO t20 VALUES (?,?)', [(struct.pack('>q', 7), v) for v in values])
    db.commit()
    db.close()
    return path


class FileContext:
    def __init__(self, files):
        self.files = files

    def get_files_found(self):
        return self.files


class DecodedPresence(unittest.TestCase):
    def test_real_encoded_matrix_native_fields_and_date_adjacency(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = write_database(Path(temporary) / 'telegram-data/account-1/postbox/db/db_sqlite')
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            headers, rows, source = module.telegramPeerPresence.__wrapped__(FileContext([str(path)]))
            self.assertEqual(headers[:2], [('Last Activity', 'datetime'), ('Status Time', 'datetime')])
            self.assertEqual(len(headers), 9)
            self.assertEqual(len(rows), 274)
            self.assertEqual(source, str(path))
            for raw, row in zip(presence_cases(), rows):
                record = _decode_root(raw)
                self.assertEqual(row[5], record.get('v'))
                self.assertEqual(type(row[5]), type(record.get('v')))
                self.assertEqual(row[7], record.get('h'))
                self.assertEqual(type(row[7]), type(record.get('h')))
                self.assertEqual(row[8], 'Yes' if record.get('h') else '')
                if record.get('v') == 1:
                    self.assertEqual(row[6], 'Stored Status 1')
                if not isinstance(record.get('t'), int) or not 0 < record['t'] < 2147483647:
                    self.assertEqual(row[1], '')
                if not isinstance(record.get('la'), int) or record['la'] <= 0:
                    self.assertEqual(row[0], '')
                self.assertEqual(row[2:5], ('1', 7, 'Alé Example (@user)'))
            self.assertEqual(rows[-2:], rows[48:50])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)

    def test_wal_changes_decoded_state_and_preserves_protected_copy(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = write_database(root / 'live/db_sqlite', [encoded_record({'v': 1, 'h': False})])
            db = sqlite3.connect(path)
            db.execute('pragma journal_mode=WAL')
            db.execute('pragma wal_autocheckpoint=0')
            db.execute('UPDATE t20 SET value=?', (encoded_record({'v': 1.0, 'h': [0], 't': 123}),))
            db.execute('INSERT INTO t20 SELECT * FROM t20')
            db.commit()
            dest = root / 'telegram-data/account-2/postbox/db/db_sqlite'
            dest.parent.mkdir(parents=True)
            initial = {}
            for suffix in ['', '-wal', '-shm']:
                shutil.copy2(str(path) + suffix, str(dest) + suffix)
                file = Path(str(dest) + suffix)
                file.chmod(0o444)
                initial[suffix] = hashlib.sha256(file.read_bytes()).hexdigest()
            _, rows, _ = module.telegramPeerPresence.__wrapped__(FileContext([str(dest)]))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0], rows[1])
            self.assertIsInstance(rows[0][5], float)
            self.assertEqual(rows[0][7:], ([0], 'Yes'))
            self.assertEqual(rows[0][6], 'Stored Status 1')
            for suffix, digest in initial.items():
                self.assertEqual(hashlib.sha256(Path(str(dest) + suffix).read_bytes()).hexdigest(), digest)
            db.close()

    def test_multiple_accounts_and_repeated_input_paths_preserve_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = [str(write_database(root / f'telegram-data/account-{n}/postbox/db/db_sqlite',
                                        [encoded_record({'v': n, 'h': n})])) for n in [1, 2]]
            _, rows, source = module.telegramPeerPresence.__wrapped__(FileContext(paths + paths[:1]))
            self.assertEqual([row[2] for row in rows], ['1', '2', '1'])
            self.assertEqual(rows[0], rows[2])
            self.assertEqual(source, '\n'.join(paths))


if __name__ == '__main__':
    unittest.main()
