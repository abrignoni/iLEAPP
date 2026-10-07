"""Preserve stored Zoom flags alongside the existing interpretation."""
import inspect
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import zoomChat

MESSAGE_COLUMNS = ('timeStamp, messageTimestamp, senderName, body, sentByMe, buddyID, '
                   'groupID, messageID, msgType, msgState, readed, giphyID, thread_id')
FILE_COLUMNS = ('name, localPath, fileSize, timestamp, messageID, webFileID, sentByMe, '
                'owner, downloaded, type')


def create_store(path, affinity=''):
    """Use real SQLite column affinity rather than assumed inserted types."""
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    for table, columns in [('msg_t_one', MESSAGE_COLUMNS), ('zoom_mm_file', FILE_COLUMNS)]:
        definition = ','.join(name.strip() + (' ' + affinity if name.strip() == 'sentByMe'
                                             and affinity else '')
                              for name in columns.split(','))
        connection.execute('CREATE TABLE ' + table + '(' + definition + ')')
    connection.commit()
    return connection


class TestZoomRawSentByMe(unittest.TestCase):
    """Check typed cursor values, repeats and an actual uncheckpointed WAL."""

    def test_storage_classes_and_affinities(self):
        values = [None, 0, 1, -1, 7, 0.0, 1.0, '1', '01', ' 1 ', '', b'1', b'', 1]
        for affinity in ['', 'INTEGER', 'TEXT']:
            with self.subTest(affinity=affinity), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = root / 'Containers/Data/Application/A/Documents/data/a@xmpp.zoom.us/a.asyn.db'
                connection = create_store(path, affinity)
                for ordinal, value in enumerate(values):
                    connection.execute('INSERT INTO msg_t_one VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                                       (1700000000, 1700000000000, 'sender', str(ordinal), value,
                                        'buddy', '', str(ordinal), 1, 2, 0, '', 'thread'))
                    connection.execute('INSERT INTO zoom_mm_file VALUES(?,?,?,?,?,?,?,?,?,?)',
                                       ('file', '', 0, 1700000000000, str(ordinal), '', value,
                                        'owner', 0, 1))
                connection.commit()
                expected = connection.execute('SELECT sentByMe FROM msg_t_one').fetchall()
                connection.close()
                context = SimpleNamespace(get_files_found=lambda path=path: [str(path)])
                for function, raw_index, width in [(zoomChat.zoom_ios_chat_messages, 2, 18),
                                                    (zoomChat.zoom_ios_shared_files, 7, 16)]:
                    _, rows, source = inspect.unwrap(function)(context)
                    self.assertEqual(source, str(path))
                    self.assertEqual(len(rows), len(values))
                    self.assertTrue(all(len(row) == width for row in rows))
                    self.assertEqual([(type(row[raw_index]), row[raw_index]) for row in rows],
                                     [(type(value), value) for (value,) in expected])
                    self.assertEqual([row[raw_index - 1] for row in rows],
                                     ['Outgoing' if str(value) == '1' else 'Incoming'
                                      for (value,) in expected])

    def test_basename_selection_keeps_account_and_container_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prefix = root / 'Containers/Data/Application'
            paths = []
            for container, account, folder, payload in [
                    ('A', 'one', 'first', b'first'),
                    ('A', 'one', 'second', b'second'),
                    ('A', 'two', 'first', b'other account'),
                    ('B', 'one', 'first', b'other container')]:
                path = (prefix / container / 'Documents/data' /
                        (account + '@xmpp.zoom.us') / folder / 'same.png')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
                paths.append(str(path))
            index = zoomChat._stored_files(paths)  # pylint: disable=protected-access
            first = paths[0]
            container = zoomChat._container(first)  # pylint: disable=protected-access
            self.assertEqual(index[(container, 'one@xmpp.zoom.us', 'same.png')], first)
            self.assertEqual(len(index), 3)
            reversed_index = zoomChat._stored_files(  # pylint: disable=protected-access
                list(reversed(paths)))
            self.assertEqual(reversed_index[(container, 'one@xmpp.zoom.us', 'same.png')], paths[1])

    def test_wal_only_rows_and_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'live.asyn.db'
            connection = create_store(path)
            connection.execute('PRAGMA journal_mode=WAL')
            connection.execute('PRAGMA wal_autocheckpoint=0')
            connection.execute('INSERT INTO msg_t_one VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                               (1700000000, 1700000000000, 'sender', 'WAL', None,
                                'buddy', '', 'repeat', 1, 0, 0, '', 'thread'))
            connection.commit()
            captured = root / 'captured.asyn.db'
            for suffix in ['', '-wal', '-shm']:
                shutil.copy2(str(path) + suffix, str(captured) + suffix)
            main_only = root / 'main.asyn.db'
            shutil.copy2(captured, main_only)
            context = SimpleNamespace(get_files_found=lambda: [str(captured)])
            _, rows, _ = inspect.unwrap(zoomChat.zoom_ios_chat_messages)(context)
            self.assertEqual(len(rows), 1)
            self.assertIsNone(rows[0][2])
            context.get_files_found = lambda: [str(main_only)]
            self.assertEqual(inspect.unwrap(zoomChat.zoom_ios_chat_messages)(context)[1], [])
            connection.close()


if __name__ == '__main__':
    unittest.main()
