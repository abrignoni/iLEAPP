__artifacts_v2__ = {
    "get_signalIOSMessages": {
        "name": "Signal - Messages",
        "description": "Parses messages from the encrypted Signal database, including direction, author, conversation and body.",
        "author": "Alexis Brignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Signal",
        "notes": "Signal encrypts its database with a key held in the iOS keychain. The keychain is captured separately from the file system extraction, so supply it with --keychain or the keychain field in the GUI. Reference: Signal-iOS, 'SDSRecordType.swift (incomingMessage = 19, outgoingMessage = 21)', https://github.com/signalapp/Signal-iOS/blob/main/SignalServiceKit/Storage/Database/SDSRecordType.swift Reference: SQLCipher documentation, 'cipher_plaintext_header_size', https://www.zetetic.net/sqlcipher/sqlcipher-api/#cipher_plaintext_header_size",
        "paths": ('*/AppGroup/*/grdb*/signal.sqlite*',
                  # attachments are stored in the clear, so they only need locating
                  '*/AppGroup/*/Attachments/*',
                  # so a keychain the extraction carries is available to decrypt with
                  '*/extra/KeychainDump/backup_keychain_v2.plist',
                  '*/keychain-backup.plist'),
        "output_types": "standard",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "conversationLabelColumn": "Conversation With",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Author",
                "mediaColumn": "Attachments",
            }
        },
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
        "paths": ('*/AppGroup/*/grdb*/signal.sqlite*',
                  # so a keychain the extraction carries is available to decrypt with
                  '*/extra/KeychainDump/backup_keychain_v2.plist',
                  '*/keychain-backup.plist'),
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
        "paths": ('*/AppGroup/*/grdb*/signal.sqlite*',
                  # so a keychain the extraction carries is available to decrypt with
                  '*/extra/KeychainDump/backup_keychain_v2.plist',
                  '*/keychain-backup.plist'),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
}

import hashlib
import os
import sqlite3
import tempfile

from scripts.ios_keychain import get_app_secret, active_keychain_path
from scripts.sqlcipher_decrypt import decrypt_sqlcipher_db
from scripts.ilapfuncs import (artifact_processor, logfunc, convert_unix_ts_to_utc,
                               check_in_media)

SIGNAL_ACCESS_GROUP = 'org.whispersystems.signal'
KEY_SPEC_ACCOUNT = 'GRDBDatabaseCipherKeySpec'
# The keychain entry is a 32 byte key followed by the 16 byte salt
KEY_SPEC_LENGTH = 48

# Signal for iOS keeps the first 32 bytes readable so the file still identifies
# as SQLite; the application must store the salt externally, and Signal keeps
# it in the keychain entry above. It also uses the SQLCipher 4 defaults of
# SHA512 for the HMAC and the KDF.
PLAINTEXT_HEADER_SIZE = 32
SIGNAL_HMAC = 'sha512'

# SDSRecordType values seen in model_TSInteraction. Incoming rows carry an
# author; outgoing rows do not, because the author is the signed-in account.
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
        if active_keychain_path():
            logfunc('Signal: the keychain in use has no Signal database key, '
                    'the database stays encrypted')
        else:
            logfunc('Signal: found an encrypted database but no keychain is available. '
                    'The extraction does not carry one, so supply it with --keychain or the '
                    'keychain field in the GUI.')
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


def _attachment_files(context):
    """Paths of the Signal attachment files present in the extraction."""
    try:
        seeker = context.get_seeker()
    except Exception:  # pylint: disable=broad-except
        return []
    return [str(path) for path in seeker.search('*/AppGroup/*/Attachments/*')
            if os.path.isfile(str(path))]


def _match_attachment(files, relative_path):
    """Find the extracted file for a localRelativeFilePath recorded in the database.

    The database stores the path relative to the Attachments folder, sometimes
    inside a per-attachment subfolder, so match on that whole suffix rather than
    on the file name alone, which is not guaranteed to be unique.
    """
    if not relative_path:
        return None
    suffix = '/Attachments/' + str(relative_path).replace('\\', '/').lstrip('/')
    for candidate in files:
        if candidate.replace('\\', '/').endswith(suffix):
            return candidate
    return None


def _attachments_by_message(context, connection):
    """Check in each attachment and group the media references by message.

    Unlike Android, Signal for iOS stores attachments in the clear, so they only
    need locating rather than decrypting.
    """
    references = {}
    columns = _table_columns(connection, 'model_TSAttachment')
    if not {'localRelativeFilePath', 'albumMessageId'} <= columns:
        return references

    files = _attachment_files(context)
    if not files:
        return references

    query = (f"SELECT {_select_list(columns, 'model_TSAttachment', ['albumMessageId', 'localRelativeFilePath', 'sourceFilename', 'contentType'])} "
             "FROM model_TSAttachment WHERE model_TSAttachment.albumMessageId IS NOT NULL")

    checked_in = 0
    for message_id, relative_path, source_name, content_type in connection.execute(query):
        path = _match_attachment(files, relative_path)
        if not path:
            continue
        try:
            reference = check_in_media(path, name=source_name or os.path.basename(path),
                                       force_type=content_type)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Signal: could not check in {os.path.basename(path)}: {error}')
            continue
        if reference:
            references.setdefault(message_id, []).append(reference)
            checked_in += 1

    if checked_in:
        logfunc(f'Signal: linked {checked_in} attachment'
                f'{"s" if checked_in > 1 else ""} to messages')
    return references


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
        attachments_by_message = _attachments_by_message(context, connection)
        cursor = connection.cursor()
        cursor.execute(f'''
        SELECT
            {_select_list(columns, 'model_TSInteraction',
                          ['timestamp', 'receivedAtTimestamp', 'recordType', 'body',
                           'authorPhoneNumber', 'authorUUID', 'uniqueThreadId', 'read',
                           'isVoiceMessage', 'isViewOnceMessage', 'wasRemotelyDeleted',
                           'expiresInSeconds', 'serverTimestamp', 'attachmentIds', 'id',
                           'uniqueId'])},
            model_TSThread.contactPhoneNumber, model_TSThread.contactUUID
        FROM model_TSInteraction
        LEFT JOIN model_TSThread ON model_TSInteraction.uniqueThreadId = model_TSThread.uniqueId
        ORDER BY model_TSInteraction.timestamp
        ''')
        for row in cursor:
            direction = MESSAGE_DIRECTIONS.get(row[2], f'Other (record type {row[2]})')
            # Outgoing rows have no author: the signed-in account sent them
            author = row[4] or row[5] or ('Signed-in account' if row[2] == RECORD_TYPE_OUTGOING else '')
            # A message can carry several attachments, so the media cell takes a list
            attachments = attachments_by_message.get(row[15], [])
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                convert_unix_ts_to_utc(row[1]),
                direction,
                author,
                row[16] or row[17] or '',
                row[3] or '',
                attachments,
                len(attachments),
                'Yes' if row[7] else 'No',
                'Yes' if row[8] else 'No',
                'Yes' if row[9] else 'No',
                'Yes' if row[10] else 'No',
                row[11] or '',
                convert_unix_ts_to_utc(row[12]) if row[12] else '',
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
        ('Attachments', 'media'),
        'Attachment Count',
        'Read',
        'Voice Message',
        'View Once',
        'Remotely Deleted',
        'Disappearing Timer (Seconds)',
        ('Server Timestamp', 'datetime'),
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
