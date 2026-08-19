__artifacts_v2__ = {
    "netflix_bookmarks": {
        "name": "Netflix - Playback Bookmarks",
        "description": "Stored playback positions the Netflix app held for a title, with the "
                       "position in seconds, the time the position was last modified and the "
                       "video identifier the position belongs to",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Netflix",
        "notes": "Read from the app's GraphQL record cache under Library/gqlData, where a record "
                 "keyed on the video id and ending in '.bookmark' carries position and "
                 "lastModified. Two key spellings were seen across the app versions tested, "
                 "'Video:<id>.bookmark' and 'UnifiedEntity:Video:<id>.bookmark', and both are "
                 "accepted. Position is stored in seconds and is also formatted as hours, "
                 "minutes and seconds. Last Modified is an ISO 8601 string carrying its own UTC "
                 "designator and is reported as stored. Each gqlData file is named "
                 "<profileGuid>-<appVersion>-gql<schemaVersion>.db; in the samples tested the "
                 "name prefix equalled the guid the same file records as currentProfile, so the "
                 "Profile Guid column is taken from the file name. Title is filled in from a "
                 "UnifiedEntity record for the same video id in the same file and is left blank "
                 "when the app had not cached one. The interactive playback progress field was "
                 "null on every bookmark in the samples tested and is reported blank rather "
                 "than dropped. A bookmark records a stored playback position; it does not by "
                 "itself establish who operated the device.",
        "paths": ('*/Library/gqlData/*gql*.db*',),
        "output_types": "standard",
        "artifact_icon": "bookmark",
    },
    "netflix_profiles": {
        "name": "Netflix - Profiles",
        "description": "Profiles recorded in the Netflix app's GraphQL record cache, with the "
                       "profile name, guid, creation time, maturity rating and the kids, PIN "
                       "lock and account owner flags as stored",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Netflix",
        "notes": "Read from QUERY_ROOT.account.profiles.<n> records under Library/gqlData. "
                 "Created At is an ISO 8601 string carrying its own UTC designator and is "
                 "reported as stored. The Lock PIN field is reported exactly as the record "
                 "holds it; where the app stored no value the column is blank, which is not "
                 "evidence that no PIN was set. Maturity Rating carries a numeric level and a "
                 "label list, both reported as stored. The Current Profile column marks the "
                 "guid the same file records as currentProfile. Profile guids also appear in "
                 "the app preference file as 'Message-myProfile-<guid>' keys; those are reported "
                 "by the Netflix - Preferences artifact and are not merged here. An extraction "
                 "normally holds several gqlData files, one per app version, and each is a "
                 "separate cache of the same account, so the same profile appears once per "
                 "file. Rows identical across every reported field are collapsed to one and the "
                 "Cache Files column gives the number of files that held it; a profile whose "
                 "stored values differ between files still produces one row per distinct set. "
                 "Lock PIN was null on every profile in the samples tested.",
        "paths": ('*/Library/gqlData/*gql*.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "netflix_account": {
        "name": "Netflix - Account",
        "description": "Account level values recorded by the Netflix app, including the signed "
                       "in account name, membership start, country of sign up, the device ESN "
                       "and the app version",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Netflix",
        "notes": "Values are drawn from QUERY_ROOT.account records under Library/gqlData and "
                 "from the app preference file com.netflix.Netflix.plist. Member Since and the "
                 "other ISO 8601 values carry their own UTC designator and are reported as "
                 "stored. The ESN is the Netflix Electronic Serial Number the client presents; "
                 "its middle segment encodes a device model string, which is reported as stored "
                 "and is not translated to a marketing name. Membership Status and plan values "
                 "are reported as stored. Presence of an account name records the value the app "
                 "retained, not that a session was active at acquisition. Country Of Sign Up is "
                 "read from the record's own code field. Rows identical across every reported "
                 "field are collapsed to one, because each gqlData file caches the same "
                 "account, and the Cache Files column gives the number of files that held the "
                 "row.",
        "paths": ('*/Library/gqlData/*gql*.db*',
                  '*/Library/Preferences/com.netflix.Netflix.plist'),
        "output_types": "standard",
        "artifact_icon": "user-circle",
    },
    "netflix_continue_watching": {
        "name": "Netflix - Continue Watching",
        "description": "Entries the Netflix app cached for its Continue Watching row, with the "
                       "displayed title and the video identifier each entry points at",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Netflix",
        "notes": "Read from records whose __typename is PinotContinueWatchingEntityTreatment "
                 "under Library/gqlData. The displayed string is the localized title the app "
                 "rendered on the row. These rows are the app's cached copy of a page the "
                 "service composed for the profile, so an entry records what the row held when "
                 "it was cached rather than an individual playback event; the Netflix - Playback "
                 "Bookmarks artifact carries the stored positions and their times. No timestamp "
                 "is stored on the row itself. The same entry is cached by more than one section "
                 "and more than one file, so rows identical across every reported field are "
                 "collapsed to one and the Cache Entries column gives the number that held it.",
        "paths": ('*/Library/gqlData/*gql*.db*',),
        "output_types": "standard",
        "artifact_icon": "player-play",
    },
    "netflix_titles": {
        "name": "Netflix - Cached Titles",
        "description": "Titles the Netflix app had cached in its GraphQL record cache, with the "
                       "video identifier, the title and the entity type as stored",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Netflix",
        "notes": "One row per distinct video id carrying a title in a UnifiedEntity or Video "
                 "record under Library/gqlData. Entity Type is the record's own __typename, for "
                 "example Movie, Show or Episode, and is reported as stored. This cache holds "
                 "the catalogue the app had fetched for browsing, which includes titles the "
                 "service placed on a page as well as titles reached deliberately, so presence "
                 "here does not establish that a title was opened or played. The artwork URL is "
                 "reported as text; see the Netflix - Cached Preview Media artifact for the "
                 "media that could be linked to a title by a recorded identifier. The same title "
                 "is cached by each gqlData file, so rows identical across every reported field "
                 "are collapsed to one and the Cache Files column gives the number that held "
                 "it.",
        "paths": ('*/Library/gqlData/*gql*.db*',),
        "output_types": "standard",
        "artifact_icon": "movie",
    },
    "netflix_log_events": {
        "name": "Netflix - Log Events",
        "description": "Client log events queued by the Netflix app in its brl.sqlite store, "
                       "decrypted, with the event time, event type, session identifier, device "
                       "ESN, device model and app version",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Netflix",
        "notes": "Rows of logblobs_table in Documents/brl-dedicated/brl.sqlite. The entry_data "
                 "blob is encrypted; see the module docstring for the container layout and the "
                 "key source, which is the app's own preference file. Rows that do not decrypt "
                 "are still reported, with the payload columns blank and Decrypted set to No, so "
                 "the row count matches the table. The timestamp_ms_added column holds Unix "
                 "seconds despite the millisecond in its name, while the clienttime value inside "
                 "the payload holds Unix milliseconds; the two agreed to under a second on every "
                 "row checked in the samples tested, and both are reported. Event Type is the "
                 "table's own entry_type value, reported as stored. The database uses WAL, so "
                 "the -wal and -shm sidecars are matched with it.",
        "paths": ('*/Documents/brl-dedicated/brl.sqlite*',
                  '*/Library/Preferences/__com.netflix.derivationkeyprovider.localPersistanceSuiteName.plist'),
        "output_types": "standard",
        "artifact_icon": "file-analytics",
    },
    "netflix_secure_store": {
        "name": "Netflix - Secure Store",
        "description": "Entries of the Netflix app's encrypted key value store, decrypted, "
                       "reported by the kind of value each entry holds",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Netflix",
        "notes": "Rows of the store table in Documents/sqlstore/store.sqlite3. The value blob is "
                 "encrypted; see the module docstring for the container layout and the key "
                 "source. The domain and value_key columns are stored in the same envelope but "
                 "did not yield readable names with the key that opens the value column, so they "
                 "are not reported and each row is identified by the shape of its own value "
                 "instead. Value Kind is derived from the decrypted bytes, for example a JSON "
                 "object's top level key or a certificate encoding. Most entries hold Message "
                 "Security Layer material; token and key values are reported by length only and "
                 "their contents are not printed. The Identity column carries the ESN string "
                 "where an entry holds one. The table mixes two storage forms: some values carry "
                 "the envelope and some are written as plain UTF-8 JSON with no envelope at "
                 "all, and the Storage column says which, so a plaintext row is not reported as "
                 "a decryption failure. Where the crypto row resolves to a key, that key is "
                 "applied to every row of the table, so an entry whose plaintext is not text is "
                 "reported as decrypted with a Value Kind that names the encoding rather than "
                 "as a failure. Where the crypto row is not opened by any key present, each key "
                 "is tried in turn and only a readable result is accepted, so a row whose key has "
                 "since been rotated out of the preference file is listed as not recovered. "
                 "Such a row is still listed with its stored length so the row count matches "
                 "the table. One sample tested carried a store whose crypto row no key opened, "
                 "and rows written under the retired key were reported that way.",
        "paths": ('*/Documents/sqlstore/store.sqlite3*',
                  '*/Library/Preferences/__com.netflix.derivationkeyprovider.localPersistanceSuiteName.plist'),
        "output_types": "standard",
        "artifact_icon": "lock",
    },
    "netflix_network_observations": {
        "name": "Netflix - Network Observations",
        "description": "Per interface network measurements the Netflix app recorded in its "
                       "sqlstore last_observed table, with the interface, the observed "
                       "throughput and the exchange identifier",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Netflix",
        "notes": "Rows of the last_observed table in Documents/sqlstore/store.sqlite3, which is "
                 "stored unencrypted. Keys take the form <metric>-<interface>[-<index>], and the "
                 "interface segment is reported as stored; values seen in the samples tested "
                 "included wifi, mobile, cellular and en0. The metric names observed were xid, "
                 "bps, observedKbps and playdelay. No timestamp is stored on these rows, so they "
                 "cannot be placed in time from this table alone. A bps or Kbps figure is a "
                 "throughput measurement the client recorded for that interface, not a record of "
                 "data transferred.",
        "paths": ('*/Documents/sqlstore/store.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "network",
    },
    "netflix_preview_media": {
        "name": "Netflix - Cached Preview Media",
        "description": "Preview clips and subtitle tracks the Netflix app cached under a "
                       "directory named after a video identifier, with the media checked in and "
                       "the title filled in where the app had cached one",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Netflix",
        "notes": "Files under Library/Caches/br/ch/<videoId>/. The directory name is the video "
                 "id, which is a recorded link rather than a correlation, so each file is "
                 "attributed to the title of that id where a UnifiedEntity record for the same "
                 "id exists under Library/gqlData. File types are decided by reading the leading "
                 "bytes rather than by trusting the file name, which carries no extension; the "
                 "samples tested held MP4 video and UTF-8 WebVTT subtitle text. Video files are "
                 "checked in and rendered. The separate image caches under "
                 "Library/Caches/com.github.kean.Nuke.DataCache and Library/assetCache were "
                 "checked for a reproducible link to a title: their file names are 40 character "
                 "hex and did not match SHA-1, MD5 or SHA-256 of the artwork URL, of the URL "
                 "without its query, of the URL path, of the final path component or of the "
                 "artwork key recorded beside the URL, so no link to those images is asserted "
                 "and they are not reported here.",
        "paths": ('*/Library/Caches/br/ch/*',
                  '*/Library/gqlData/*gql*.db*'),
        "output_types": "standard",
        "artifact_icon": "video",
    },
    "netflix_preferences": {
        "name": "Netflix - Preferences",
        "description": "Selected values from the Netflix app preference file, including "
                       "identifiers the app persisted, the recorded app version and the profile "
                       "guids the app kept message state for",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Netflix",
        "notes": "Read from Library/Preferences/com.netflix.Netflix.plist. Keys are reported "
                 "with their stored names so a reader can go back to the file. Date valued keys "
                 "are reported as the plist stored them. Keys whose names begin with a profile "
                 "guid pattern, such as Message-myProfile-<guid>, are listed so the guids "
                 "present in the preference file can be compared with the profiles recorded in "
                 "the GraphQL cache. Feature flag keys are numerous and are not all reported; "
                 "the file itself carries the full set.",
        "paths": ('*/Library/Preferences/com.netflix.Netflix.plist',),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
}

"""Netflix for iOS.

Several of the app's local stores are encrypted. The envelope, established from the
samples tested, is:

    [16 byte AES-CBC IV][1 byte: count of trailing zero pad bytes][ciphertext]

The cipher is AES-128-CBC and the plaintext is zero padded to a 16 byte multiple, with
the pad count carried in the byte after the IV.

The keys are not held in the keychain. The app persists them in its own preference
domain, base64 encoded, in

    Library/Preferences/__com.netflix.derivationkeyprovider.localPersistanceSuiteName.plist

under the key __com.netflix.derivationkeyprovider.containerKey. Decoding that base64
yields an NSKeyedArchiver plist holding a DerivationKeyContainer whose materials map is
keyed by a numeric key id; each DerivationKeyRecord carries a 16 byte derivationKey.

Each encrypted database carries a one row crypto table whose entity column is the same
envelope wrapping a 16 byte value. The derivation key that unwraps it, recognised because
the plaintext is 16 bytes followed by zero padding, is the key id that database was
written under. That is a recorded selector rather than a guess, and in the samples tested
it named the key the payload columns needed in every case where it unwrapped. A store can
still hold rows written under a previously rotated key, so each blob falls back to trying
the remaining keys.

Where no key in the preference file opens a value, the row is reported with the payload
columns blank rather than dropped, so a reported row count always matches the table.
"""

import base64
import binascii
import datetime
import json
import os
import plistlib
import re
import sqlite3

from scripts.ilapfuncs import (artifact_processor, check_in_media,
                               get_sqlite_db_records, logfunc,
                               open_sqlite_db_readonly)

try:
    from Crypto.Cipher import AES
except ImportError:  # pragma: no cover - pycryptodome is a hard requirement of iLEAPP
    AES = None

PREFS_BASENAME = 'com.netflix.Netflix.plist'
KEYSTORE_BASENAME = '__com.netflix.derivationkeyprovider.localPersistanceSuiteName.plist'
CONTAINER_KEY = '__com.netflix.derivationkeyprovider.containerKey'

BOOKMARK_KEY_RE = re.compile(r'(?:^|:)Video:(\d+)\.bookmark$')
VIDEO_ID_RE = re.compile(r'(?:^|:)Video:(\d+)')
PROFILE_KEY_RE = re.compile(r'^QUERY_ROOT\.account\.profiles\.(\d+)$')
PROFILE_PREF_RE = re.compile(r'^Message-(?:myProfile|download|share)-([A-Z0-9]{20,})$')
GQL_NAME_RE = re.compile(r'^(?P<guid>[A-Z0-9]+)-(?P<version>[0-9.]+)-gql(?P<schema>[0-9.]+)\.db$')


# ---------------------------------------------------------------- generic helpers

def _iso(value):
    """Normalise an ISO 8601 string that carries its own UTC designator.

    fromisoformat did not accept a trailing Z or a fractional part other than three or
    six digits before Python 3.11, and iLEAPP supports older runtimes, so the string is
    normalised before parsing and returned as stored if it still will not parse.
    """
    if not value or not isinstance(value, str):
        return ''
    text = value.strip()
    normalised = text[:-1] + '+00:00' if text.endswith('Z') else text
    match = re.match(r'^(.*\.)(\d{1,6})(.*)$', normalised)
    if match:
        normalised = f'{match.group(1)}{match.group(2).ljust(6, "0")}{match.group(3)}'
    try:
        parsed = datetime.datetime.fromisoformat(normalised)
    except ValueError:
        return text
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(datetime.timezone.utc)
    return parsed.strftime('%Y-%m-%d %H:%M:%S')


def _unix_seconds(value):
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc).strftime(
            '%Y-%m-%d %H:%M:%S')
    except (TypeError, ValueError, OSError, OverflowError):
        return ''


def _unix_millis(value):
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc).strftime(
            '%Y-%m-%d %H:%M:%S')
    except (TypeError, ValueError, OSError, OverflowError):
        return ''


def _blank(value):
    """None must not reach a report cell as the string 'None'."""
    return '' if value is None else value


def _dedupe(rows, key_length):
    """Collapse rows identical over their first key_length fields.

    Each gqlData file is a separate cache of the same account, so the same profile,
    account or title is present once per file. Returns (row, occurrences) keeping the
    first source path seen.
    """
    order, counts = [], {}
    for row in rows:
        key = tuple(row[:key_length])
        if key not in counts:
            counts[key] = [row, 0]
            order.append(key)
        counts[key][1] += 1
    return [(counts[k][0], counts[k][1]) for k in order]


def _hms(seconds):
    try:
        total = int(seconds)
    except (TypeError, ValueError):
        return ''
    if total < 0:
        return ''
    return f'{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}'


def _plist(path):
    try:
        with open(path, 'rb') as handle:
            return plistlib.load(handle)
    except (OSError, ValueError, EOFError, plistlib.InvalidFileException) as error:
        logfunc(f'Netflix: could not read plist {path}: {error}')
        return {}


def _container_of(path):
    """Longest ancestor that still looks like the app container root."""
    parts = path.replace('\\', '/').split('/')
    for marker in ('Library', 'Documents'):
        if marker in parts:
            return '/'.join(parts[:parts.index(marker)])
    return os.path.dirname(path)


def _pick_for(target, candidates):
    """Choose the candidate sharing the longest path prefix with target."""
    if not candidates:
        return None
    container = _container_of(target)
    same = [c for c in candidates if _container_of(c) == container]
    if same:
        return same[0]
    return max(candidates, key=lambda c: len(os.path.commonprefix([c, target])))


def _files(files_found, predicate):
    seen, out = set(), []
    for path in files_found:
        normalised = str(path).replace('\\', '/')
        if normalised in seen:
            continue
        seen.add(normalised)
        if predicate(normalised):
            out.append(str(path))
    return out


def _databases(files_found, *suffixes):
    def match(path):
        return any(path.endswith(suffix) for suffix in suffixes)
    return _files(files_found, match)


def _gql_databases(files_found):
    def match(path):
        name = path.rsplit('/', 1)[-1]
        return '/Library/gqlData/' in path and name.endswith('.db') and 'gql' in name
    return _files(files_found, match)


# ---------------------------------------------------------------- decryption

def _load_keys(files_found, near):
    """Return {key_id: 16 byte key} from the app's derivation key preference file."""
    stores = _files(files_found, lambda p: p.endswith(KEYSTORE_BASENAME))
    chosen = _pick_for(near, stores) if stores else None
    if not chosen:
        return {}, None
    encoded = _plist(chosen).get(CONTAINER_KEY)
    if not encoded:
        return {}, chosen
    try:
        archive = plistlib.loads(base64.b64decode(encoded))
        objects = archive['$objects']

        def deref(ref):
            return objects[ref.data] if isinstance(ref, plistlib.UID) else ref

        materials = deref(deref(archive['$top']['root'])['materials'])
        keys = {}
        for key_ref, obj_ref in zip(materials['NS.keys'], materials['NS.objects']):
            record = deref(obj_ref)
            material = deref(record.get('derivationKey'))
            if isinstance(material, (bytes, bytearray)) and len(material) == 16:
                keys[str(deref(key_ref))] = bytes(material)
        return keys, chosen
    except (AttributeError, binascii.Error, IndexError, KeyError, TypeError,
            ValueError, plistlib.InvalidFileException) as error:
        logfunc(f'Netflix: could not read derivation keys from {chosen}: {error}')
        return {}, chosen


def _split_envelope(blob):
    if blob is None:
        return None
    raw = bytes(blob)
    if len(raw) < 17 or (len(raw) - 17) % 16:
        return None
    return raw[:16], raw[16], raw[17:]


def _decrypt(blob, key):
    parts = _split_envelope(blob)
    if parts is None or AES is None:
        return None
    iv, pad, ciphertext = parts
    if not ciphertext:
        return b''
    try:
        plain = AES.new(key, AES.MODE_CBC, iv).decrypt(ciphertext)
    except (ValueError, TypeError):
        return None
    return plain[:len(plain) - pad] if pad else plain


def _readable(plain):
    """An empty plaintext is not accepted: every key decrypts a fully padded blob to b''."""
    if not plain:
        return False
    if plain[:1] in (b'{', b'[') or plain[:8] == b'bplist00' or plain[:5] == b'-----':
        return True
    head = plain[:64]
    printable = sum(1 for byte in head if 9 <= byte <= 13 or 32 <= byte <= 126)
    return printable / len(head) > 0.85


def _stored_plain(blob):
    """Some store rows are written without the envelope, as plain UTF-8 JSON.

    Their length does not fit [16 IV][1 pad][16n ciphertext], and the bytes read as text
    from the first byte, so they are reported as stored rather than as a decryption
    failure.
    """
    if blob is None:
        return None
    raw = bytes(blob)
    if not raw or (len(raw) - 17) % 16 == 0:
        return None
    if raw[:1] not in (b'{', b'[', b'-') and raw[:8] != b'bplist00':
        return None
    head = raw[:64]
    printable = sum(1 for byte in head if 9 <= byte <= 13 or 32 <= byte <= 126)
    return raw if printable / len(head) > 0.95 else None


def _named_key(db_path, keys):
    """The key id the database's one row crypto table names, or None."""
    if not keys:
        return None
    try:
        database = open_sqlite_db_readonly(db_path)
        cursor = database.cursor()
        cursor.execute('SELECT entity FROM crypto LIMIT 1')
        row = cursor.fetchone()
        database.close()
    except (sqlite3.Error, OSError, TypeError, AttributeError):
        return None
    if not row or row[0] is None:
        return None
    parts = _split_envelope(row[0])
    if parts is None or AES is None:
        return None
    iv, _pad, ciphertext = parts
    for key_id, key in keys.items():
        try:
            plain = AES.new(key, AES.MODE_CBC, iv).decrypt(ciphertext)
        except (ValueError, TypeError):
            continue
        if len(plain) >= 32 and plain[16:] == b'\x00' * (len(plain) - 16):
            return key_id
    return None


def _open_named(blob, keys, named):
    """Decrypt with the key the database's crypto row names.

    That row is a recorded selector rather than a guess, so when it resolves the result
    is correct by construction even where the plaintext is not text. Returns
    (key_id, plaintext) or (None, None) when there is no named key or the envelope is
    malformed.
    """
    if not named or named not in keys:
        return None, None
    plain = _decrypt(blob, keys[named])
    if plain is None:
        return None, None
    return named, plain


def _open_blob(blob, keys, preferred=None):
    """Try the key the database names first, then the rest. Returns (key_id, plaintext)."""
    order = ([preferred] if preferred in keys else []) + [k for k in keys if k != preferred]
    for key_id in order:
        plain = _decrypt(blob, keys[key_id])
        if _readable(plain):
            return key_id, plain
    return None, None


# ---------------------------------------------------------------- gqlData helpers

def _gql_meta(db_path):
    match = GQL_NAME_RE.match(db_path.replace('\\', '/').rsplit('/', 1)[-1])
    if not match:
        return '', '', ''
    return match.group('guid'), match.group('version'), match.group('schema')


def _gql_records(db_path):
    query = 'SELECT key, record FROM records'
    for record in get_sqlite_db_records(db_path, query):
        try:
            yield record['key'], json.loads(record['record'])
        except (ValueError, TypeError):
            continue


def _title_index(db_path):
    """{video id: (title, __typename)} for records in one gqlData file."""
    index = {}
    for _key, value in _gql_records(db_path):
        if not isinstance(value, dict):
            continue
        title = value.get('title')
        video_id = value.get('videoId')
        if title and video_id is not None:
            index.setdefault(str(video_id), (title, value.get('__typename', '')))
    return index


def _reference_target(value):
    if isinstance(value, dict) and '$reference' in value:
        return str(value['$reference'])
    return ''


# ---------------------------------------------------------------- artifacts

@artifact_processor
def netflix_bookmarks(context):
    data_list = []
    for db_path in _gql_databases(context.get_files_found()):
        profile_guid, app_version, _schema = _gql_meta(db_path)
        titles = _title_index(db_path)
        for key, value in _gql_records(db_path):
            match = BOOKMARK_KEY_RE.search(key)
            if not match or not isinstance(value, dict):
                continue
            video_id = match.group(1)
            title, entity_type = titles.get(video_id, ('', ''))
            data_list.append((
                _iso(value.get('lastModified')),
                video_id,
                title,
                entity_type,
                _blank(value.get('position')),
                _hms(value.get('position')),
                _blank(value.get('interactivePlaybackProgressPercentage')),
                profile_guid,
                app_version,
                context.get_relative_path(db_path),
            ))

    data_headers = (
        ('Last Modified', 'datetime'),
        'Video ID',
        'Title',
        'Entity Type (as stored)',
        'Position (seconds)',
        'Position (hh:mm:ss)',
        'Interactive Progress Percentage (as stored)',
        'Profile Guid (from file name)',
        'App Version (from file name)',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def netflix_profiles(context):
    data_list, rows = [], []
    for db_path in _gql_databases(context.get_files_found()):
        records = dict(_gql_records(db_path))
        current = ''
        current_record = records.get('QUERY_ROOT.currentProfile')
        if isinstance(current_record, dict):
            current = current_record.get('guid', '')

        for key, value in records.items():
            if not PROFILE_KEY_RE.match(key) or not isinstance(value, dict):
                continue
            maturity = records.get(f'{key}.maturityRating')
            level, labels = '', ''
            if isinstance(maturity, dict):
                level = maturity.get('level', '')
                labels = ', '.join(maturity.get('labels') or []) if isinstance(
                    maturity.get('labels'), list) else maturity.get('labels', '')
            avatar = ''
            for avatar_key in (k for k in records if k.startswith(f'{key}.avatar')):
                candidate = records[avatar_key]
                if isinstance(candidate, dict) and candidate.get('url'):
                    avatar = candidate['url']
                    break
            secondary = value.get('secondaryLanguages')
            if isinstance(secondary, list):
                secondary = ', '.join(str(item) for item in secondary)
            guid = value.get('guid', '')
            rows.append((
                _iso(value.get('createdAt')),
                _blank(value.get('name')),
                guid,
                'Yes' if guid and guid == current else '',
                _blank(value.get('isAccountOwner')),
                _blank(value.get('isKids')),
                _blank(value.get('isPinLocked')),
                _blank(value.get('lockPin')),
                _blank(level),
                _blank(labels),
                _blank(value.get('primaryLanguage')),
                _blank(secondary),
                _blank(value.get('isAutoStartEnabled')),
                _blank(value.get('isProfileCreationLocked')),
                _blank(avatar),
                context.get_relative_path(db_path),
            ))

    # The avatar URL is a per cache CDN link and differs between files for the same
    # profile, so it is carried but not part of the identity the dedupe keys on.
    for row, occurrences in _dedupe(rows, 14):
        data_list.append(row[:15] + (occurrences, row[15]))

    data_headers = (
        ('Created At', 'datetime'),
        'Profile Name',
        'Profile Guid',
        'Current Profile',
        'Is Account Owner (as stored)',
        'Is Kids (as stored)',
        'Is PIN Locked (as stored)',
        'Lock PIN (as stored)',
        'Maturity Level (as stored)',
        'Maturity Labels (as stored)',
        'Primary Language',
        'Secondary Languages',
        'Auto Start Enabled (as stored)',
        'Profile Creation Locked (as stored)',
        'Avatar URL',
        'Cache Files Holding This Row',
        'Source Path (first cache file)',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def netflix_account(context):
    data_list, rows = [], []
    files_found = context.get_files_found()

    for db_path in _gql_databases(files_found):
        records = dict(_gql_records(db_path))
        account = records.get('QUERY_ROOT.account')
        if not isinstance(account, dict):
            continue
        country = records.get('QUERY_ROOT.account.countryOfSignUp')
        country_value = ''
        if isinstance(country, dict):
            country_value = country.get('code') or country.get('id') or country.get('name') or ''
        elif country is not None:
            country_value = str(country)
        plan = records.get('QUERY_ROOT.account.currentPlan.plan')
        plan_value = ''
        if isinstance(plan, dict):
            plan_value = plan.get('name') or plan.get('id') or ''
        profile_count = len(account.get('profiles') or []) if isinstance(
            account.get('profiles'), list) else ''
        rows.append((
            _iso(account.get('memberSince')),
            'GraphQL cache',
            '',
            country_value,
            _blank(account.get('membershipStatus')),
            plan_value,
            profile_count,
            _blank(account.get('canCreateUserProfile')),
            context.get_relative_path(db_path),
        ))

    for prefs_path in _files(files_found, lambda p: p.endswith(PREFS_BASENAME)):
        prefs = _plist(prefs_path)
        if not prefs:
            continue
        relative = context.get_relative_path(prefs_path)
        version = prefs.get('kFullVersion') or prefs.get('kVersionKey') or ''
        for label, key in (('Preference file account', 'currentLoginAccount'),
                           ('Preference file ESN', 'kESN'),
                           ('Preference file proxy ESN', 'cdmAuthProxyEsn'),
                           ('Preference file device id', 'cdxClientDeviceId'),
                           ('Preference file app version', 'kFullVersion')):
            value = prefs.get(key)
            if not value:
                continue
            rows.append(('', label, str(value), '', '', '', '', version, relative))

    for row, occurrences in _dedupe(rows, 8):
        data_list.append(row[:8] + (occurrences, row[8]))

    data_headers = (
        ('Member Since', 'datetime'),
        'Source',
        'Value',
        'Country Of Sign Up (as stored)',
        'Membership Status (as stored)',
        'Plan (as stored)',
        'Profile Count',
        'Can Create Profile (as stored)',
        'Cache Files Holding This Row',
        'Source Path (first cache file)',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def netflix_continue_watching(context):
    data_list, rows = [], []
    for db_path in _gql_databases(context.get_files_found()):
        profile_guid, _version, _schema = _gql_meta(db_path)
        titles = _title_index(db_path)
        for _key, value in _gql_records(db_path):
            if not isinstance(value, dict):
                continue
            if value.get('__typename') != 'PinotContinueWatchingEntityTreatment':
                continue
            target = _reference_target(value.get('unifiedEntity'))
            video_match = VIDEO_ID_RE.search(target)
            video_id = video_match.group(1) if video_match else ''
            title, entity_type = titles.get(video_id, ('', ''))
            rows.append((
                _blank(value.get('displayString')),
                video_id,
                title,
                entity_type,
                profile_guid,
                context.get_relative_path(db_path),
            ))

    for row, occurrences in _dedupe(rows, 5):
        data_list.append(row[:5] + (occurrences, row[5]))

    data_headers = (
        'Displayed Title',
        'Video ID',
        'Cached Title',
        'Entity Type (as stored)',
        'Profile Guid (from file name)',
        'Cache Entries Holding This Row',
        'Source Path (first cache file)',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def netflix_titles(context):
    data_list, rows = [], []
    for db_path in _gql_databases(context.get_files_found()):
        seen, artwork = {}, {}
        for key, value in _gql_records(db_path):
            if not isinstance(value, dict):
                continue
            if value.get('__typename') == 'Image' and value.get('url'):
                video_match = VIDEO_ID_RE.search(key)
                if video_match:
                    artwork.setdefault(video_match.group(1), value['url'])
            title = value.get('title')
            video_id = value.get('videoId')
            if title and video_id is not None:
                seen.setdefault(str(video_id), (title, value.get('__typename', '')))
        for video_id, (title, entity_type) in seen.items():
            rows.append((
                video_id,
                title,
                entity_type,
                artwork.get(video_id, ''),
                context.get_relative_path(db_path),
            ))

    # The artwork URL is a per cache CDN link and differs between files for the same
    # title, so it is carried but not part of the identity the dedupe keys on.
    for row, occurrences in _dedupe(rows, 3):
        data_list.append(row[:4] + (occurrences, row[4]))

    data_headers = (
        'Video ID',
        'Title',
        'Entity Type (as stored)',
        'Artwork URL',
        'Cache Files Holding This Row',
        'Source Path (first cache file)',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def netflix_log_events(context):
    data_list = []
    files_found = context.get_files_found()
    for db_path in _databases(files_found, '/brl.sqlite'):
        keys, _source = _load_keys(files_found, db_path)
        named = _named_key(db_path, keys)
        if not keys:
            logfunc(f'Netflix: no derivation keys available for {db_path}; '
                    'log event payloads are reported undecrypted')
        query = ('SELECT id, entry_type, timestamp_ms_added, timestamp_ms_tried, '
                 'work_unit_identifier, entry_data FROM logblobs_table ORDER BY id')
        for record in get_sqlite_db_records(db_path, query):
            key_id, plain = _open_blob(record['entry_data'], keys, named)
            payload = {}
            if plain:
                try:
                    parsed = json.loads(plain.decode('utf-8', 'replace'))
                    if isinstance(parsed, dict):
                        payload = parsed
                except ValueError:
                    payload = {}
            message = payload.get('msg') or payload.get('message') or ''
            if isinstance(message, (dict, list)):
                message = json.dumps(message)[:500]
            data_list.append((
                _unix_seconds(record['timestamp_ms_added']),
                _unix_millis(payload.get('clienttime')) if payload.get('clienttime') else '',
                _unix_seconds(record['timestamp_ms_tried']),
                record['entry_type'],
                payload.get('sessionId', ''),
                payload.get('esn', ''),
                payload.get('devmod', ''),
                payload.get('osver', ''),
                payload.get('osBuildVersion', ''),
                payload.get('clver', ''),
                payload.get('appId', ''),
                payload.get('sev', ''),
                str(message)[:500],
                'Yes' if plain else 'No',
                key_id or '',
                record['id'],
                context.get_relative_path(db_path),
            ))

    data_headers = (
        ('Added Time', 'datetime'),
        ('Client Time', 'datetime'),
        ('Last Try Time', 'datetime'),
        'Event Type (as stored)',
        'Session ID',
        'Device ESN',
        'Device Model (as stored)',
        'OS Version',
        'OS Build Version',
        'Client Version',
        'App ID (as stored)',
        'Severity (as stored)',
        'Message',
        'Decrypted',
        'Key ID Used',
        'Row ID',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


def _value_kind(plain):
    """Describe a decrypted secure store value without printing secret material."""
    if plain is None:
        return 'not recovered', ''
    if plain == b'':
        return 'empty', ''
    if plain[:5] == b'-----':
        return 'PEM certificate', ''
    if plain[:3] == b'MII':
        return 'base64 DER certificate', ''
    if plain[:8] == b'YnBsaXN0':
        return 'base64 NSKeyedArchiver plist', ''
    if plain[:8] == b'bplist00':
        return 'binary plist', ''
    if plain[:1] == b'{':
        try:
            parsed = json.loads(plain.decode('utf-8', 'replace'))
        except ValueError:
            return 'JSON (unparsed)', ''
        if isinstance(parsed, dict):
            top = ', '.join(sorted(parsed))
            identity = ''
            if 'proxyESN' in parsed and isinstance(parsed['proxyESN'], str):
                identity = parsed['proxyESN']
            contexts = parsed.get('cryptoContexts')
            if isinstance(contexts, list) and contexts:
                first = contexts[0]
                if isinstance(first, dict):
                    inner = first.get('cryptoContext')
                    if isinstance(inner, dict) and isinstance(inner.get('identity'), str):
                        identity = inner['identity']
            return f'JSON: {top}', identity
        return 'JSON array', ''
    try:
        text = plain.decode('utf-8')
    except UnicodeDecodeError:
        return 'binary', ''
    if text.startswith('NFAPPL'):
        return 'ESN string', text
    return 'text', ''


@artifact_processor
def netflix_secure_store(context):
    data_list = []
    files_found = context.get_files_found()
    for db_path in _databases(files_found, '/store.sqlite3'):
        keys, _source = _load_keys(files_found, db_path)
        named = _named_key(db_path, keys)
        if not keys:
            logfunc(f'Netflix: no derivation keys available for {db_path}; '
                    'encrypted secure store values are reported undecrypted')
        elif not named:
            logfunc(f'Netflix: the crypto row in {db_path} is not opened by any key in the '
                    'preference file; rows are decrypted by trying each key in turn')
        query = 'SELECT rowid, length(value) AS stored_length, value FROM store ORDER BY rowid'
        for record in get_sqlite_db_records(db_path, query):
            plain = _stored_plain(record['value'])
            if plain is not None:
                storage, key_id = 'Plaintext', ''
            else:
                key_id, plain = _open_named(record['value'], keys, named)
                if key_id is None:
                    key_id, plain = _open_blob(record['value'], keys, named)
                storage = 'Encrypted' if plain is not None else 'Not recovered'
            kind, identity = _value_kind(plain)
            data_list.append((
                kind,
                identity,
                storage,
                len(plain) if plain is not None else '',
                record['stored_length'],
                key_id or '',
                record['rowid'],
                context.get_relative_path(db_path),
            ))

    data_headers = (
        'Value Kind',
        'Identity',
        'Storage',
        'Recovered Length (bytes)',
        'Stored Length (bytes)',
        'Key ID Used',
        'Row ID',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def netflix_network_observations(context):
    data_list = []
    for db_path in _databases(context.get_files_found(), '/store.sqlite3'):
        query = 'SELECT key, value FROM last_observed'
        try:
            records = list(get_sqlite_db_records(db_path, query))
        except (sqlite3.Error, OSError, TypeError) as error:
            logfunc(f'Netflix: could not read last_observed from {db_path}: {error}')
            continue
        for record in records:
            key = record['key']
            key_text = key.decode('utf-8', 'replace') if isinstance(key, bytes) else str(key)
            value = record['value']
            value_text = value.decode('utf-8', 'replace') if isinstance(value, bytes) else str(value)
            parts = key_text.split('-')
            metric = parts[0] if parts else key_text
            interface = parts[1] if len(parts) > 1 else ''
            index = parts[2] if len(parts) > 2 else ''
            data_list.append((
                metric,
                interface,
                index,
                value_text,
                key_text,
                context.get_relative_path(db_path),
            ))

    data_headers = (
        'Metric (as stored)',
        'Interface (as stored)',
        'Index (as stored)',
        'Value (as stored)',
        'Stored Key',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


def _sniff(path):
    """Decide the media type from the leading bytes; these files carry no extension."""
    try:
        with open(path, 'rb') as handle:
            head = handle.read(16)
    except OSError:
        return '', ''
    if head[4:8] == b'ftyp':
        return 'MP4 video', 'mp4'
    if head[:3] == b'\xff\xd8\xff':
        return 'JPEG image', 'jpg'
    if head[:8] == b'\x89PNG\r\n\x1a\n':
        return 'PNG image', 'png'
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'WebP image', 'webp'
    if head[:6] == b'\xef\xbb\xbfWEB' or head[:6] == b'WEBVTT':
        return 'WebVTT subtitles', 'vtt'
    return f'unrecognised (0x{binascii.hexlify(head[:4]).decode()})', ''


def _preview_row(path, titles):
    """One row for a cached preview file, keyed on the video id in its directory name."""
    segments = path.replace('\\', '/').split('/Library/Caches/br/ch/', 1)[1].split('/')
    video_id = segments[0] if segments else ''
    title, entity_type = titles.get(video_id, ('', ''))
    kind, extension = _sniff(path)
    media_ref = ''
    if extension in ('mp4', 'jpg', 'png', 'webp'):
        media_ref = check_in_media(path, name=f'{video_id} {segments[-1]}',
                                   force_extension=extension)
    return (video_id, title, entity_type, segments[-1] if segments else '',
            kind, os.path.getsize(path), media_ref)


@artifact_processor
def netflix_preview_media(context):
    data_list = []
    files_found = context.get_files_found()

    titles = {}
    for db_path in _gql_databases(files_found):
        for video_id, pair in _title_index(db_path).items():
            titles.setdefault(video_id, pair)

    for path in _files(files_found, lambda p: '/Library/Caches/br/ch/' in p):
        if not os.path.isfile(path):
            continue
        data_list.append(_preview_row(path, titles) + (context.get_relative_path(path),))

    data_headers = (
        'Video ID (from directory name)',
        'Title',
        'Entity Type (as stored)',
        'File Name',
        'File Type (from leading bytes)',
        'Size (bytes)',
        ('Media', 'media'),
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


PREFERENCE_KEYS = (
    'currentLoginAccount', 'kESN', 'cdmAuthProxyEsn', 'NfLastESNPrefixKey',
    'cdxClientDeviceId', 'BugsnagUserUserId', 'bugsnagCurrentLaunchID',
    'kFullVersion', 'kVersionKey', 'kAppInternalVersion', 'kServerPathVersion',
    'kSDKVersion', 'canary.lastAppVersion', 'canary.lastAppUpdate',
    'lastAppCrashVersion', 'lastVersionPromptedForReview', 'lastReviewRequestDate',
    'kEndpointURLBase', 'kEndpointURLBaseOverride', 'clEndpointUrl',
    'OCMReachability', 'CLPayloadRetryManager.lastCleanupDate',
    'FirstStartAfterInstallKey', 'kInstallReported',
    'NFSmartDownloadsEnabled', 'backgroundFetchRefreshedLolomoKey',
    'LiveActivityPushToStartToken', 'SKPurchaseIntentUpdatesLastChecked',
    'com.google.cast.analytics_logging_pseudonymous_sender_id',
    'com.google.cast.analytics_logging_app_bundle_version',
    'bugsnagRolloutValue', 'clUsesUnixEpoch',
)


@artifact_processor
def netflix_preferences(context):
    data_list = []
    for prefs_path in _files(context.get_files_found(),
                             lambda p: p.endswith(PREFS_BASENAME)):
        prefs = _plist(prefs_path)
        relative = context.get_relative_path(prefs_path)
        for name in PREFERENCE_KEYS:
            if name not in prefs:
                continue
            value = prefs[name]
            if isinstance(value, (bytes, bytearray)):
                rendered = f'<{len(value)} bytes>'
            elif isinstance(value, (dict, list)):
                rendered = json.dumps(value, default=str)[:500]
            elif isinstance(value, datetime.datetime):
                rendered = value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                rendered = str(value)
            data_list.append((name, rendered, '', relative))
        for name in sorted(prefs):
            match = PROFILE_PREF_RE.match(name)
            if match:
                data_list.append((name, '', match.group(1), relative))

    data_headers = (
        'Preference Key (as stored)',
        'Value',
        'Profile Guid In Key',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'
