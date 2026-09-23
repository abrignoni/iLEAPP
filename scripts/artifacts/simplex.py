__artifacts_v2__ = {
    "simplexMessages": {
        "name": "SimpleX - Messages",
        "description": "Messages from the SimpleX Chat iOS SQLCipher database, decrypted with "
                       "the database passphrase held in the keychain.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "SimpleX",
        "notes": "SimpleX Chat keeps its data in a SQLCipher-encrypted database, "
                 "simplex_v1_chat.db, in the group.chat.simplex.app app group. The database "
                 "passphrase is stored in the iOS keychain (generic-password account "
                 "databasePassword, access group chat.simplex.app). The keychain is captured "
                 "separately from the file system, so supply it with --keychain or the keychain "
                 "field in the GUI; a keychain the extraction carries is picked up automatically. "
                 "The database is decrypted in memory to a temporary copy using the SQLCipher 4 "
                 "defaults (page size 4096, 256000 PBKDF2-HMAC-SHA512 iterations, SHA512 HMAC), "
                 "which authenticated every page on the tested sample. One row per row in "
                 "chat_items. Sent is the item_ts timestamp. Direction is Sent when item_sent is 1 "
                 "and Received when it is 0. Message is the item_text the app stored for display. "
                 "Chat is the contact's profile name for a direct chat, or the group's profile name "
                 "for a group chat. Sender is the other party's name on a received message (the "
                 "contact, or the group member for a group message), and blank on a sent message "
                 "because the sender is the account. Media renders an attached file when the app "
                 "kept it: attachments are stored unencrypted under app_files and linked to the "
                 "message through the files table. Deleted and Status are reported as stored. "
                 "Field mapping was done against a private sample; no sample data is recorded for "
                 "it.",
        "paths": ('*/AppGroup/*/simplex_v1_chat.db*',
                  '*/AppGroup/*/app_files/*',
                  '*/extra/KeychainDump/backup_keychain_v2.plist',
                  '*/keychain-backup.plist'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat ID",
                "conversationLabelColumn": "Chat",
                "timeColumn": "Sent",
                "directionColumn": "Direction",
                "directionSentValue": "Sent",
                "senderColumn": "Sender",
                "textColumn": "Message",
                "mediaColumn": "Media",
            }
        },
    },
    "simplexContacts": {
        "name": "SimpleX - Contacts",
        "description": "Contacts from the SimpleX Chat iOS SQLCipher database.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "SimpleX",
        "notes": "Read from the contacts table joined to contact_profiles in the decrypted "
                 "simplex_v1_chat.db (see the Messages artifact for how the database is decrypted "
                 "from the keychain passphrase). Display Name is the profile name, Local Alias is "
                 "the name the account set locally for the contact, Full Name is the profile's full "
                 "name. Created is created_at. Field mapping was done against a private sample; no "
                 "sample data is recorded for it.",
        "paths": ('*/AppGroup/*/simplex_v1_chat.db*',
                  '*/extra/KeychainDump/backup_keychain_v2.plist',
                  '*/keychain-backup.plist'),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "simplexGroups": {
        "name": "SimpleX - Group Members",
        "description": "Group members from the SimpleX Chat iOS SQLCipher database.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-22",
        "last_update_date": "2026-09-22",
        "requirements": "none",
        "category": "SimpleX",
        "notes": "Read from group_members joined to groups, group_profiles and contact_profiles in "
                 "the decrypted simplex_v1_chat.db (see the Messages artifact for how the database "
                 "is decrypted from the keychain passphrase). One row per group member. Group is "
                 "the group's profile name, Member is the member's profile name, Member Role and "
                 "Member Status are reported as stored. Field mapping was done against a private "
                 "sample; no sample data is recorded for it.",
        "paths": ('*/AppGroup/*/simplex_v1_chat.db*',
                  '*/extra/KeychainDump/backup_keychain_v2.plist',
                  '*/keychain-backup.plist'),
        "output_types": "standard",
        "artifact_icon": "users-group",
    },
}

import hashlib
import os
import sqlite3
import tempfile

from scripts.ios_keychain import get_app_secret, active_keychain_path
from scripts.sqlcipher_decrypt import decrypt_sqlcipher_db
from scripts.ilapfuncs import (artifact_processor, logfunc, check_in_media,
                               convert_ts_human_to_utc, get_sqlite_db_records)

# SimpleX keychain and SQLCipher settings.
SIMPLEX_ACCESS_GROUP = 'chat.simplex.app'
SIMPLEX_KEY_ACCOUNT = 'databasePassword'
# SimpleX links SQLCipher 4 and passes the passphrase as a string, so the file uses the
# SQLCipher 4 defaults: 4096 byte pages, 256000 PBKDF2-HMAC-SHA512 iterations, SHA512 HMAC.
SIMPLEX_PAGE_SIZE = 4096
SIMPLEX_KDF_ITER = 256000
SIMPLEX_HMAC = 'sha512'

_decrypted_cache = {}


def _decrypted_database(database_path):
    """Decrypt simplex_v1_chat.db once per run; return a path or None."""
    if database_path in _decrypted_cache:
        return _decrypted_cache[database_path]
    _decrypted_cache[database_path] = None  # do not retry for every artifact

    secret = get_app_secret(SIMPLEX_ACCESS_GROUP, SIMPLEX_KEY_ACCOUNT)
    if not secret:
        if active_keychain_path():
            logfunc('SimpleX: the keychain in use has no SimpleX database passphrase, '
                    'the database stays encrypted')
        else:
            logfunc('SimpleX: found an encrypted database but no keychain is available. '
                    'The extraction does not carry one, so supply it with --keychain or the '
                    'keychain field in the GUI.')
        return None

    try:
        passphrase = secret.decode('utf-8')
    except UnicodeDecodeError:
        logfunc('SimpleX: the keychain passphrase is not text, cannot use it as a key')
        return None

    digest = hashlib.sha1(database_path.encode('utf-8', 'replace')).hexdigest()[:12]
    output_dir = os.path.join(tempfile.gettempdir(), 'ileapp_simplex')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'simplex_{digest}.db')
    try:
        pages, verified = decrypt_sqlcipher_db(
            database_path, passphrase, output_path,
            page_size=SIMPLEX_PAGE_SIZE, kdf_iterations=SIMPLEX_KDF_ITER,
            hmac_algorithm=SIMPLEX_HMAC, kdf_algorithm=SIMPLEX_HMAC)
    except (OSError, ValueError, sqlite3.Error) as error:
        logfunc(f'SimpleX: decryption failed for {database_path}: {error}')
        return None

    if not pages or not verified:
        logfunc('SimpleX: the keychain passphrase did not authenticate the database. It may '
                'belong to a different device than this extraction.')
        return None
    if verified != pages:
        logfunc(f'SimpleX: {pages - verified} of {pages} decrypted pages failed HMAC '
                'verification, the recovered data may be incomplete')

    _decrypted_cache[database_path] = output_path
    return output_path


def _encrypted_databases(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        name = os.path.basename(file_found.replace('\\', '/'))
        if name == 'simplex_v1_chat.db':
            yield file_found


def _media_index(files_found):
    """Index the unencrypted app_files media by basename."""
    index = {}
    for file_found in files_found:
        file_found = str(file_found)
        norm = file_found.replace('\\', '/')
        if '/app_files/' in norm and not norm.endswith('/'):
            index.setdefault(os.path.basename(norm), file_found)
    return index


def _contact_names(plain_db):
    """contact_id -> best display name."""
    names = {}
    query = ('SELECT c.contact_id, p.local_alias, p.display_name '
             'FROM contacts c LEFT JOIN contact_profiles p '
             'ON p.contact_profile_id = c.contact_profile_id')
    for row in get_sqlite_db_records(plain_db, query):
        name = (row['local_alias'] or '').strip() or (row['display_name'] or '').strip()
        if row['contact_id'] is not None:
            names[row['contact_id']] = name
    return names


def _group_names(plain_db):
    query = ('SELECT g.group_id, p.display_name '
             'FROM groups g LEFT JOIN group_profiles p '
             'ON p.group_profile_id = g.group_profile_id')
    names = {}
    for row in get_sqlite_db_records(plain_db, query):
        if row['group_id'] is not None:
            names[row['group_id']] = (row['display_name'] or '').strip()
    return names


def _member_names(plain_db):
    query = ('SELECT m.group_member_id, m.local_display_name, p.display_name '
             'FROM group_members m LEFT JOIN contact_profiles p '
             'ON p.contact_profile_id = m.member_profile_id')
    names = {}
    for row in get_sqlite_db_records(plain_db, query):
        name = (row['display_name'] or '').strip() or (row['local_display_name'] or '').strip()
        if row['group_member_id'] is not None:
            names[row['group_member_id']] = name
    return names


def _files_by_item(plain_db):
    files = {}
    for row in get_sqlite_db_records(plain_db, 'SELECT chat_item_id, file_name FROM files'):
        if row['chat_item_id'] is not None and row['file_name']:
            files.setdefault(row['chat_item_id'], row['file_name'])
    return files


@artifact_processor
def simplexMessages(context):
    data_headers = (
        ('Sent', 'datetime'),
        'Direction',
        'Sender',
        'Chat',
        'Message',
        ('Media', 'media'),
        'Chat ID',
        'Message Status',
        'Deleted',
        'Source File',
    )
    data_list = []
    source_paths = []
    files_found = [str(f) for f in context.get_files_found()]
    media_index = _media_index(files_found)

    for db_path in _encrypted_databases(files_found):
        plain_db = _decrypted_database(db_path)
        if not plain_db:
            continue
        contact_names = _contact_names(plain_db)
        group_names = _group_names(plain_db)
        member_names = _member_names(plain_db)
        files_map = _files_by_item(plain_db)

        query = ('SELECT chat_item_id, contact_id, group_id, group_member_id, item_sent, '
                 'item_ts, item_text, item_status, item_deleted FROM chat_items')
        rows = 0
        for row in get_sqlite_db_records(plain_db, query):
            group_id = row['group_id']
            contact_id = row['contact_id']
            if group_id is not None:
                chat = group_names.get(group_id, '')
                chat_id = f'group:{group_id}'
            else:
                chat = contact_names.get(contact_id, '')
                chat_id = f'contact:{contact_id}'

            if row['item_sent'] == 1:
                direction = 'Sent'
                sender = ''
            else:
                direction = 'Received'
                if group_id is not None:
                    sender = member_names.get(row['group_member_id'], '')
                else:
                    sender = contact_names.get(contact_id, '')

            media = ''
            file_name = files_map.get(row['chat_item_id'])
            if file_name and file_name in media_index:
                media = check_in_media(media_index[file_name], file_name) or ''

            sent = ''
            if row['item_ts']:
                try:
                    sent = convert_ts_human_to_utc(row['item_ts'])
                except (ValueError, TypeError):
                    sent = ''

            data_list.append((
                sent,
                direction,
                sender,
                chat,
                row['item_text'] or '',
                media,
                chat_id,
                row['item_status'] or '',
                'Yes' if row['item_deleted'] else '',
                context.get_relative_path(db_path),
            ))
            rows += 1
        if rows:
            source_paths.append(db_path)

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def simplexContacts(context):
    data_headers = (
        ('Created', 'datetime'),
        'Display Name',
        'Local Alias',
        'Full Name',
        'Contact ID',
        'Source File',
    )
    data_list = []
    source_paths = []
    files_found = [str(f) for f in context.get_files_found()]

    for db_path in _encrypted_databases(files_found):
        plain_db = _decrypted_database(db_path)
        if not plain_db:
            continue
        query = ('SELECT c.contact_id, c.created_at, p.display_name, p.local_alias, p.full_name '
                 'FROM contacts c LEFT JOIN contact_profiles p '
                 'ON p.contact_profile_id = c.contact_profile_id')
        rows = 0
        for row in get_sqlite_db_records(plain_db, query):
            created = ''
            if row['created_at']:
                try:
                    created = convert_ts_human_to_utc(row['created_at'])
                except (ValueError, TypeError):
                    created = ''
            data_list.append((
                created,
                row['display_name'] or '',
                row['local_alias'] or '',
                row['full_name'] or '',
                row['contact_id'] if row['contact_id'] is not None else '',
                context.get_relative_path(db_path),
            ))
            rows += 1
        if rows:
            source_paths.append(db_path)

    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def simplexGroups(context):
    data_headers = (
        'Group',
        'Member',
        'Member Role',
        'Member Status',
        'Group ID',
        'Source File',
    )
    data_list = []
    source_paths = []
    files_found = [str(f) for f in context.get_files_found()]

    for db_path in _encrypted_databases(files_found):
        plain_db = _decrypted_database(db_path)
        if not plain_db:
            continue
        query = ('SELECT gp.display_name AS group_name, m.group_id, m.member_role, '
                 'm.member_status, m.local_display_name, p.display_name AS member_name '
                 'FROM group_members m '
                 'LEFT JOIN groups g ON g.group_id = m.group_id '
                 'LEFT JOIN group_profiles gp ON gp.group_profile_id = g.group_profile_id '
                 'LEFT JOIN contact_profiles p ON p.contact_profile_id = m.member_profile_id')
        rows = 0
        for row in get_sqlite_db_records(plain_db, query):
            member = (row['member_name'] or '').strip() or (row['local_display_name'] or '').strip()
            data_list.append((
                row['group_name'] or '',
                member,
                row['member_role'] or '',
                row['member_status'] or '',
                row['group_id'] if row['group_id'] is not None else '',
                context.get_relative_path(db_path),
            ))
            rows += 1
        if rows:
            source_paths.append(db_path)

    return data_headers, data_list, '\n'.join(source_paths)
