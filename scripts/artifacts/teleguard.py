__artifacts_v2__ = {
    "teleguardMessages": {
        "name": "Teleguard Messages",
        "description": "TeleGuard chat messages and shared media",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-07-03", "requirements": "none",
        "category": "Teleguard", "notes": "Timestamps are UTC (epoch milliseconds).",
        "paths": ('*/Shared/AppGroup/*/Library/teleguard_database.db*',
                  '*/Library/Caches/images/*'),
        "output_types": "standard", "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat ID",
                "textColumn": "Content",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender",
                "mediaColumn": "Media"
            }
        },
    },
    "teleguardPosts": {
        "name": "Teleguard Posts",
        "description": "TeleGuard channel posts",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Teleguard", "notes": "Timestamps are UTC (epoch milliseconds).",
        "paths": ('*/Shared/AppGroup/*/Library/teleguard_database.db*',),
        "output_types": "standard", "artifact_icon": "file-text"
    },
    "teleguardContacts": {
        "name": "Teleguard Contacts",
        "description": "TeleGuard contacts (with avatar thumbnails)",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Teleguard", "notes": "Timestamps are UTC (epoch milliseconds).",
        "paths": ('*/Shared/AppGroup/*/Library/teleguard_database.db*',),
        "output_types": "standard", "artifact_icon": "users"
    },
    "teleguardChannels": {
        "name": "Teleguard Channels",
        "description": "TeleGuard channels",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Teleguard", "notes": "",
        "paths": ('*/Shared/AppGroup/*/Library/teleguard_database.db*',),
        "output_types": "standard", "artifact_icon": "radio"
    }
}

import json

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, check_in_media,
                               check_in_embedded_media)


def _find_db(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('teleguard_database.db'):
            return file_found
    return ''


@artifact_processor
def teleguardMessages(context):
    data_headers = (('Timestamp', 'datetime'), ('User Time', 'datetime'), 'Type', 'Sender',
                    'Receiver', 'Content', 'Metadata', ('Media', 'media'), 'Status', 'Is Edited?',
                    'Direction', 'Chat ID')
    data_list = []
    db_path = _find_db(context)
    if not db_path:
        return data_headers, data_list, ''

    # local account id lives in the service table ('user' row) of the same db
    owner_id = ''
    for (svc_data,) in get_sqlite_db_records(db_path, "SELECT data FROM service WHERE id = 'user'"):
        try:
            owner_id = (json.loads(svc_data) or {}).get('serverId', '')
        except (json.JSONDecodeError, TypeError, ValueError):
            owner_id = ''

    query = '''
    SELECT
        datetime(createDate/1000, 'unixepoch'),
        datetime(userTime/1000, 'unixepoch'),
        type, sender, receiver, content, metadata, status, isEdited, chatId
    FROM messages
    '''
    for row in get_sqlite_db_records(db_path, query):
        media_refs = []
        if row[2] == 'MEDIA' and row[6]:
            try:
                files = (json.loads(row[6]) or {}).get('files') or {}
            except (json.JSONDecodeError, TypeError, ValueError):
                files = {}
            for fname in files:
                ref = check_in_media(fname)
                if ref:
                    media_refs.append(ref)
        if owner_id and row[3]:
            direction = 'Outgoing' if row[3] == owner_id else 'Incoming'
        else:
            direction = ''
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                          media_refs or '', row[7], row[8], direction, row[9]))

    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def teleguardPosts(context):
    data_headers = (('Timestamp', 'datetime'), 'Channel ID', 'Header', 'Content', 'Type',
                    'Local Status', 'Views Count', 'Likes Count', 'Dislikes Count', 'Metadata', 'Media')
    data_list = []
    db_path = _find_db(context)
    if not db_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(createDate/1000, 'unixepoch'),
        channelId, header, content, type, localStatus, viewsCount, likesCount,
        dislikesCount, metadata, media
    FROM posts
    '''
    for row in get_sqlite_db_records(db_path, query):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def teleguardContacts(context):
    data_headers = (('Last Activity Timestamp', 'datetime'), 'Server ID', 'Alias', 'Type', 'Color',
                    ('Avatar', 'media'), 'Options', 'Info', ('Last Visit Time', 'datetime'),
                    'Personal ID')
    data_list = []
    db_path = _find_db(context)
    if not db_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(lastActivityTime/1000, 'unixepoch'),
        serverId, alias, type, color, avatar, options, info,
        datetime(lastVisitTime/1000, 'unixepoch'),
        personalId
    FROM contacts
    '''
    for row in get_sqlite_db_records(db_path, query):
        avatar = ''
        if row[5] is not None:
            avatar = check_in_embedded_media(db_path, row[5], f'teleguard_avatar_{row[1]}')
        data_list.append((row[0], row[1], row[2], row[3], row[4], avatar, row[6], row[7], row[8], row[9]))

    return data_headers, data_list, context.get_relative_path(db_path)


@artifact_processor
def teleguardChannels(context):
    data_headers = ('ID', 'Alias', 'Description', 'Category', 'Color', 'Avatar ID',
                    'Subscribers Count', 'Admin', 'Posts Count', 'Is Deleted', 'Language', 'Type')
    data_list = []
    db_path = _find_db(context)
    if not db_path:
        return data_headers, data_list, ''

    for row in get_sqlite_db_records(db_path, 'SELECT * FROM channels'):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(db_path)
