"""Actual Postbox SQLite peers, optional membership failures and WAL snapshots."""
import hashlib
from pathlib import Path
import shutil
import sqlite3
import struct
import tempfile
import unittest
from unittest.mock import patch

import mmh3
from scripts.artifacts import telegramAccounts as module
from scripts.artifacts.telegramAccounts import _contact_read_diagnostic


class FileContext:
    def __init__(self, root, files, relative=None):
        self.root, self.files, self.relative = Path(root), files, relative

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return self.relative if self.relative is not None else str(Path(path).relative_to(self.root))


def encoded_peer(peer_id):
    """A real Postbox root object with integer and UTF8 string fields."""
    payload = b''
    for key, value in [('i', peer_id), ('fn', 'Alé'), ('ln', 'Example'),
                       ('un', 'user'), ('p', '+100'), ('t', 'Title')]:
        name = key.encode()
        payload += struct.pack('<B', len(name)) + name
        if isinstance(value, int):
            payload += b'\x01' + struct.pack('<q', value)
        else:
            raw = value.encode()
            payload += b'\x04' + struct.pack('<i', len(raw)) + raw
    return b'\x01_\x05' + struct.pack('<ii', mmh3.hash('TelegramUser', seed=4157243346),
                                    len(payload)) + payload


def write_database(path, membership='populated'):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE t2 (key, value)')
    db.execute('CREATE TABLE t7 (key)')
    peers = [0, -1, 7, 7, 8]
    for index, peer in enumerate(peers):
        key = struct.pack('>q', peer) if index % 2 == 0 else peer
        db.execute('INSERT INTO t2 VALUES (?, ?)', (key, encoded_peer(peer)))
    db.executemany('INSERT INTO t7 VALUES (?)', [(struct.pack('>q', 7),)] * 2)
    if membership != 'missing':
        db.execute('CREATE TABLE t16 (key)')
        if membership == 'populated':
            db.executemany('INSERT INTO t16 VALUES (?)',
                           [(struct.pack('>q', 0),), (-1,), (7,), (7,), (b'bad',),
                            ('8',), (None,), (8.5,)])
    db.commit()
    db.close()
    return path


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in Path(root).rglob('*') if p.is_file()}


class ContactReadDiagnostics(unittest.TestCase):
    def test_actual_peers_membership_missing_and_invocation_cap(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            files = [str(write_database(root / f'telegram-data/account-{i}/postbox/db/db_sqlite',
                                        state)) for i, state in enumerate(
                                            ['populated', 'empty'] + ['missing'] * 13)]
            initial = hashes(root)
            with patch.object(module, 'logfunc') as logs:
                headers, rows, source = module.telegramContacts.__wrapped__(FileContext(root, files))
            self.assertEqual(len(headers), 12)
            self.assertEqual(len(rows), 75)
            self.assertEqual([r[9] for r in rows[:5]], ['Yes'] * 4 + [''])
            self.assertTrue(all(r[9] == '' for r in rows[5:]))
            self.assertEqual([r[1] for r in rows[:5]], [0, -1, 7, 7, 8])
            self.assertEqual([r[2] for r in rows], ['User'] * 75)
            self.assertEqual(rows[2][8], 2)
            self.assertEqual(source, '\n'.join(files))
            self.assertEqual(logs.call_count, 11)
            self.assertIn('failures=13, shown=10, suppressed=3', logs.call_args.args[0])
            with patch.object(module, 'logfunc') as again:
                module.telegramContacts.__wrapped__(FileContext(root, [files[-1]]))
            self.assertEqual(again.call_count, 2)
            self.assertEqual(hashes(root), initial)

    def test_actual_wal_changes_membership_without_mutating_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            live = write_database(root / 'live/telegram-data/account-1/postbox/db/db_sqlite')
            db = sqlite3.connect(live)
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('PRAGMA wal_autocheckpoint=0')
            db.execute('DELETE FROM t16')
            db.execute('INSERT INTO t16 VALUES (8)')
            db.commit()
            copies = []
            for state in ['complete', 'mainonly']:
                dest = root / state / 'telegram-data/account-1/postbox/db/db_sqlite'
                dest.parent.mkdir(parents=True)
                for suffix in ['', '-wal', '-shm'] if state == 'complete' else ['']:
                    shutil.copy2(str(live) + suffix, str(dest) + suffix)
                copies.append(dest)
            for protected in root.rglob('*'):
                if protected.is_file() and '/live/' not in str(protected):
                    protected.chmod(0o444)
            initial = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in root.rglob('*') if p.is_file() and '/live/' not in str(p)}
            with patch.object(module, 'logfunc') as logs:
                output = [module.telegramContacts.__wrapped__(FileContext(root, [str(p)]))[1]
                          for p in copies]
            self.assertEqual([r[9] for r in output[0]], [''] * 4 + ['Yes'])
            self.assertEqual([r[9] for r in output[1]], ['Yes'] * 4 + [''])
            self.assertFalse(logs.called)
            for name, digest in initial.items():
                self.assertEqual(hashlib.sha256(Path(name).read_bytes()).hexdigest(), digest)
            db.close()

    def test_controlled_midcursor_failure_retains_collected_ids(self):
        # Supplementary controlled failure on a real DB, not damaged or genuine evidence.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = write_database(root / 'telegram-data/account-1/postbox/db/db_sqlite')
            db = sqlite3.connect(path)
            cursor = db.cursor()

            class Cursor:
                failed = False

                def execute(self, sql):
                    self.failed = sql == 'SELECT key FROM t16'
                    cursor.execute(sql)

                def __iter__(self):
                    if self.failed:
                        yield cursor.fetchone()
                        raise sqlite3.OperationalError('/private/PRIVATE <script>\nsecret SQL')
                    yield from cursor

                def fetchall(self):
                    return cursor.fetchall()

            class Database:
                closed = False

                def cursor(self):
                    return Cursor()

                def close(self):
                    self.closed = True
                    db.close()

            connection = Database()
            with patch.object(module, 'open_sqlite_db_readonly', return_value=connection), \
                    patch.object(module, 'logfunc') as logs:
                _, rows, _ = module.telegramContacts.__wrapped__(FileContext(root, [str(path)]))
            self.assertEqual([r[9] for r in rows], ['Yes', '', '', '', ''])
            self.assertEqual(len(rows), 5)
            self.assertTrue(connection.closed)
            self.assertEqual(logs.call_count, 2)
            self.assertNotIn('PRIVATE', str(logs.call_args_list))
            self.assertNotIn('secret SQL', str(logs.call_args_list))

    def test_bounded_escaped_paths_and_fixed_exception_class(self):
        for relative in ['evidence/<script>&\n\té', 'long/' + 'é' * 1000,
                         '/private/examiner/secret', 'C:\\examiner\\secret',
                         '\\\\host\\secret']:
            context = FileContext('.', [], relative)
            message = _contact_read_diagnostic(context, '/HOST_PATH',
                                               sqlite3.OperationalError('PRIVATE SQL'))
            for forbidden in ['<', '>', '&', '\n', '\t', 'PRIVATE', 'examiner', 'HOST_PATH']:
                self.assertNotIn(forbidden, message)
            path_part = message.split(' at ')[1].split(' (path length=')[0]
            self.assertLessEqual(len(path_part), 512)
            self.assertIn('OperationalError', message)
            self.assertIn('truncated=True' if relative.startswith('long/') else 'truncated=False',
                          message)
        class UnexpectedError(sqlite3.Error):
            pass
        self.assertIn('; Error)', _contact_read_diagnostic(FileContext('.', [], 'relative'),
                                                         '', UnexpectedError('PRIVATE')))


if __name__ == '__main__':
    unittest.main()
