__artifacts_v2__ = {
    "gettr_ios_messages": {
        "name": "GETTR - Messages",
        "description": "Direct messages from the app's per account chat database, with the "
                       "sender, the conversation and the message text.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "GETTR",
        "notes": "The chat database is Documents/db_u<account id>.sqlite, one per account; its "
                 "table names match the Stream Chat client schema, which is not sourced here. "
                 "Message Direction is derived by comparing each message's user id against the "
                 "account id the same database records in connection_events.own_user, so it "
                 "comes from a value the app stored rather than from the file name, and it is "
                 "left blank when that row is absent. Sender is the username the users table "
                 "carries for that id and falls back to the raw id when no users row matches. "
                 "The timestamps are Unix seconds. Rows with Message Type deleted carried no "
                 "text, so such a row still "
                 "shows when it was sent and by whom: 3 of the 32 messages on the tested image "
                 "were in that state, and 28 of the 32 carried text. Attachments holds the "
                 "descriptor JSON as stored. Those descriptors name remote URLs rather than "
                 "local files, and the four attachment URLs on the tested image matched no row "
                 "of the app's own image cache, so no media is attached to a message here and "
                 "the Cached Images artifact is where any recovered picture appears. Reaction "
                 "Counts is reported as stored. Conversation holds the channel identifier and "
                 "separates conversations on a device that has more than one. "
                 "Reply Count held the single value 0 on all 32 rows of the tested image, so "
                 "no message there carried a threaded reply. "
                 "The 32 messages on the tested image were spread across two conversations, 17 "
                 "outgoing and 15 incoming.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/db_u*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Sender",
            }
        },
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | GETTR | 32 rows",
        },
    },
    "gettr_ios_conversation_members": {
        "name": "GETTR - Conversation Members",
        "description": "One row per account in each conversation the chat database holds, with "
                       "that account's role and ban state.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "GETTR",
        "notes": "Built from the members table of Documents/db_u<account id>.sqlite, joined to "
                 "the users table for the account details and to the reads table for that "
                 "account's last read position in the conversation. A row records that the "
                 "account belongs to the conversation, which is not the same as the account "
                 "having written anything in it. Username comes from the users row and falls "
                 "back to the raw id. The roles, ban flags and the online flag are reported as "
                 "stored. Four member rows and three user rows were present on the tested image. "
                 "Channel Role, Invited, Banned In Conversation, Shadow Banned and Account "
                 "Banned each held one value across the four rows of the tested image, which "
                 "is what a single ordinary conversation with no restricted account looks "
                 "like; four rows is too few for that to say anything about the app in "
                 "general. "
                 "The tested image held two conversations and four member rows across three "
                 "accounts, so one account belonged to both.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/db_u*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | GETTR | 4 rows",
        },
    },
    "gettr_ios_notifications": {
        "name": "GETTR - Notifications",
        "description": "Rows from the notification tables of the app's per account database, "
                       "each carrying an action code and a payload.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "GETTR",
        "notes": "One row per row of the notification, notification_v, notification_ls, "
                 "notification_poll, mentions and mentions_v tables in "
                 "Documents/private_<account name>.db, told apart by the Source Table column. "
                 "The account name is taken from the file name, which is how the app names the "
                 "store. Action is the app's own code and is reported as stored. Payload is the "
                 "row's JSON as stored, and the other account identifiers and display names are "
                 "read out of it where it parses. All six tables were empty on the tested image, "
                 "so this reader is code present and was not exercised, and the columns are the "
                 "ones the tables declare rather than ones observed carrying values.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/private_*.db*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | GETTR | 0 rows",
        },
    },
    "gettr_ios_app_state": {
        "name": "GETTR - App State",
        "description": "Key and value rows from the app's two key value stores, including an "
                       "account record and a device identifier.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "GETTR",
        "notes": "One row per row of the kv table in Documents/g.db and in "
                 "Documents/private_<account name>.db, told apart by the Store column. The "
                 "second file's name carries the account it belongs to and that name is reported "
                 "in the Account column; g.db is not per account and its Account column is "
                 "blank. Values are reported as stored, because the store mixes plain strings, "
                 "JSON documents and cached page content under one column and nothing separates "
                 "them but the key. On the tested image the keys user_me and auth_device_id in "
                 "g.db held an account record and a device identifier, and the per account file "
                 "held a cached timeline, a cached user search "
                 "result list and a direct message chat identifier. 20 rows were present in g.db "
                 "and 19 in the per account file.",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/g.db*',
                  '*/mobile/Containers/Data/Application/*/Documents/private_*.db*'),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | GETTR | 39 rows",
        },
    },
    "gettr_ios_cached_images": {
        "name": "GETTR - Cached Images",
        "description": "Rows from the app's image cache, each pairing the address it requested "
                       "with the file it wrote and the picture where it was recovered.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "GETTR",
        "notes": "One row per row of the cacheObject table in "
                 "Library/Application Support/libCachedImageData.db. Each row names the address "
                 "the app requested and the file it wrote under Library/Caches/"
                 "libCachedImageData, and where that file is in the extraction it is attached to "
                 "the row, so the picture is shown rather than only named. A cached file is "
                 "paired with the database from its own app container, so two containers holding "
                 "a file of the same name are never confused. Touched and Valid Until are Unix "
                 "milliseconds. A row records that the app fetched the address, which is not by "
                 "itself evidence that a person chose to look at it; the cache does not record "
                 "whether the picture was opened. All 12 rows on the "
                 "tested image resolved to a file and every one of them was a picture. "
                 "URL and Cache Key held the same value on all 12 rows of the tested image, so "
                 "the app keyed this cache on the address it requested. Both are kept because "
                 "the key is what the database joins on and a different release could key it "
                 "otherwise.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/libCachedImageData.db*',
                  '*/mobile/Containers/Data/Application/*/Library/Caches/libCachedImageData/*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | GETTR | 12 rows",
        },
    },
}

import json
import os

from scripts.ilapfuncs import (artifact_processor, check_in_media, convert_unix_ts_to_utc,
                               does_table_exist_in_db, get_sqlite_db_records, logfunc)

_SIDECARS = ('-wal', '-shm', '-journal')
_CONTAINER_MARK = '/Containers/Data/Application/'


def _container(path):
    '''The app data container a path sits in, or '' when it is not under one.

    Keyed on the container directory rather than on a name, so a file from one app's
    container is never paired with another's.
    '''
    text = str(path).replace('\\', '/')
    if _CONTAINER_MARK not in text:
        return ''
    head, tail = text.split(_CONTAINER_MARK, 1)
    guid = tail.split('/', 1)[0]
    return head + _CONTAINER_MARK + guid


def _stores(files_found, matches):
    '''Files whose base name the test accepts, directories and sidecars dropped.'''
    found = []
    for file_found in files_found:
        path = str(file_found)
        if os.path.isdir(path) or path.endswith(_SIDECARS):
            continue
        if matches(os.path.basename(path)) and path not in found:
            found.append(path)
    return found


def _rows(path, table, statement):
    '''Rows of a statement, or nothing when the store lacks the table.'''
    if not does_table_exist_in_db(path, table):
        return []
    try:
        return list(get_sqlite_db_records(path, statement))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'GETTR: could not read {table}: {error}')
        return []


def _account_from_private(path):
    '''The account name a private_<name>.db file name carries.'''
    name = os.path.basename(path)
    if name.startswith('private_') and name.endswith('.db'):
        return name[len('private_'):-len('.db')]
    return ''


def _own_user(db_path):
    '''(account id, account name) the chat database records for the device account.'''
    for (blob,) in _rows(db_path, 'connection_events',
                         'SELECT own_user FROM connection_events'):
        if not blob:
            continue
        try:
            own = json.loads(blob)
        except (TypeError, ValueError) as error:
            logfunc(f'GETTR: connection_events.own_user did not parse as JSON: {error}')
            continue
        if isinstance(own, dict):
            return own.get('id', ''), (own.get('username') or own.get('name') or '')
    return '', ''


def _usernames(db_path):
    '''{user id: username} out of the users table's extra_data JSON.'''
    names = {}
    for user_id, extra in _rows(db_path, 'users', 'SELECT id, extra_data FROM users'):
        label = ''
        if extra:
            try:
                data = json.loads(extra)
                if isinstance(data, dict):
                    label = data.get('username') or data.get('name') or data.get('nickname') or ''
            except (TypeError, ValueError) as error:
                logfunc(f'GETTR: users.extra_data did not parse as JSON for {user_id}: {error}')
        names[user_id] = label
    return names


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


@artifact_processor
def gettr_ios_messages(context):
    data_list = []
    source_paths = []

    for db_path in _stores(context.get_files_found(),
                           lambda n: n.startswith('db_u') and n.endswith('.sqlite')):
        own_id, _own_name = _own_user(db_path)
        names = _usernames(db_path)
        rows = _rows(db_path, 'messages', '''
            SELECT created_at, updated_at, deleted_at, user_id, channel_cid, message_text,
                   type, attachments, quoted_message_id, reply_count, reaction_counts, id
            FROM messages ORDER BY created_at''')
        if not rows:
            continue
        source_paths.append(db_path)
        for (created, updated, deleted, user_id, channel, text, kind, attachments, quoted,
             replies, reactions, message_id) in rows:
            if not own_id:
                direction = ''
            else:
                direction = 'Outgoing' if user_id == own_id else 'Incoming'
            data_list.append((
                convert_unix_ts_to_utc(created) if created else '',
                convert_unix_ts_to_utc(updated) if updated else '',
                convert_unix_ts_to_utc(deleted) if deleted else '',
                direction, names.get(user_id) or _text(user_id), _text(text), _text(channel),
                _text(kind), '' if attachments in ('[]', None) else _text(attachments),
                _text(quoted), '' if replies is None else _text(replies), _text(reactions),
                _text(message_id), _text(user_id),
            ))

    data_headers = (
        ('Message Timestamp', 'datetime'), ('Updated Timestamp', 'datetime'),
        ('Deleted Timestamp', 'datetime'), 'Message Direction', 'Sender', 'Message',
        'Conversation', 'Message Type', 'Attachments', 'Quoted Message ID', 'Reply Count',
        'Reaction Counts', 'Message ID', 'User ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def gettr_ios_conversation_members(context):
    data_list = []
    source_paths = []

    for db_path in _stores(context.get_files_found(),
                           lambda n: n.startswith('db_u') and n.endswith('.sqlite')):
        names = _usernames(db_path)
        users = {}
        for (user_id, created, updated, active, online, banned) in _rows(
                db_path, 'users',
                'SELECT id, created_at, updated_at, last_active, online, banned FROM users'):
            users[user_id] = (created, updated, active, online, banned)
        reads = {}
        for (last_read, user_id, channel, unread) in _rows(
                db_path, 'reads',
                'SELECT last_read, user_id, channel_cid, unread_messages FROM reads'):
            reads[(user_id, channel)] = (last_read, unread)
        rows = _rows(db_path, 'members', '''
            SELECT user_id, channel_cid, role, channel_role, invited, banned, shadow_banned
            FROM members''')
        if not rows:
            continue
        source_paths.append(db_path)
        for user_id, channel, role, channel_role, invited, banned, shadow in rows:
            created, updated, active, online, account_banned = users.get(
                user_id, ('', '', '', '', ''))
            last_read, unread = reads.get((user_id, channel), ('', ''))
            data_list.append((
                convert_unix_ts_to_utc(last_read) if last_read else '',
                convert_unix_ts_to_utc(created) if created else '',
                convert_unix_ts_to_utc(active) if active else '',
                names.get(user_id) or _text(user_id), _text(channel), _text(channel_role),
                _text(role), _text(invited), _text(banned), _text(shadow), _text(unread),
                _text(online), _text(account_banned), _text(user_id),
            ))

    data_headers = (
        ('Last Read Timestamp', 'datetime'), ('Account Created', 'datetime'),
        ('Last Active', 'datetime'), 'Username', 'Conversation', 'Channel Role', 'Member Role',
        'Invited', 'Banned In Conversation', 'Shadow Banned', 'Unread Messages', 'Online',
        'Account Banned', 'User ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)


_NOTIFICATION_TABLES = ('notification', 'notification_v', 'notification_ls',
                        'notification_poll', 'mentions', 'mentions_v')


@artifact_processor
def gettr_ios_notifications(context):
    data_list = []
    source_paths = []

    for db_path in _stores(context.get_files_found(),
                           lambda n: n.startswith('private_') and n.endswith('.db')):
        account = _account_from_private(db_path)
        seen = False
        for table in _NOTIFICATION_TABLES:
            for (msg_id, date, action, user_id, tag, is_read, payload) in _rows(
                    db_path, table,
                    f'SELECT msg_id, msg_date, msg_action, msg_user_id, msg_tag, msg_is_read, '
                    f'msg_data FROM {table}'):
                seen = True
                others, display = '', ''
                if payload:
                    try:
                        parsed = json.loads(payload)
                    except (TypeError, ValueError):
                        parsed = None
                    if isinstance(parsed, dict):
                        others = _text(parsed.get('userIds') or parsed.get('uids') or '')
                        display = _text(parsed.get('nickNames') or parsed.get('names') or '')
                data_list.append((
                    convert_unix_ts_to_utc(date) if date else '', account, _text(action),
                    others, display, _text(is_read), _text(tag), _text(user_id),
                    _text(msg_id), _text(payload), table,
                ))
        if seen:
            source_paths.append(db_path)

    data_headers = (
        ('Notification Timestamp', 'datetime'), 'Account', 'Action (as stored)',
        'Other Account Identifiers', 'Other Account Display Names', 'Read', 'Tag',
        'Notification User ID (as stored)', 'Notification ID', 'Payload (as stored)',
        'Source Table',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def gettr_ios_app_state(context):
    data_list = []
    source_paths = []

    def _kv(db_path, store, account):
        rows = _rows(db_path, 'kv', 'SELECT key, value FROM kv ORDER BY key')
        if rows:
            source_paths.append(db_path)
        for key, value in rows:
            data_list.append((_text(key), _text(value), store, account))

    files_found = context.get_files_found()
    for db_path in _stores(files_found, lambda n: n == 'g.db'):
        _kv(db_path, 'g.db', '')
    for db_path in _stores(files_found,
                           lambda n: n.startswith('private_') and n.endswith('.db')):
        _kv(db_path, os.path.basename(db_path), _account_from_private(db_path))

    data_headers = ('Key', 'Value (as stored)', 'Store', 'Account')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def gettr_ios_cached_images(context):
    data_list = []
    source_paths = []

    files_found = context.get_files_found()
    files_by_key = {}
    for file_found in files_found:
        path = str(file_found)
        if os.path.isdir(path):
            continue
        files_by_key.setdefault((_container(path), os.path.basename(path)), path)

    for db_path in _stores(files_found, lambda n: n == 'libCachedImageData.db'):
        rows = _rows(db_path, 'cacheObject', '''
            SELECT touched, validTill, url, relativePath, length, eTag, key
            FROM cacheObject ORDER BY touched''')
        if not rows:
            continue
        source_paths.append(db_path)
        container = _container(db_path)
        for touched, valid_till, url, relative, length, etag, key in rows:
            media = ''
            cached = files_by_key.get((container, relative)) if relative else None
            if cached:
                media = check_in_media(cached, relative)
            data_list.append((
                convert_unix_ts_to_utc(touched / 1000) if touched else '',
                convert_unix_ts_to_utc(valid_till / 1000) if valid_till else '',
                media, _text(url), _text(relative),
                '' if length is None else _text(length), _text(etag), _text(key),
            ))

    data_headers = (
        ('Touched Timestamp', 'datetime'), ('Valid Until', 'datetime'), ('Media', 'media'),
        'URL', 'Cached File', 'Length', 'ETag', 'Cache Key',
    )
    return data_headers, data_list, '\n'.join(source_paths)
