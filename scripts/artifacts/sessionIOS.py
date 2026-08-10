__artifacts_v2__ = {
    "session_messages": {
        "name": "Session - Messages",
        "description": "Parses messages from the encrypted Session (Oxen) database, including "
                       "direction, author, conversation and body.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-10",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "Session",
        "notes": "Session for iOS keeps its database key in the iOS keychain, which is captured "
                 "separately from the file system extraction, so supply it with --keychain or "
                 "the keychain field in the GUI. The database is SQLCipher with a 32 byte "
                 "plaintext header (the file still identifies as SQLite) and the salt held in "
                 "the keychain entry, decrypted here with the shared pure-python reader.\n"
                 "Direction is taken from the interaction variant: 0 is an outgoing message and "
                 "1 an incoming one, which the data bears out (variant 0 rows are authored by "
                 "the local account and variant 1 rows by the remote party). Other variants are "
                 "Session's info and control messages, which carry no user body and are reported "
                 "with the variant shown. The author and conversation names are the display "
                 "name or nickname from the profile table, falling back to the Session ID "
                 "(the account's public key) where no profile is stored.\n"
                 "Reference: Session-iOS, 'Interaction.Variant (standardOutgoing = 0, "
                 "standardIncoming = 1)', "
                 "https://github.com/oxen-io/session-ios. "
                 "Reference: SQLCipher documentation, 'cipher_plaintext_header_size', "
                 "https://www.zetetic.net/sqlcipher/sqlcipher-api/#cipher_plaintext_header_size",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/database/Session.sqlite*',
                  # Session stores its attachments in the clear, so they only need locating.
                  '*/AppGroup/*/Attachments/*',
                  # The keychain is captured separately from the file system, so a keychain
                  # the extraction carries is available to decrypt with.
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
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 51 rows",
            "hickman_ios15": "iOS 15.0.2 | 24 rows",
            "dexter_ios18": "iOS 18.3.2 | 10 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows (no keychain in the extraction)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (no keychain in the extraction)",
        },
    },
    "session_contacts": {
        "name": "Session - Contacts",
        "description": "Parses the contacts and their profile names from the encrypted Session "
                       "database.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-10",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "Session",
        "notes": "Requires the keychain, supplied with --keychain or the keychain field in the "
                 "GUI. Session ID is the contact's public key. Name and Nickname come from the "
                 "profile table; the approval and block flags come from the contact table and "
                 "are reported as stored.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/database/Session.sqlite*',
                  '*/extra/KeychainDump/backup_keychain_v2.plist',
                  '*/keychain-backup.plist'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "hickman_ios15": "iOS 15.0.2 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows (no keychain in the extraction)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (no keychain in the extraction)",
        },
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

# Session (Oxen) stores its GRDB database key under its own keychain access
# group; the entry is a 32 byte key followed by a 16 byte salt, the same shape
# Signal uses, because both are GRDB SQLCipher apps.
SESSION_ACCESS_GROUP = 'com.loki-project.loki-messenger'
KEY_SPEC_ACCOUNT = 'GRDBDatabaseCipherKeySpec'
KEY_SPEC_LENGTH = 48

# Session keeps the first 32 bytes of the file readable so it still identifies
# as SQLite, and uses the SQLCipher 4 defaults of SHA512 for the HMAC and KDF.
PLAINTEXT_HEADER_SIZE = 32
SESSION_HMAC = 'sha512'

# interaction.variant values that carry a user message. Everything else is an
# info / control message with no body.
VARIANT_OUTGOING = 0
VARIANT_INCOMING = 1
MESSAGE_DIRECTIONS = {VARIANT_OUTGOING: 'Outgoing', VARIANT_INCOMING: 'Incoming'}

_decrypted_cache = {}


def _decrypted_database(database_path):
    """Decrypt the Session database once per run; return a path or None."""
    if database_path in _decrypted_cache:
        return _decrypted_cache[database_path]
    _decrypted_cache[database_path] = None  # do not retry for every artifact

    key_spec = get_app_secret(SESSION_ACCESS_GROUP, KEY_SPEC_ACCOUNT,
                              expected_length=KEY_SPEC_LENGTH)
    if not key_spec:
        if active_keychain_path():
            logfunc('Session: the keychain in use has no Session database key, '
                    'the database stays encrypted')
        else:
            logfunc('Session: found an encrypted database but no keychain is available. '
                    'The extraction does not carry one, so supply it with --keychain or the '
                    'keychain field in the GUI.')
        return None

    digest = hashlib.sha1(database_path.encode('utf-8', 'replace')).hexdigest()[:12]
    output_path = os.path.join(tempfile.gettempdir(), 'ileapp_session', f'session_{digest}.db')
    try:
        pages, verified = decrypt_sqlcipher_db(
            database_path, key_spec[:32], output_path, raw_key=True,
            external_salt=key_spec[32:KEY_SPEC_LENGTH],
            plaintext_header_size=PLAINTEXT_HEADER_SIZE,
            hmac_algorithm=SESSION_HMAC, kdf_algorithm=SESSION_HMAC)
    except Exception as error:  # pylint: disable=broad-except
        logfunc(f'Session: decryption failed for {database_path}: {error}')
        return None

    if not pages or not verified:
        logfunc('Session: the keychain key did not authenticate the database. It may belong '
                'to a different device than this extraction.')
        return None
    if verified != pages:
        logfunc(f'Session: {pages - verified} of {pages} decrypted pages failed HMAC '
                'verification, the recovered data may be incomplete')

    _decrypted_cache[database_path] = output_path
    return output_path


def _open_session_databases(context):
    """Yield (connection, source_path) for each decryptable Session database."""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.basename(file_found) != 'Session.sqlite':
            continue
        decrypted = _decrypted_database(file_found)
        if not decrypted:
            continue
        yield sqlite3.connect(decrypted), file_found


def _attachment_files(context):
    """Paths of the Session attachment files present in the extraction."""
    try:
        seeker = context.get_seeker()
    except Exception:  # pylint: disable=broad-except
        return []
    return [str(path) for path in seeker.search('*/AppGroup/*/Attachments/*')
            if os.path.isfile(str(path))]


def _attachments_by_message(context, connection):
    """Check in each attachment and group the media references by message id.

    Session stores attachments in the clear under the app group's Attachments
    folder, named by the attachment id with the content type's extension, so
    each row's file is located by matching that id in the file name.
    """
    files = _attachment_files(context)
    by_id = {}
    for path in files:
        by_id.setdefault(os.path.basename(path).split('.')[0], path)

    attachments = {}
    checked_in = 0
    try:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT ia.interactionId, a.id, a.sourceFilename
            FROM interactionAttachment ia
            LEFT JOIN attachment a ON a.id = ia.attachmentId
            ORDER BY ia.interactionId, ia.albumIndex
        ''')
        rows = cursor.fetchall()
    except sqlite3.Error:
        return attachments

    for interaction_id, attachment_id, source_name in rows:
        path = by_id.get(attachment_id)
        if not path:
            continue
        reference = check_in_media(path, name=source_name or os.path.basename(path))
        if reference:
            attachments.setdefault(interaction_id, []).append(reference)
            checked_in += 1

    if checked_in:
        logfunc(f'Session: linked {checked_in} attachment'
                f'{"" if checked_in == 1 else "s"} to messages')
    return attachments


@artifact_processor
def session_messages(context):
    data_list = []
    source_path = ''
    # interaction.threadId is the conversation's Session ID (a public key), which
    # joins to thread.id. On an outgoing message Session stores the recipient in
    # authorId rather than the sender, the same shape Signal uses, so the author
    # is only meaningful on incoming rows and is left blank on outgoing ones.
    query = '''
        SELECT
            i.id,
            i.threadId,
            COALESCE(cp.nickname, cp.name, t.id) AS conversation,
            i.variant,
            COALESCE(ap.nickname, ap.name, i.authorId) AS author,
            i.body,
            i.timestampMs,
            i.receivedAtTimestampMs,
            CASE i.wasRead WHEN 1 THEN 'Yes' WHEN 0 THEN 'No' END AS was_read,
            i.serverHash
        FROM interaction i
        LEFT JOIN thread t ON t.id = i.threadId
        LEFT JOIN profile cp ON cp.id = t.id
        LEFT JOIN profile ap ON ap.id = i.authorId
        ORDER BY i.timestampMs
    '''
    for connection, file_found in _open_session_databases(context):
        source_path = file_found
        attachments_by_message = _attachments_by_message(context, connection)
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
        except sqlite3.Error as error:
            logfunc(f'Session: could not read messages from {file_found}: {error}')
            rows = []
        finally:
            connection.close()

        for (interaction_id, thread_id, conversation, variant, author, body,
             timestamp_ms, received_ms, was_read, server_hash) in rows:
            direction = MESSAGE_DIRECTIONS.get(variant, f'Info / Control ({variant})')
            # On an outgoing message authorId is the recipient, not the sender,
            # so the author is only reported on incoming messages.
            reported_author = author if variant == VARIANT_INCOMING else ''
            media = ''.join(attachments_by_message.get(interaction_id, []))
            data_list.append((
                convert_unix_ts_to_utc(timestamp_ms / 1000) if timestamp_ms else '',
                convert_unix_ts_to_utc(received_ms / 1000) if received_ms else '',
                direction,
                reported_author,
                conversation,
                body,
                media,
                was_read,
                thread_id,
                server_hash,
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Received Timestamp', 'datetime'),
        'Direction',
        'Author',
        'Conversation With',
        'Message',
        ('Attachments', 'media'),
        'Was Read',
        'Thread ID',
        'Server Hash',
    )
    return data_headers, data_list, source_path


@artifact_processor
def session_contacts(context):
    data_list = []
    source_path = ''
    query = '''
        SELECT
            c.id,
            p.name,
            p.nickname,
            CASE c.isApproved WHEN 1 THEN 'Yes' WHEN 0 THEN 'No' END,
            CASE c.didApproveMe WHEN 1 THEN 'Yes' WHEN 0 THEN 'No' END,
            CASE c.isBlocked WHEN 1 THEN 'Yes' WHEN 0 THEN 'No' END,
            c.lastKnownClientVersion
        FROM contact c
        LEFT JOIN profile p ON p.id = c.id
        ORDER BY p.name
    '''
    for connection, file_found in _open_session_databases(context):
        source_path = file_found
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
        except sqlite3.Error as error:
            logfunc(f'Session: could not read contacts from {file_found}: {error}')
            rows = []
        finally:
            connection.close()
        data_list.extend(rows)

    data_headers = (
        'Session ID',
        'Name',
        'Nickname',
        'Approved',
        'Approved Me',
        'Blocked',
        'Last Known Client Version',
    )
    return data_headers, data_list, source_path
