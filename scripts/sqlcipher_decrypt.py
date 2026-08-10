"""Minimal pure-python SQLCipher reader.

Implemented with PyCryptodome (already an iLEAPP requirement) rather than a
native SQLCipher build, so packaged/frozen iLEAPP builds keep working without
an extra binary dependency.

Only the subset needed to read an encrypted database is implemented: the file
is decrypted to a plaintext copy which callers open with the stdlib sqlite3.
"""
import hashlib
import hmac
import os
import struct

from Crypto.Cipher import AES

DEFAULT_PAGE_SIZE = 4096
IV_LENGTH = 16
FAST_KDF_ITER = 2  # SQLCipher's iteration count for the HMAC subkey

HMAC_LENGTHS = {'sha1': 20, 'sha256': 32, 'sha512': 64}

WAL_HEADER_SIZE = 32
WAL_FRAME_HEADER_SIZE = 24
WAL_MAGIC = (0x377F0682, 0x377F0683)


def _reserve_size(hmac_length):
    """Bytes reserved at the end of each page: IV + HMAC, padded to an AES block."""
    return ((IV_LENGTH + hmac_length + 15) // 16) * 16


def _decrypt_page(page, page_number, encryption_key, hmac_key, digest, hmac_length, reserve,
                  page_size, plaintext_header_size=0):
    """Decrypt one SQLCipher page. Returns (plaintext_body, hmac_verified)."""
    # Page 1 starts after whatever is stored in the clear: either the salt, or a
    # plaintext header when the database keeps one
    body_start = (plaintext_header_size or 16) if page_number == 1 else 0
    body_end = page_size - reserve
    iv = page[body_end:body_end + IV_LENGTH]
    stored_hmac = page[body_end + IV_LENGTH:body_end + IV_LENGTH + hmac_length]
    calculated = hmac.new(hmac_key,
                          page[body_start:body_end + IV_LENGTH]
                          + page_number.to_bytes(4, 'little'),
                          digest).digest()
    body = AES.new(encryption_key, AES.MODE_CBC, iv).decrypt(page[body_start:body_end])
    if page_number == 1:
        # Restore the bytes that were never encrypted
        body = (page[:plaintext_header_size] if plaintext_header_size
                else b'SQLite format 3\x00') + body
    return body + b'\x00' * reserve, hmac.compare_digest(calculated, stored_hmac)


def _wal_pages(wal_path, page_size):
    """Yield (page_number, raw_encrypted_page) for the committed frames of a SQLCipher WAL.

    SQLCipher leaves the WAL and frame headers readable and encrypts only the page
    payloads, so frames can be located without the key. Later frames supersede
    earlier ones for the same page; anything after the final commit frame is an
    incomplete transaction and is ignored.
    """
    with open(wal_path, 'rb') as wal_file:
        wal = wal_file.read()
    if len(wal) < WAL_HEADER_SIZE:
        return {}, 0
    if struct.unpack('>I', wal[0:4])[0] not in WAL_MAGIC:
        return {}, 0

    header_salts = wal[16:24]
    frame_size = WAL_FRAME_HEADER_SIZE + page_size
    frame_count = (len(wal) - WAL_HEADER_SIZE) // frame_size

    latest = {}
    committed = {}
    database_pages = 0
    for index in range(frame_count):
        offset = WAL_HEADER_SIZE + index * frame_size
        frame_header = wal[offset:offset + WAL_FRAME_HEADER_SIZE]
        if frame_header[8:16] != header_salts:
            continue  # frame belongs to an earlier WAL generation
        page_number = struct.unpack('>I', frame_header[0:4])[0]
        commit_size = struct.unpack('>I', frame_header[4:8])[0]
        latest[page_number] = wal[offset + WAL_FRAME_HEADER_SIZE:offset + frame_size]
        if commit_size:
            # Transaction boundary: everything seen so far is durable
            committed = dict(latest)
            database_pages = commit_size
    return committed, database_pages


def decrypt_sqlcipher_db(encrypted_path, passphrase, output_path, page_size=DEFAULT_PAGE_SIZE,
                         kdf_iterations=1, hmac_algorithm='sha1', kdf_algorithm='sha1',
                         raw_key=False, apply_wal=True, plaintext_header_size=0,
                         external_salt=None):
    """Decrypt a SQLCipher database to a plaintext SQLite file.

    Args:
        encrypted_path: path to the encrypted database.
        passphrase: passphrase string, or hex string when raw_key is True.
        output_path: where the decrypted database is written.
        page_size: SQLCipher page size.
        kdf_iterations: PBKDF2 iterations for the encryption key. Signal uses 1
            because its key is already random.
        hmac_algorithm: 'sha1', 'sha256' or 'sha512'.
        kdf_algorithm: PBKDF2 hash, usually matching hmac_algorithm.
        raw_key: treat passphrase as a hex-encoded key used directly (PRAGMA
            key = "x'..'") instead of deriving it.
        apply_wal: replay a sibling '-wal' file over the database image. Without
            this, recent records that have not been checkpointed are missed.
        plaintext_header_size: bytes at the start of the file left unencrypted.
            Apps that need the file to stay recognisable as SQLite set this,
            usually to 32.
        external_salt: the 16 byte salt, when it is not stored in the file. A
            non-zero plaintext header displaces the salt, so it is kept with the
            key instead (Signal for iOS stores both together in the keychain).

    Returns:
        (pages_decrypted, pages_whose_hmac_verified), counting replayed WAL frames
        as well as main-image pages. Equal values mean everything authenticated;
        0 verified means the passphrase or settings are wrong.
    """
    hmac_length = HMAC_LENGTHS[hmac_algorithm]
    reserve = _reserve_size(hmac_length)

    with open(encrypted_path, 'rb') as encrypted_file:
        raw = encrypted_file.read()
    if len(raw) < page_size:
        return 0, 0

    salt = external_salt if external_salt else raw[:16]
    if raw_key:
        encryption_key = passphrase if isinstance(passphrase, (bytes, bytearray)) \
            else bytes.fromhex(passphrase)
    else:
        encryption_key = hashlib.pbkdf2_hmac(kdf_algorithm, passphrase.encode(), salt,
                                             kdf_iterations, 32)
    hmac_key = hashlib.pbkdf2_hmac(kdf_algorithm, encryption_key,
                                   bytes(byte ^ 0x3A for byte in salt), FAST_KDF_ITER, 32)

    digest = getattr(hashlib, hmac_algorithm)
    decrypted_pages = verified = 0

    pages = []
    for page_index in range(len(raw) // page_size):
        body, page_ok = _decrypt_page(raw[page_index * page_size:(page_index + 1) * page_size],
                                      page_index + 1, encryption_key, hmac_key, digest,
                                      hmac_length, reserve, page_size, plaintext_header_size)
        pages.append(body)
        decrypted_pages += 1
        verified += page_ok

    # Recent activity often lives only in the write-ahead log, so replay it over
    # the main database image before handing the file to sqlite3
    if apply_wal:
        wal_path = encrypted_path + '-wal'
        if os.path.exists(wal_path):
            wal_pages, database_pages = _wal_pages(wal_path, page_size)
            for page_number, encrypted_page in sorted(wal_pages.items()):
                body, page_ok = _decrypt_page(encrypted_page, page_number, encryption_key,
                                              hmac_key, digest, hmac_length, reserve, page_size,
                                              plaintext_header_size)
                while len(pages) < page_number:
                    pages.append(b'\x00' * page_size)
                pages[page_number - 1] = body
                decrypted_pages += 1
                verified += page_ok
            if database_pages:
                pages = pages[:database_pages]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as output_file:
        output_file.write(b''.join(pages))
    return decrypted_pages, verified
