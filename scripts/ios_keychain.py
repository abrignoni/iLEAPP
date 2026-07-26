"""Lookup of app secrets in an examiner-supplied iOS keychain.

iOS keychains are captured separately from the file system extraction, so an
app that keeps its database key in the keychain cannot find that key inside the
extraction. The examiner supplies the keychain with --keychain (or the field in
the GUI) and artifacts read it through here.

Apps whose keys live in the keychain include Signal and Session (both a 48 byte
GRDBDatabaseCipherKeySpec that is a 32 byte key followed by a 16 byte salt),
Snapchat, Trust Wallet and what3words, so the lookup is deliberately generic
rather than written around one app.

Supported inputs are the plist keychain dumps produced by extraction tools,
which hold generic passwords under a 'genp' list. Entries carry an access group
('agrp') naming the owning app, an account ('acct'), a service ('svce') and the
secret itself in 'v_Data'.
"""
import plistlib

from scripts.context import Context
from scripts.ilapfuncs import logfunc

GENERIC_PASSWORD_KEY = 'genp'

_cache = {}


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
    except (OSError, ValueError) as error:
        logfunc(f'Keychain: could not read {keychain_path}: {error}')
        return _cache[keychain_path]

    if not isinstance(parsed, dict) or GENERIC_PASSWORD_KEY not in parsed:
        logfunc(f'Keychain: {keychain_path} is not a supported keychain dump '
                '(no generic password entries found)')
        return _cache[keychain_path]

    entries = parsed.get(GENERIC_PASSWORD_KEY) or []
    _cache[keychain_path] = [entry for entry in entries if isinstance(entry, dict)]
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
    keychain_path = Context.get_keychain_path()
    if not keychain_path:
        return None

    matches = find_keychain_secrets(keychain_path, access_group, account, service)
    if expected_length is not None:
        matches = [secret for secret in matches if len(secret) == expected_length]
    if not matches:
        return None
    if len(matches) > 1:
        logfunc(f'Keychain: {len(matches)} entries matched {access_group}/{account}, '
                'using the first')
    return matches[0]
