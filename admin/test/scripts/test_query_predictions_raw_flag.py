"""Actual SQLite types, duplicate rows and complete WAL source selection."""
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts import queryPredictions as artifact  # pylint: disable=wrong-import-position


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def create_store(root, tenant='', wal=False, prefix=''):
    folder = Path(root) / tenant / 'Library/QueryPredictions'
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        source = Path(work) / 'query_predictions.db'
        connection = sqlite3.connect(source)
        if wal:
            connection.execute('pragma journal_mode=wal')
            connection.execute('pragma wal_autocheckpoint=0')
        connection.execute('CREATE TABLE messages(creationTimestamp, isSent, content, conversationId, id, uuid)')
        connection.commit()
        if wal:
            connection.execute('pragma wal_checkpoint(truncate)')
        flags = [None, 0, 1, 2, -1, 1.25, '1', '0', 'sent', '', b'\x00\xff']
        rows = [(1700000000 + index, flag, prefix + 'record-' + str(index), 'thread', index, 'uuid-' + str(index)) for index, flag in enumerate(flags)]
        rows.append(rows[2])
        rows.extend([(value, 2, prefix + 'date-' + str(index), 'thread', 100 + index, 'date-uuid') for index, value in enumerate([None, 'invalid-date', 1e20])])
        connection.executemany('INSERT INTO messages VALUES(?,?,?,?,?,?)', rows)
        connection.commit()
        for item in Path(work).glob('query_predictions.db*'):
            shutil.copyfile(item, folder / item.name)
        connection.close()
    for item in folder.iterdir():
        item.chmod(0o444)
    return folder / 'query_predictions.db'


def direct_rows(path):
    connection = sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True)
    rows = connection.execute("SELECT datetime(creationTimestamp,'unixepoch'),isSent,content,conversationId,id,uuid FROM messages").fetchall()
    types = connection.execute('SELECT typeof(isSent) FROM messages').fetchall()
    connection.close()
    return rows, types


class TestRawFlag(unittest.TestCase):
    def test_native_values_duplicates_and_invalid_date_rows(self):
        with tempfile.TemporaryDirectory() as root:
            path = create_store(root)
            headers, rows, source = artifact.queryPredictions.__wrapped__(Context(root, [path]))
            oracle, types = direct_rows(path)
            self.assertEqual(rows, oracle)
            self.assertEqual(len(rows), 15)
            self.assertEqual(len(headers), 6)
            self.assertEqual([type(row[1]) for row in rows[:11]], [type(None), int, int, int, int, float, str, str, str, str, bytes])
            self.assertEqual([row[0] for row in rows[-3:]], [None, None, None])
            self.assertEqual(rows[2], rows[11])
            self.assertEqual(types[:11], [('null',), ('integer',), ('integer',), ('integer',), ('integer',), ('real',), ('text',), ('text',), ('text',), ('text',), ('blob',)])
            self.assertEqual(source, str(path.relative_to(root)))

    def test_complete_wal_state(self):
        with tempfile.TemporaryDirectory() as root:
            path = create_store(root, wal=True)
            self.assertGreater(Path(str(path) + '-wal').stat().st_size, 0)
            _, rows, _ = artifact.queryPredictions.__wrapped__(Context(root, [path]))
            self.assertEqual(rows, direct_rows(path)[0])
            self.assertEqual(len(rows), 15)

    def test_first_main_and_sidecars_selection_unchanged(self):
        with tempfile.TemporaryDirectory() as root:
            a = create_store(root, 'a', wal=True, prefix='A')
            b = create_store(root, 'b', wal=True, prefix='B')
            files = [Path(str(a) + '-wal'), Path(str(b) + '-shm'), b, a]
            _, rows, source = artifact.queryPredictions.__wrapped__(Context(root, files))
            self.assertEqual(rows, direct_rows(b)[0])
            self.assertEqual(source, str(b.relative_to(root)))
            self.assertTrue(all(row[2].startswith('B') for row in rows))

    def test_no_main_returns_no_rows(self):
        with tempfile.TemporaryDirectory() as root:
            path = create_store(root, wal=True)
            headers, rows, source = artifact.queryPredictions.__wrapped__(Context(root, [Path(str(path) + '-wal')]))
            self.assertEqual(len(headers), 6)
            self.assertEqual(rows, [])
            self.assertEqual(source, '')


if __name__ == '__main__':
    unittest.main()
