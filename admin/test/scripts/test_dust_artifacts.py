"""Synthetic Dust store, container provenance, and record-state regressions."""
from contextlib import closing
import json
from pathlib import Path
import plistlib
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from Crypto.Cipher import AES
from scripts.artifacts import dust

STORE = 'messages-12345678-1234-5678-9abc-123456789abc.sqlite3'
GROUP = 'group.com.mentionmobile.cyberdust'
KEY = bytes(range(32))


def seal(message_id, plaintext):
    # Deterministic, distinct fixture nonces for the IDs used below.
    nonce = message_id.encode().ljust(12, b'\0')
    cipher = AES.new(KEY, AES.MODE_GCM, nonce=nonce)
    cipher.update(f'dust:messages:v1:chat:{message_id}'.encode())
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return nonce + ciphertext + tag


class TestDust(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.files = []
        self.context = SimpleNamespace(
            get_files_found=lambda: self.files,
            get_relative_path=lambda p: Path(p).relative_to(self.root).as_posix(),
            get_seeker=lambda: SimpleNamespace(search=lambda pattern: self.root.rglob(pattern.removeprefix('*/'))))

    def file(self, relative, data=b''):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def rows(self, artifact):
        headers, rows, _ = artifact.__wrapped__(self.context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        return [dict(zip(names, row, strict=True)) for row in rows]

    def store(self, folder, identifier, records):
        base = 'private/var/mobile/Containers/Shared/AppGroup/' + folder
        if identifier:
            self.file(base + '/.com.apple.mobile_container_manager.metadata.plist',
                      plistlib.dumps({'MCMMetadataIdentifier': identifier}))
        path = self.file(base + '/dust/' + STORE)
        self.files.append(str(path))
        with closing(sqlite3.connect(path)) as db:
            db.execute('CREATE TABLE messages(conversation_id, message_id, sent_at, sealed)')
            db.executemany("INSERT INTO messages VALUES ('chat', ?, 1700000000.125, ?)", records)
            db.commit()

    def test_realm_sources_and_different_schemas(self):
        def stored(path, table):
            self.assertEqual(table, 'class_Account')
            folder = Path(path).parents[1].name
            return [{'id': folder, 'laterProperty': 7}] if folder == 'B' else [{'id': folder}]

        for folder in ('A', 'B', 'unrelated'):
            base = 'private/var/mobile/Containers/Data/Application/' + folder
            self.files.append(self.file(base + '/Documents/default.realm'))
            if folder != 'unrelated':
                self.files.append(self.file(base + '/Library/Preferences/com.mentionmobile.cyberdust.plist'))
        with patch.object(dust, 'realm_rows', side_effect=stored):
            rows = self.rows(dust.dustAccount)
        self.assertEqual([(r['id'], r['laterProperty']) for r in rows], [('A', ''), ('B', 7)])
        for row in rows:
            self.assertEqual(row['Source File'], f"private/var/mobile/Containers/Data/Application/{row['id']}/Documents/default.realm")

    def test_message_store_ownership_and_partial_extractions(self):
        for folder, group in [('A', GROUP), ('B', 'group.other'), ('C', None)]:
            self.store(folder, group, [(folder, b'')])
        with patch.object(dust, '_history_key', return_value=(None, 'Not decrypted: no keychain supplied')):
            rows = self.rows(dust.dustMessages)
        self.assertEqual({r['Message ID']: r['App Group'] for r in rows}, {'A': GROUP, 'C': 'Unverified'})
        self.assertEqual(len({r['Source File'] for r in rows}), 2)
        self.assertTrue(all(r['Sent At'].microsecond == 125000 for r in rows))

    def test_authenticated_payloads_and_damaged_records(self):
        messages = {
            'empty': b'{}', 'bad-json': b'bad', 'array': b'[]',
            'valid': json.dumps({'outgoing': False, 'payload': {'body': 'hello', 'sent_at': 1700000000.75,
                                                                 'message_ids': ['m1', 'm2']}}).encode(),
            'odd': b'{"outgoing":"false","payload":{"message_ids":123}}',
        }
        records = [(m, seal(m, body)) for m, body in messages.items()]
        records += [('bad-tag', seal('other-id', b'{}')), ('short', b'x')]
        self.store('A', GROUP, records)
        with patch.object(dust, '_history_key', return_value=(KEY, '')):
            rows = {r['Message ID']: r for r in self.rows(dust.dustMessages)}
        self.assertEqual(len(rows), len(records))
        self.assertEqual(rows['empty']['Decryption State'], 'Decrypted')
        self.assertEqual(rows['bad-json']['Decryption State'], 'Decrypted: invalid JSON')
        self.assertEqual(rows['array']['Decryption State'], 'Decrypted: unexpected JSON type')
        self.assertEqual(rows['bad-tag']['Decryption State'], 'Not decrypted: authentication failed')
        self.assertEqual(rows['short']['Decryption State'], 'Not decrypted: invalid sealed data')
        self.assertEqual(rows['odd']['Direction'], '')
        self.assertEqual(rows['valid']['Direction'], 'Incoming')
        self.assertEqual(rows['valid']['Referenced Message IDs'], 'm1, m2')
        self.assertEqual(rows['valid']['Sender Sent At'].microsecond, 750000)


if __name__ == '__main__':
    unittest.main()
