"""Regression tests for the pure-python SQLCipher reader.

The reader's scheme correctness was established against real encrypted
databases: Signal for Android, which keeps its salt in the file, and Signal for
iOS, which keeps a plaintext header and an external salt. Those files cannot be
committed, so these tests encrypt known page-aligned content in the same
on-disk layout and check the reader returns it byte for byte, guarding the
page, HMAC, WAL and plaintext-header handling against future edits.

The comparison is at byte level rather than by opening the result with sqlite3.
A real SQLCipher database reserves the tail of every page for the IV and HMAC,
so its pages are laid out differently from one written by plain sqlite3, and a
fixture built with sqlite3 would not survive the reserved-tail carve-out.
"""
import hashlib
import hmac
import os
import pathlib
import struct
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Crypto.Cipher import AES  # noqa: E402  pylint: disable=wrong-import-position

from scripts.sqlcipher_decrypt import decrypt_sqlcipher_db  # noqa: E402  pylint: disable=wrong-import-position

PAGE_SIZE = 4096
IV_LENGTH = 16
HMAC_LENGTHS = {'sha1': 20, 'sha256': 32, 'sha512': 64}


def reserve_for(hmac_name):
    return ((IV_LENGTH + HMAC_LENGTHS[hmac_name] + 15) // 16) * 16


def build_page_content(page_count, reserve, plaintext_header_size=0):
    """Pages shaped like a SQLCipher database: content followed by a reserved tail."""
    usable = PAGE_SIZE - reserve
    pages = []
    for index in range(page_count):
        body = bytes([(index + 1) % 251]) * usable
        if index == 0:
            prefix = (b'H' * plaintext_header_size if plaintext_header_size
                      else b'SQLite format 3\x00')
            body = prefix + body[len(prefix):]
        pages.append(body + b'\x00' * reserve)
    return b''.join(pages)


def encrypt_like_sqlcipher(content, out_path, key, salt, hmac_name='sha1',
                           plaintext_header_size=0):
    """Write content in the SQLCipher on-disk layout: ciphertext, then IV, then HMAC."""
    mac_length = HMAC_LENGTHS[hmac_name]
    reserve = reserve_for(hmac_name)
    hmac_key = hashlib.pbkdf2_hmac(hmac_name, key, bytes(b ^ 0x3A for b in salt), 2, 32)
    digest = getattr(hashlib, hmac_name)
    clear_size = plaintext_header_size or 16

    out = bytearray()
    for index in range(len(content) // PAGE_SIZE):
        page = content[index * PAGE_SIZE:(index + 1) * PAGE_SIZE]
        if index == 0:
            # Page 1 keeps a prefix in the clear: the salt, or the plaintext header
            clear = page[:clear_size] if plaintext_header_size else salt
            body = page[clear_size:PAGE_SIZE - reserve]
        else:
            clear = b''
            body = page[:PAGE_SIZE - reserve]

        iv = os.urandom(IV_LENGTH)
        cipher = AES.new(key, AES.MODE_CBC, iv).encrypt(body)
        # The HMAC covers the ciphertext and IV, never the cleartext prefix
        mac = hmac.new(hmac_key, cipher + iv + (index + 1).to_bytes(4, 'little'),
                       digest).digest()
        out += clear + cipher + iv + mac + b'\x00' * (reserve - IV_LENGTH - mac_length)
    pathlib.Path(out_path).write_bytes(bytes(out))


class TestSqlcipherDecrypt(unittest.TestCase):

    def _roundtrip(self, hmac_name, plaintext_header_size, pages=6):
        reserve = reserve_for(hmac_name)
        content = build_page_content(pages, reserve, plaintext_header_size)
        key, salt = os.urandom(32), os.urandom(16)
        with tempfile.TemporaryDirectory() as folder:
            encrypted = os.path.join(folder, 'enc.db')
            recovered = os.path.join(folder, 'out.db')
            encrypt_like_sqlcipher(content, encrypted, key, salt, hmac_name,
                                   plaintext_header_size)
            decrypted, verified = decrypt_sqlcipher_db(
                encrypted, key, recovered, raw_key=True,
                external_salt=salt if plaintext_header_size else None,
                plaintext_header_size=plaintext_header_size,
                hmac_algorithm=hmac_name, kdf_algorithm=hmac_name)
            self.assertEqual(decrypted, pages)
            self.assertEqual(verified, pages, 'every page should authenticate')
            self.assertEqual(pathlib.Path(recovered).read_bytes(), content,
                             'decrypted bytes should match the original content')

    def test_roundtrip_salt_in_file(self):
        """The Android shape: salt stored in the file, sha1 HMAC."""
        self._roundtrip('sha1', plaintext_header_size=0)

    def test_roundtrip_plaintext_header_and_external_salt(self):
        """The iOS shape: 32 byte plaintext header, salt supplied separately, sha512."""
        self._roundtrip('sha512', plaintext_header_size=32)

    def test_roundtrip_sha256(self):
        """The HMAC choice drives the reserved size, so cover the middle option too."""
        self._roundtrip('sha256', plaintext_header_size=0)

    def test_wrong_key_authenticates_nothing(self):
        """A wrong key must report zero verified pages rather than raising."""
        reserve = reserve_for('sha1')
        content = build_page_content(4, reserve)
        with tempfile.TemporaryDirectory() as folder:
            encrypted = os.path.join(folder, 'enc.db')
            encrypt_like_sqlcipher(content, encrypted, os.urandom(32), os.urandom(16))
            _, verified = decrypt_sqlcipher_db(encrypted, os.urandom(32),
                                               os.path.join(folder, 'out.db'), raw_key=True)
            self.assertEqual(verified, 0)

    def test_short_file_is_handled(self):
        """A truncated file must return zeros, not raise."""
        with tempfile.TemporaryDirectory() as folder:
            encrypted = os.path.join(folder, 'tiny.db')
            pathlib.Path(encrypted).write_bytes(b'\x00' * 100)
            self.assertEqual(
                decrypt_sqlcipher_db(encrypted, os.urandom(32),
                                     os.path.join(folder, 'out.db'), raw_key=True),
                (0, 0))

    def test_malformed_wal_is_ignored(self):
        """A WAL without the expected magic must be skipped, leaving the main image."""
        reserve = reserve_for('sha1')
        content = build_page_content(4, reserve)
        key, salt = os.urandom(32), os.urandom(16)
        with tempfile.TemporaryDirectory() as folder:
            encrypted = os.path.join(folder, 'enc.db')
            recovered = os.path.join(folder, 'out.db')
            encrypt_like_sqlcipher(content, encrypted, key, salt)
            pathlib.Path(encrypted + '-wal').write_bytes(
                struct.pack('>I', 0xDEADBEEF) + b'\x00' * 60)
            pages, verified = decrypt_sqlcipher_db(encrypted, key, recovered, raw_key=True)
            self.assertEqual(pages, verified)
            self.assertEqual(pathlib.Path(recovered).read_bytes(), content)


if __name__ == '__main__':
    unittest.main()
