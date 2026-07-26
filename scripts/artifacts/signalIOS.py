__artifacts_v2__ = {
    "get_signalIOSMessages": {
        "name": "Signal - Messages",
        "description": "Parses messages from the encrypted Signal database, including direction, author, conversation and body.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "Signal",
        "notes": "Signal encrypts its database with a key held in the iOS keychain. The keychain is captured separately from the file system extraction, so supply it with --keychain or the keychain field in the GUI.",
        "paths": ('*/AppGroup/*/grdb/signal.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
    },
    "get_signalIOSContacts": {
        "name": "Signal - Contacts",
        "description": "Parses Signal recipients, including phone numbers and ACI/PNI identifiers.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "Signal",
        "notes": "Requires the keychain, supplied with --keychain or the keychain field in the GUI.",
        "paths": ('*/AppGroup/*/grdb/signal.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_signalIOSThreads": {
        "name": "Signal - Conversations",
        "description": "Parses Signal conversations, including the other party, creation time and archived state.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "Signal",
        "notes": "Requires the keychain, supplied with --keychain or the keychain field in the GUI.",
        "paths": ('*/AppGroup/*/grdb/signal.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
}

import hashlib
import os
import sqlite3
import tempfile

from scripts.context import Context
from scripts.ios_keychain import get_app_secret
from scripts.sqlcipher_decrypt import decrypt_sqlcipher_db
from scripts.ilapfuncs import artifact_processor, logfunc, convert_unix_ts_to_utc

SIGNAL_ACCESS_GROUP = 'org.whispersystems.signal'
KEY_SPEC_ACCOUNT = 'GRDBDatabaseCipherKeySpec'
# The keychain entry is a 32 byte key followed by the 16 byte salt
KEY_SPEC_LENGTH = 48

# Signal for iOS keeps the first 32 bytes readable so the file still identifies
# as SQLite, which displaces the salt into the keychain entry above. It also
# uses the SQLCipher 4 defaults of SHA512 for the HMAC and the KDF.
PLAINTEXT_HEADER_SIZE = 32
SIGNAL_HMAC = 'sha512'

# SDSRecordType values seen in model_TSInteraction. Incoming rows carry an
# author; outgoing rows do not, because the author is the device owner.
RECORD_TYPE_INCOMING = 19
RECORD_TYPE_OUTGOING = 21
MESSAGE_DIRECTIONS = {RECORD_TYPE_INCOMING: 'Incoming', RECORD_TYPE_OUTGOING: 'Outgoing'}

_decrypted_cache = {}


def _decrypted_database(database_path):
    """Decrypt the Signal database once per run; return a path or None."""
    if database_path in _decrypted_cache:
        return _decrypted_cache[database_path]
    _decrypted_cache[database_path] = None  # do not retry for every artifact

    key_spec = get_app_secret(SIGNAL_ACCESS_GROUP, KEY_SPEC_ACCOUNT,
                              expected_length=KEY_SPEC_LENGTH)
    if not key_spec:
        if Context.get_keychain_path():
            logfunc('Signal: the supplied keychain has no Signal database key, '
                    'the database stays encrypted')
        else:
            logfunc('Signal: found an encrypted database but no keychain was supplied. '
                    'Pass one with --keychain, or the keychain field in the GUI, to decrypt it.')
        return None

    digest = hashlib.sha1(database_path.encode('utf-8', 'replace')).hexdigest()[:12]
    output_path = os.path.join(tempfile.gettempdir(), 'ileapp_signal', f'signal_{digest}.db')
    try:
        pages, verified = decrypt_sqlcipher_db(
            database_path, key_spec[:32], output_path, raw_key=True,
            external_salt=key_spec[32:KEY_SPEC_LENGTH],
            plaintext_header_size=PLAINTEXT_HEADER_SIZE,
            hmac_algorithm=SIGNAL_HMAC, kdf_algorithm=SIGNAL_HMAC)
    except Exception as error:  # pylint: disable=broad-except
        logfunc(f'Signal: decryption failed for {database_path}: {error}')
        return None

    if not pages or not verified:
        logfunc('Signal: the keychain key did not authenticate the database. It may belong '
                'to a different device than this extraction.')
        return None
    if verified != pages:
        logfunc(f'Signal: {pages - verified} of {pages} decrypted pages failed HMAC '
                'verification, the recovered data may be incomplete')

    _decrypted_cache[database_path] = output_path
    return output_path


def _open_signal_database(context):
    """Yield (connection, source_path) for each decryptable Signal database."""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.basename(file_found) != 'signal.sqlite':
            continue
        decrypted = _decrypted_database(file_found)
        if not decrypted:
            continue
        yield sqlite3.connect(decrypted), file_found


def _table_columns(connection, table):
    return {row[1] for row in connection.execute(f'PRAGMA table_info({table})')}


def _select_list(available, table_alias, columns):
    """Build SELECT expressions, substituting NULL for columns this version lacks."""
    return ', '.join(f'{table_alias}.{column}' if column in available else 'NULL'
                     for column in columns)


@artifact_processor
def get_signalIOSMessages(context):
    data_list = []
    source_path = ''
    for connection, source_path in _open_signal_database(context):
        columns = _table_columns(connection, 'model_TSInteraction')
        if not columns:
            connection.close()
            continue
        cursor = connection.cursor()
        cursor.execute(f'''
        SELECT
            {_select_list(columns, 'model_TSInteraction',
                          ['timestamp', 'receivedAtTimestamp', 'recordType', 'body',
                           'authorPhoneNumber', 'authorUUID', 'uniqueThreadId', 'read',
                           'isVoiceMessage', 'isViewOnceMessage', 'wasRemotelyDeleted',
                           'expiresInSeconds', 'serverTimestamp', 'attachmentIds', 'id'])},
            model_TSThread.contactPhoneNumber, model_TSThread.contactUUID
        FROM model_TSInteraction
        LEFT JOIN model_TSThread ON model_TSInteraction.uniqueThreadId = model_TSThread.uniqueId
        ORDER BY model_TSInteraction.timestamp
        ''')
        for row in cursor:
            direction = MESSAGE_DIRECTIONS.get(row[2], f'Other (record type {row[2]})')
            # Outgoing rows have no author: the device owner sent them
            author = row[4] or row[5] or ('Device owner' if row[2] == RECORD_TYPE_OUTGOING else '')
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                convert_unix_ts_to_utc(row[1]),
                direction,
                author,
                row[15] or row[16] or '',
                row[3] or '',
                'Yes' if row[7] else 'No',
                'Yes' if row[8] else 'No',
                'Yes' if row[9] else 'No',
                'Yes' if row[10] else 'No',
                row[11] or '',
                convert_unix_ts_to_utc(row[12]) if row[12] else '',
                'Yes' if row[13] else 'No',
                row[6] or '',
                row[14],
            ))
        connection.close()

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Received Timestamp', 'datetime'),
        'Direction',
        'Author',
        'Conversation With',
        'Message',
        'Read',
        'Voice Message',
        'View Once',
        'Remotely Deleted',
        'Disappearing Timer (Seconds)',
        ('Server Timestamp', 'datetime'),
        'Has Attachment',
        'Thread ID',
        'Row ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_signalIOSContacts(context):
    data_list = []
    source_path = ''
    for connection, source_path in _open_signal_database(context):
        columns = _table_columns(connection, 'model_SignalRecipient')
        if not columns:
            connection.close()
            continue
        cursor = connection.cursor()
        cursor.execute(f'''
        SELECT {_select_list(columns, 'model_SignalRecipient',
                             ['recipientPhoneNumber', 'recipientUUID', 'pni',
                              'unregisteredAtTimestamp', 'isPhoneNumberDiscoverable',
                              'devices', 'uniqueId'])}
        FROM model_SignalRecipient
        ORDER BY model_SignalRecipient.id
        ''')
        for row in cursor:
            data_list.append((
                row[0] or '',
                row[1] or '',
                row[2] or '',
                'Yes' if row[3] else 'No',
                convert_unix_ts_to_utc(row[3]) if row[3] else '',
                'Yes' if row[4] else 'No',
                row[6] or '',
            ))
        connection.close()

    data_headers = (
        'Phone Number',
        'ACI',
        'PNI',
        'Unregistered',
        ('Unregistered Timestamp', 'datetime'),
        'Phone Number Discoverable',
        'Unique ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_signalIOSThreads(context):
    data_list = []
    source_path = ''
    for connection, source_path in _open_signal_database(context):
        columns = _table_columns(connection, 'model_TSThread')
        if not columns:
            connection.close()
            continue
        cursor = connection.cursor()
        cursor.execute(f'''
        SELECT {_select_list(columns, 'model_TSThread',
                             ['creationDate', 'contactPhoneNumber', 'contactUUID',
                              'groupModel', 'isArchived', 'isMarkedUnread',
                              'messageDraft', 'mutedUntilTimestamp', 'uniqueId'])},
            (SELECT count(*) FROM model_TSInteraction
             WHERE model_TSInteraction.uniqueThreadId = model_TSThread.uniqueId)
        FROM model_TSThread
        ORDER BY model_TSThread.creationDate
        ''')
        for row in cursor:
            data_list.append((
                convert_unix_ts_to_utc(row[0]) if row[0] else '',
                row[1] or row[2] or '',
                'Group' if row[3] else 'One to one',
                row[9],
                'Yes' if row[4] else 'No',
                'Yes' if row[5] else 'No',
                row[6] or '',
                convert_unix_ts_to_utc(row[7]) if row[7] else '',
                row[8] or '',
            ))
        connection.close()

    data_headers = (
        ('Created Timestamp', 'datetime'),
        'Conversation With',
        'Type',
        'Message Count',
        'Archived',
        'Marked Unread',
        'Draft Message',
        ('Muted Until', 'datetime'),
        'Thread ID',
    )
    return data_headers, data_list, source_path
