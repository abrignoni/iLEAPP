__artifacts_v2__ = {
    "dustMessages": {
        "name": "Dust - Messages",
        "description": "Dust (com.mentionmobile.cyberdust) chat messages from the sealed message store in the "
                       "app group container, decrypted with the message-history key from the device keychain.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "pycryptodome",
        "category": "Dust",
        "notes": ("Read from dust/messages-<store id>.sqlite3 in the group.com.mentionmobile.cyberdust "
                  "container, table messages (conversation_id, message_id, sent_at, sealed). App Group comes from "
                  "the container metadata or a named iTunes backup domain. App Group held one value on all 6 tested "
                  "rows. An unidentified container is labeled Unverified, and a known unrelated group is skipped. "
                  "The sealed column "
                  "is opened as Dust's own unseal function does, read from the app's JavaScript bundle "
                  "(main.jsbundle, Dust 8.0.3): AES-GCM with the 32-byte key stored base64 in the keychain item "
                  "with account dust and service dust:history:key:<store id> (access group "
                  "com.mentionmobile.cyberdust), a 12-byte IV at the start of the blob, the ciphertext and "
                  "16-byte tag after it, and additional data 'dust:messages:v1:<conversation_id>:<message_id>'. "
                  "The keychain is captured separately from the file system, so supply it with --keychain or "
                  "the keychain field in the GUI; without it, or without a matching key, rows are kept with "
                  "Decryption State explaining the result. Without a key, Sender Sent At, Direction, Type, Body, "
                  "Referenced Message IDs, Sender Account ID and Sender Device ID are blank. The decrypted record is JSON; "
                  "Direction is its outgoing key as stored (true Outgoing, false Incoming), Type, Body, "
                  "Referenced Message IDs (message_ids) and Sender Sent At (sent_at) come from its payload, and "
                  "Sender Account ID and Sender Device ID are senderAccountId and senderDeviceId. Sent At is the "
                  "table's sent_at, read as Unix seconds; on the tested image it equalled the record's "
                  "insertedAt on all 6 rows and Sender Sent At on 4, the other 2 being 1 second later. On the "
                  "tested image Type was text on 3 rows and receipt on 3, and every receipt's Referenced "
                  "Message IDs named a message in the same table. On the tested image all 6 rows were in one "
                  "conversation, so Conversation ID held one value on all 6 rows, and Decryption State held "
                  "Decrypted on all 6 rows."),
        "paths": ('*/Containers/Shared/AppGroup/*/dust/messages-*.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Dust 8.0.3 | 6 rows",
            "hc_ios17_2": "iOS 17.2.1 | Dust 7.3.0 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Dust 7.4.3 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | Dust 7.4.3 | 0 rows",
        }
    },
    "dustAccount": {
        "name": "Dust - Account",
        "description": "Account rows of the Account class in Dust's Documents/default.realm.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Dust",
        "notes": ("One row per object of the Realm class Account in Documents/default.realm of the Dust app "
                  "container, read with iLEAPP's Realm parser (live objects only). Column names are the stored "
                  "property names and values are shown as stored; no meaning is assigned to them. On the tested "
                  "iOS 27.2 image firstName, lastName, email, bio and website had no value on the 1 row. Across "
                  "the three older acquisitions phone and overThirteen each held one value. Only a "
                  "container that also holds Library/Preferences/com.mentionmobile.cyberdust.plist is read."),
        "paths": ('*/Containers/Data/Application/*/Documents/default.realm',
                  '*/Containers/Data/Application/*/Library/Preferences/com.mentionmobile.cyberdust.plist'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Dust 8.0.3 | 1 row",
            "hc_ios17_2": "iOS 17.2.1 | Dust 7.3.0 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | Dust 7.4.3 | 1 row",
            "hc_ios26": "iOS 26.5.2 | Dust 7.4.3 | 1 row",
        }
    },
    "dustContacts": {
        "name": "Dust - Contacts",
        "description": "Rows of the DSTContact class in Dust's Documents/default.realm.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Dust",
        "notes": ("One row per object of the Realm class DSTContact in Documents/default.realm of the Dust app "
                  "container, read with iLEAPP's Realm parser (live objects only). Column names are the stored "
                  "property names and values are shown as stored; createdDate and updatedDate are stored as "
                  "strings and are not converted, and no meaning is assigned to any property. "
                  "thumbnailImageData is reported as its size in bytes. On the tested image username, photoURL "
                  "and thumbnailImageData had no value on any of 2 rows. Across the seven contacts in the three "
                  "older acquisitions rawEntityType, batchNumber, hasProfileId, mutual, rawMuteFlag, invited, "
                  "favorite and engagementFactor each held one value. On those rows contactName and displayName "
                  "were identical, as were createdDate and updatedDate. Only a container that also holds "
                  "Library/Preferences/com.mentionmobile.cyberdust.plist is read."),
        "paths": ('*/Containers/Data/Application/*/Documents/default.realm',
                  '*/Containers/Data/Application/*/Library/Preferences/com.mentionmobile.cyberdust.plist'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Dust 8.0.3 | 2 rows",
            "hc_ios17_2": "iOS 17.2.1 | Dust 7.3.0 | 3 rows",
            "hc_ios18_7": "iOS 18.7.8 | Dust 7.4.3 | 2 rows",
            "hc_ios26": "iOS 26.5.2 | Dust 7.4.3 | 2 rows",
        }
    },
    "dustProfilePictureMetadata": {
        "name": "Dust - Profile Picture Metadata",
        "description": "Rows of the ProfilePictureMetadata class in Dust's Documents/default.realm.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Dust",
        "notes": ("One row per object of the Realm class ProfilePictureMetadata in Documents/default.realm of the "
                  "Dust app container, read with iLEAPP's Realm parser (live objects only). Column names are the "
                  "stored property names and values are shown as stored: updated and syncTimeStamp are stored "
                  "as doubles and are not converted to dates, because what they count from is not established. "
                  "On the tested image updated held one value on all 3 rows. "
                  "Only a container that also holds Library/Preferences/com.mentionmobile.cyberdust.plist is "
                  "read."),
        "paths": ('*/Containers/Data/Application/*/Documents/default.realm',
                  '*/Containers/Data/Application/*/Library/Preferences/com.mentionmobile.cyberdust.plist'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Dust 8.0.3 | 3 rows",
            "hc_ios17_2": "iOS 17.2.1 | Dust 7.3.0 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | Dust 7.4.3 | 3 rows",
            "hc_ios26": "iOS 26.5.2 | Dust 7.4.3 | 3 rows",
        }
    }
}

import base64
import binascii
import json
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import PurePosixPath

from Crypto.Cipher import AES

from scripts.ilapfuncs import artifact_processor, get_plist_file_content, logfunc, open_sqlite_db_readonly
from scripts.ios_keychain import active_keychain_path, get_app_secret
from scripts.realm_parser import realm_rows

_ACCESS_GROUP = 'com.mentionmobile.cyberdust'
_GROUP = 'group.com.mentionmobile.cyberdust'
_METADATA = '.com.apple.mobile_container_manager.metadata.plist'
_STORE = re.compile(r'messages-([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})\.sqlite3', re.I)
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_IV_LENGTH = 12
_TAG_LENGTH = 16


def _history_key(store_id):
    """The 32-byte AES key for one message store, or (None, reason)."""
    if not active_keychain_path():
        return None, 'Not decrypted: no keychain supplied'
    secret = get_app_secret(_ACCESS_GROUP, account='dust', service=f'dust:history:key:{store_id}')
    if not secret:
        return None, 'Not decrypted: history key not in keychain'
    try:
        key = base64.b64decode(secret, validate=True)
    except (binascii.Error, ValueError):
        return None, 'Not decrypted: history key not base64'
    if len(key) != 32:
        return None, 'Not decrypted: history key not 32 bytes'
    return key, ''


def _unseal(key, conversation_id, message_id, sealed):
    if not isinstance(sealed, bytes) or len(sealed) < _IV_LENGTH + _TAG_LENGTH:
        return {}, 'Not decrypted: invalid sealed data'
    cipher = AES.new(key, AES.MODE_GCM, nonce=sealed[:_IV_LENGTH])
    cipher.update(f'dust:messages:v1:{conversation_id}:{message_id}'.encode('utf-8'))
    try:
        plaintext = cipher.decrypt_and_verify(sealed[_IV_LENGTH:-_TAG_LENGTH], sealed[-_TAG_LENGTH:])
    except ValueError:
        return {}, 'Not decrypted: authentication failed'
    try:
        record = json.loads(plaintext)
    except (ValueError, RecursionError):
        return {}, 'Decrypted: invalid JSON'
    if not isinstance(record, dict):
        return {}, 'Decrypted: unexpected JSON type'
    return record, 'Decrypted'


def _text(value):
    if value is None:
        return ''
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _group_identifier(context, root):
    if root.name.startswith('group.'):  # iTunes backup domains are named by the app group.
        return root.name
    try:
        candidates = context.get_seeker().search(f'*/Containers/Shared/AppGroup/{root.name}/{_METADATA}')
    except (ValueError, OSError) as error:
        logfunc(f'Dust: could not look up group metadata for {root}: {error}')
        return ''
    for path in candidates:
        evidence_path = PurePosixPath(context.get_relative_path(str(path)).replace('\\', '/'))
        if evidence_path == root / _METADATA:
            metadata = get_plist_file_content(str(path))
            if isinstance(metadata, dict):
                return metadata.get('MCMMetadataIdentifier') or ''
    return ''


def _timestamp(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        return None
    try:
        return _EPOCH + timedelta(seconds=value)
    except (OverflowError, ValueError):
        return None


def _message_row(key, state, group, conversation_id, message_id, sent_at, sealed):
    record = {}
    if key:
        record, state = _unseal(key, conversation_id, message_id, sealed)
    payload = record.get('payload')
    if not isinstance(payload, dict):
        payload = {}
    outgoing = record.get('outgoing')
    direction = ''
    if isinstance(outgoing, bool):
        direction = 'Outgoing' if outgoing else 'Incoming'
    references = payload.get('message_ids')
    if isinstance(references, list):
        references = ', '.join(map(_text, references))
    return (_timestamp(sent_at), _timestamp(payload.get('sent_at')), direction,
            _text(payload.get('type')), _text(payload.get('body')), _text(references),
            _text(record.get('senderAccountId')), _text(record.get('senderDeviceId')),
            conversation_id, message_id, state, group or 'Unverified')


def _result(context, headers, by_source):
    sources = [path for path, rows in by_source if rows]
    if len(sources) > 1:
        headers = (*headers, 'Source File')
        data = [(*row, context.get_relative_path(path)) for path, rows in by_source for row in rows]
    else:
        data = [row for _, rows in by_source for row in rows]
    return headers, data, '\n'.join(sources)


@artifact_processor
def dustMessages(context):
    by_source = []
    groups = {}
    for file_found in dict.fromkeys(map(str, context.get_files_found())):
        source = PurePosixPath(context.get_relative_path(file_found).replace('\\', '/'))
        match = _STORE.fullmatch(source.name)
        if not match or source.parent.name != 'dust':
            continue
        root = source.parent.parent
        if root.parent.parts[-3:] != ('Containers', 'Shared', 'AppGroup'):
            continue
        if root not in groups:
            groups[root] = _group_identifier(context, root)
        group = groups[root]
        if group and group != _GROUP:
            continue
        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        try:
            with closing(db):
                cursor = db.execute('SELECT conversation_id, message_id, sent_at, sealed FROM messages '
                                    'ORDER BY sent_at, message_id')
                key, state = _history_key(match.group(1))
                rows = [_message_row(key, state, group, *row) for row in cursor]
        except sqlite3.Error as ex:
            logfunc(f'Dust: could not read {source}: {ex}')
            continue
        by_source.append((file_found, rows))

    data_headers = (('Sent At', 'datetime'), ('Sender Sent At', 'datetime'), 'Direction', 'Type', 'Body',
                    'Referenced Message IDs', 'Sender Account ID', 'Sender Device ID', 'Conversation ID',
                    'Message ID', 'Decryption State', 'App Group')
    return _result(context, data_headers, by_source)


# --- app container stores ----------------------------------------------------------------------------

_APP_MARKER = 'Library/Preferences/com.mentionmobile.cyberdust.plist'
_APP_CONTAINER = re.compile(r'((?:.*/)?Containers/Data/Application/[^/]+)/(.*)$')


def _app_files(context, inner_path):
    """Yield each matching store from a container with the Dust preference marker."""
    containers = {}
    markers = set()
    for file_found in dict.fromkeys(str(found) for found in context.get_files_found()):
        match = _APP_CONTAINER.match(context.get_relative_path(file_found).replace('\\', '/'))
        if not match:
            continue
        if match.group(2) == _APP_MARKER:
            markers.add(match.group(1))
        elif match.group(2) == inner_path:
            containers.setdefault(match.group(1), file_found)
    for container, path in containers.items():
        if container in markers:
            yield path


def _as_stored(value):
    if value is None:
        return ''
    if isinstance(value, (bytes, bytearray)):
        return f'{len(value)} bytes'
    if isinstance(value, bool):
        return 'True' if value else 'False'
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, default=_as_stored)
    return value


_ACCOUNT_COLUMNS = ('id', 'username', 'phone', 'photoURL', 'firstName', 'lastName', 'email', 'overThirteen',
                    'bio', 'website')
_CONTACT_COLUMNS = ('id', 'username', 'contactId', 'contactName', 'displayName', 'sortByDisplayName',
                    'phoneNumber', 'label', 'photoURL', 'thumbnailImageData', 'createdDate', 'updatedDate',
                    'rawEntityType', 'batchNumber', 'hasProfileId', 'mutual', 'rawMuteFlag', 'invited',
                    'favorite', 'engagementFactor')
_PROFILE_COLUMNS = ('accountId', 'updated', 'syncTimeStamp')


def _ordered(context, class_name, columns):
    by_source = []
    extra = {}
    for path in _app_files(context, 'Documents/default.realm'):
        try:
            rows = list(realm_rows(path, class_name))
        except (OSError, ValueError, IndexError, OverflowError) as error:
            logfunc(f'Dust: could not read {class_name} in {context.get_relative_path(path)}: {error}')
            continue
        for row in rows:
            extra.update(dict.fromkeys(name for name in row if name not in columns))
        by_source.append((path, rows))
    headers = (*columns, *extra)
    values = [(path, [tuple(_as_stored(row.get(h)) for h in headers) for row in rows])
              for path, rows in by_source]
    return _result(context, headers, values)


@artifact_processor
def dustAccount(context):
    return _ordered(context, 'class_Account', _ACCOUNT_COLUMNS)


@artifact_processor
def dustContacts(context):
    return _ordered(context, 'class_DSTContact', _CONTACT_COLUMNS)


@artifact_processor
def dustProfilePictureMetadata(context):
    return _ordered(context, 'class_ProfilePictureMetadata', _PROFILE_COLUMNS)
