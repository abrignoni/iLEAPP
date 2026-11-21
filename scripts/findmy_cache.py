"""Read a Find My fmipcore or fmfcore cache file, opening the encrypted form.

Older iOS versions write these files as plain JSON. Newer ones write a binary plist holding
encryptedData and signature. encryptedData is a 12 byte nonce, the ChaCha20-Poly1305 ciphertext and
a 16 byte tag. The key is the 32 byte symmetricKey.key.data of a binary plist kept in the keychain
item whose service and account are FMIPDataManager / FMIPDataManagerKey for fmipcore files and
FMFDataManager / FMFDataManagerKey for fmfcore files.

The layout was published in PnutCN/findmy-cache-decryptor (MIT):
https://github.com/PnutCN/findmy-cache-decryptor/blob/ff01ffda51dafdf1993ddd9ae15ff7e206120266/decrypt_findmy.py#L149-L267
That source names the key files; the keychain service, account and access group were matched on
the corpus keychains. This is an independent implementation. The signature value is not checked here; a file is accepted
only when its Poly1305 tag verifies.
"""
import json
import plistlib
from pathlib import Path
from xml.parsers.expat import ExpatError

from Crypto.Cipher import ChaCha20_Poly1305

from scripts.ilapfuncs import logfunc
from scripts.ios_keychain import active_keychain_path, find_keychain_secrets

ACCESS_GROUP = 'com.apple.findmy'
NONCE_LENGTH = 12
TAG_LENGTH = 16
KEY_LENGTH = 32
# The decrypted plists carry this text where the JSON form of the same key holds null.
NULL_TEXT = '$null'

_PLIST_ERRORS = (plistlib.InvalidFileException, ValueError, TypeError, IndexError, KeyError,
                 OverflowError, RecursionError, ExpatError)


def _loads_plist(raw):
    try:
        return plistlib.loads(raw)
    except _PLIST_ERRORS:
        return None


def _restore_nulls(value):
    if isinstance(value, dict):
        return {key: _restore_nulls(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_restore_nulls(item) for item in value]
    return None if value == NULL_TEXT else value


def _symmetric_keys(file_found):
    """Every 32 byte key the keychain holds for this file's cache."""
    keychain = active_keychain_path()
    if not keychain:
        return None
    name = 'FMFDataManager' if Path(file_found).parent.name == 'com.apple.findmy.fmfcore' \
        else 'FMIPDataManager'
    keys = []
    for secret in find_keychain_secrets(keychain, ACCESS_GROUP, f'{name}Key', name):
        wrapped = _loads_plist(secret)
        symmetric = wrapped.get('symmetricKey') if isinstance(wrapped, dict) else None
        inner = symmetric.get('key') if isinstance(symmetric, dict) else None
        data = inner.get('data') if isinstance(inner, dict) else None
        if isinstance(data, bytes) and len(data) == KEY_LENGTH:
            keys.append(data)
    return keys


def _open_encrypted(file_found, blob):
    if not isinstance(blob, bytes) or len(blob) < NONCE_LENGTH + TAG_LENGTH:
        logfunc(f'{file_found}: encryptedData is too short to hold a nonce and tag; not read')
        return None
    keys = _symmetric_keys(file_found)
    if keys is None:
        logfunc(f'{file_found} is encrypted and no keychain is available; not read. '
                'Supply the extraction\'s keychain with --keychain.')
        return None
    if not keys:
        logfunc(f'{file_found} is encrypted and the keychain in use holds no key for it; not read')
        return None
    for key in keys:
        cipher = ChaCha20_Poly1305.new(key=key, nonce=blob[:NONCE_LENGTH])
        try:
            plain = cipher.decrypt_and_verify(blob[NONCE_LENGTH:-TAG_LENGTH], blob[-TAG_LENGTH:])
        except ValueError:
            continue
        document = _loads_plist(plain)
        if document is None:
            logfunc(f'{file_found}: decrypted content is not a plist; not read')
            return None
        return _restore_nulls(document)
    logfunc(f'{file_found}: the authentication tag did not verify with the keychain key; not read')
    return None


def read_find_my_cache(file_found):
    """Return the parsed content of a cache file, or None where it cannot be read (logged)."""
    with open(file_found, 'rb') as cache_file:
        raw = cache_file.read()
    try:
        return json.loads(raw)
    except ValueError:
        pass
    if raw[:8] == b'bplist00':
        outer = _loads_plist(raw)
        if isinstance(outer, dict) and 'encryptedData' in outer:
            return _open_encrypted(file_found, outer['encryptedData'])
        logfunc(f'{file_found} is a binary plist without encryptedData; not read')
        return None
    logfunc(f'{file_found} is not JSON; not read')
    return None
