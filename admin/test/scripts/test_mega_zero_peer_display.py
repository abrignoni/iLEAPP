"""Actual SQLite affinity, contact lookup and WAL peer-display boundaries."""
from collections import Counter
import hashlib
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts import ilapfuncs
from scripts.artifacts import mega as module


def peers():
    return [None, 0, '0', 0.0, -0.0, '', 1, -1, 0.5, 'opaque', 'é', b'', b'0', b'\xff']


def write_database(path, wal=False, native=False, empty=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    if wal:
        db.execute('pragma journal_mode=WAL')
        db.execute('pragma wal_autocheckpoint=0')
    if native:
        db.execute('CREATE TABLE chats(ts_created,chatid,peer,title,shard,mode)')
        db.execute('CREATE TABLE contacts(userid,email)')
    else:
        db.execute('CREATE TABLE chats(chatid int64 unique primary key, shard tinyint, '
                   'own_priv tinyint, peer int64 default -1, peer_priv tinyint default 0, '
                   'title text, ts_created int64 not null default 0, last_seen int64 default 0, '
                   'last_recv int64 default 0, archived tinyint default 0, mode tinyint default 0, '
                   'unified_key blob, rsn blob, meeting tinyint default 0, chat_options tinyint default 0)')
        db.execute('CREATE TABLE contacts(userid int64 PRIMARY KEY,email text,visibility int,'
                   'since int64 not null default 0)')
    db.commit()
    if wal:
        db.execute('pragma wal_checkpoint(TRUNCATE)')
    if empty:
        return db
    rows = [(1700000000 + i, i + 1, peer, 'title & <é>' if i % 2 else None,
             i % 3, b'raw' if i % 2 else 0) for i, peer in enumerate(peers())]
    rows.append((1700000001, 500, 0, 'repeat peer', None, None))
    if native:
        rows.append(rows[1])
    db.executemany('INSERT INTO chats(ts_created,chatid,peer,title,shard,mode) VALUES(?,?,?,?,?,?)', rows)
    db.executemany('INSERT INTO contacts(userid,email) VALUES(?,?)',
                   [(0, ''), (1, 'one@example.invalid'), (-1, None), (0.5, 0),
                    ('opaque', b'lookup-bytes'), (None, 'null@example.invalid')])
    db.commit()
    return db


class Context:
    def __init__(self, files):
        self.files = files

    def get_files_found(self):
        return self.files


class MegaZeroPeerDisplayTest(unittest.TestCase):
    def setUp(self):
        connections = []
        original = ilapfuncs.open_sqlite_db_readonly

        def tracked(*args, **kwargs):
            connection = original(*args, **kwargs)
            if connection:
                connections.append(connection)
            return connection

        def close_connections():
            for connection in connections:
                connection.close()

        tracker = patch.object(ilapfuncs, 'open_sqlite_db_readonly', side_effect=tracked)
        tracker.start()
        self.addCleanup(tracker.stop)
        self.addCleanup(close_connections)

    def test_target_affinity_and_native_fallback_values(self):
        for native in [False, True]:
            with self.subTest(native=native), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / 'karere-test.db'
                db = write_database(path, native=native)
                db.execute('DELETE FROM contacts')
                db.commit()
                selected = db.execute('select ts_created,chatid,peer,title,shard,mode '
                                      'from chats order by ts_created').fetchall()
                db.close()
                headers, rows, source = module.mega_chats.__wrapped__(Context([path]))
                self.assertEqual([row[2] for row in rows],
                                 ['' if row[2] is None else str(row[2]) for row in selected])
                self.assertEqual(rows[1][2], '0')
                self.assertIn("b''", [row[2] for row in rows])
                self.assertEqual(len(rows), 16 if native else 15)
                if native:
                    self.assertEqual(Counter(rows).most_common(1)[0][1], 2)
                    self.assertIn('0.0', [row[2] for row in rows])
                self.assertEqual(headers[:3], (('Created', 'datetime'), 'Chat ID', 'Peer Display Value'))
                self.assertEqual(source, str(path))

    def test_truthy_lookup_literal_none_duplicates_and_vars_independence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'karere-test.db'
            db = write_database(path, native=True)
            db.execute('DELETE FROM contacts')
            db.executemany('INSERT INTO contacts VALUES(?,?)',
                           [(0, 'first'), ('0', 'second'), (0, ''), (0, None), (0, 0), (0, 0.0),
                            (0, b''), (0.0, b'real-lookup'), (None, 'null-lookup'), ('opaque', 7)])
            db.commit()
            _, rows, _ = module.mega_chats.__wrapped__(Context([path]))
            by_id = {row[1]: row[2] for row in rows}
            self.assertEqual(by_id['1'], 'null-lookup')
            self.assertEqual(by_id['2'], 'second')
            self.assertEqual(by_id['3'], 'second')
            self.assertEqual(by_id['4'], b'real-lookup')
            self.assertEqual(by_id['10'], 7)
            db.execute('CREATE TABLE vars(name text,value blob)')
            db.executemany('INSERT INTO vars VALUES(?,?)', [('my_handle', 0), ('my_handle', None),
                                                          ('my_email', 'unrelated')])
            db.commit()
            db.close()
            self.assertEqual(module.mega_chats.__wrapped__(Context([path]))[1], rows)

    def test_actual_wal_empty_first_main_and_hashes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            writer_path = root / 'writer/karere-test.db'
            writer = write_database(writer_path, wal=True)
            control = root / 'main-only.db'
            shutil.copy2(writer_path, control)
            db = sqlite3.connect(f'file:{control}?mode=ro', uri=True)
            self.assertEqual(db.execute('select count(*) from chats').fetchone()[0], 0)
            db.close()
            target = root / 'protected'
            target.mkdir()
            for p in writer_path.parent.iterdir():
                shutil.copy2(p, target / p.name)
                (target / p.name).chmod(0o444)
            target.chmod(0o555)
            other = root / 'empty/karere-other.db'
            db = write_database(other, empty=True)
            db.close()
            hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()}
            _, rows, source = module.mega_chats.__wrapped__(
                Context([target / 'karere-test.db-wal', target / 'karere-test.db', other]))
            self.assertEqual(len(rows), 15)
            self.assertEqual(source, str(target / 'karere-test.db'))
            self.assertEqual(hashes, {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in target.iterdir()})
            self.assertEqual(module.mega_chats.__wrapped__(Context([other, target / 'karere-test.db']))[1], [])
            writer.close()
            target.chmod(0o755)


if __name__ == '__main__':
    unittest.main()
