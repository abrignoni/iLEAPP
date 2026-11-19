__artifacts_v2__ = {
    "dustMessages": {
        "name": "Dust - Messages",
        "description": "Dust (com.mentionmobile.cyberdust) chat messages from the sealed message store in the "
                       "app group container, decrypted with the message-history key from the device keychain.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "pycryptodome",
        "category": "Dust",
        "notes": ("Read from dust/messages-<store id>.sqlite3 in the group.com.mentionmobile.cyberdust "
                  "container, table messages (conversation_id, message_id, sent_at, sealed). The sealed column "
                  "is opened as Dust's own unseal function does, read from the app's JavaScript bundle "
                  "(main.jsbundle, Dust 8.0.3): AES-GCM with the 32-byte key stored base64 in the keychain item "
                  "with account dust and service dust:history:key:<store id> (access group "
                  "com.mentionmobile.cyberdust), a 12-byte IV at the start of the blob, the ciphertext and "
                  "16-byte tag after it, and additional data 'dust:messages:v1:<conversation_id>:<message_id>'. "
                  "The keychain is captured separately from the file system, so supply it with --keychain or "
                  "the keychain field in the GUI; without it, or without a matching key, rows are kept with "
                  "Decryption State saying so and the decrypted columns blank. The decrypted record is JSON; "
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
        }
    },
    "dustAccount": {
        "name": "Dust - Account",
        "description": "Account rows of the Account class in Dust's Documents/default.realm.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Dust",
        "notes": ("One row per object of the Realm class Account in Documents/default.realm of the Dust app "
                  "container, read with iLEAPP's Realm parser (live objects only). Column names are the stored "
                  "property names and values are shown as stored; no meaning is assigned to them. On the tested "
                  "image firstName, lastName, email, bio and website had no value on the 1 row. Only a "
                  "container that also holds Library/Preferences/com.mentionmobile.cyberdust.plist is read."),
        "paths": ('*/Containers/Data/Application/*/Documents/default.realm',
                  '*/Containers/Data/Application/*/Library/Preferences/com.mentionmobile.cyberdust.plist'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Dust 8.0.3 | 1 row",
        }
    },
    "dustContacts": {
        "name": "Dust - Contacts",
        "description": "Rows of the DSTContact class in Dust's Documents/default.realm.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Dust",
        "notes": ("One row per object of the Realm class DSTContact in Documents/default.realm of the Dust app "
                  "container, read with iLEAPP's Realm parser (live objects only). Column names are the stored "
                  "property names and values are shown as stored; createdDate and updatedDate are stored as "
                  "strings and are not converted, and no meaning is assigned to any property. "
                  "thumbnailImageData is reported as its size in bytes. On the tested image username, photoURL "
                  "and thumbnailImageData had no value on any of 2 rows. Only a container that also holds "
                  "Library/Preferences/com.mentionmobile.cyberdust.plist is read."),
        "paths": ('*/Containers/Data/Application/*/Documents/default.realm',
                  '*/Containers/Data/Application/*/Library/Preferences/com.mentionmobile.cyberdust.plist'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Dust 8.0.3 | 2 rows",
        }
    },
    "dustProfilePictureMetadata": {
        "name": "Dust - Profile Picture Metadata",
        "description": "Rows of the ProfilePictureMetadata class in Dust's Documents/default.realm.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
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
        }
    }
}

import base64
import binascii
import json
import os
import re
import sqlite3

from Crypto.Cipher import AES

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc, open_sqlite_db_readonly
from scripts.ios_keychain import active_keychain_path, get_app_secret
from scripts.realm_parser import realm_rows

_ACCESS_GROUP = 'com.mentionmobile.cyberdust'
_STORE = re.compile(r'messages-([0-9A-Fa-f-]{36})\.sqlite3$')
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
    if not isinstance(sealed, bytes) or len(sealed) <= _IV_LENGTH + _TAG_LENGTH:
        return None
    cipher = AES.new(key, AES.MODE_GCM, nonce=sealed[:_IV_LENGTH])
    cipher.update(f'dust:messages:v1:{conversation_id}:{message_id}'.encode('utf-8'))
    try:
        plaintext = cipher.decrypt_and_verify(sealed[_IV_LENGTH:-_TAG_LENGTH], sealed[-_TAG_LENGTH:])
        record = json.loads(plaintext)
    except ValueError:
        return None
    return record if isinstance(record, dict) else None


def _text(value):
    if value is None:
        return ''
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


@artifact_processor
def dustMessages(context):
    data_list = []
    sources = []
    for file_found in dict.fromkeys(str(found) for found in context.get_files_found()):
        match = _STORE.search(os.path.basename(file_found))
        if not match:
            continue
        store_id = match.group(1)
        key, state = _history_key(store_id)
        try:
            db = open_sqlite_db_readonly(file_found)
            rows = db.execute('SELECT conversation_id, message_id, sent_at, sealed FROM messages '
                              'ORDER BY sent_at, message_id').fetchall()
            db.close()
        except sqlite3.Error as ex:
            logfunc(f'Dust: could not read {file_found}: {ex}')
            continue
        sources.append(file_found)
        for conversation_id, message_id, sent_at, sealed in rows:
            record = _unseal(key, conversation_id, message_id, sealed) if key else None
            row_state = state if not key else ('Decrypted' if record else 'Not decrypted: authentication failed')
            record = record or {}
            payload = record.get('payload') if isinstance(record.get('payload'), dict) else {}
            outgoing = record.get('outgoing')
            sender_sent = payload.get('sent_at')
            data_list.append((
                convert_unix_ts_to_utc(sent_at) if isinstance(sent_at, int) else None,
                convert_unix_ts_to_utc(sender_sent) if isinstance(sender_sent, int) else None,
                '' if outgoing is None else ('Outgoing' if outgoing else 'Incoming'),
                _text(payload.get('type')), _text(payload.get('body')),
                ', '.join(str(x) for x in payload.get('message_ids') or []),
                _text(record.get('senderAccountId')), _text(record.get('senderDeviceId')),
                conversation_id, message_id, row_state))

    data_headers = (('Sent At', 'datetime'), ('Sender Sent At', 'datetime'), 'Direction', 'Type', 'Body',
                    'Referenced Message IDs', 'Sender Account ID', 'Sender Device ID', 'Conversation ID',
                    'Message ID', 'Decryption State')
    return data_headers, data_list, '\n'.join(sources)


# --- app container stores ----------------------------------------------------------------------------

_APP_MARKER = 'Library/Preferences/com.mentionmobile.cyberdust.plist'
_APP_CONTAINER = re.compile(r'(.*?/Containers/Data/Application/[^/]+)/(.*)$')


def _app_file(context, inner_path):
    """The file at inner_path in a container that also holds the Dust preference file, or ''."""
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
            return path
    return ''


def _as_stored(value):
    if value is None:
        return ''
    if isinstance(value, (bytes, bytearray)):
        return f'{len(value)} bytes'
    if isinstance(value, bool):
        return 'True' if value else 'False'
    return value


def _realm_class(context, class_name):
    """(headers, rows, source) for every live object of class_name in Documents/default.realm."""
    path = _app_file(context, 'Documents/default.realm')
    if not path:
        return [], [], ''
    rows = list(realm_rows(path, class_name))
    headers = list(rows[0].keys()) if rows else []
    return headers, [tuple(_as_stored(row.get(h)) for h in headers) for row in rows], path


_ACCOUNT_COLUMNS = ('id', 'username', 'phone', 'photoURL', 'firstName', 'lastName', 'email', 'overThirteen',
                    'bio', 'website')
_CONTACT_COLUMNS = ('id', 'username', 'contactId', 'contactName', 'displayName', 'sortByDisplayName',
                    'phoneNumber', 'label', 'photoURL', 'thumbnailImageData', 'createdDate', 'updatedDate',
                    'rawEntityType', 'batchNumber', 'hasProfileId', 'mutual', 'rawMuteFlag', 'invited',
                    'favorite', 'engagementFactor')
_PROFILE_COLUMNS = ('accountId', 'updated', 'syncTimeStamp')


def _ordered(context, class_name, columns):
    headers, rows, source = _realm_class(context, class_name)
    index = {name: i for i, name in enumerate(headers)}
    data_list = [tuple(row[index[c]] if c in index else '' for c in columns) for row in rows]
    extra = [h for h in headers if h not in columns]
    if extra:
        logfunc(f'Dust: {class_name} has properties not reported: {", ".join(extra)}')
    return data_list, source


@artifact_processor
def dustAccount(context):
    data_list, source = _ordered(context, 'class_Account', _ACCOUNT_COLUMNS)
    return _ACCOUNT_COLUMNS, data_list, source


@artifact_processor
def dustContacts(context):
    data_list, source = _ordered(context, 'class_DSTContact', _CONTACT_COLUMNS)
    return _CONTACT_COLUMNS, data_list, source


@artifact_processor
def dustProfilePictureMetadata(context):
    data_list, source = _ordered(context, 'class_ProfilePictureMetadata', _PROFILE_COLUMNS)
    return _PROFILE_COLUMNS, data_list, source
