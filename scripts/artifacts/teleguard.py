__artifacts_v2__ = {
    "teleguardMessages": {
        "name": "Teleguard Messages",
        "description": "TeleGuard chat messages, with the shared media file where the extraction "
                       "holds it",
        "author": "@abrignoni", "creation_date": "2026-06-23", "last_update_date": "2026-10-09", "requirements": "none",
        "category": "Teleguard",
        "notes": "Timestamps are UTC (epoch milliseconds). Direction is derived by comparing the "
                 "row's sender with the local account's serverId from the service table; it is "
                 "blank when either is missing. Every teleguard_database.db matched is read, "
                 "one per app group container, and the located-at line lists each one. Is Edited? held 0 on every message row of the tested extraction and is "
                 "reported as stored, so an extraction where the flag is set will show it. Media "
                 "was empty on every row: each item is looked up by the server file id a message "
                 "records in its metadata, by file name, among the files of a "
                 "Library/Caches/images directory. Only a container that also holds "
                 "Library/Preferences/ch.swisscows.messenger.teleguardapp.plist is searched, "
                 "so another app's image cache is never used; when no such container is "
                 "matched the Media column stays empty. The tested extraction carried no "
                 "such file for TeleGuard, so the media link has not been exercised on real "
                 "data. Call events and membership events are "
                 "rows of this same table, of type CALL and SERVICE, and are also reported in full by "
                 "Teleguard Calls and Teleguard Chat Events.",
        "paths": ('*/Shared/AppGroup/*/Library/teleguard_database.db*',
                  '*/Library/Preferences/ch.swisscows.messenger.teleguardapp.plist',
                  '*/Library/Caches/images/*'),
        "output_types": "standard", "artifact_icon": "message-circle",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | TeleGuard 4.0.1, Truth Social 1.11.0 | 70 rows",
        },
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
        "author": "@abrignoni", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "Teleguard", "notes": "createDate is read as epoch milliseconds, as on the "
                                          "messages table. The posts table held no rows on the "
                                          "tested extraction, so this artifact has not been run "
                                          "against data.",
        "paths": ('*/Shared/AppGroup/*/Library/teleguard_database.db*',),
        "output_types": "standard", "artifact_icon": "file-text",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | TeleGuard 4.0.1 | 0 rows",
        },
    },
    "teleguardContacts": {
        "name": "Teleguard Contacts",
        "description": "TeleGuard contacts (with avatar thumbnails)",
        "author": "@abrignoni", "creation_date": "2026-06-23", "last_update_date": "2026-08-21", "requirements": "none",
        "category": "Teleguard",
        "notes": "Timestamps are UTC (epoch milliseconds). Personal ID is the personalId column, "
                 "reported as stored; it is a separate column from Server ID. The app's own "
                 "binary labels it 'Personal TeleGuard ID', carries a 'Change personal ID' action "
                 "and a buyPersonalId endpoint, and adds the column to this table in a migration; "
                 "the app version and platform that binary was read from are not recorded here. "
                 "It was null on "
                 "every contact row of the tested extraction.",
        "paths": ('*/Shared/AppGroup/*/Library/teleguard_database.db*',),
        "output_types": "standard", "artifact_icon": "users",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | TeleGuard 4.0.1 | 5 rows",
        },
    },
    "teleguardChannels": {
        "name": "Teleguard Channels",
        "description": "Rows of the channels table of the TeleGuard database, with "
                       "the table's own column names as headers.",
        "author": "@abrignoni", "creation_date": "2026-06-23", "last_update_date": "2026-10-09", "requirements": "none",
        "category": "Teleguard",
        "notes": "Headers are the column names the channels table itself declares, in table "
                 "order, and values are reported as stored. No meaning is assigned to a "
                 "column here. Each teleguard_database.db matched is read. The table held no "
                 "rows on the tested extraction, so this artifact has not been run against "
                 "data.",
        "paths": ('*/Shared/AppGroup/*/Library/teleguard_database.db*',),
        "output_types": "standard", "artifact_icon": "radio",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | TeleGuard 4.0.1 | 0 rows",
        },
    },
    "teleguardCalls": {
        "name": "Teleguard Calls",
        "description": "TeleGuard audio and video call events",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-21", "last_update_date": "2026-10-09", "requirements": "none",
        "category": "Teleguard",
        "notes": "Call events are stored as rows of the messages table with type 'CALL', not in a "
                 "separate call log. Each row carries a JSON metadata object with the keys "
                 "isSuccessfull, subtext, membersText and callType; all call rows in the tested "
                 "extraction carried all four. Direction is derived by comparing the row's sender "
                 "with the local account's serverId from the service table, which agreed with the "
                 "app's own English event label on every call row in the tested extraction. Duration "
                 "and outcome are reported as stored: on the call rows of the tested extraction "
                 "subtext was a display string holding either a minutes and seconds count in "
                 "words or a word for a call that did not connect, not a numeric duration. "
                 "isSuccessfull (as stored) is the isSuccessfull key of that metadata, shown "
                 "as true or false when it is a JSON boolean and as stored otherwise; its "
                 "meaning is not sourced here. No numeric duration column was found "
                 "for these rows. The messages table's userTime column is not reported here "
                 "because it held exactly the same value as createDate on every call row, unlike the "
                 "text rows of the same table where the two differ. The database also carries an "
                 "empty sipcalls table with number, name, duration, date and cost columns; it held no "
                 "rows in the tested extraction and is not reported.",
        "paths": ('*/Shared/AppGroup/*/Library/teleguard_database.db*',),
        "output_types": "standard", "artifact_icon": "phone",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | TeleGuard 4.0.1 | 10 rows",
        },
    },
    "teleguardChatEvents": {
        "name": "Teleguard Chat Events",
        "description": "TeleGuard invitation and group membership events",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-21", "last_update_date": "2026-08-21", "requirements": "none",
        "category": "Teleguard",
        "notes": "This artifact reports the rows of the messages table with type 'SERVICE'. On "
                 "the tested extraction those five rows were membership and invitation events. "
                 "The event text is the app's own localised display string and is "
                 "reported as stored. These rows carry no sender in the tested extraction, so no "
                 "direction is derived for them. The messages table's userTime column is not "
                 "reported here because it was null on every service row of the tested extraction.",
        "paths": ('*/Shared/AppGroup/*/Library/teleguard_database.db*',),
        "output_types": "standard", "artifact_icon": "users-plus",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | TeleGuard 4.0.1 | 5 rows",
        },
    },
    "teleguardAccount": {
        "name": "Teleguard Account",
        "description": "TeleGuard local account identity",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-21", "last_update_date": "2026-08-21", "requirements": "none",
        "category": "Teleguard",
        "notes": "The local account is stored as the 'user' row of the service table, whose data "
                 "column is JSON. Server ID is the account identifier that appears in the sender, "
                 "receiver and chatId columns of the messages table. The module reads publicKey "
                 "and privateKey from the same JSON. Neither was present on the tested "
                 "extraction, so the key columns have not been exercised on iOS data, and Public "
                 "Key Present and Private Key Present record No and Public Key SHA-256 and "
                 "Private Key SHA-256 are blank there. Where a key is present the key material itself "
                 "is not written to the report; the columns record whether each key was present and a "
                 "SHA-256 fingerprint of the DER body, which is enough to correlate the account "
                 "across extractions without copying a private key into report output. Personal ID "
                 "and Current Phone were empty on the tested extraction and are reported as "
                 "stored. The settings key holding the "
                 "phone value was spelled 'currentPhone' on iOS and '_currentPhone' on Android in the "
                 "tested extractions and both spellings are read.",
        "paths": ('*/Shared/AppGroup/*/Library/teleguard_database.db*',),
        "output_types": "standard", "artifact_icon": "user-circle",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | TeleGuard 4.0.1 | 1 row",
        },
    },
    "teleguardDrafts": {
        "name": "Teleguard Drafts",
        "description": "Rows of the draft table of TeleGuard's teleguard_temp.db, with the "
                       "recipient's alias where the contacts table holds it",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-21", "last_update_date": "2026-08-21", "requirements": "none",
        "category": "Teleguard",
        "notes": "Drafts live in a second database, teleguard_temp.db, in the same directory as "
                 "teleguard_database.db. The draft table is keyed on the recipient's serverId, which "
                 "is resolved to a contact alias from the contacts table of the main database in the "
                 "same app group container. The Draft Text column was an empty string, not null, on "
                 "every row of the tested extraction, so this artifact reported no draft text "
                 "there; what causes a row to exist with empty text is not established "
                 "here. The same "
                 "database carries a messages_buffer table, which held no rows in the tested "
                 "extraction and is not reported.",
        "paths": ('*/Shared/AppGroup/*/Library/teleguard_temp.db*',
                  '*/Shared/AppGroup/*/Library/teleguard_database.db*'),
        "output_types": "standard", "artifact_icon": "pencil",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | TeleGuard 4.0.1 | 3 rows",
        },
    },
    "teleguardAppSettings": {
        "name": "Teleguard App Settings",
        "description": "TeleGuard notification and cache settings",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-21", "last_update_date": "2026-10-09", "requirements": "none",
        "category": "Teleguard",
        "notes": "Hide Push Content, Hide Push Author, Channel Notifications Enabled and Unread Count "
                 "are read from the app group's own preferences plist, "
                 "group.ch.swisscows.messenger.teleguardapp.plist. The two hide settings are "
                 "reported as stored; they are a statement "
                 "about the app's configuration, not about what any particular notification "
                 "contained. Last Cache Clearing is the flutter.lastCacheClearing value of "
                 "ch.swisscows.messenger.teleguardapp.plist, read as Unix milliseconds. What "
                 "event it marks is not sourced here. That plist sits in the app's data "
                 "container and the group plist in the app group container, and nothing read "
                 "here records which data container belongs to which app group. When exactly "
                 "one of each is matched they are reported on one row. Otherwise each plist "
                 "gets its own row, with the columns the other file holds left blank, so a "
                 "data container plist is reported when no group plist is matched. Preferences "
                 "File names the file or files a row was read from. Other keys of "
                 "ch.swisscows.messenger.teleguardapp.plist are not reported.",
        "paths": ('*/Shared/AppGroup/*/Library/Preferences/group.ch.swisscows.messenger.teleguardapp.plist',
                  '*/Library/Preferences/ch.swisscows.messenger.teleguardapp.plist'),
        "output_types": "standard", "artifact_icon": "settings",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | TeleGuard 4.0.1 | 1 row",
        },
    }
}

import base64
import datetime
import hashlib
import json
import os

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, check_in_media,
                               check_in_embedded_media, get_plist_file_content, logfunc)

APP_GROUP_MARKER = '/Shared/AppGroup/'


def _group_containers(context):
    """Files grouped by the app group container directory they sit in.

    An iOS install has one app group container, so this normally yields a single
    group; keying on the container rather than taking the first match means an
    extraction that carries more than one is reported rather than silently reduced
    to whichever the seeker returned first.
    """
    grouped = {}
    for file_found in context.get_files_found():
        path = str(file_found).replace('\\', '/')
        index = path.find(APP_GROUP_MARKER)
        if index == -1:
            continue
        rest = path[index + len(APP_GROUP_MARKER):]
        container = path[:index + len(APP_GROUP_MARKER)] + rest.split('/')[0]
        grouped.setdefault(container, []).append(str(file_found))
    return grouped


def _pick(paths, filename):
    for path in paths:
        if os.path.basename(path) == filename:
            return path
    return ''


def _owner_id(db_path):
    """The local account's serverId, used to derive message and call direction."""
    for (data,) in get_sqlite_db_records(db_path, "SELECT data FROM service WHERE id = 'user'"):
        try:
            return (json.loads(data) or {}).get('serverId', '') or ''
        except (json.JSONDecodeError, TypeError, ValueError):
            return ''
    return ''


def _ms_to_utc(value):
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, TypeError, OSError, OverflowError):
        return ''


def _pem_fingerprint(pem):
    """SHA-256 of a PEM body's DER bytes, so a key can be correlated without copying it."""
    if not pem:
        return ''
    body = ''.join(line for line in str(pem).splitlines()
                   if 'BEGIN' not in line and 'END' not in line)
    try:
        der = base64.b64decode(body, validate=False)
    except (ValueError, TypeError):
        return ''
    return hashlib.sha256(der).hexdigest() if der else ''


def _find_db(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('teleguard_database.db'):
            return file_found
    return ''


def _all_dbs(context):
    """Every teleguard_database.db matched, one per app group container."""
    found = []
    for paths in _group_containers(context).values():
        db_path = _pick(paths, 'teleguard_database.db')
        if db_path and db_path not in found:
            found.append(db_path)
    return found


def _teleguard_cached_images(context):
    """Cached image files, by name, from TeleGuard's own data container only.

    The container is identified by the app's preferences plist; a
    Library/Caches/images directory in any other container is ignored, and no
    file is offered when the plist is not matched.
    """
    marker = '/Library/Preferences/ch.swisscows.messenger.teleguardapp.plist'
    roots = set()
    for file_found in context.get_files_found():
        path = str(file_found).replace('\\', '/')
        if path.endswith(marker):
            roots.add(path[:-len(marker)])
    images = {}
    for file_found in context.get_files_found():
        path = str(file_found).replace('\\', '/')
        for root in roots:
            prefix = root + '/Library/Caches/images/'
            if path.startswith(prefix) and os.path.isfile(str(file_found)):
                images.setdefault(path.rsplit('/', 1)[-1], str(file_found))
    return images


@artifact_processor
def teleguardMessages(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        ('User Time', 'datetime'),
        'Direction',
        'Sender',
        'Content',
        ('Media', 'media'),
        'Type',
        'Receiver',
        'Metadata',
        'Status',
        'Is Edited?',
        'Chat ID',
    )
    data_list = []
    sources = []
    cached_images = _teleguard_cached_images(context)

    query = '''
    SELECT
        datetime(createDate/1000, 'unixepoch'),
        datetime(userTime/1000, 'unixepoch'),
        type, sender, receiver, content, metadata, status, isEdited, chatId
    FROM messages
    '''
    for db_path in _all_dbs(context):
        sources.append(db_path)
        # local account id lives in the service table ('user' row) of the same db
        owner_id = _owner_id(db_path)
        for row in get_sqlite_db_records(db_path, query):
            media_refs = []
            if row[2] == 'MEDIA' and row[6]:
                try:
                    files = (json.loads(row[6]) or {}).get('files') or {}
                except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
                    files = {}
                for fname in files:
                    image_path = cached_images.get(str(fname))
                    if not image_path:
                        continue
                    ref = check_in_media(image_path)
                    if ref:
                        media_refs.append(ref)
            if owner_id and row[3]:
                direction = 'Outgoing' if row[3] == owner_id else 'Incoming'
            else:
                direction = ''
            data_list.append((
                row[0],
                row[1],
                direction,
                row[3],
                row[5],
                media_refs or '',
                row[2],
                row[4],
                row[6],
                row[7],
                row[8],
                row[9],
            ))

    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


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
    # headers are the table's own column names, taken from the first database
    # read; a database whose channels table declares other columns is logged and
    # skipped so no value is ever placed under another column's name
    data_headers = ()
    data_list = []
    sources = []
    for db_path in _all_dbs(context):
        cursor = get_sqlite_db_records(db_path, 'SELECT * FROM channels')
        description = getattr(cursor, 'description', None)
        if not description:
            continue
        columns = tuple(column[0] for column in description)
        if not data_headers:
            data_headers = columns
        elif columns != data_headers:
            logfunc(f'Teleguard Channels: {context.get_relative_path(db_path)} declares '
                    'different channels columns and was not reported')
            continue
        sources.append(db_path)
        for row in cursor:
            data_list.append(tuple(row))

    if not data_headers:
        data_headers = ('channels table not read',)
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def teleguardCalls(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Call Type',
        'isSuccessfull (as stored)',
        'Duration or Result (as stored)',
        'Members (as stored)',
        'Event Label (as stored)',
        'Sender',
        'Chat ID',
        'Message ID',
    )
    data_list = []
    sources = []
    for paths in _group_containers(context).values():
        db_path = _pick(paths, 'teleguard_database.db')
        if not db_path:
            continue
        query = '''
        SELECT
            datetime(createDate/1000, 'unixepoch'),
            sender, chatId, content, metadata, id
        FROM messages WHERE type = 'CALL'
        '''
        rows = list(get_sqlite_db_records(db_path, query))
        if not rows:
            continue
        sources.append(db_path)
        owner_id = _owner_id(db_path)
        for row in rows:
            try:
                meta = json.loads(row[4]) or {}
            except (json.JSONDecodeError, TypeError, ValueError):
                meta = {}
            if owner_id and row[1]:
                direction = 'Outgoing' if row[1] == owner_id else 'Incoming'
            else:
                direction = ''
            successful = meta.get('isSuccessfull')
            if successful is None:
                successful = ''
            elif isinstance(successful, bool):
                successful = 'true' if successful else 'false'
            data_list.append((
                row[0],
                direction,
                meta.get('callType', ''),
                successful,
                meta.get('subtext', ''),
                meta.get('membersText') or '',
                row[3],
                row[1],
                row[2],
                row[5],
            ))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def teleguardChatEvents(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Event (as stored)',
        'Sender',
        'Chat ID',
        'Message ID',
    )
    data_list = []
    sources = []
    for paths in _group_containers(context).values():
        db_path = _pick(paths, 'teleguard_database.db')
        if not db_path:
            continue
        query = '''
        SELECT
            datetime(createDate/1000, 'unixepoch'),
            content, sender, chatId, id
        FROM messages WHERE type = 'SERVICE'
        '''
        rows = list(get_sqlite_db_records(db_path, query))
        if not rows:
            continue
        sources.append(db_path)
        for row in rows:
            data_list.append((row[0], row[1], row[2] or '', row[3], row[4]))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def teleguardAccount(context):
    data_headers = (
        'Server ID',
        'Alias',
        'User ID',
        'Personal ID',
        'Avatar Ref ID',
        'Current Phone',
        'Public Key Present',
        'Public Key SHA-256',
        'Private Key Present',
        'Private Key SHA-256',
    )
    data_list = []
    sources = []
    for paths in _group_containers(context).values():
        db_path = _pick(paths, 'teleguard_database.db')
        if not db_path:
            continue
        user = {}
        for (data,) in get_sqlite_db_records(db_path, "SELECT data FROM service WHERE id = 'user'"):
            try:
                user = json.loads(data) or {}
            except (json.JSONDecodeError, TypeError, ValueError):
                user = {}
        if not user:
            continue
        settings = {}
        for (data,) in get_sqlite_db_records(
                db_path, "SELECT data FROM service WHERE id = 'settings'"):
            try:
                settings = json.loads(data) or {}
            except (json.JSONDecodeError, TypeError, ValueError):
                settings = {}
        # the key was spelled 'currentPhone' on iOS and '_currentPhone' on Android in the
        # tested extractions, so both spellings are resolved rather than one replaced
        phone = settings.get('currentPhone', settings.get('_currentPhone', ''))
        public_key = user.get('publicKey') or ''
        private_key = user.get('privateKey') or ''
        sources.append(db_path)
        data_list.append((
            user.get('serverId', '') or '',
            user.get('alias', '') or '',
            user.get('userId', '') or '',
            user.get('personalId', '') or '',
            user.get('avatarRefId', '') or '',
            phone or '',
            'Yes' if public_key else 'No',
            _pem_fingerprint(public_key),
            'Yes' if private_key else 'No',
            _pem_fingerprint(private_key),
        ))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def teleguardDrafts(context):
    data_headers = (
        'Recipient Server ID',
        'Recipient Alias',
        'Draft Text',
    )
    data_list = []
    sources = []
    for paths in _group_containers(context).values():
        temp_path = _pick(paths, 'teleguard_temp.db')
        if not temp_path:
            continue
        rows = list(get_sqlite_db_records(temp_path, 'SELECT serverId, text FROM draft'))
        if not rows:
            continue
        sources.append(temp_path)
        aliases = {}
        db_path = _pick(paths, 'teleguard_database.db')
        if db_path:
            for server_id, alias in get_sqlite_db_records(
                    db_path, 'SELECT serverId, alias FROM contacts'):
                aliases[server_id] = alias
            if db_path not in sources:
                sources.append(db_path)
        for server_id, text in rows:
            data_list.append((server_id, aliases.get(server_id, ''), text or ''))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def teleguardAppSettings(context):
    data_headers = (
        ('Last Cache Clearing', 'datetime'),
        'Hide Push Content',
        'Hide Push Author',
        'Channel Notifications Enabled',
        'Unread Count',
        'Preferences File',
    )
    data_list = []
    sources = []

    # the cache-clearing value lives in the app's own data container, which is a
    # different container from the app group holding the databases and group plist
    app_paths = []
    for file_found in context.get_files_found():
        path = str(file_found)
        if (os.path.basename(path) == 'ch.swisscows.messenger.teleguardapp.plist'
                and path not in app_paths):
            app_paths.append(path)
    group_paths = []
    for paths in _group_containers(context).values():
        group_path = _pick(paths, 'group.ch.swisscows.messenger.teleguardapp.plist')
        if group_path:
            group_paths.append(group_path)

    def _group_values(path):
        plist = get_plist_file_content(path) or {}
        return (
            plist.get('hidePushContent', ''),
            plist.get('hidePushAuthor', ''),
            plist.get('enableChannelsNotifications', ''),
            plist.get('unreadCount', ''),
        )

    def _clearing(path):
        plist = get_plist_file_content(path) or {}
        return _ms_to_utc(plist.get('flutter.lastCacheClearing'))

    if len(app_paths) == 1 and len(group_paths) == 1:
        # one install: the two files are reported together
        sources.extend((group_paths[0], app_paths[0]))
        data_list.append(
            (_clearing(app_paths[0]),) + _group_values(group_paths[0])
            + ('\n'.join(context.get_relative_path(p) for p in sources),))
    else:
        # nothing read here ties a data container to an app group, so each file
        # is reported on its own row
        for path in group_paths:
            sources.append(path)
            data_list.append(('',) + _group_values(path) + (context.get_relative_path(path),))
        for path in app_paths:
            sources.append(path)
            data_list.append(
                (_clearing(path), '', '', '', '', context.get_relative_path(path)))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)
