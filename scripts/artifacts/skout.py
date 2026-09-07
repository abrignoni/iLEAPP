__artifacts_v2__ = {
    "skout_ios_chat_messages": {
        "name": "Skout - Chat Messages",
        "description": "Messages held in the Skout app's chat cache, with the sender and recipient "
                       "identifiers each row carries.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Skout",
        "notes": "One row per row of ZSKCACHEDCHATMESSAGE in Library/Application "
                 "Support/SKOUT/SKCache.sqlite. Each row carries an NSKeyedArchiver blob as well "
                 "as its columns, and the blob is where the sender, the recipient, the message "
                 "type and any picture address live, so it is read and its keys are used as it "
                 "names them. Message Date is a Core Data time, seconds since 2001, reported in "
                 "UTC, and the nine rows on the one tested image that holds them fall inside "
                 "thirteen minutes of one day in the period the image covers. **Direction is "
                 "worked out from identifiers the app recorded**, not guessed: the blob names a "
                 "from and a to user, the chat row points at the cached user it is a chat with, "
                 "and a message whose sender is that cached user is read as incoming. On the "
                 "tested image that gives 5 outgoing and 4 incoming, and both identifiers are "
                 "reported so the reading can be checked. Message takes the text column, and "
                 "falls back to the blob's own description where the column is empty, which is "
                 "what fills the row that says a picture was sent; two rows are picture messages "
                 "with no text in either place and are left blank. Three rows carry a picture "
                 "address, two addresses between them, and all three are shown: the app keeps the "
                 "picture in its own remote image cache under a name that is the address, and "
                 "each cache entry is an archive wrapping the image, so the wrapper is opened and "
                 "the bytes are attached only when they carry a JPEG or PNG signature. An address "
                 "can have several entries at different sizes and one of them may hold no image, "
                 "so every entry whose name carries the picture's identifier is read and the "
                 "largest that yields one is used. That cache folder is named for the image "
                 "library rather than for the app, so an entry is only used for a store in the "
                 "same container. One row carries a negative message identifier and no type, and "
                 "its picture address is the same as another row's, so a picture can be named "
                 "twice. Chat Partner ID holds one value across all nine rows because the store "
                 "held one conversation. Deleted Locally read No on all nine rows. The store also "
                 "sits beside an advertising library's own database under Library/Caches, which "
                 "is that library's and is read by nothing here.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/SKOUT/SKCache.sqlite*',
                  '*/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
                           "hickman_ios13": "iOS 13.3.1 | Skout | 9 rows",
                       },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat Partner ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Date",
                "senderColumn": "From User ID",
                "mediaColumn": "Picture",
            }
        },
    },
    "skout_ios_cached_users": {
        "name": "Skout - Cached Users",
        "description": "Profiles the Skout app cached for the accounts it holds a chat with, with "
                       "the place and distance each profile carries.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Skout",
        "notes": "One row per row of ZSKCACHEDUSER in Library/Application "
                 "Support/SKOUT/SKCache.sqlite. The row carries an NSKeyedArchiver blob and "
                 "almost everything reported here comes out of it, under the key names the "
                 "archive itself uses. Cached and Last Seen are Core Data times, seconds since "
                 "2001, reported in UTC. The one tested image that holds the store has a single "
                 "row, the account the device was chatting with, so this is not an address book "
                 "and one row cannot show what the table looks like with several. Gender, Online "
                 "Status, Friend Status, Blocked Status and Favorite Status hold the app's own "
                 "vocabulary and are reported exactly as stored rather than translated. City, "
                 "State, Country and Distance come from the profile's location, which on this row "
                 "names a town, a state and a country with a distance of 0.5 and no coordinates: "
                 "Latitude and Longitude are present in the archive and empty on this row, so "
                 "they are reported and blank. Profile Picture URL is an address on the app's "
                 "servers, and the picture itself is attached from the same image cache the "
                 "messages use. On the one tested row that address is the app's own default "
                 "avatar rather than a photograph, so the attached picture shows what the app "
                 "displayed and not the person.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/SKOUT/SKCache.sqlite*',
                  '*/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINRemoteImageManagerCache/*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
                           "hickman_ios13": "iOS 13.3.1 | Skout | 1 row",
                       },
    },
}

import os
import plistlib
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media,
                               does_table_exist_in_db, get_sqlite_db_records, logfunc)

_CORE_DATA_EPOCH_UTC = datetime(2001, 1, 1, tzinfo=timezone.utc)
_CONTAINER = re.compile(r'(.*/Containers/Data/Application/[^/]+)/', re.I)
_CACHE = 'com.pinterest.PINDiskCache.PINRemoteImageManagerCache'
_JPEG = b'\xff\xd8\xff'
_PNG = b'\x89PNG'


def _stores(files_found):
    '''Every SKCache.sqlite among the matches, directories and sidecars skipped.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or path.endswith(('-wal', '-shm')):
            continue
        if os.path.basename(path) == 'SKCache.sqlite' and path not in seen:
            seen.append(path)
    return seen


def _container(path):
    '''The app data container a file sits in, or '' when it is not under one.'''
    match = _CONTAINER.match(str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _cached_images(files_found):
    '''[(container, decoded cache key, path)] for the app's own remote image cache.

    The cache folder is named for the image library rather than for the app, so every entry is
    kept with the container it was found in and is only used for a store in that same container.
    '''
    entries = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path) or f'/{_CACHE}/' not in path.replace('\\', '/'):
            continue
        entries.append((_container(path), unquote(os.path.basename(path)), path))
    return entries


def _rows(path, table, columns):
    '''Rows of a table, or nothing when the store does not have it.'''
    if not does_table_exist_in_db(path, table):
        return []
    try:
        return list(get_sqlite_db_records(path, f'SELECT {columns} FROM {table}'))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Skout: could not read {table}: {error}')
        return []


def _text(value):
    '''A stored value as text, with a stored null or an archived null read as absent.'''
    if value is None or value == '$null':
        return ''
    return str(value)


def _core_data_to_utc(value):
    '''Core Data seconds since 2001 to an aware UTC datetime, or ''.'''
    if value in (None, '', 0):
        return ''
    try:
        return _CORE_DATA_EPOCH_UTC + timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _archive(blob):
    '''The root object of an NSKeyedArchiver blob with its references resolved, or {}.'''
    if not blob:
        return {}
    try:
        plist = plistlib.loads(bytes(blob))
        objects = plist['$objects']
        root = plist['$top']['root']
    except Exception:                            # pylint: disable=broad-except
        return {}

    def walk(node, depth=0):
        if isinstance(node, plistlib.UID):
            return walk(objects[node.data], depth + 1)
        if isinstance(node, dict):
            if 'NS.string' in node:
                return node['NS.string']
            if 'NS.time' in node:
                return node['NS.time']
            if depth > 6:
                return None
            return {k: walk(v, depth + 1) for k, v in node.items() if k != '$class'}
        if isinstance(node, list):
            return [walk(v, depth + 1) for v in node]
        return node

    value = walk(root)
    return value if isinstance(value, dict) else {}


def _cached_image_bytes(path):
    """The picture a cache entry holds, or b''.

    An entry is either the picture itself or an NSKeyedArchiver wrapper around one data
    object, which is what this cache writes, so both forms are read and neither is assumed:
    the bytes are only returned when they carry a JPEG or PNG signature.
    """
    try:
        with open(path, 'rb') as handle:
            raw = handle.read()
    except OSError:
        return b''
    if raw.startswith(_JPEG) or raw.startswith(_PNG):
        return raw
    if not raw.startswith(b'bplist00'):
        return b''
    try:
        objects = plistlib.loads(raw).get('$objects') or []
    except Exception:                            # pylint: disable=broad-except
        return b''
    for obj in objects:
        if isinstance(obj, (bytes, bytearray)):
            data = bytes(obj)
            if data.startswith(_JPEG) or data.startswith(_PNG):
                return data
    return b''


def _picture_id(url):
    '''The identifier part of a message picture address, or ''.'''
    name = os.path.basename(_text(url).split('?')[0])
    return os.path.splitext(name)[0]


def _cached_picture(images, container, url):
    """The largest readable copy of a picture the app cached, as a media reference, or ''.

    A cache entry is named for the address it was fetched from, so an address can have several
    entries at different sizes and one of them may hold no image at all. Every entry whose name
    carries the picture's identifier is read and the largest that yields a JPEG or PNG is used,
    so the choice does not depend on the order the files were found in.
    """
    wanted = _picture_id(url)
    if not wanted:
        return ''
    best = b''
    best_path = ''
    for (its_container, key, path) in images:
        if its_container != container or wanted not in key:
            continue
        data = _cached_image_bytes(path)
        if len(data) > len(best):
            best, best_path = data, path
    return check_in_embedded_media(best_path, best, wanted) if best else ''


@artifact_processor
def skout_ios_chat_messages(context):
    data_list = []
    sources = []
    files_found = context.get_files_found()
    images = _cached_images(files_found)
    for source_path in _stores(files_found):
        sources.append(source_path)
        container = _container(source_path)
        partners = {}
        for (chat_pk, user_pk) in _rows(source_path, 'ZSKCACHEDCHAT', 'Z_PK, ZCACHEDUSER'):
            partners[chat_pk] = user_pk
        user_ids = {}
        for (user_pk, user_id) in _rows(source_path, 'ZSKCACHEDUSER', 'Z_PK, ZSKOUTUSERID'):
            user_ids[user_pk] = _text(user_id)
        for (stamp, text, message_id, user_id, chat, deleted, blob) in _rows(
                source_path, 'ZSKCACHEDCHATMESSAGE',
                'ZSKOUTMESSAGEDATE, ZSKOUTMESSAGETEXT, ZSKOUTMESSAGEID, ZSKOUTUSERID, ZCHAT, '
                'ZDELETEDLOCALLY, ZSKOUTMESSAGE'):
            archive = _archive(blob)
            partner = user_ids.get(partners.get(chat, ''), _text(user_id))
            sender = _text(archive.get('fromUserId'))
            direction = ''
            if sender and partner:
                direction = 'Incoming' if sender == partner else 'Outgoing'
            picture_url = _text(archive.get('pictureUrl'))
            media = _cached_picture(images, container, picture_url) if picture_url else ''
            data_list.append((
                _core_data_to_utc(stamp), direction, _text(archive.get('fromUserId')),
                _text(text) or _text(archive.get('description')), media,
                _text(archive.get('toUserId')), picture_url,
                _text(archive.get('type')), partner, _text(message_id),
                'Yes' if deleted else 'No', _text(archive.get('unreadCount')),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (
        ('Message Date', 'datetime'), 'Direction', 'From User ID', 'Message',
        ('Picture', 'media'), 'To User ID', 'Picture URL', 'Message Type (as stored)',
        'Chat Partner ID', 'Message ID (as stored)', 'Deleted Locally',
        'Unread Count (as stored)',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def skout_ios_cached_users(context):
    data_list = []
    sources = []
    files_found = context.get_files_found()
    images = _cached_images(files_found)
    for source_path in _stores(files_found):
        sources.append(source_path)
        container = _container(source_path)
        for (user_id, username, stamp, blob) in _rows(
                source_path, 'ZSKCACHEDUSER',
                'ZSKOUTUSERID, ZSKOUTUSERNAME, ZTIMESTAMP, ZSKOUTUSER'):
            archive = _archive(blob)
            location = archive.get('userLocation') or {}
            if not isinstance(location, dict):
                location = {}
            profile_url = _text(archive.get('pictureUrl'))
            picture = _cached_picture(images, container, profile_url) if profile_url else ''
            data_list.append((
                _core_data_to_utc(stamp), _core_data_to_utc(archive.get('lastSeen')),
                _text(user_id) or _text(archive.get('userId')),
                _text(archive.get('firstname')) or _text(username),
                _text(archive.get('age')), _text(archive.get('gender')),
                _text(archive.get('onlineStatus')),
                _text(location.get('city')), _text(location.get('state')),
                _text(location.get('country')), _text(location.get('distance')),
                _text(location.get('latitude')), _text(location.get('longitude')),
                picture, profile_url, _text(archive.get('friendStatus')),
                _text(archive.get('blockedStatus')), _text(archive.get('favoriteStatus')),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)
    data_headers = (
        ('Cached', 'datetime'), ('Last Seen', 'datetime'), 'User ID', 'Name',
        'Age (as stored)', 'Gender (as stored)', 'Online Status (as stored)',
        'City', 'State', 'Country', 'Distance (as stored)', 'Latitude', 'Longitude',
        ('Profile Picture', 'media'), 'Profile Picture URL', 'Friend Status (as stored)',
        'Blocked Status (as stored)', 'Favorite Status (as stored)',
    )
    return data_headers, data_list, '\n'.join(sources)
