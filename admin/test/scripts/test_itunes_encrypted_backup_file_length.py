"""A file from an encrypted backup is staged at its stored length, not its manifest Size.

FileSeekerItunes decrypted a file and wrote decrypted[0:Size], with Size taken from the
file's Manifest.db record. For SQLite databases that Size can differ from the copy the
backup stored, in both directions. Measured on two encrypted backups of one device
(iOS 13.3.1 and iOS 14.3): 69 of 3,075 and 88 of 4,520 files, every one a SQLite
database, and in every one the header page count times the page size equalled the
stored length with its PKCS#7 padding removed and never equalled Size. A smaller Size
cut pages off the end and SQLite refused the file; a larger Size left the 16 byte
padding block on the end.

The decrypted Manifest.db the seeker stages carried the same 16 byte padding block on
both backups (stored 6,758,416 and 9,273,360 bytes, header 6,758,400 and 9,273,344).
SQLite read it either way.

These tests build an encrypted backup with a constructed keybag and read files back
through the seeker.
"""
import hashlib
import os
import pathlib
import plistlib
import sqlite3
import struct
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.keywrap import aes_key_wrap
from cryptography.hazmat.primitives.padding import PKCS7

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.search_files import FileSeekerItunes, decrypt_itunes_backup  # noqa: E402  pylint: disable=wrong-import-position

PASSCODE = 'constructed'
CLASS_ID = 3
ZERO_IV = b'\x00' * 16
PAGE_SIZE = 4096
ROWS = 400


def _encrypt(key, plaintext, pad=True):
    if pad:
        padder = PKCS7(algorithms.AES.block_size).padder()
        plaintext = padder.update(plaintext) + padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.CBC(ZERO_IV)).encryptor()
    return encryptor.update(plaintext) + encryptor.finalize()


def _tlv(tag, value):
    return tag + struct.pack('>I', len(value)) + value


def _file_record(wrapped_key, size):
    """The NSKeyedArchiver MBFile record a Manifest.db row holds for one file."""
    return plistlib.dumps({
        '$version': 100000,
        '$archiver': 'NSKeyedArchiver',
        '$top': {'root': plistlib.UID(1)},
        '$objects': [
            '$null',
            {'Size': size, 'Birth': 1600000000, 'LastModified': 1600000000,
             'ProtectionClass': CLASS_ID, 'EncryptionKey': plistlib.UID(2),
             '$class': plistlib.UID(4)},
            {'NS.data': struct.pack('<I', CLASS_ID) + wrapped_key, '$class': plistlib.UID(3)},
            {'$classname': 'NSMutableData', '$classes': ['NSMutableData', 'NSData', 'NSObject']},
            {'$classname': 'MBFile', '$classes': ['MBFile', 'NSObject']},
        ],
    }, fmt=plistlib.PlistFormat.FMT_BINARY)


class EncryptedBackupFileLengthTests(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        self.backup = self.tmp / 'backup'
        self.backup.mkdir()
        self.data_folder = self.tmp / 'data'
        self.data_folder.mkdir()

        self.class_key = os.urandom(32)
        self.manifest_key = os.urandom(32)
        dpsl, salt = os.urandom(20), os.urandom(20)
        passcode_key = hashlib.pbkdf2_hmac(
            'sha1', hashlib.pbkdf2_hmac('sha256', PASSCODE.encode(), dpsl, 1), salt, 1, dklen=32)
        keybag = b''.join((
            _tlv(b'UUID', os.urandom(16)),
            _tlv(b'DPSL', dpsl), _tlv(b'DPIC', struct.pack('>I', 1)),
            _tlv(b'SALT', salt), _tlv(b'ITER', struct.pack('>I', 1)),
            _tlv(b'UUID', os.urandom(16)),
            _tlv(b'CLAS', struct.pack('>I', CLASS_ID)),
            _tlv(b'WPKY', aes_key_wrap(passcode_key, self.class_key)),
        ))
        (self.backup / 'Manifest.plist').write_bytes(plistlib.dumps({
            'IsEncrypted': True,
            'BackupKeyBag': keybag,
            'ManifestKey': struct.pack('<I', CLASS_ID)
                           + aes_key_wrap(self.class_key, self.manifest_key),
        }))
        self.records = []
        self.manifest_contents = b''

    def _database(self):
        """A SQLite database of several pages, as bytes."""
        path = self.tmp / 'source.db'
        db = sqlite3.connect(path)
        db.execute(f'PRAGMA page_size={PAGE_SIZE}')
        db.execute('CREATE TABLE message (id INTEGER PRIMARY KEY, body TEXT)')
        db.executemany('INSERT INTO message (body) VALUES (?)', [('x' * 200,)] * ROWS)
        db.commit()
        db.close()
        contents = path.read_bytes()
        path.unlink()
        return contents

    def _add_file(self, relative_path, plaintext, manifest_size, pad=True):
        file_key = os.urandom(32)
        file_id = hashlib.sha1(f'HomeDomain-{relative_path}'.encode()).hexdigest()
        folder = self.backup / file_id[:2]
        folder.mkdir(exist_ok=True)
        (folder / file_id).write_bytes(_encrypt(file_key, plaintext, pad))
        self.records.append((file_id, 'HomeDomain', relative_path, 1,
                             _file_record(aes_key_wrap(self.class_key, file_key), manifest_size)))

    def _seeker(self, pad_manifest=True):
        manifest = self.tmp / 'Manifest.plain.db'
        db = sqlite3.connect(manifest)
        db.execute('CREATE TABLE Files (fileID TEXT PRIMARY KEY, domain TEXT, '
                   'relativePath TEXT, flags INTEGER, file BLOB)')
        db.executemany('INSERT INTO Files VALUES (?, ?, ?, ?, ?)', self.records)
        db.commit()
        db.close()
        self.manifest_contents = manifest.read_bytes()
        (self.backup / 'Manifest.db').write_bytes(
            _encrypt(self.manifest_key, self.manifest_contents, pad_manifest))
        manifest.unlink()

        keys, message = decrypt_itunes_backup(str(self.backup), PASSCODE)
        self.assertEqual(message, 'Decryption successful')
        return FileSeekerItunes(str(self.backup), str(self.data_folder), 'db', keys)

    def _stage(self, pattern):
        found = self._seeker().search(pattern)
        self.assertEqual(len(found), 1)
        return pathlib.Path(found[0])

    def _assert_reads(self, staged):
        db = sqlite3.connect(f'file:{staged}?mode=ro', uri=True)
        self.addCleanup(db.close)
        self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(db.execute('SELECT count(*) FROM message').fetchone()[0], ROWS)

    def test_manifest_size_smaller_than_stored_file(self):
        contents = self._database()
        self.assertGreater(len(contents), 4 * PAGE_SIZE)
        self._add_file('Library/Stale/small.db', contents, len(contents) - 2 * PAGE_SIZE)
        staged = self._stage('*/small.db')
        self.assertEqual(staged.read_bytes(), contents)
        self._assert_reads(staged)

    def test_manifest_size_larger_than_stored_file(self):
        contents = self._database()
        self._add_file('Library/Stale/large.db', contents, len(contents) + 2 * PAGE_SIZE)
        staged = self._stage('*/large.db')
        self.assertEqual(staged.read_bytes(), contents)
        self._assert_reads(staged)

    def test_manifest_size_equal_to_stored_file(self):
        for name, contents in (('odd.bin', b'seven b'), ('block.bin', b'b' * 32)):
            self._add_file(f'Library/Exact/{name}', contents, len(contents))
        self.assertEqual(self._stage('*/odd.bin').read_bytes(), b'seven b')
        self.assertEqual(self._stage('*/block.bin').read_bytes(), b'b' * 32)

    def test_no_valid_padding_falls_back_to_manifest_size(self):
        # Stored without padding, and the last byte (0) is not a padding length.
        contents = b'a' * 20 + b'\x00' * 12
        self._add_file('Library/Unpadded/raw.bin', contents, 20, pad=False)
        self.assertEqual(self._stage('*/raw.bin').read_bytes(), b'a' * 20)

    def test_manifest_is_staged_without_its_padding(self):
        self._add_file('Library/Exact/odd.bin', b'seven b', 7)
        self._seeker()
        self.assertEqual((self.data_folder / 'Manifest.db').read_bytes(), self.manifest_contents)

    def test_manifest_with_no_valid_padding_is_staged_as_decrypted(self):
        self._add_file('Library/Exact/odd.bin', b'seven b', 7)
        seeker = self._seeker(pad_manifest=False)
        self.assertEqual((self.data_folder / 'Manifest.db').read_bytes(), self.manifest_contents)
        self.assertEqual(len(seeker.search('*/odd.bin')), 1)



if __name__ == '__main__':
    unittest.main()
