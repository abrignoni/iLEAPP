""" Telegram accounts, cached peers/contacts, and app settings """
__artifacts_v2__ = {
    "telegramAccounts": {
        "name": "Telegram Accounts",
        "description": (
            "Parses Telegram account records from the accounts-metadata atomic-state file "
            "and each account's Postbox database (table t0). Reports the account IDs "
            "registered on the device, which one was active, the signed-in user ID, the "
            "production/test environment flag, and the key names of the "
            "accessChallengeData object, reported as stored."
        ),
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Key IDs and record layouts are those of the open-source Telegram-iOS "
                 "client (Postbox metadata table t0 key 2; accounts-metadata JSON). The "
                 "metadata table is tableSpec(0) "
                 "(https://github.com/TelegramMessenger/Telegram-iOS/blob/"
                 "6ad963e5b62d354da79040f388ae2b9132fb17b8/submodules/Postbox/Sources/"
                 "Postbox.swift#L1881). No file or line of the client source is cited "
                 "here for the key 2 record or the accounts-metadata JSON layout; their "
                 "field names are reported as stored. "
                 "The update state timestamp is the `state.date` field of the account "
                 "state record in t0.",
        "paths": (
            '*/telegram-data/accounts-metadata/atomic-state',
            '*/telegram-data/account-*/postbox/db/db_sqlite*'
        ),
        "output_types": "standard",
        "artifact_icon": "brand-telegram",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | Telegram Messenger 11.0 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | Telegram Messenger 12.6.3 | 1 row",
        },
    },
    "telegramContacts": {
        "name": "Telegram Contacts & Peers",
        "description": (
            "Parses cached peer records (users, bots, groups, channels, secret chats) from "
            "table t2 of each Telegram account's Postbox database, joined with the contact "
            "list (table t16), the Spotlight contact cache, and cached avatar images. "
            "A peer record can be present without any exchanged messages and without being a "
            "saved contact; "
            "the Messages In Chat column is 0 and In Contact List is blank for such peers."
        ),
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Peer record field names (fn, ln, un, p, ph) follow the open-source "
                 "Telegram-iOS Postbox serialization. Contact-list membership is read "
                 "from the Postbox ContactTable (table t16; "
                 "https://github.com/TelegramMessenger/Telegram-iOS/blob/"
                 "6ad963e5b62d354da79040f388ae2b9132fb17b8/submodules/Postbox/Sources/"
                 "Postbox.swift#L1926), keyed by peer id. If a table read fails, membership "
                 "may be incomplete: IDs already read can still show Yes, and other rows "
                 "are blank. Up to ten failed reads are logged per invocation, followed by "
                 "a summary. Original parser and research credit: @AlexisBrignoni. "
                 "Avatar images are matched "
                 "from telegram-peer-photo-size files in postbox/media and from the "
                 "accounts-metadata Spotlight cache.",
        "paths": (
            '*/telegram-data/account-*/postbox/db/db_sqlite*',
            '*/telegram-data/accounts-metadata/spotlight/p*/data.json',
            '*/telegram-data/accounts-metadata/spotlight/p*/avatar.png',
            '*/telegram-data/account-*/postbox/media/telegram-peer-photo-size-*'
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | Telegram Messenger 11.0 | 296 rows",
            "hc_ios18_7": "iOS 18.7.8 | Telegram Messenger 12.6.3 | 253 rows",
        },
    },
    "telegramChats": {
        "name": "Telegram Chats",
        "description": (
            "Parses the Telegram chat list from the Postbox chat list table, reporting each "
            "chat with the time of its most recent message, whether it is pinned, whether it "
            "sits in the main list or the archive, the number of messages stored for it and "
            "the unread count."
        ),
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-04",
        "last_update_date": "2026-08-04",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The chat list is table t9, the Postbox ChatListTable (tableSpec(9) in "
                 "Postbox.swift). Its key carries the whole entry, big-endian: a group id, "
                 "a pinning value, the timestamp, namespace and id of the top message, the "
                 "peer id and an entry type "
                 "(https://github.com/TelegramMessenger/Telegram-iOS/blob/"
                 "6ad963e5b62d354da79040f388ae2b9132fb17b8/submodules/Postbox/Sources/"
                 "ChatListTable.swift#L145-L152). The entry type is not read here, so a "
                 "hole entry (type 2) is listed like a chat. Group id 1 is the archive; "
                 "every other group id is shown as Main. A "
                 "pinning value of 0 means the chat is not pinned. Unread counts come from "
                 "table t14, the MessageHistoryReadStateTable, whose id-based records carry "
                 "the count and a marked-unread flag. Names are resolved from the peer table "
                 "(t2) and the stored message count from the message table (t7).",
        "paths": (
            '*/telegram-data/account-*/postbox/db/db_sqlite*',
        ),
        "output_types": "standard",
        "artifact_icon": "messages",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | Telegram Messenger 11.0 | 13 rows",
            "hc_ios18_7": "iOS 18.7.8 | Telegram Messenger 12.6.3 | 5 rows",
        },
    },
    "telegramDeviceContacts": {
        "name": "Telegram Device Contacts",
        "description": (
            "Parses the device address-book entries Telegram recorded for contact import, "
            "from table t54 of each account's Postbox database. Each entry is keyed by a "
            "phone number from the device address book and carries the name as stored on the "
            "device, the import state (imported or retry later), the importers count the "
            "server returned for the number (Telegram API popularContact: 'How many people "
            "imported this contact'), and the Telegram user the number resolved to when it "
            "resolved to one. A record can be stored without a Telegram user id (the client "
            "declares peerId as optional), so a row is a device address-book number the "
            "client processed for import, not a Telegram contact."
        ),
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-08-05",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Table t54 is the Postbox DeviceContactImportInfoTable (tableSpec(54) in "
                 "Postbox.swift). The key is a one-byte prefix of 0 followed by the "
                 "normalised phone number, per TelegramDeviceContactImportIdentifier. The "
                 "value is a TelegramDeviceContactImportedData record: '_t' 0 is imported and "
                 "1 is a deferred retry, 'd' holds the device contact data with 'f' first "
                 "name, 'l' last name and 'dis' the device's own contact identifiers, 'c' is "
                 "the imported-by count the server returned, and 'pid' is the resolved "
                 "Telegram peer id when present. The imported-by count is the importers "
                 "value the server returned for the number (ContactSyncManager.swift lines "
                 "360 to 378 at Telegram-iOS 6ad963e5); the client writes 0 when the server "
                 "returned none, or when the number already belonged to a known user with "
                 "the same first and last name (line 297).",
        "paths": (
            '*/telegram-data/account-*/postbox/db/db_sqlite*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "address-book",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | Telegram Messenger 11.0 | 1016 rows",
        },
    },
    "telegramPeerPresence": {
        "name": "Telegram Peer Presence",
        "description": (
            "Parses cached presence records from table t20 of each Telegram account's "
            "Postbox database. Reports the current decoder's v and h values beside the "
            "status interpretation and h truthiness, with Last Activity and Status Time."
        ),
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Table t20 is the Postbox PeerPresenceTable (tableSpec(20) in Postbox.swift). "
                 "The record is a TelegramUserPresence: 'v' selects the status, where 0 is "
                 "none, 1 is present with the time in 't', which the client fills with either "
                 "the time an online status expires or the time the peer was last online (the "
                 "Status Interpretation shows Stored Status 1 without choosing either meaning), 2 is "
                 "recently, 3 is last week and 4 is last month, and 'h' is the isHidden flag "
                 "those bucketed statuses carry, which the client sets from the server's "
                 "by_me bit. Telegram's API documentation says that bit means the peer's "
                 "exact status is available but is not shown to this account unless it has "
                 "Premium or lets that peer see its own exact last-seen time "
                 "(core.telegram.org/constructor/userStatusRecently). Decoded v and Decoded h "
                 "retain the current decoder results, not the original Postbox bytes. "
                 "Missing and explicit null fields both show blank. h Truthiness keeps "
                 "the existing Yes for truthy h and blank for falsy h. "
                 "'la' is the last activity value the client stored. The bucketed statuses "
                 "are reported as stored and are not an exact time; what causes the server to "
                 "return a bucketed status rather than a time is not sourced here. The other "
                 "status labels remain existing interpretations; this change does not "
                 "verify them for all app versions. Original parser and research credit: "
                 "@AlexisBrignoni.",
        "paths": (
            '*/telegram-data/account-*/postbox/db/db_sqlite*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user-circle",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | Telegram Messenger 11.0 | 266 rows",
        },
    },
    "telegramMessageTags": {
        "name": "Telegram Message Tags",
        "description": (
            "Parses the per-message category index Telegram maintains in table t12 of each "
            "account's Postbox database. Each row ties a stored message to a category such "
            "as photo, video, file, music, voice, link or pinned, so the messages of one "
            "kind within a chat can be listed from the index alone."
        ),
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-08-09",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Table t12 is the Postbox MessageHistoryTagsTable (tableSpec(12) in "
                 "Postbox.swift). The whole entry is in the key, big-endian: peer id, tag "
                 "value, namespace, timestamp and message id, per the key function in "
                 "MessageHistoryTagsTable.swift. The tag values are the MessageTags bit "
                 "flags defined in the client, from photoOrVideo at bit 0 through "
                 "unseenPollVote at bit 15 "
                 "(https://github.com/TelegramMessenger/Telegram-iOS/blob/"
                 "6ad963e5b62d354da79040f388ae2b9132fb17b8/submodules/TelegramCore/"
                 "Sources/SyncCore/SyncCore_Namespaces.swift#L175-L190, a commit that "
                 "was not matched to the app versions tested); a bit with no name in the "
                 "client source is "
                 "reported as its raw value. An entry records how the client indexed the "
                 "message, so it reflects the client's categorisation rather than an "
                 "independent examination of the message content.",
        "paths": (
            '*/telegram-data/account-*/postbox/db/db_sqlite*',
        ),
        "output_types": "standard",
        "artifact_icon": "tags",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | Telegram Messenger 11.0 | 2328 rows",
        },
    },
    "telegramCachedPeerData": {
        "name": "Telegram Cached Peer Details",
        "description": (
            "Parses the cached peer detail records Telegram stores for users and channels "
            "in table t18 of each account's Postbox database. Reports the profile bio or "
            "channel description, a user's stored birthday, whether a user is blocked, "
            "the number of groups in common, scheduled-message and auto-delete state, and "
            "who invited the account to a channel. A row does not show whether any "
            "message was exchanged with the peer; this artifact does not read the message "
            "table."
        ),
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Table t18 is the Postbox CachedPeerDataTable (tableSpec(18) in "
                 "Postbox.swift), keyed by peer id. Field names are taken from the "
                 "open-source Telegram-iOS client: CachedUserData encodes 'a' as about, "
                 "'b' as isBlocked, 'cg' as commonGroupCount and 'bday' as a JSON birthday; "
                 "CachedChannelData encodes 'a' as about and 'b' as botInfos, so the "
                 "Blocked column is populated only for user records. The keys were read at "
                 "Telegram-iOS commit 6ad963e5 "
                 "(https://github.com/TelegramMessenger/Telegram-iOS/blob/"
                 "6ad963e5b62d354da79040f388ae2b9132fb17b8/submodules/TelegramCore/Sources/"
                 "SyncCore/SyncCore_CachedUserData.swift#L1510-L1545 and "
                 "https://github.com/TelegramMessenger/Telegram-iOS/blob/"
                 "6ad963e5b62d354da79040f388ae2b9132fb17b8/submodules/TelegramCore/Sources/"
                 "SyncCore/SyncCore_CachedChannelData.swift#L755-L765), which was not "
                 "matched to the app versions tested. The auto-delete "
                 "field wraps its value in a known/unknown record, so 'None set' means "
                 "Telegram cached the timer state and found none, while a blank means it "
                 "was never cached. Peer names are resolved from the peer table (t2).",
        "paths": (
            '*/telegram-data/account-*/postbox/db/db_sqlite*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "address-book",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | Telegram Messenger 11.0 | 33 rows",
            "hc_ios18_7": "iOS 18.7.8 | Telegram Messenger 12.6.3 | 90 rows",
        },
    },
    "telegramSettings": {
        "name": "Telegram Settings",
        "description": (
            "Parses named Telegram settings from the shared accounts-metadata table t2 "
            "and account Postbox table t35. Headline settings receive a placeholder when "
            "no supported stored record is reported for the key. That placeholder does "
            "not establish whether the app uses a default value."
        ),
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Setting key IDs are taken from the open-source Telegram-iOS client "
                 "(SyncCore_Namespaces.swift PreferencesKeyValues/SharedDataKeyValues and "
                 "TelegramUIPreferences PostboxKeys.swift; application-specific keys are "
                 "stored as ID + 1000). Values are reported as stored, using Telegram's "
                 "internal field names, and cut at 1,000 characters. Keys with no name "
                 "in this module are not reported. App passcode, media auto-download and "
                 "save-to-Photos settings get a placeholder when no supported named record "
                 "was reported for the key. This parser requires a four-byte key and a byte "
                 "value with a mapped key ID; an existing record with an unsupported shape "
                 "can also lead to a placeholder. Original parser and research credit: "
                 "@AlexisBrignoni.",
        "paths": (
            '*/telegram-data/accounts-metadata/db/db_sqlite*',
            '*/telegram-data/account-*/postbox/db/db_sqlite*'
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | Telegram Messenger 11.0 | 16 rows",
            "hc_ios18_7": "iOS 18.7.8 | Telegram Messenger 12.6.3 | 18 rows",
        },
    },
}

import datetime
import io
import json
import os
import re
import sqlite3
import struct

import mmh3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media, logfunc


# --- Generic Postbox value decoding -----------------------------------------
# Same on-disk format handled in telegramMesssages.py, decoded generically into
# dicts instead of registered classes so unknown objects still render.

def _murmur(name):
    return mmh3.hash(name, seed=4157243346)

# Type-hash labels for peer records stored in Postbox table t2.
_PEER_TYPE_NAMES = {
    _murmur('TelegramUser'): 'User',
    _murmur('TelegramGroup'): 'Group',
    _murmur('TelegramChannel'): 'Channel',
    _murmur('TelegramSecretChat'): 'Secret Chat',
}


class _ByteReader:
    def __init__(self, data):
        self.buf = io.BytesIO(data)
        self.size = len(data)

    def read_fmt(self, fmt):
        raw = self.buf.read(struct.calcsize(fmt))
        if len(raw) < struct.calcsize(fmt):
            raise EOFError('short read')
        return struct.unpack(fmt, raw)[0]

    def read_bytes(self):
        length = self.read_fmt('<i')
        return self.buf.read(length)

    def read_str(self):
        return self.read_bytes().decode('utf-8', 'replace')

    def read_short_str(self):
        length = self.read_fmt('<B')
        return self.buf.read(length).decode('utf-8', 'replace')


def _decode_value(reader):
    value_type = reader.read_fmt('<B')
    if value_type == 0:
        return reader.read_fmt('<i')
    if value_type == 1:
        return reader.read_fmt('<q')
    if value_type == 2:
        return reader.read_fmt('<B') != 0
    if value_type == 3:
        return reader.read_fmt('<d')
    if value_type == 4:
        return reader.read_str()
    if value_type == 5:
        return _decode_object(reader)
    if value_type == 6:
        return [reader.read_fmt('<i') for _ in range(reader.read_fmt('<i'))]
    if value_type == 7:
        return [reader.read_fmt('<q') for _ in range(reader.read_fmt('<i'))]
    if value_type == 8:
        return [_decode_object(reader) for _ in range(reader.read_fmt('<i'))]
    if value_type == 9:
        return [(_decode_object(reader), _decode_object(reader))
                for _ in range(reader.read_fmt('<i'))]
    if value_type == 10:
        return _render_bytes(reader.read_bytes())
    if value_type == 11:
        return None
    if value_type == 12:
        return [reader.read_str() for _ in range(reader.read_fmt('<i'))]
    if value_type == 13:
        return [_render_bytes(reader.read_bytes()) for _ in range(reader.read_fmt('<i'))]
    raise ValueError(f'unknown Postbox value type {value_type}')


def _render_bytes(data):
    # MediaAutoSaveSettings and similar objects store nested JSON as raw bytes.
    if data[:1] in (b'{', b'['):
        try:
            return json.loads(data.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass
    return f'<{len(data)} bytes>'


def _decode_object(reader):
    type_hash = reader.read_fmt('<i')
    length = reader.read_fmt('<i')
    payload = reader.buf.read(length)
    result = {}
    sub = _ByteReader(payload)
    try:
        while sub.buf.tell() < sub.size:
            key = sub.read_short_str()
            result[key] = _decode_value(sub)
    except (EOFError, ValueError):
        pass
    result['@type'] = type_hash
    return result


def _decode_root(data):
    reader = _ByteReader(data)
    result = {}
    try:
        while reader.buf.tell() < reader.size:
            key = reader.read_short_str()
            result[key] = _decode_value(reader)
    except (EOFError, ValueError):
        pass
    root = result.get('_')
    return root if isinstance(root, dict) else result


def _account_id_from_path(path):
    match = re.search(r'account-(\d+)', str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _postbox_dbs(files_found):
    '''Yields (account_id, db_path) for each account Postbox database.'''
    for file_found in files_found:
        path = str(file_found)
        normalized = path.replace('\\', '/')
        if normalized.endswith('/postbox/db/db_sqlite'):
            yield _account_id_from_path(normalized), path


# --- Telegram Accounts -------------------------------------------------------

@artifact_processor
def telegramAccounts(context):
    """ see artifact description """
    data_headers = [
        ('Update State Timestamp', 'datetime'),
        'Account ID',
        'Active Account',
        'User ID',
        'Environment',
        'Master Datacenter',
        'Sort Order',
        'App Passcode Lock',
    ]
    data_list = []
    source_paths = []

    # Per-account details from each Postbox metadata table (t0, key 2).
    t0_info = {}
    for account_id, db_path in _postbox_dbs(context.get_files_found()):
        db = open_sqlite_db_readonly(db_path)
        if db is None:
            continue
        try:
            cursor = db.cursor()
            cursor.execute('SELECT value FROM t0 WHERE key = 2')
            row = cursor.fetchone()
            if row:
                decoded = _decode_root(row[0])
                state = decoded.get('state') or {}
                t0_info[account_id] = {
                    'user_id': decoded.get('peerId', ''),
                    'environment': 'Test' if decoded.get('isTestingEnvironment') else 'Production',
                    'datacenter': decoded.get('masterDatacenterId', ''),
                    'state_date': state.get('date'),
                }
                source_paths.append(db_path)
        except sqlite3.Error as err:
            logfunc(f'Telegram accounts: error reading {db_path}: {err}')
        finally:
            db.close()

    # Account roster and app lock state from atomic-state.
    for file_found in context.get_files_found():
        path = str(file_found)
        if not path.replace('\\', '/').endswith('/accounts-metadata/atomic-state'):
            continue
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                state = json.load(handle)
        except (OSError, json.JSONDecodeError) as err:
            logfunc(f'Telegram accounts: error reading {path}: {err}')
            continue
        source_paths.append(path)

        challenge = state.get('accessChallengeData') or {}
        if challenge:
            passcode = ', '.join(sorted(challenge.keys()))
        else:
            passcode = 'None'
        current_id = str(state.get('currentRecordId', ''))

        for record in state.get('records', []):
            record_id = str(record.get('id', ''))
            sort_order = ''
            environment = ''
            for attribute in record.get('attributes', []):
                if 'sortOrder' in attribute:
                    sort_order = attribute['sortOrder'].get('order', '')
                if 'environment' in attribute:
                    environment = ('Test' if attribute['environment'].get('environment')
                                   else 'Production')
            info = t0_info.get(record_id, {})
            state_date = info.get('state_date')
            timestamp = (datetime.datetime.fromtimestamp(state_date, tz=datetime.timezone.utc)
                         if state_date else '')
            data_list.append((
                timestamp,
                record_id,
                'Yes' if record_id == current_id else '',
                info.get('user_id', ''),
                info.get('environment', environment),
                info.get('datacenter', ''),
                sort_order,
                passcode,
            ))

    # Accounts that have a Postbox database but no atomic-state record.
    listed = {row[1] for row in data_list}
    for account_id, info in t0_info.items():
        if account_id in listed:
            continue
        state_date = info.get('state_date')
        timestamp = (datetime.datetime.fromtimestamp(state_date, tz=datetime.timezone.utc)
                     if state_date else '')
        data_list.append((
            timestamp, account_id, '', info.get('user_id', ''),
            info.get('environment', ''), info.get('datacenter', ''), '', '',
        ))

    source_path = '\n'.join(dict.fromkeys(source_paths)) if source_paths else 'Unknown'
    return data_headers, data_list, source_path


# --- Telegram Contacts & Peers ----------------------------------------------

def _contact_read_diagnostic(context, db_path, err):
    """Bound the optional-table diagnostic without exposing SQLite error text."""
    relative = context.get_relative_path(db_path)
    if relative.startswith(('/', '\\')) or re.match(r'^[A-Za-z]:[/\\]', relative):
        relative = 'relative-path-unavailable'
    escaped = json.dumps(relative, ensure_ascii=True)
    for character, replacement in (('<', '\\u003c'), ('>', '\\u003e'), ('&', '\\u0026')):
        escaped = escaped.replace(character, replacement)
    truncated = len(escaped) > 512
    error_class = type(err).__name__
    if error_class not in (
            'Error', 'DatabaseError', 'DataError', 'IntegrityError', 'InterfaceError',
            'InternalError', 'NotSupportedError', 'OperationalError', 'ProgrammingError'):
        error_class = 'Error'
    return (f'Telegram contacts: t16 read failed at {escaped[:512]} '
            f'(path length={len(relative)}, truncated={truncated}; {error_class}); '
            'membership may be incomplete.')


@artifact_processor
def telegramContacts(context):
    """ see artifact description """
    data_headers = [
        'Account ID',
        'Peer ID',
        'Type',
        'First Name',
        'Last Name',
        'Username',
        'Phone',
        'Title',
        'Messages In Chat',
        'In Contact List',
        'In Spotlight Cache',
        ('Avatar', 'media'),
    ]
    data_list = []
    source_paths = []
    files_found = [str(f) for f in context.get_files_found()]

    # Spotlight contact cache: peer id -> names, avatar file.
    spotlight = {}
    for path in files_found:
        normalized = path.replace('\\', '/')
        match = re.search(r'/spotlight/p:(\d+)/data\.json$', normalized)
        if not match:
            continue
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                entry = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        avatar = os.path.join(os.path.dirname(path), 'avatar.png')
        spotlight[int(match.group(1))] = {
            'first': entry.get('firstName', ''),
            'last': entry.get('lastName', ''),
            'avatar': avatar if avatar in files_found or os.path.isfile(avatar) else None,
        }

    # Cached avatar files in postbox/media, keyed by the photo id component.
    avatar_files = {}
    for path in files_found:
        name = os.path.basename(path.replace('\\', '/'))
        if not name.startswith('telegram-peer-photo-size-'):
            continue
        if name.endswith('.meta') or '_partial' in name:
            continue
        parts = name.split('-')
        # telegram-peer-photo-size-{datacenter}-{photoId}-...
        if len(parts) >= 6:
            avatar_files.setdefault((_account_id_from_path(path), parts[5]), path)

    contact_read_failures = 0
    contact_read_examples = 0
    for account_id, db_path in _postbox_dbs(files_found):
        db = open_sqlite_db_readonly(db_path)
        if db is None:
            continue
        try:
            cursor = db.cursor()

            # Message count per chat peer, from the t7 key prefix (big-endian peer id).
            chat_counts = {}
            cursor.execute('SELECT key FROM t7')
            for (key,) in cursor:
                if isinstance(key, bytes) and len(key) >= 8:
                    peer = struct.unpack('>q', key[:8])[0]
                    chat_counts[peer] = chat_counts.get(peer, 0) + 1

            # Contact-list membership: the Postbox ContactTable (table t16) is
            # keyed by the peer id of each saved contact, distinguishing real
            # contacts from peers merely cached by search.
            contact_ids = set()
            try:
                cursor.execute('SELECT key FROM t16')
                for (key,) in cursor:
                    if isinstance(key, bytes) and len(key) == 8:
                        contact_ids.add(struct.unpack('>q', key)[0])
                    elif isinstance(key, int):
                        contact_ids.add(key)
            except sqlite3.Error as err:
                contact_read_failures += 1
                if contact_read_examples < 10:
                    logfunc(_contact_read_diagnostic(context, db_path, err))
                    contact_read_examples += 1

            cursor.execute('SELECT key, value FROM t2')
            for key, value in cursor.fetchall():
                if not isinstance(value, bytes):
                    continue
                peer = _decode_root(value)
                if isinstance(key, bytes) and len(key) == 8:
                    peer_id = struct.unpack('>q', key)[0]
                elif isinstance(key, int):
                    peer_id = key
                else:
                    peer_id = peer.get('i', '')
                peer_type = _PEER_TYPE_NAMES.get(peer.get('@type'), 'Unknown')

                media_ref = ''
                photo_reps = peer.get('ph') or []
                for rep in photo_reps:
                    resource = rep.get('r') if isinstance(rep, dict) else None
                    photo_id = resource.get('p') if isinstance(resource, dict) else None
                    if photo_id is None:
                        continue
                    avatar_path = avatar_files.get((account_id, str(photo_id)))
                    if avatar_path:
                        media_ref = check_in_media(file_path=avatar_path)
                        break
                cached = spotlight.get(peer_id)
                if not media_ref and cached and cached.get('avatar'):
                    media_ref = check_in_media(file_path=cached['avatar'])

                data_list.append((
                    account_id,
                    peer_id,
                    peer_type,
                    peer.get('fn', ''),
                    peer.get('ln', ''),
                    peer.get('un', ''),
                    peer.get('p', ''),
                    peer.get('t', ''),
                    chat_counts.get(peer_id, 0),
                    'Yes' if peer_id in contact_ids else '',
                    'Yes' if cached else '',
                    media_ref,
                ))
            source_paths.append(db_path)
        except sqlite3.Error as err:
            logfunc(f'Telegram contacts: error reading {db_path}: {err}')
        finally:
            db.close()

    if contact_read_failures:
        logfunc(f'Telegram contacts: t16 read failures={contact_read_failures}, '
                f'shown={contact_read_examples}, '
                f'suppressed={contact_read_failures - contact_read_examples}; '
                'membership may be incomplete.')
    source_path = '\n'.join(dict.fromkeys(source_paths)) if source_paths else 'Unknown'
    return data_headers, data_list, source_path


# --- Telegram Chats ----------------------------------------------------------

def _read_chat_list_key(key):
    """Unpack a ChatListTable key.

    Layout from ChatListTable.swift extractKey: group id, pinning value, top
    message timestamp, namespace, message id, peer id, entry type. Postbox keys
    are big-endian so that they sort.
    """
    if not isinstance(key, bytes) or len(key) < 23:
        return None
    group_id = struct.unpack('>i', key[0:4])[0]
    pinning = struct.unpack('>H', key[4:6])[0]
    timestamp = struct.unpack('>i', key[6:10])[0]
    peer_id = struct.unpack('>q', key[15:23])[0]
    return group_id, pinning, timestamp, peer_id


def _read_read_states(db):
    """Unread counts per peer from the MessageHistoryReadStateTable (t14).

    Value layout from MessageHistoryReadStateTable.swift: a namespace count,
    then per namespace an id and a kind byte; an id-based record carries the
    max read ids, the unread count and a flags word whose first bit is the
    manually marked-unread state. Values are written natively, little-endian.
    """
    states = {}
    try:
        cursor = db.cursor()
        cursor.execute('SELECT key, value FROM t14')
        rows = cursor.fetchall()
    except sqlite3.Error:
        return states
    for key, value in rows:
        peer_id = _peer_key_to_id(key)
        if not isinstance(value, bytes) or len(value) < 4:
            continue
        try:
            offset = 0
            namespaces = struct.unpack_from('<i', value, offset)[0]
            offset += 4
            unread, marked = 0, False
            for _ in range(max(0, min(namespaces, 16))):
                offset += 4                                  # namespace id
                kind = value[offset]
                offset += 1
                if kind == 0:
                    offset += 12                             # three max ids
                    unread = max(unread, struct.unpack_from('<i', value, offset)[0])
                    offset += 4
                    flags = struct.unpack_from('<i', value, offset)[0]
                    offset += 4
                    marked = marked or bool(flags & 1)
                else:
                    break                                    # index-based record
            states[peer_id] = (unread, marked)
        except (struct.error, IndexError):
            continue
    return states


@artifact_processor
def telegramChats(context):
    """ see artifact description """
    data_headers = [
        ('Last Message', 'datetime'),
        'Account ID',
        'Chat ID',
        'Chat',
        'Type',
        'Folder',
        'Pinned',
        'Messages Stored',
        'Unread Count',
        'Marked Unread',
    ]
    data_list = []
    source_paths = []

    for account_id, db_path in _postbox_dbs(context.get_files_found()):
        db = open_sqlite_db_readonly(db_path)
        if db is None:
            continue
        try:
            cursor = db.cursor()

            names, types = {}, {}
            cursor.execute('SELECT key, value FROM t2')
            for key, value in cursor.fetchall():
                if not isinstance(value, bytes):
                    continue
                peer = _decode_root(value)
                peer_id = _peer_key_to_id(key, peer.get('i', ''))
                names[peer_id] = _peer_display_name(peer)
                types[peer_id] = _PEER_TYPE_NAMES.get(peer.get('@type'), 'Unknown')

            counts = {}
            cursor.execute('SELECT key FROM t7')
            for (key,) in cursor:
                if isinstance(key, bytes) and len(key) >= 8:
                    peer = struct.unpack('>q', key[:8])[0]
                    counts[peer] = counts.get(peer, 0) + 1

            read_states = _read_read_states(db)

            cursor.execute('SELECT key FROM t9')
            for (key,) in cursor.fetchall():
                entry = _read_chat_list_key(key)
                if entry is None:
                    continue
                group_id, pinning, timestamp, peer_id = entry
                unread, marked = read_states.get(peer_id, (0, False))
                data_list.append((
                    datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
                    if timestamp else '',
                    account_id,
                    peer_id,
                    names.get(peer_id, ''),
                    types.get(peer_id, ''),
                    'Archived' if group_id == 1 else 'Main',
                    'Yes' if pinning else '',
                    counts.get(peer_id, 0),
                    unread,
                    'Yes' if marked else '',
                ))
            source_paths.append(db_path)
        except sqlite3.Error as err:
            logfunc(f'Telegram chats: error reading {db_path}: {err}')
        finally:
            db.close()

    source_path = '\n'.join(dict.fromkeys(source_paths)) if source_paths else 'Unknown'
    return data_headers, data_list, source_path


# --- Telegram Device Contacts ------------------------------------------------

@artifact_processor
def telegramDeviceContacts(context):
    """ see artifact description """
    data_headers = [
        'Account ID',
        'Phone Number',
        'First Name',
        'Last Name',
        'Import State',
        'Imported By Count',
        'Telegram User ID',
        'Device Contact Identifiers',
    ]
    data_list = []
    source_paths = []

    for account_id, db_path in _postbox_dbs(context.get_files_found()):
        db = open_sqlite_db_readonly(db_path)
        if db is None:
            continue
        try:
            cursor = db.cursor()
            cursor.execute('SELECT key, value FROM t54')
            for key, value in cursor.fetchall():
                if not isinstance(key, bytes) or len(key) < 2:
                    continue
                # One-byte prefix of 0, then the normalised number.
                if key[0] != 0:
                    continue
                phone = key[1:].decode('utf-8', 'replace')
                record = _decode_root(value) if isinstance(value, bytes) else {}
                contact = record.get('d') if isinstance(record.get('d'), dict) else {}
                state = record.get('_t')
                if state == 0:
                    state_text = 'Imported'
                elif state == 1:
                    state_text = 'Retry later'
                else:
                    state_text = ''
                identifiers = contact.get('dis')
                if isinstance(identifiers, list):
                    identifiers = ', '.join(str(item) for item in identifiers)
                else:
                    identifiers = ''
                count = record.get('c')
                data_list.append((
                    account_id,
                    phone,
                    contact.get('f', ''),
                    contact.get('l', ''),
                    state_text,
                    count if isinstance(count, int) else '',
                    record.get('pid', ''),
                    identifiers,
                ))
            source_paths.append(db_path)
        except sqlite3.Error as err:
            logfunc(f'Telegram device contacts: error reading {db_path}: {err}')
        finally:
            db.close()

    source_path = '\n'.join(dict.fromkeys(source_paths)) if source_paths else 'Unknown'
    return data_headers, data_list, source_path


# --- Telegram Peer Presence --------------------------------------------------

# UserPresenceStatus, per SyncCore_TelegramUserPresence.swift.
_PRESENCE_STATUS = {
    0: 'None', 1: 'Stored Status 1', 2: 'Recently',
    3: 'Within last week', 4: 'Within last month',
}

# MessageTags bit flags, per SyncCore_Namespaces.swift.
_MESSAGE_TAGS = {
    0: 'Photo or video', 1: 'File', 2: 'Music', 3: 'Web page',
    4: 'Voice or instant video', 5: 'Unseen personal message', 6: 'Live location',
    7: 'GIF', 8: 'Photo', 9: 'Video', 10: 'Pinned', 11: 'Unseen reaction',
    12: 'Voice', 13: 'Round video', 14: 'Poll', 15: 'Unseen poll vote',
}


def _peer_names(cursor):
    names = {}
    try:
        cursor.execute('SELECT key, value FROM t2')
        for key, value in cursor.fetchall():
            if not isinstance(value, bytes):
                continue
            peer = _decode_root(value)
            names[_peer_key_to_id(key, peer.get('i', ''))] = _peer_display_name(peer)
    except sqlite3.Error:
        pass
    return names


@artifact_processor
def telegramPeerPresence(context):
    """ see artifact description """
    data_headers = [
        ('Last Activity', 'datetime'),
        ('Status Time', 'datetime'),
        'Account ID',
        'Peer ID',
        'Peer',
        'Decoded v',
        'Status Interpretation',
        'Decoded h',
        'h Truthiness',
    ]
    data_list = []
    source_paths = []

    for account_id, db_path in _postbox_dbs(context.get_files_found()):
        db = open_sqlite_db_readonly(db_path)
        if db is None:
            continue
        try:
            cursor = db.cursor()
            names = _peer_names(cursor)
            cursor.execute('SELECT key, value FROM t20')
            for key, value in cursor.fetchall():
                if not isinstance(value, bytes):
                    continue
                record = _decode_root(value)
                peer_id = _peer_key_to_id(key)
                variant = record.get('v')
                status_time = record.get('t')
                activity = record.get('la')
                data_list.append((
                    datetime.datetime.fromtimestamp(activity, tz=datetime.timezone.utc)
                    if isinstance(activity, int) and activity > 0 else '',
                    datetime.datetime.fromtimestamp(status_time, tz=datetime.timezone.utc)
                    if isinstance(status_time, int) and 0 < status_time < 2147483647 else '',
                    account_id,
                    peer_id,
                    names.get(peer_id, ''),
                    variant,
                    _PRESENCE_STATUS.get(variant, f'Unrecognised ({variant})'),
                    record.get('h'),
                    'Yes' if record.get('h') else '',
                ))
            source_paths.append(db_path)
        except sqlite3.Error as err:
            logfunc(f'Telegram peer presence: error reading {db_path}: {err}')
        finally:
            db.close()

    source_path = '\n'.join(dict.fromkeys(source_paths)) if source_paths else 'Unknown'
    return data_headers, data_list, source_path


# --- Telegram Message Tags ---------------------------------------------------

@artifact_processor
def telegramMessageTags(context):
    """ see artifact description """
    data_headers = [
        ('Timestamp', 'datetime'),
        'Account ID',
        'Chat ID',
        'Chat',
        'Category',
        'Message ID',
    ]
    data_list = []
    source_paths = []

    for account_id, db_path in _postbox_dbs(context.get_files_found()):
        db = open_sqlite_db_readonly(db_path)
        if db is None:
            continue
        try:
            cursor = db.cursor()
            # Older postbox layouts predate the tag table entirely (observed on
            # the felix_ios17 image); absence means nothing to read, not an error.
            cursor.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't12'")
            if cursor.fetchone() is None:
                continue
            names = _peer_names(cursor)
            cursor.execute('SELECT key FROM t12')
            for (key,) in cursor.fetchall():
                # peerId int64, tag uint32, namespace int32, timestamp int32,
                # message id int32, all big-endian per the table's key function.
                if not isinstance(key, bytes) or len(key) < 24:
                    continue
                peer_id = struct.unpack('>q', key[0:8])[0]
                tag = struct.unpack('>I', key[8:12])[0]
                timestamp = struct.unpack('>i', key[16:20])[0]
                message_id = struct.unpack('>i', key[20:24])[0]
                labels = [name for bit, name in _MESSAGE_TAGS.items() if tag & (1 << bit)]
                unknown = tag & ~sum(1 << bit for bit in _MESSAGE_TAGS)
                if unknown:
                    labels.append(f'{unknown:#x}')
                data_list.append((
                    datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
                    if timestamp else '',
                    account_id,
                    peer_id,
                    names.get(peer_id, ''),
                    ', '.join(labels) if labels else '',
                    message_id,
                ))
            source_paths.append(db_path)
        except sqlite3.Error as err:
            logfunc(f'Telegram message tags: error reading {db_path}: {err}')
        finally:
            db.close()

    source_path = '\n'.join(dict.fromkeys(source_paths)) if source_paths else 'Unknown'
    return data_headers, data_list, source_path


# --- Telegram Cached Peer Details -------------------------------------------

# Type-hash labels for the cached peer detail records stored in table t18.
_CACHED_TYPE_NAMES = {
    _murmur('CachedUserData'): 'User',
    _murmur('CachedGroupData'): 'Group',
    _murmur('CachedChannelData'): 'Channel',
    _murmur('CachedSecretChatData'): 'Secret Chat',
}


def _peer_display_name(peer):
    """Best available label for a decoded t2 peer record."""
    name = f"{peer.get('fn', '')} {peer.get('ln', '')}".strip()
    if not name:
        name = peer.get('t', '') or ''
    username = peer.get('un', '')
    if name and username:
        return f'{name} (@{username})'
    if username:
        return f'@{username}'
    return name


def _format_birthday(value):
    """Telegram stores the birthday as JSON; the year is optional."""
    if not isinstance(value, dict):
        return ''
    day = value.get('day')
    month = value.get('month')
    if not day or not month:
        return ''
    year = value.get('year')
    if year:
        return f'{year:04d}-{month:02d}-{day:02d}'
    return f'--{month:02d}-{day:02d}'


def _format_autoremove(value):
    """Render the autoremoveTimeout known/unknown wrapper.

    Telegram encodes _v = 1 when the timeout is known and 0 when it has not
    been fetched; a known wrapper holding no value means the peer has no
    auto-delete timer set, which is distinct from never having been cached.
    """
    if not isinstance(value, dict):
        return ''
    if value.get('_v') != 1:
        return ''
    inner = value.get('v')
    if isinstance(inner, dict):
        seconds = inner.get('peerValue')
        if isinstance(seconds, int) and not isinstance(seconds, bool):
            return f'{seconds} seconds'
        return ''
    return 'None set'


def _peer_key_to_id(key, fallback=''):
    if isinstance(key, bytes) and len(key) == 8:
        return struct.unpack('>q', key)[0]
    if isinstance(key, int):
        return key
    return fallback


@artifact_processor
def telegramCachedPeerData(context):
    """ see artifact description """
    data_headers = [
        'Account ID',
        'Peer ID',
        'Peer Name',
        'Record Type',
        'About / Description',
        'Birthday',
        'Blocked',
        'Common Group Count',
        'Has Scheduled Messages',
        'Auto-Delete Timer',
        'Invited By',
    ]
    data_list = []
    source_paths = []

    for account_id, db_path in _postbox_dbs(context.get_files_found()):
        db = open_sqlite_db_readonly(db_path)
        if db is None:
            continue
        try:
            cursor = db.cursor()

            # Peer names, so cached records read as more than bare ids.
            peer_names = {}
            try:
                cursor.execute('SELECT key, value FROM t2')
                for key, value in cursor.fetchall():
                    if not isinstance(value, bytes):
                        continue
                    decoded = _decode_root(value)
                    peer_id = _peer_key_to_id(key, decoded.get('i', ''))
                    name = _peer_display_name(decoded)
                    if name:
                        peer_names[peer_id] = name
            except sqlite3.Error:
                pass

            cursor.execute('SELECT key, value FROM t18')
            for key, value in cursor.fetchall():
                if not isinstance(value, bytes):
                    continue
                cached = _decode_root(value)
                peer_id = _peer_key_to_id(key)
                record_type = _CACHED_TYPE_NAMES.get(cached.get('@type'), 'Unknown')
                is_user = record_type == 'User'

                # 'b' is isBlocked on user records but botInfos on channel records,
                # so it is only meaningful for users.
                blocked = ''
                if is_user and isinstance(cached.get('b'), int) \
                        and not isinstance(cached.get('b'), bool):
                    blocked = 'Yes' if cached['b'] else 'No'

                common_groups = ''
                if is_user and isinstance(cached.get('cg'), int):
                    common_groups = cached['cg']

                scheduled = cached.get('hsm')
                if isinstance(scheduled, bool):
                    scheduled = 'Yes' if scheduled else 'No'
                elif isinstance(scheduled, int):
                    scheduled = 'Yes' if scheduled else 'No'
                else:
                    scheduled = ''

                invited_by = cached.get('invBy')
                if isinstance(invited_by, int) and not isinstance(invited_by, bool):
                    invited_name = peer_names.get(invited_by)
                    invited_by = (f'{invited_name} ({invited_by})'
                                  if invited_name else str(invited_by))
                else:
                    invited_by = ''

                about = cached.get('a')
                about = about.strip() if isinstance(about, str) else ''

                data_list.append((
                    account_id,
                    peer_id,
                    peer_names.get(peer_id, ''),
                    record_type,
                    about,
                    _format_birthday(cached.get('bday')),
                    blocked,
                    common_groups,
                    scheduled,
                    _format_autoremove(cached.get('artv')),
                    invited_by,
                ))
            source_paths.append(db_path)
        except sqlite3.Error as err:
            logfunc(f'Telegram cached peer data: error reading {db_path}: {err}')
        finally:
            db.close()

    source_path = '\n'.join(dict.fromkeys(source_paths)) if source_paths else 'Unknown'
    return data_headers, data_list, source_path


# --- Telegram Settings -------------------------------------------------------

# TelegramCore SyncCore_Namespaces.swift SharedDataKeyValues.
_SHARED_CORE_KEYS = {
    0: 'Logging settings',
    2: 'Cache storage settings',
    3: 'Localization settings',
    4: 'Proxy settings',
    5: 'Media auto-download presets (server)',
    6: 'Theme settings',
    8: 'Wallpapers state',
    11: 'Synced device contacts',
}

# TelegramUIPreferences PostboxKeys.swift ApplicationSpecificSharedDataKeyValues (+1000).
_SHARED_APP_KEYS = {
    1000: 'In-app notification settings',
    1001: 'App passcode settings',
    1002: 'Media auto-download settings',
    1003: 'Generated media store settings',
    1004: 'Voice call settings',
    1005: 'Presentation theme settings',
    1007: 'Call list settings',
    1009: 'Music playback settings',
    1010: 'Media input settings',
    1012: 'Sticker settings',
    1015: 'Contact synchronization settings',
    1016: 'Web browser settings',
    1017: 'Siri intents settings',
    1018: 'Translation settings',
    1019: 'Drawing settings',
    1020: 'Media display settings',
    1022: 'Chat settings',
}

# TelegramCore SyncCore_Namespaces.swift PreferencesKeyValues.
_ACCOUNT_CORE_KEYS = {
    0: 'Global notification settings',
    8: 'Content privacy settings',
    9: 'Network settings',
    12: 'App version changelog state',
    16: 'Contacts synchronization (account)',
    19: 'Content settings',
    20: 'Chat list filters (folders)',
    23: 'Secret chat settings',
    24: 'Quick reaction settings',
    27: 'Default auto-delete timer settings',
    28: 'Account cache storage settings',
    31: 'Global privacy settings',
    32: 'Stories configuration (stealth mode state)',
}

# TelegramUIPreferences PostboxKeys.swift ApplicationSpecificPreferencesKeyValues (+1000).
_ACCOUNT_APP_KEYS = {
    1017: 'Chat archive settings',
    1018: 'Chat list filter settings',
    1019: 'Widget settings',
    1020: 'Save to Photos settings',
    1021: 'Age verification state',
}

# Headline settings get a placeholder when no supported named record was reported
# for the key.
_HEADLINE_SHARED = {
    1001: 'App passcode settings',
    1002: 'Media auto-download settings',
}
_HEADLINE_ACCOUNT = {
    1020: 'Save to Photos settings',
}

_ABSENT_VALUE = 'No supported stored record reported'
_VALUE_LIMIT = 1000


def _format_setting_value(decoded):
    rendered = json.dumps(decoded, ensure_ascii=False, default=str)
    if len(rendered) > _VALUE_LIMIT:
        rendered = rendered[:_VALUE_LIMIT] + '… [truncated]'
    return rendered


def _read_settings_table(db_path, table, core_names, app_names, scope, data_list):
    db = open_sqlite_db_readonly(db_path)
    if db is None:
        return False
    found_keys = set()
    try:
        cursor = db.cursor()
        cursor.execute(f'SELECT key, value FROM {table}')
        for key, value in cursor.fetchall():
            if not isinstance(key, bytes) or len(key) != 4 or not isinstance(value, bytes):
                continue
            key_id = struct.unpack('>i', key)[0]
            name = core_names.get(key_id) or app_names.get(key_id)
            if name is None:
                continue
            found_keys.add(key_id)
            data_list.append((
                scope, name, _format_setting_value(_decode_root(value)), key_id,
            ))
    except sqlite3.Error as err:
        logfunc(f'Telegram settings: error reading {db_path}: {err}')
        return False
    finally:
        db.close()

    headline = _HEADLINE_SHARED if table == 't2' else _HEADLINE_ACCOUNT
    for key_id, name in headline.items():
        if key_id not in found_keys:
            data_list.append((scope, name, _ABSENT_VALUE, key_id))
    return True


@artifact_processor
def telegramSettings(context):
    """ see artifact description """
    data_headers = [
        'Scope',
        'Setting',
        'Value',
        'Key ID',
    ]
    data_list = []
    source_paths = []

    for file_found in context.get_files_found():
        path = str(file_found)
        normalized = path.replace('\\', '/')
        if normalized.endswith('/accounts-metadata/db/db_sqlite'):
            if _read_settings_table(path, 't2', _SHARED_CORE_KEYS, _SHARED_APP_KEYS,
                                    'Shared', data_list):
                source_paths.append(path)
        elif normalized.endswith('/postbox/db/db_sqlite'):
            account_id = _account_id_from_path(normalized)
            if _read_settings_table(path, 't35', _ACCOUNT_CORE_KEYS, _ACCOUNT_APP_KEYS,
                                    f'Account {account_id}', data_list):
                source_paths.append(path)

    source_path = '\n'.join(dict.fromkeys(source_paths)) if source_paths else 'Unknown'
    return data_headers, data_list, source_path
