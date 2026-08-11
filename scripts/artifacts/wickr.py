__artifacts_v2__ = {
    "wickr_messages": {
        "name": "Wickr - Messages (Metadata Only)",
        "description": "NO MESSAGE CONTENT. Wickr stores message text encrypted and it is not "
                       "recovered here. This artifact reports message metadata only: the "
                       "timestamp, the conversation, the sending user, the read and delivery "
                       "timestamps, the stored type values and any attached file",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Wickr",
        "notes": "Read from ZWICKR_MESSAGE in wickrLocal.sqlite, the Core Data store in the Wickr "
                 "app group container. Every text-bearing column in this database is stored as an "
                 "encrypted blob, so this artifact reports message metadata only; ZBODY is not "
                 "decoded and no message content is recovered here. Conversation and sender are "
                 "resolved through ZCONVO and ZUSERSENDER; users are identified by the stored "
                 "ZUSERIDHASH and ZUSERALIASHASH values, which are the only identifiers held in "
                 "the clear. Message Type and Primary Type are the stored ZFULLTYPE and "
                 "ZPRIMARYTYPE integers; the app binary declares a WickrMessageType enum but does "
                 "not carry its case names, so the values ship unlabelled with one exception. "
                 "ZFULLTYPE 6000 is labelled File Transfer: on the tested image the set of "
                 "messages carrying a linked file and the set with ZFULLTYPE 6000 are identical "
                 "and no other value appears among file-linked messages, and the same value is "
                 "reported independently by Josh Hickman, 'Wickr - Alright, We'll Call It A "
                 "Draw', thebinaryhick.blog, 2019-08-23. The other values present in this table "
                 "on the tested image (1000, 4001, 4007, 7000, 8000) have no such support and "
                 "are reported as stored. The app's logs carry two further type values, 4006 and "
                 "9000, which do not appear in this table at all; see the Wickr - App Log "
                 "Message Events artifact.\n"
                 "Timestamps are Cocoa Core Data epoch. Where a ZMSGID here also appears in the "
                 "app's own plaintext logs, the Cocoa timestamp and the independently logged "
                 "arrival time agree to within a second, which cross-validates both readings.",
        "paths": ('*/wickrLocal.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "iphone11_ios17": "iOS 17 | AWS Wickr (com.wickr.pro.prod) | 44 rows",
            "felix23_ios16": "iOS 16 | Wickr Me (com.mywickr.wickr) | 0 rows",
        },
    },
    "wickr_conversations": {
        "name": "Wickr - Conversations (No Names)",
        "description": "NO CONVERSATION NAMES. Wickr stores room names and descriptions encrypted "
                       "and they are not recovered here. This artifact reports the group "
                       "identifier, the kind of conversation, the last message and sync "
                       "timestamps, the member list and the room administrators",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Wickr",
        "notes": "Read from ZSECEX_CONVO in wickrLocal.sqlite. The Kind column is the Core Data "
                 "entity name looked up from the Z_PRIMARYKEY table in the same file, which maps "
                 "Z_ENT 5 to Secex_Convo and Z_ENT 6 to Secex_Secure_Room in the tested images. "
                 "Those entity numbers are model-version specific and differ between the two "
                 "images tested, so they are resolved from Z_PRIMARYKEY at run time rather than "
                 "hardcoded. The member and administrator join tables are named after those same "
                 "entity numbers, so they are located at run time by decoding their column names "
                 "through Z_PRIMARYKEY rather than by name; the file-to-message join is Z_13MSG "
                 "on both images tested but is reported as Z_11MSG on a 2019 app version. "
                 "Members and administrators are reported as the users' stored ZUSERIDHASH "
                 "values. Conversation "
                 "names and descriptions are stored as encrypted blobs and are not decoded.",
        "paths": ('*/wickrLocal.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "iphone11_ios17": "iOS 17 | AWS Wickr (com.wickr.pro.prod) | 6 rows",
            "felix23_ios16": "iOS 16 | Wickr Me (com.mywickr.wickr) | 1 row",
        },
    },
    "wickr_users": {
        "name": "Wickr - Users (Hashes Only)",
        "description": "NO USER NAMES. Wickr stores user names and aliases encrypted and they are "
                       "not recovered here. Users are identified only by the stored hash values. "
                       "This artifact reports those hashes, the network membership flags and the "
                       "last activity timestamp",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Wickr",
        "notes": "Read from ZSECEX_USER in wickrLocal.sqlite. ZUSERNAME, ZUSERALIAS, ZUSERID and "
                 "ZUSERIMAGE are stored as encrypted blobs and are not decoded; the ZUSERIDHASH "
                 "and ZUSERALIASHASH columns are stored in the clear and are reported as stored. "
                 "The Source column is the stored ZSOURCE string, observed as 'ME' on the Wickr Me "
                 "image and 'PRO' on the AWS Wickr image. Flag columns are reported as stored.",
        "paths": ('*/wickrLocal.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "iphone11_ios17": "iOS 17 | AWS Wickr (com.wickr.pro.prod) | 4 rows",
            "felix23_ios16": "iOS 16 | Wickr Me (com.mywickr.wickr) | 2 rows",
        },
    },
    "wickr_files": {
        "name": "Wickr - Files (Metadata Only)",
        "description": "NO FILE NAMES OR CONTENT. Wickr stores file titles and mime types "
                       "encrypted, and the attachment files themselves are encrypted on disk. "
                       "This artifact reports the file GUID, the stored status value and the "
                       "message each file is linked to",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Wickr",
        "notes": "Read from ZWICKR_FILE in wickrLocal.sqlite, linked to messages through the "
                 "Core Data join table for the file and message entities. That table is named "
                 "after the entity numbers, so it is Z_13MSG on both images tested and Z_11MSG "
                 "on a 2019 app version; it is located at run time through Z_PRIMARYKEY rather "
                 "than by name. ZTITLE and ZMIMETYPE are stored as encrypted blobs and are "
                 "not decoded. On the tested image each ZGUID matches the name of a file held in "
                 "the app group container; those files are encrypted at rest, so they are reported "
                 "by name and are not checked in as media. Status is the stored ZSTATUS integer.",
        "paths": ('*/wickrLocal.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "iphone11_ios17": "iOS 17 | AWS Wickr (com.wickr.pro.prod) | 4 rows",
            "felix23_ios16": "iOS 16 | Wickr Me (com.mywickr.wickr) | 0 rows",
        },
    },
    "wickr_account": {
        "name": "Wickr - Account Settings",
        "description": "The Wickr account row, with the security group identifier, the notification "
                       "and lock settings and the stored secure shredder values",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Wickr",
        "notes": "Read from ZSECEX_ACCOUNT in wickrLocal.sqlite. The account user name, keys and "
                 "configuration are stored as encrypted blobs and are not decoded; this artifact "
                 "reports the columns held in the clear, as stored. ZAFENABLE and ZAFSPEED are "
                 "reported under their stored names. Alongside them the app container holds "
                 "tmp/aforensics/random.af0 and random.af1, and the app binary carries the class "
                 "names ForensicsManager, AntiForencisOperation and ManualForensicsSweepOperation; "
                 "the correspondence is noted, but what the feature does to stored data is not "
                 "established here. Column availability differs between app versions, so optional "
                 "columns are checked before they are selected.",
        "paths": ('*/wickrLocal.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "iphone11_ios17": "iOS 17 | AWS Wickr (com.wickr.pro.prod) | 1 row",
            "felix23_ios16": "iOS 16 | Wickr Me (com.mywickr.wickr) | 1 row",
        },
    },
    "wickr_devices": {
        "name": "Wickr - Devices",
        "description": "Per-device records from the Wickr local store, giving the stored device "
                       "identifier hash and the user each one belongs to",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Wickr",
        "notes": "Read from ZSECEX_APP in wickrLocal.sqlite, which the Z_PRIMARYKEY table in the "
                 "same file names Secex_App. Rows are joined to ZSECEX_USER through ZUSER. "
                 "ZAPPIDHASH is stored in the clear and is reported as stored; ZSAPPID, ZPUBS and "
                 "ZPUBSIG are encrypted blobs and are not decoded. A row count above one for a "
                 "given user reflects the number of these records present in this database.",
        "paths": ('*/wickrLocal.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "iphone11_ios17": "iOS 17 | AWS Wickr (com.wickr.pro.prod) | 49 rows",
            "felix23_ios16": "iOS 16 | Wickr Me (com.mywickr.wickr) | 2 rows",
        },
    },
    "wickr_recent_searches": {
        "name": "Wickr - Recent Searches",
        "description": "Entries held in the Wickr recent search table, with the stored query text "
                       "and its timestamp",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Wickr",
        "notes": "Read from ZRECENT_SEARCH in wickrLocal.sqlite. ZSEARCHQUERY is one of the few "
                 "columns in this database held in the clear rather than as an encrypted blob, so "
                 "the query text is reported as stored. The timestamp is Cocoa Core Data epoch. "
                 "The table was present in both images tested and populated in one of them.",
        "paths": ('*/wickrLocal.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "felix23_ios16": "iOS 16 | Wickr Me (com.mywickr.wickr) | 1 row",
            "iphone11_ios17": "iOS 17 | AWS Wickr (com.wickr.pro.prod) | 0 rows",
        },
    },
    "wickr_keychain_account": {
        "name": "Wickr - Account Identity (Keychain)",
        "description": "The Wickr account identity held in the iOS keychain, including the user "
                       "name in the clear, the device identifier and the server the app was "
                       "registered against. Needs a keychain, supplied or carried by the "
                       "extraction",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Wickr",
        "notes": "Read from the keychain items in Wickr's access group, which on the tested image "
                 "is the team identifier W8RC3R952A. These are the only Wickr strings recovered in "
                 "the clear anywhere: the database itself stores every text-bearing column as an "
                 "encrypted blob, so without a keychain the user is visible only as the hash in "
                 "the Wickr - Users artifact. The items reported are the wickrusername and userID "
                 "accounts, the devid account and the baseURL account. All four were stored with "
                 "the accessible-after-first-unlock-this-device-only protection class on the "
                 "tested image. Nothing here decrypts the message database; the storage key is "
                 "not among these items. Requires a keychain, so this artifact is empty when none "
                 "is supplied and none is found in the extraction.",
        "paths": ('*/wickrLocal.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "iphone11_ios17": "iOS 17 | AWS Wickr, with the extraction's own keychain | 4 rows",
        },
    },
    "wickr_app_log": {
        "name": "Wickr - App Log Message Events",
        "description": "Incoming message events recorded in the Wickr application logs, with the "
                       "log timestamp, the message and conversation identifiers, the sending user "
                       "hash and the stored message type",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Wickr",
        "notes": "Read from the plaintext application logs the app writes under its Logs "
                 "directories. The parsed lines are the notification payloads logged as "
                 "'Payload: {\"messageId\"...}' and the 'Download Message with Type' lines, both "
                 "of which carry identifiers in the clear. These logs are rolling files, so the "
                 "events present depend on what had not yet been rotated away. Log line "
                 "timestamps are recorded by the app without a zone and are reported as written.\n"
                 "Where an identifier here also appears in ZWICKR_MESSAGE, the log arrival time "
                 "and the database timestamp agree to within a second, which is what "
                 "cross-validates the database timestamp reading.\n"
                 "Most of them do not appear there. On the tested image the logs name 69 distinct "
                 "message identifiers and 48 of those have no row in ZWICKR_MESSAGE, so this "
                 "artifact reports the arrival of messages the message store no longer holds, "
                 "together with the conversation, the sending user hash and the stored type for "
                 "each. Those 48 include the only occurrences of type values 4006 and 9000 "
                 "anywhere in the data. Why a logged message has no row is not established here: "
                 "a rolling log covering a longer period than the store retains would produce "
                 "this, and so would removal of the rows, and the records do not distinguish "
                 "them.",
        "paths": ('*/Logs/com.wickr*.log', '*/Logs/com.mywickr*.log'),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "iphone11_ios17": "iOS 17 | AWS Wickr (com.wickr.pro.prod) | 120 rows from 9 log files",
            "felix23_ios16": "iOS 16 | Wickr Me (com.mywickr.wickr) | 0 rows from 5 log files",
        },
    },
}

import json
import re

from scripts.ios_keychain import active_keychain_path, find_keychain_secrets
from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc,
                               convert_unix_ts_to_utc, does_column_exist_in_db,
                               does_table_exist_in_db, get_sqlite_db_records, null_absent_columns, logfunc)

PAYLOAD_RE = re.compile(r'^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}):\d+\s+Payload: (\{"messageId".*\})\s*$')
DOWNLOAD_RE = re.compile(r'^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}):\d+\s+Download Message with Type: (\d+), '
                         r'ConvoID: (?:Optional\("([^"]*)"\)|nil), MsgID: (\S+)')


def _db_paths(files_found):
    """wickrLocal.sqlite lives in the app group container; Wickr Me and Wickr Pro
    can both be installed, so return every store rather than the first."""
    paths = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('wickrLocal.sqlite'):
            paths.append(file_found)
    return paths


def _entity_names(path):
    """Z_PRIMARYKEY maps Z_ENT to the Core Data entity name. The numbering is
    model-version specific and shifts between app versions, so read it per file."""
    names = {}
    if not does_table_exist_in_db(path, 'Z_PRIMARYKEY'):
        return names
    for record in get_sqlite_db_records(path, 'SELECT Z_ENT, Z_NAME FROM Z_PRIMARYKEY'):
        names[record[0]] = record[1]
    return names


def _find_join(path, entities, entity_a, entity_b):
    """Core Data names a many-to-many join table and its columns after the entity
    numbers, so the same relationship is Z_11MSG on one app version and Z_13MSG on
    another. Resolve the table and its two columns by decoding the column names
    through Z_PRIMARYKEY instead of hardcoding either name.

    Returns (table, column_for_entity_a, column_for_entity_b) or None."""
    query = ("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Z\\_%' "
             "ESCAPE '\\' AND name NOT IN ('Z_PRIMARYKEY','Z_METADATA','Z_MODELCACHE')")
    for record in get_sqlite_db_records(path, null_absent_columns(path, query)):
        table = record[0]
        columns = {}
        for column in get_sqlite_db_records(path, f'PRAGMA table_info("{table}")'):
            match = re.match(r'Z_(\d+)(.+)', column[1])
            if match:
                columns[entities.get(int(match.group(1)))] = column[1]
        if entity_a in columns and entity_b in columns:
            return table, columns[entity_a], columns[entity_b]
    return None


def _cocoa(value):
    if value in (None, '', 0):
        return ''
    return convert_cocoa_core_data_ts_to_utc(value)


def _unix(value):
    if value in (None, '', 0):
        return ''
    return convert_unix_ts_to_utc(value)


def _optional(path, table, column, default='NULL'):
    """Wickr adds columns between app versions; select them only where present."""
    return column if does_column_exist_in_db(path, table, column) else default


def _text(value):
    """Columns absent on older app versions come back as None; report them empty."""
    return '' if value is None else value


def _message_type(value):
    """ZFULLTYPE is otherwise undocumented, so only the one value with support is
    labelled and the rest ship as the stored integer. See the artifact notes."""
    if value == 6000:
        return '6000 (File Transfer)'
    return value


def _user_hashes(path):
    hashes = {}
    for record in get_sqlite_db_records(path, 'SELECT Z_PK, ZUSERIDHASH FROM ZSECEX_USER'):
        hashes[record[0]] = record[1] or ''
    return hashes


def _joined(path, entities, owner_entity, hashes):
    """Read the join table linking owner_entity to Secex_User into
    {owner pk: [user hash, ...]}."""
    result = {}
    join = _find_join(path, entities, owner_entity, 'Secex_User')
    if not join:
        return result
    table, owner_column, user_column = join
    for record in get_sqlite_db_records(path, f'SELECT {owner_column}, {user_column} FROM {table}'):
        result.setdefault(record[0], []).append(hashes.get(record[1], str(record[1])))
    return result


@artifact_processor
def wickr_messages(context):
    data_list = []
    source_path = ''

    for path in _db_paths(context.get_files_found()):
        if not does_table_exist_in_db(path, 'ZWICKR_MESSAGE'):
            continue
        source_path = path

        files_by_message = {}
        join = _find_join(path, _entity_names(path), 'Wickr_file', 'Wickr_Message')
        if join and does_table_exist_in_db(path, 'ZWICKR_FILE'):
            table, file_column, message_column = join
            guids = {}
            for record in get_sqlite_db_records(path, 'SELECT Z_PK, ZGUID FROM ZWICKR_FILE'):
                guids[record[0]] = record[1] or ''
            query = f'SELECT {file_column}, {message_column} FROM {table}'
            for record in get_sqlite_db_records(path, null_absent_columns(path, query)):
                files_by_message.setdefault(record[1], []).append(guids.get(record[0], ''))

        read_ts = _optional(path, 'ZWICKR_MESSAGE', 'ZREADTIMESTAMP')
        delivery_ts = _optional(path, 'ZWICKR_MESSAGE', 'ZDELIVERYTIMESTAMP')
        receipt_status = _optional(path, 'ZWICKR_MESSAGE', 'ZREADRECEIPTSTATUS')

        query = f'''
        SELECT m.Z_PK, m.ZTIMESTAMP, {read_ts}, {delivery_ts}, c.ZVGROUPID, u.ZUSERIDHASH,
               m.ZFULLTYPE, m.ZPRIMARYTYPE, m.ZISREAD, m.ZISSTARRED, m.ZISLOCKED, m.ZISSYNCED,
               {receipt_status}, m.ZCLEANUPTIME, m.ZMSGID, m.ZCONVO, m.ZUSERSENDER
        FROM ZWICKR_MESSAGE m
        LEFT JOIN ZSECEX_CONVO c ON m.ZCONVO = c.Z_PK
        LEFT JOIN ZSECEX_USER u ON m.ZUSERSENDER = u.Z_PK
        ORDER BY m.ZTIMESTAMP
        '''
        for record in get_sqlite_db_records(path, null_absent_columns(path, query)):
            data_list.append((
                _cocoa(record[1]),
                _cocoa(record[2]),
                _cocoa(record[3]),
                record[4] or (f'Convo {record[15]}' if record[15] else ''),
                record[5] or (f'User {record[16]}' if record[16] else ''),
                _message_type(record[6]),
                record[7],
                'Yes' if record[8] else 'No',
                'Yes' if record[9] else 'No',
                'Yes' if record[10] else 'No',
                'Yes' if record[11] else 'No',
                record[12],
                _cocoa(record[13]),
                ', '.join(f for f in files_by_message.get(record[0], []) if f),
                record[14],
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Read Timestamp', 'datetime'),
        ('Delivery Timestamp', 'datetime'),
        'Conversation Group ID',
        'Sender User ID Hash',
        'Message Type',
        'Primary Type (as stored)',
        'Is Read',
        'Is Starred',
        'Is Locked',
        'Is Synced',
        'Read Receipt Status (as stored)',
        ('Cleanup Time', 'datetime'),
        'Attached File GUIDs',
        'Message ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def wickr_conversations(context):
    data_list = []
    source_path = ''

    for path in _db_paths(context.get_files_found()):
        if not does_table_exist_in_db(path, 'ZSECEX_CONVO'):
            continue
        source_path = path
        entities = _entity_names(path)
        hashes = _user_hashes(path)
        members = _joined(path, entities, 'Secex_Convo', hashes)
        masters = _joined(path, entities, 'Secex_Secure_Room', hashes)

        is_external = _optional(path, 'ZSECEX_CONVO', 'ZISEXTERNAL')
        is_pinned = _optional(path, 'ZSECEX_CONVO', 'ZISPINNED')
        pending = _optional(path, 'ZSECEX_CONVO', 'ZPENDINGMESSAGESCOUNT')

        query = f'''
        SELECT Z_PK, Z_ENT, ZVGROUPID, ZLASTTIMESTAMP, ZLASTSYNCTIMESTAMP, ZMSGSYNTIMESTAMP,
               {is_external}, {is_pinned}, ZCHATBLOCKED, ZUNREADMESSAGES, {pending},
               ZENABLENOTIFICATIONS, ZSHOWNOTIFICATIONCONTENT, ZCALLSTATUS
        FROM ZSECEX_CONVO
        ORDER BY ZLASTTIMESTAMP
        '''
        for record in get_sqlite_db_records(path, null_absent_columns(path, query)):
            data_list.append((
                _unix(record[3]),
                _unix(record[4]),
                _unix(record[5]),
                entities.get(record[1], f'Z_ENT {record[1]}'),
                record[2],
                ', '.join(members.get(record[0], [])),
                ', '.join(masters.get(record[0], [])),
                'Yes' if record[6] else 'No',
                'Yes' if record[7] else 'No',
                'Yes' if record[8] else 'No',
                _text(record[9]),
                _text(record[10]),
                'Yes' if record[11] else 'No',
                'Yes' if record[12] else 'No',
                _text(record[13]),
            ))

    data_headers = (
        ('Last Timestamp', 'datetime'),
        ('Last Sync Timestamp', 'datetime'),
        ('Message Sync Timestamp', 'datetime'),
        'Kind',
        'Group ID',
        'Member User ID Hashes',
        'Administrator User ID Hashes',
        'Is External',
        'Is Pinned',
        'Chat Blocked',
        'Unread Messages',
        'Pending Messages',
        'Notifications Enabled',
        'Show Notification Content',
        'Call Status (as stored)',
    )
    return data_headers, data_list, source_path


@artifact_processor
def wickr_users(context):
    data_list = []
    source_path = ''

    for path in _db_paths(context.get_files_found()):
        if not does_table_exist_in_db(path, 'ZSECEX_USER'):
            continue
        source_path = path

        domain = _optional(path, 'ZSECEX_USER', 'ZDOMAIN')
        is_guest = _optional(path, 'ZSECEX_USER', 'ZISGUEST')
        capabilities = _optional(path, 'ZSECEX_USER', 'ZCAPABILITIES')

        query = f'''
        SELECT ZLASTACTIVITYTIME, ZUSERIDHASH, ZUSERALIASHASH, ZSOURCE, {domain}, ZISACTIVE,
               ZINNETWORK, ZISBLOCKED, {is_guest}, ZIS_BOT, ZISHIDDEN, ZISSTARRED, ZISSUSPENDED,
               ZHASNODEVICES, {capabilities}, Z_PK
        FROM ZSECEX_USER
        ORDER BY ZLASTACTIVITYTIME
        '''
        for record in get_sqlite_db_records(path, null_absent_columns(path, query)):
            data_list.append((
                _unix(record[0]),
                _text(record[1]),
                _text(record[2]),
                _text(record[3]),
                _text(record[4]),
                'Yes' if record[5] else 'No',
                'Yes' if record[6] else 'No',
                'Yes' if record[7] else 'No',
                'Yes' if record[8] else 'No',
                'Yes' if record[9] else 'No',
                'Yes' if record[10] else 'No',
                'Yes' if record[11] else 'No',
                'Yes' if record[12] else 'No',
                'Yes' if record[13] else 'No',
                _text(record[14]),
                record[15],
            ))

    data_headers = (
        ('Last Activity Time', 'datetime'),
        'User ID Hash',
        'User Alias Hash',
        'Source',
        'Domain',
        'Is Active',
        'In Network',
        'Is Blocked',
        'Is Guest',
        'Is Bot',
        'Is Hidden',
        'Is Starred',
        'Is Suspended',
        'Has No Devices',
        'Capabilities (as stored)',
        'Record ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def wickr_files(context):
    data_list = []
    source_path = ''

    for path in _db_paths(context.get_files_found()):
        if not does_table_exist_in_db(path, 'ZWICKR_FILE'):
            continue
        source_path = path

        messages = {}
        join = _find_join(path, _entity_names(path), 'Wickr_file', 'Wickr_Message')
        if join and does_table_exist_in_db(path, 'ZWICKR_MESSAGE'):
            table, file_column, message_column = join
            query = f'''
            SELECT j.{file_column}, m.ZMSGID, m.ZTIMESTAMP, c.ZVGROUPID
            FROM {table} j
            LEFT JOIN ZWICKR_MESSAGE m ON j.{message_column} = m.Z_PK
            LEFT JOIN ZSECEX_CONVO c ON m.ZCONVO = c.Z_PK
            '''
            for record in get_sqlite_db_records(path, null_absent_columns(path, query)):
                messages[record[0]] = (record[1], record[2], record[3])

        for record in get_sqlite_db_records(path, 'SELECT Z_PK, ZGUID, ZSTATUS FROM ZWICKR_FILE'):
            message = messages.get(record[0], ('', None, ''))
            data_list.append((
                _cocoa(message[1]),
                record[1],
                record[2],
                message[2] or '',
                message[0] or '',
            ))

    data_headers = (
        ('Message Timestamp', 'datetime'),
        'File GUID',
        'Status (as stored)',
        'Conversation Group ID',
        'Message ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def wickr_account(context):
    data_list = []
    source_path = ''

    for path in _db_paths(context.get_files_found()):
        if not does_table_exist_in_db(path, 'ZSECEX_ACCOUNT'):
            continue
        source_path = path

        network_timestamp = 'NULL'
        if does_table_exist_in_db(path, 'ZWICKR_NETWORK'):
            for record in get_sqlite_db_records(path, 'SELECT ZTIMESTAMP FROM ZWICKR_NETWORK'):
                network_timestamp = record[0]
                break

        censorship = _optional(path, 'ZSECEX_ACCOUNT', 'ZENABLECENSORSHIP')
        anonymous = _optional(path, 'ZSECEX_ACCOUNT', 'ZANONYMOUSNOTIFICATION')

        query = f'''
        SELECT ZSECURITYGROUPID, ZAFENABLE, ZAFSPEED, ZTOUCHID, ZENABLENOTIFICATIONS,
               ZSHOWNOTIFICATIONCONTENT, {anonymous}, ZISFRIENDFINDERENABLED,
               ZAUTOUNLOCKMESSAGES, ZWASRECOVERED, ZISNEWUSER, ZNEEDSBACKUP, ZWANTSCBACKUP,
               {censorship}, ZLASTMSGSEQUENCE, ZHIGHE, ZLASTAPID, ZIDCPCOUNT
        FROM ZSECEX_ACCOUNT
        '''
        for record in get_sqlite_db_records(path, null_absent_columns(path, query)):
            data_list.append((
                _unix(network_timestamp) if network_timestamp != 'NULL' else '',
                record[0],
                record[1],
                record[2],
                'Yes' if record[3] else 'No',
                'Yes' if record[4] else 'No',
                'Yes' if record[5] else 'No',
                'Yes' if record[6] else 'No',
                'Yes' if record[7] else 'No',
                'Yes' if record[8] else 'No',
                'Yes' if record[9] else 'No',
                'Yes' if record[10] else 'No',
                'Yes' if record[11] else 'No',
                'Yes' if record[12] else 'No',
                'Yes' if record[13] else 'No',
                record[14],
                record[15],
                record[16],
                record[17],
            ))

    data_headers = (
        ('Network Timestamp', 'datetime'),
        'Security Group ID',
        'ZAFENABLE (as stored)',
        'ZAFSPEED (as stored)',
        'Touch ID',
        'Notifications Enabled',
        'Show Notification Content',
        'Anonymous Notification',
        'Friend Finder Enabled',
        'Auto Unlock Messages',
        'Was Recovered',
        'Is New User',
        'Needs Backup',
        'Wants Cloud Backup',
        'Censorship Enabled',
        'Last Message Sequence',
        'ZHIGHE (as stored)',
        'Last App ID (as stored)',
        'ID CP Count (as stored)',
    )
    return data_headers, data_list, source_path


@artifact_processor
def wickr_devices(context):
    data_list = []
    source_path = ''

    for path in _db_paths(context.get_files_found()):
        if not does_table_exist_in_db(path, 'ZSECEX_APP'):
            continue
        source_path = path
        entities = _entity_names(path)

        query = '''
        SELECT a.Z_PK, a.Z_ENT, a.ZAPPIDHASH, u.ZUSERIDHASH, u.ZUSERALIASHASH, u.ZSOURCE, a.ZUSER
        FROM ZSECEX_APP a
        LEFT JOIN ZSECEX_USER u ON a.ZUSER = u.Z_PK
        ORDER BY a.Z_PK
        '''
        for record in get_sqlite_db_records(path, null_absent_columns(path, query)):
            data_list.append((
                _text(record[2]),
                record[3] or (f'User {record[6]}' if record[6] else ''),
                _text(record[4]),
                _text(record[5]),
                entities.get(record[1], f'Z_ENT {record[1]}'),
                record[0],
            ))

    data_headers = (
        'App ID Hash',
        'User ID Hash',
        'User Alias Hash',
        'Source',
        'Kind',
        'Record ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def wickr_recent_searches(context):
    data_list = []
    source_path = ''

    for path in _db_paths(context.get_files_found()):
        if not does_table_exist_in_db(path, 'ZRECENT_SEARCH'):
            continue
        source_path = path
        query = 'SELECT ZTIMESTAMP, ZSEARCHQUERY FROM ZRECENT_SEARCH ORDER BY ZTIMESTAMP'
        for record in get_sqlite_db_records(path, null_absent_columns(path, query)):
            data_list.append((
                _cocoa(record[0]),
                _text(record[1]),
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Search Query',
    )
    return data_headers, data_list, source_path


# The keychain accounts Wickr uses, and what each one holds. The access group is
# the team identifier, which is what keeps this from matching another app.
WICKR_ACCESS_GROUP = 'W8RC3R952A'
WICKR_KEYCHAIN_ACCOUNTS = (
    ('!wickrusername!', 'User Name'),
    ('userID', 'User ID'),
    ('!devid!', 'Device Identifier'),
    ('baseURL', 'Server'),
)


def _printable(raw):
    """Wickr's keychain values are UTF-8 strings, except devid which is a binary
    prefix followed by a UUID. Report text as text and anything else as hex."""
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        tail = raw[32:]
        try:
            return f'{raw[:32].hex()} + {tail.decode("ascii")}'
        except UnicodeDecodeError:
            return raw.hex()
    return text if text.isprintable() else raw.hex()


@artifact_processor
def wickr_keychain_account(context):
    data_list = []
    source_path = ''
    for path in _db_paths(context.get_files_found()):
        source_path = path
        break

    keychain_path = active_keychain_path()
    if not keychain_path:
        if source_path:
            logfunc('Wickr: no keychain is available, so the account identity stays hidden. '
                    'The database holds only hashes. Supply a keychain with --keychain or the '
                    'keychain field in the GUI.')
        return _KEYCHAIN_HEADERS, data_list, source_path

    for account, label in WICKR_KEYCHAIN_ACCOUNTS:
        for secret in find_keychain_secrets(keychain_path, WICKR_ACCESS_GROUP, account):
            data_list.append((label, account, _printable(secret), len(secret)))

    return _KEYCHAIN_HEADERS, data_list, source_path or keychain_path


_KEYCHAIN_HEADERS = (
    'Item',
    'Keychain Account',
    'Value',
    'Length',
)


@artifact_processor
def wickr_app_log(context):
    data_list = []
    source_path = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.log'):
            continue
        source_path = file_found
        try:
            with open(file_found, 'r', encoding='utf-8', errors='replace') as handle:
                lines = handle.readlines()
        except OSError as error:
            logfunc(f'Error reading Wickr log {file_found}: {error}')
            continue

        for line in lines:
            match = PAYLOAD_RE.match(line.rstrip('\n'))
            if match:
                try:
                    payload = json.loads(match.group(2))
                except ValueError:
                    continue
                data_list.append((
                    match.group(1).replace('/', '-'),
                    'Notification Payload',
                    payload.get('messageId', ''),
                    payload.get('convoId', ''),
                    payload.get('userId', ''),
                    payload.get('messageType', ''),
                ))
                continue
            match = DOWNLOAD_RE.match(line.rstrip('\n'))
            if match:
                data_list.append((
                    match.group(1).replace('/', '-'),
                    'Download Message',
                    match.group(4),
                    match.group(3) or '',
                    '',
                    match.group(2),
                ))

    data_list.sort(key=lambda row: row[0])

    data_headers = (
        'Log Timestamp',
        'Event',
        'Message ID',
        'Conversation Group ID',
        'Sender User ID Hash',
        'Message Type (as stored)',
    )
    return data_headers, data_list, source_path
