"""An unreadable media entry costs that entry, not the message or the artifact."""
from pathlib import Path
import sqlite3
import struct
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import mmh3

from scripts.artifacts import telegramMesssages as module

TEXT, ACTION_DATA = 5, 10
PEER, TIMESTAMP = 7, 1700000000


def blob(value):
    return struct.pack('<i', len(value)) + value


def media_file_object(fields):
    """A TelegramMediaFile root object holding the encoded fields."""
    return b'\x01_\x05' + struct.pack(
        '<i', mmh3.hash('TelegramMediaFile', seed=4157243346)) + blob(fields)


def media_file(file_id):
    """A TelegramMediaFile root object whose 'i' field holds file_id."""
    return media_file_object(b'\x01i\x0a' + blob(file_id))


def truncated_media_file():
    """A TelegramMediaFile whose 'i' field ends inside its 4-byte length prefix."""
    return media_file_object(b'\x01i\x0a' + b'\x01\x00')


def message(text, embedded=(), referenced=()):
    return (struct.pack('<bIIBIIbb', 0, 1, 0, 0, 4, 0, 0, 0)
            + blob(text)
            + struct.pack('<i', 0)  # no attributes
            + struct.pack('<i', len(embedded)) + b''.join(blob(m) for m in embedded)
            + struct.pack('<i', len(referenced))
            + b''.join(struct.pack('<iq', ns, mid) for ns, mid in referenced))


def message_key(msg_id):
    return struct.pack('>qiii', PEER, 0, TIMESTAMP, msg_id)


def reference_entry(msg_id):
    """A t6 MessageReference entry pointing at message msg_id."""
    return b'\x01' + struct.pack('<qiii', PEER, 0, msg_id, TIMESTAMP)


def run(t6, t7):
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / 'telegram-data/account-1/postbox/db/db_sqlite'
        path.parent.mkdir(parents=True)
        with sqlite3.connect(path) as db:
            for table in ('t2', 't6', 't7'):
                db.execute(f'CREATE TABLE {table} (key, value)')
            db.executemany('INSERT INTO t6 VALUES (?, ?)',
                           [(struct.pack('>iq', *key), value) for key, value in t6])
            db.executemany('INSERT INTO t7 VALUES (?, ?)',
                           [(message_key(msg_id), value) for msg_id, value in t7])
        with patch.object(module, 'logfunc') as log:
            _, rows, _ = module.telegramMessages.__wrapped__(
                SimpleNamespace(get_files_found=lambda: [str(path)]))
        return rows, [call.args[0] for call in log.call_args_list]


class TelegramMessageUnreadableMedia(unittest.TestCase):
    def test_resolved_reference_is_reported(self):
        # Control: a 12-byte ID in the referenced message matches the reference.
        rows, logs = run(
            t6=[((1, 42), reference_entry(1))],
            t7=[(1, message(b'holder', embedded=[media_file(struct.pack('<iq', 1, 42))],
                            referenced=[(1, 42)]))])
        self.assertEqual([r[TEXT] for r in rows], ['holder'])
        self.assertNotIn('could not be read', rows[0][ACTION_DATA])
        self.assertEqual(logs, [])

    def test_unresolved_reference_keeps_every_row(self):
        # The referenced message holds no media with that ID, which raised ValueError
        # and cost the artifact every row.
        rows, logs = run(
            t6=[((1, 42), reference_entry(1))],
            t7=[(1, message(b'first', referenced=[(1, 42)])),
                (2, message(b'second', referenced=[(1, 42)])),
                (3, message(b'unrelated'))])
        self.assertEqual([r[TEXT] for r in rows], ['first', 'second', 'unrelated'])
        self.assertEqual(rows[0][ACTION_DATA],
                         'Referenced media could not be read: ns=1, id=42')
        self.assertEqual(rows[1][ACTION_DATA], rows[0][ACTION_DATA])
        self.assertEqual(rows[2][ACTION_DATA], '')
        # The failed record is cached, so it is logged once, not once per message.
        self.assertEqual(len(logs), 1)
        self.assertIn('referenced media ns=1, id=42 could not be read (ValueError', logs[0])

    def test_truncated_embedded_media_keeps_the_message(self):
        # A media entry that ends mid-field raised struct.error while the message
        # itself was decoded.
        rows, logs = run(
            t6=[],
            t7=[(1, message(b'with truncated media', embedded=[truncated_media_file()])),
                (2, message(b'after it'))])
        self.assertEqual([r[TEXT] for r in rows], ['with truncated media', 'after it'])
        self.assertEqual(rows[0][ACTION_DATA], 'Embedded media could not be read')
        self.assertEqual(len(logs), 1)
        self.assertIn('embedded media entry 0', logs[0])
        self.assertIn('could not be read (struct.error', logs[0])


if __name__ == '__main__':
    unittest.main()
