"""A short referenced media ID must not abort message parsing."""
from pathlib import Path
import sqlite3
import struct
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import mmh3

from scripts.artifacts import telegramMesssages as module


def blob(value):
    return struct.pack('<i', len(value)) + value


class TelegramMessageMediaIds(unittest.TestCase):
    def test_short_referenced_file_id_preserves_message(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'telegram-data/account-1/postbox/db/db_sqlite'
            path.parent.mkdir(parents=True)
            # Postbox root object containing a file with a one-byte ID.
            fields = b'\x01i\x0a' + blob(b'\x01')
            media = b'\x01_\x05' + struct.pack(
                '<i', mmh3.hash('TelegramMediaFile', seed=4157243346)) + blob(fields)
            message = (struct.pack('<bIIBIIbb', 0, 1, 0, 0, 4, 0, 0, 0)
                       + blob(b'message with short media ID')
                       + struct.pack('<iii', 0, 0, 1)  # No attributes or embedded media; one reference.
                       + struct.pack('<iq', 1, 42))
            with sqlite3.connect(path) as db:
                for table in ('t2', 't6', 't7'):
                    db.execute(f'CREATE TABLE {table} (key, value)')
                db.execute('INSERT INTO t6 VALUES (?, ?)',
                           (struct.pack('>iq', 1, 42), b'\0' + blob(media)))
                db.execute('INSERT INTO t7 VALUES (?, ?)',
                           (struct.pack('>qiii', 7, 0, 1700000000, 1), message))
            with patch.object(module, 'logfunc') as log:
                _, rows, _ = module.telegramMessages.__wrapped__(
                    SimpleNamespace(get_files_found=lambda: [str(path)]))
            self.assertEqual([row[5] for row in rows], ['message with short media ID'])
            log.assert_called_once_with(
                'TelegramMediaFile: short media ID (1 bytes); using unknown ID')


if __name__ == '__main__':
    unittest.main()
