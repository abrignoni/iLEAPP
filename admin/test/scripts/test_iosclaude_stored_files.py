"""Actual SQLite JSON and WAL values retain old message cells and exact stored files."""
import ast
import hashlib
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts import ilapfuncs
from scripts.artifacts import iOSclaude as module
from scripts.ilapfuncs import convert_human_ts_to_utc


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def message_query():
    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'iOSclaudeMessages')
    return next(n.value.value for n in function.body if isinstance(n, ast.Assign)
                and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'query')


def files_cases():
    return [None, 'null', '[]', '[{}]', '[{"fileName":null}]', '[{"fileName":""}]',
            '[{"fileName":0}]', '[{"fileName":true}]', '[{"fileName":"photo.jpg"}]',
            '  [ { "fileName": "é & <x>.pdf", "unknown": true }, {"fileName":"two.txt"}, '
            '{"fileName":"two.txt"} ]  ', '{"fileName":"root.txt"}', '"scalar"',
            0, 0.5, b'[{"fileName":"blob.txt"}]']


def write_database(path, wal=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    if wal:
        db.execute('pragma journal_mode=WAL')
        db.execute('pragma wal_autocheckpoint=0')
    db.execute('CREATE TABLE messages(createdAT TEXT, content TEXT, files, sender, conversationId)')
    db.execute('CREATE TABLE conversations(id TEXT,name TEXT)')
    db.commit()
    if wal:
        db.execute('pragma wal_checkpoint(TRUNCATE)')
    db.execute('INSERT INTO conversations VALUES (?,?)', ('conversation', 'title & é'))
    content = '[{"type":"text","text":"first"},{"type":"image","text":"not text"},{"type":"text","text":"last"}]'
    rows = [('2026-01-01 00:00:00', content, value, 'human', 'conversation') for value in files_cases()]
    rows += [rows[9], (None, '[]', '[]', 'assistant', 'absent'),
             ('2026-01-02 00:00:00', None, None, None, None)]
    db.executemany('INSERT INTO messages VALUES(?,?,?,?,?)', rows)
    db.commit()
    return db


class IOSClaudeStoredFilesTest(unittest.TestCase):
    def setUp(self):
        # The shared cursor helper transfers an open connection to its caller.
        # Track actual connections for test cleanup without replacing SQL/records.
        connections = []
        original = ilapfuncs.open_sqlite_db_readonly

        def tracked(*args, **kwargs):
            connection = original(*args, **kwargs)
            if connection:
                connections.append(connection)
            return connection

        tracker = patch.object(ilapfuncs, 'open_sqlite_db_readonly', side_effect=tracked)
        tracker.start()
        self.addCleanup(tracker.stop)
        self.addCleanup(lambda: [connection.close() for connection in connections])

    def test_actual_json_shapes_native_values_and_old_mapping(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'container/ClaudeCache/cache_test.sqlite'
            db = write_database(path)
            selected = db.execute(message_query()).fetchall()
            db.close()
            headers, rows, source = module.iOSclaudeMessages.__wrapped__(Context(folder, [path]))
            expected = [(convert_human_ts_to_utc(r[0]) if r[0] else None,
                         r[3], r[4], r[1], r[2], r[6], r[5], str(path.relative_to(folder)))
                        for r in selected]
            self.assertEqual(rows, expected)
            self.assertEqual(len(rows), 18)
            self.assertEqual([type(row[5]) for row in rows], [type(row[6]) for row in selected])
            self.assertEqual(rows[9][5], files_cases()[9])
            self.assertEqual(rows[9], rows[15])
            self.assertEqual(rows[-2][2:5], (None, None, None))
            self.assertEqual(rows[0][3], 'first last')
            self.assertEqual(headers[4:6], ('First Attached File Name', 'Files (As Stored)'))
            self.assertEqual(source, str(path))

    def test_actual_wal_rows_and_sorted_main_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            writer_path = root / 'writer/cache_test.sqlite'
            writer = write_database(writer_path, wal=True)
            control = root / 'main-only.sqlite'
            shutil.copy2(writer_path, control)
            db = sqlite3.connect(f'file:{control}?mode=ro', uri=True)
            self.assertEqual(db.execute('select count(*) from messages').fetchone()[0], 0)
            db.close()
            dest = root / 'B/ClaudeCache'
            dest.mkdir(parents=True)
            for path in writer_path.parent.iterdir():
                shutil.copy2(path, dest / path.name)
                (dest / path.name).chmod(0o444)
            dest.chmod(0o555)
            other = root / 'A/ClaudeCache/cache_other.sqlite'
            connection = write_database(other)
            connection.close()
            hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.iterdir()}
            _, rows, source = module.iOSclaudeMessages.__wrapped__(
                Context(root, [dest / 'cache_test.sqlite-wal', dest / 'cache_test.sqlite', other]))
            self.assertEqual(len(rows), 36)
            self.assertEqual(source.splitlines(), [str(other), str(dest / 'cache_test.sqlite')])
            self.assertEqual(rows[0][-1], str(other.relative_to(root)))
            self.assertEqual(hashes, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.iterdir()})
            writer.close()
            dest.chmod(0o755)

    def test_unsupported_json_query_behavior_new_only(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'cache_test.sqlite'
            db = write_database(path)
            for field in ['files', 'content']:
                db.execute('DELETE FROM messages')
                db.execute('INSERT INTO messages VALUES (?,?,?,?,?)',
                           ('2026-01-01 00:00:00', '[]', '[]', 'human', None))
                db.execute(f'UPDATE messages SET {field}=?', ('not JSON',))
                with self.assertRaises(sqlite3.DatabaseError):
                    db.execute(message_query()).fetchall()
            db.close()


if __name__ == '__main__':
    unittest.main()
