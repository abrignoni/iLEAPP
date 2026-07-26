"""Lookup of app secrets in an examiner-supplied iOS keychain.

iOS keychains are captured separately from the file system extraction, so an
app that keeps its database key in the keychain cannot find that key inside the
extraction. The examiner supplies the keychain with --keychain (or the field in
the GUI) and artifacts read it through here.

Apps whose keys live in the keychain include Signal and Session (both a 48 byte
GRDBDatabaseCipherKeySpec that is a 32 byte key followed by a 16 byte salt),
Snapchat, Trust Wallet and what3words, so the lookup is deliberately generic
rather than written around one app.

Two plist layouts are supported.

Decrypted dumps hold generic passwords under a 'genp' list, where each entry
carries an access group ('agrp') naming the owning app, an account ('acct'), a
service ('svce') and the secret itself in 'v_Data'.

Encrypted dumps, written by UFED as backup_keychain_v2.plist, instead hold a
'keychainEntries' list where the account name and the secret are both
ciphertext. They can still be read, because the extraction stores the material
needed alongside the data: each entry carries its own unwrapped data key, and
the metadata key is unwrapped with a per-class key from
'classKeyIdxToUnwrappedMetadataClassKey'. Both payloads are NSKeyedArchiver
blobs holding an AES-GCM ciphertext, initialisation vector and authentication
code, and the plaintext is ASN.1 DER.

Credit for documenting that encrypted layout goes to Matthieu Regnery and Matt
Smith, whose UFED keychain decrypter described it. This is an independent
implementation using iLEAPP's existing dependencies.
"""
import io
import os
import plistlib

import nska_deserialize
from Crypto.Cipher import AES
from pyasn1.codec.der.decoder import decode as der_decode

from scripts.context import Context
from scripts.ilapfuncs import logfunc

GENERIC_PASSWORD_KEY = 'genp'
ENCRYPTED_ENTRIES_KEY = 'keychainEntries'
METADATA_CLASS_KEYS_KEY = 'classKeyIdxToUnwrappedMetadataClassKey'

# Some extractions carry a keychain dump of their own. These are the locations
# worth looking in when the examiner did not supply one, matching the paths the
# keychain artifact already uses.
IN_EXTRACTION_KEYCHAIN_GLOBS = (
    '*/extra/KeychainDump/backup_keychain_v2.plist',
    '*/keychain-backup.plist',
)

_cache = {}
_discovered = {}


def _decrypt_gcm(archived_blob, key):
    """Open an NSKeyedArchiver-wrapped AES-GCM payload."""
    root = nska_deserialize.deserialize_plist(io.BytesIO(archived_blob),
                                              full_recurse_convert_nska=True, format=dict)
    cipher = AES.new(key[:32], AES.MODE_GCM, root['SFInitializationVector'])
    return cipher.decrypt_and_verify(root['SFCiphertext'], root['SFAuthenticationCode'])


def _der_fields(plaintext):
    """Turn the decrypted ASN.1 DER structure into a plain dict."""
    decoded = der_decode(plaintext)[0]
    fields = {}
    for pair in decoded:
        value = pair[1]
        fields[str(pair[0])] = bytes(value) if 'Octet' in str(type(value)) else str(value)
    return fields


def _decrypt_wrapped_entries(parsed, keychain_path):
    """Convert UFED's encrypted keychain entries into decrypted genp-style dicts."""
    class_keys = parsed.get(METADATA_CLASS_KEYS_KEY)
    if not isinstance(class_keys, dict):
        class_keys = {}
    wrapped = parsed.get(ENCRYPTED_ENTRIES_KEY)
    if not isinstance(wrapped, list):
        logfunc(f'Keychain: {keychain_path} is not a supported keychain dump '
                '(its encrypted entries are not a list)')
        return []

    entries = []
    failures = 0
    for entry in wrapped:
        # Entries stored in the clear carry rawData instead of an encrypted pair
        if not isinstance(entry, dict) or 'rawData' in entry:
            continue
        try:
            metadata_part = entry['metadata']
            class_key = class_keys[str(entry['classKeyIdx'])]
            metadata_key = _decrypt_gcm(metadata_part['wrappedKey'], class_key)
            fields = _der_fields(_decrypt_gcm(metadata_part['ciphertext'], metadata_key))
            data_part = entry['data']
            fields.update(_der_fields(_decrypt_gcm(data_part['ciphertext'],
                                                   data_part['unwrappedKey'])))
            entries.append(fields)
        except Exception:  # pylint: disable=broad-except
            failures += 1

    if entries:
        message = f'Keychain: decrypted {len(entries)} entries from {keychain_path}'
        if failures:
            message += f' ({failures} could not be decrypted)'
        logfunc(message)
    elif failures:
        logfunc(f'Keychain: none of the {failures} encrypted entries in {keychain_path} '
                'could be decrypted')
    return entries


def _text(entry, field):
    """Keychain string fields are sometimes bytes and sometimes str."""
    value = entry.get(field)
    if isinstance(value, bytes):
        return value.decode('utf-8', 'ignore').rstrip('\x00')
    return str(value) if value is not None else ''


def load_keychain_entries(keychain_path):
    """Return the generic-password entries of a keychain plist, cached per path."""
    if keychain_path in _cache:
        return _cache[keychain_path]

    _cache[keychain_path] = []
    try:
        with open(keychain_path, 'rb') as keychain_file:
            parsed = plistlib.load(keychain_file)
    except Exception as error:  # pylint: disable=broad-except
        # The file is whatever the examiner pointed at, and plistlib does not funnel
        # every way it can fail into one exception type: a truncated binary plist
        # raises InvalidFileException, a malformed XML one raises ExpatError from
        # expat, and a deeply nested one raises RecursionError. Anything unreadable
        # means the same thing here, so report it rather than letting it escape.
        logfunc(f'Keychain: could not read {keychain_path}: {error}')
        return _cache[keychain_path]

    if not isinstance(parsed, dict):
        logfunc(f'Keychain: {keychain_path} is not a supported keychain dump')
        return _cache[keychain_path]

    if GENERIC_PASSWORD_KEY in parsed:
        entries = parsed.get(GENERIC_PASSWORD_KEY)
        if not isinstance(entries, list):
            logfunc(f'Keychain: {keychain_path} is not a supported keychain dump '
                    '(its generic password entries are not a list)')
            return _cache[keychain_path]
        _cache[keychain_path] = [entry for entry in entries if isinstance(entry, dict)]
        logfunc(f'Keychain: read {len(_cache[keychain_path])} entries from {keychain_path}')
    elif ENCRYPTED_ENTRIES_KEY in parsed:
        _cache[keychain_path] = _decrypt_wrapped_entries(parsed, keychain_path)
    else:
        logfunc(f'Keychain: {keychain_path} is not a supported keychain dump '
                '(no generic password or encrypted entries found)')
    return _cache[keychain_path]


def find_keychain_secrets(keychain_path, access_group=None, account=None, service=None):
    """Return the raw secrets matching the given access group, account and service.

    Each filter is optional and matched case-insensitively as a substring, so
    'whispersystems' matches the full 'TEAMID.org.whispersystems.signal'.
    """
    matches = []
    for entry in load_keychain_entries(keychain_path):
        if access_group and access_group.lower() not in _text(entry, 'agrp').lower():
            continue
        if account and account.lower() not in _text(entry, 'acct').lower():
            continue
        if service and service.lower() not in _text(entry, 'svce').lower():
            continue
        secret = entry.get('v_Data')
        if isinstance(secret, (bytes, bytearray)):
            matches.append(bytes(secret))
    return matches


def _discover_keychain():
    """Look for a keychain the extraction carries, when none was supplied.

    Returns a path, or None. The result is cached, including the negative case,
    so the search runs once per run rather than once per artifact.
    """
    if 'path' in _discovered:
        return _discovered['path']
    _discovered['path'] = None

    try:
        seeker = Context.get_seeker()
    except Exception:  # pylint: disable=broad-except
        return None  # called outside an artifact, nothing to search
    if seeker is None:
        return None

    for glob in IN_EXTRACTION_KEYCHAIN_GLOBS:
        try:
            found = [str(path) for path in seeker.search(glob)]
        except Exception:  # pylint: disable=broad-except
            continue
        for candidate in found:
            if not os.path.isfile(candidate):
                continue
            logfunc('Keychain: no keychain was supplied, trying the one carried by the '
                    f'extraction at {candidate}')
            # Only accept it if it actually yields entries we can read
            if load_keychain_entries(candidate):
                _discovered['path'] = candidate
                return candidate
            logfunc('Keychain: that keychain yielded no readable entries, ignoring it')
    return None


def active_keychain_path():
    """The keychain to read: the supplied one, else one found in the extraction."""
    return Context.get_keychain_path() or _discover_keychain()


def report_supplied_keychain():
    """Record the examiner-supplied keychain in the log at the start of a run.

    Reading it here rather than waiting for an artifact to ask for a secret gives
    the report a note of which keychain was used, and tells the examiner straight
    away when the file they picked is not a keychain at all. Without this, a run
    where no keychain-reading artifact happens to fire says nothing either way.
    """
    keychain_path = Context.get_keychain_path()
    if not keychain_path:
        return  # nothing supplied; a keychain carried by the extraction is found later
    if not load_keychain_entries(keychain_path):
        logfunc('Keychain: the supplied file yielded no usable entries, so artifacts '
                'that need the keychain will report their data as still encrypted.')


def get_app_secret(access_group, account=None, service=None, expected_length=None):
    """Return one secret for an app from the examiner-supplied keychain, or None.

    Args:
        access_group: substring of the owning app's access group, for example
            'org.whispersystems.signal'.
        account: substring of the account name, for example
            'GRDBDatabaseCipherKeySpec'.
        service: substring of the service name, when needed to disambiguate.
        expected_length: if given, only a secret of exactly this many bytes is
            returned, which guards against picking up an unrelated entry.

    Returns:
        The secret as bytes, or None when no keychain was supplied or nothing matched.
    """
    path = active_keychain_path()
    if not path:
        return None

    matches = find_keychain_secrets(path, access_group, account, service)
    if expected_length is not None:
        matches = [secret for secret in matches if len(secret) == expected_length]
    if not matches:
        return None
    if len(matches) > 1:
        logfunc(f'Keychain: {len(matches)} entries matched {access_group}/{account}, '
                'using the first')
    return matches[0]
