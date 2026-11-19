__artifacts_v2__ = {
    "locketAccount": {
        "name": "Locket - Account",
        "description": "The Locket user's own account, from the user document in the app's Firestore cache.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Locket",
        "notes": ("Read from the Firestore cache (LevelDB, read with Alex Caithness's ccl_leveldb) under "
                  "Library/Application Support/firestore in the Locket app container. The account is the "
                  "users/<uid> document whose uid also owns the cached conversations, history and friend "
                  "documents. Field names are as stored; Firestore timestamps are UTC. The cache holds only "
                  "documents the app fetched, so it is not a full copy of the server account. Only a "
                  "container that also holds Library/Preferences/com.locket.Locket.plist is read."),
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/firestore/*/*/main/*',
                  '*/Containers/Data/Application/*/Library/Preferences/com.locket.Locket.plist'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Locket 2.71.2 | 1 row",
        }
    },
    "locketFriends": {
        "name": "Locket - Friends",
        "description": "Locket friends and contacts known to the app, from light_friends_cache in the shared "
                       "app group container, with the friend documents of the Firestore cache.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Locket",
        "notes": ("One row per uid in light_friends_cache (a JSON list in the group.com.locket.Locket-Shared "
                  "container). Friend is the file's friend key as stored; Temp is its temp key as stored. "
                  "In Friends Collection is Yes when the Firestore cache holds a users/<uid>/friends/<friend uid> "
                  "document for that uid. On the tested image Friend and In Friends Collection were identical "
                  "on both rows. Only a group container that also holds "
                  "Library/Preferences/group.com.locket.Locket-Shared.plist, and an app container that also "
                  "holds Library/Preferences/com.locket.Locket.plist, are read."),
        "paths": ('*/Containers/Shared/AppGroup/*/light_friends_cache',
                  '*/Containers/Shared/AppGroup/*/Library/Preferences/group.com.locket.Locket-Shared.plist',
                  '*/Containers/Data/Application/*/Library/Application Support/firestore/*/*/main/*',
                  '*/Containers/Data/Application/*/Library/Preferences/com.locket.Locket.plist'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Locket 2.71.2 | 2 rows",
        }
    },
    "locketFriendRequests": {
        "name": "Locket - Friend Requests",
        "description": "Incoming and outgoing Locket friend requests from the app's Firestore cache.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Locket",
        "notes": ("Documents under users/<uid>/incoming_friend_requests and outgoing_friend_requests. A request "
                  "the cache records as no longer existing (a Firestore no-document entry, as stored) is kept with State No Longer Exists and its read time as "
                  "Created; on the tested image the one incoming request was in that state. Source, Messenger "
                  "and Platform are stored only on some requests and are blank where absent. Names are resolved "
                  "from light_friends_cache and the account document. Only containers that hold the Locket "
                  "preference files are read."),
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/firestore/*/*/main/*',
                  '*/Containers/Data/Application/*/Library/Preferences/com.locket.Locket.plist',
                  '*/Containers/Shared/AppGroup/*/light_friends_cache',
                  '*/Containers/Shared/AppGroup/*/Library/Preferences/group.com.locket.Locket-Shared.plist'),
        "output_types": "standard",
        "artifact_icon": "user-plus",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Locket 2.71.2 | 3 rows",
        }
    },
    "locketMessages": {
        "name": "Locket - Messages",
        "description": "Locket chat messages from the app's Firestore cache.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Locket",
        "notes": ("Documents under conversations/<conversation id>/messages. Members are taken from the "
                  "matching users/<uid>/conversations/<conversation id> document. Sender is the sender uid, "
                  "with the name resolved from light_friends_cache and the account document. Reply Moment and "
                  "Thumbnail URL were null on every tested message and are shown blank where null. The cache "
                  "holds only messages the app fetched. On the tested image all 3 messages were in one "
                  "conversation, so Conversation ID and Members held one value on all 3 rows. Only containers "
                  "that hold the Locket preference files are read."),
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/firestore/*/*/main/*',
                  '*/Containers/Data/Application/*/Library/Preferences/com.locket.Locket.plist',
                  '*/Containers/Shared/AppGroup/*/light_friends_cache',
                  '*/Containers/Shared/AppGroup/*/Library/Preferences/group.com.locket.Locket-Shared.plist'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Locket 2.71.2 | 3 rows",
        }
    },
    "locketMoments": {
        "name": "Locket - Moments",
        "description": "Locket moments (shared photos) from the history entries of the app's Firestore cache, "
                       "with the cached thumbnail where the app's image cache holds it.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Locket",
        "notes": ("Documents under history/<uid>/entries. Direction is Sent when the entry's user is the account "
                  "uid and Received otherwise; this reading was verified against known activity on the tested "
                  "image, not sourced from app documentation. Sent To All "
                  "and Sent To Self Only are stored only on some entries and are blank where absent. On the "
                  "tested image Sent To All and Sent To Self Only were identical on both rows. Thumbnail is "
                  "the file in com.locket.imgcache of the shared app group container named with the MD5 of the "
                  "entry's thumbnail_url; that naming was measured, not sourced: on the tested image both entries "
                  "had such a file. On the tested image the cached thumbnail's MD5 equalled the stored md5 on 1 "
                  "of the 2 entries. What md5 is computed over is not established. "
                  "Only a file starting with a WebP, JPEG or PNG signature is attached. Only containers that "
                  "hold the Locket preference files are read."),
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/firestore/*/*/main/*',
                  '*/Containers/Data/Application/*/Library/Preferences/com.locket.Locket.plist',
                  '*/Containers/Shared/AppGroup/*/com.locket.imgcache/*',
                  '*/Containers/Shared/AppGroup/*/light_friends_cache',
                  '*/Containers/Shared/AppGroup/*/Library/Preferences/group.com.locket.Locket-Shared.plist'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | Locket 2.71.2 | 2 rows",
        }
    },
}

import datetime
import hashlib
import json
import os
import re
import struct

from scripts.vendor.ccl import ccl_leveldb
from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc

_APP_MARKER = 'Library/Preferences/com.locket.Locket.plist'
_GROUP_MARKER = 'Library/Preferences/group.com.locket.Locket-Shared.plist'
_CONTAINER = re.compile(r'(.*?/Containers/(?:Data/Application|Shared/AppGroup)/[^/]+)/(.*)$')
_REMOTE_DOCUMENT = b'\x85remote_document\x00'
_IMAGE_SIGNATURES = (b'\xff\xd8\xff', b'\x89PNG\r\n\x1a\n')
_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


# --- Firestore protobuf (MaybeDocument / Document / Value), decoded by field number ---------------

def _varint(buf, pos):
    result = shift = 0
    while True:
        byte = buf[pos]
        pos += 1
        result |= (byte & 0x7f) << shift
        shift += 7
        if byte < 0x80:
            return result, pos


def _fields(buf):
    pos = 0
    out = []
    while pos < len(buf):
        key, pos = _varint(buf, pos)
        number, wire = key >> 3, key & 7
        if wire == 0:
            value, pos = _varint(buf, pos)
        elif wire == 1:
            value = buf[pos:pos + 8]
            pos += 8
        elif wire == 5:
            value = buf[pos:pos + 4]
            pos += 4
        elif wire == 2:
            length, pos = _varint(buf, pos)
            value = buf[pos:pos + length]
            pos += length
        else:
            raise ValueError(f'unsupported wire type {wire}')
        out.append((number, wire, value))
    return out


def _timestamp(buf):
    seconds = nanos = 0
    for number, _, value in _fields(buf):
        if number == 1:
            seconds = value
        elif number == 2:
            nanos = value
    return _EPOCH + datetime.timedelta(seconds=seconds, microseconds=nanos // 1000)


def _map(buf):
    result = {}
    for number, _, entry in _fields(buf):
        if number != 1:
            continue
        key = value = None
        for field, _, data in _fields(entry):
            if field == 1:
                key = data.decode('utf-8', 'replace')
            elif field == 2:
                value = _value(data)
        result[key] = value
    return result


def _value(buf):
    # google.firestore.v1.Value oneof
    for number, _, data in _fields(buf):
        if number == 11:
            return None
        if number == 1:
            return bool(data)
        if number == 2:
            return data - (1 << 64) if data >= 1 << 63 else data
        if number == 3:
            return struct.unpack('<d', data)[0]
        if number == 10:
            return _timestamp(data)
        if number == 17:
            return data.decode('utf-8', 'replace')
        if number == 18:
            return data.hex()
        if number == 5:
            return data.decode('utf-8', 'replace')
        if number == 8:
            point = {field: struct.unpack('<d', raw)[0] for field, _, raw in _fields(data)}
            return f'{point.get(1, "")}, {point.get(2, "")}'
        if number == 9:
            return [_value(item) for field, _, item in _fields(data) if field == 1]
        if number == 6:
            return _map(data)
    return None


def _maybe_document(buf):
    """Return (exists, path, fields, time). time is the read time of a no-document entry."""
    for number, wire, data in _fields(buf):
        if wire != 2:
            continue
        if number == 2:
            path = ''
            fields = {}
            for field, _, raw in _fields(data):
                if field == 1:
                    path = raw.decode('utf-8', 'replace')
                elif field == 2:
                    key = value = None
                    for part, _, item in _fields(raw):
                        if part == 1:
                            key = item.decode('utf-8', 'replace')
                        elif part == 2:
                            value = _value(item)
                    fields[key] = value
            return True, path, fields, None
        if number == 1:
            path = ''
            read_time = None
            for field, _, raw in _fields(data):
                if field == 1:
                    path = raw.decode('utf-8', 'replace')
                elif field == 2:
                    read_time = _timestamp(raw)
            return False, path, {}, read_time
    return None, '', {}, None


# --- locating Locket's files ------------------------------------------------------------------------

def _split(context, file_found):
    match = _CONTAINER.match(context.get_relative_path(str(file_found)).replace('\\', '/'))
    return (match.group(1), match.group(2)) if match else ('', '')


def _locket_files(context):
    """{(container, inner path): file} for files in containers that hold a Locket marker."""
    entries = {}
    markers = set()
    for file_found in dict.fromkeys(str(found) for found in context.get_files_found()):
        container, inner = _split(context, file_found)
        if not container:
            continue
        if inner in (_APP_MARKER, _GROUP_MARKER):
            markers.add(container)
        entries[(container, inner)] = file_found
    return {key: path for key, path in entries.items() if key[0] in markers}


def _firestore_documents(files):
    """{document path: (exists, fields, time, source file)}, the newest live record of each key."""
    stores = {os.path.dirname(path) for (_, inner), path in files.items()
              if inner.startswith('Library/Application Support/firestore/') and inner.endswith('/CURRENT')}
    latest = {}
    for store in sorted(stores):
        try:
            records = list(ccl_leveldb.RawLevelDb(store).iterate_records_raw())
        except Exception as ex:  # pylint: disable=broad-except
            logfunc(f'Locket: could not read Firestore cache {store}: {ex}')
            continue
        for record in records:
            if not record.user_key.startswith(_REMOTE_DOCUMENT) or not record.value:
                continue
            if record.state != ccl_leveldb.KeyState.Live:
                continue
            try:
                exists, path, fields, when = _maybe_document(record.value)
            except (ValueError, IndexError, struct.error, UnicodeDecodeError) as ex:
                logfunc(f'Locket: could not decode a document in {store}: {ex}')
                continue
            if exists is None or not path:
                continue
            doc_path = path.split('/documents/', 1)[-1]
            previous = latest.get(doc_path)
            if previous is None or record.seq > previous[0]:
                latest[doc_path] = (record.seq, exists, fields, when, store)
    return {path: value[1:] for path, value in latest.items()}


def _friends_cache(files):
    """(rows from light_friends_cache, its path)."""
    for (_, inner), path in files.items():
        if inner == 'light_friends_cache':
            try:
                with open(path, 'r', encoding='utf-8') as handle:
                    data = json.load(handle)
                return (data if isinstance(data, list) else []), path
            except (OSError, ValueError) as ex:
                logfunc(f'Locket: could not read {path}: {ex}')
    return [], ''


def _account(documents):
    for path, (exists, fields, _, store) in documents.items():
        parts = path.split('/')
        if exists and len(parts) == 2 and parts[0] == 'users':
            return parts[1], fields, store
    return '', {}, ''


def _names(documents, friends):
    names = {}
    for entry in friends:
        if isinstance(entry, dict) and entry.get('uid'):
            names[entry['uid']] = ' '.join(x for x in (entry.get('first_name'), entry.get('last_name')) if x)
    uid, fields, _ = _account(documents)
    if uid:
        names[uid] = ' '.join(x for x in (fields.get('first_name'), fields.get('last_name')) if x)
    return names


def _blank(value):
    if value is None:
        return ''
    if isinstance(value, (list, dict)):
        return json.dumps(value, default=str, ensure_ascii=False)
    return value


def _yes_no(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


# --- artifacts --------------------------------------------------------------------------------------

@artifact_processor
def locketAccount(context):
    documents = _firestore_documents(_locket_files(context))
    uid, fields, store = _account(documents)
    data_list = []
    if uid:
        data_list.append((
            fields.get('created_at'), fields.get('first_seen_at'), uid, _blank(fields.get('username')),
            _blank(fields.get('first_name')), _blank(fields.get('last_name')), _blank(fields.get('phone')),
            fields.get('username_last_updated'), fields.get('last_friends_change'),
            _blank(fields.get('invite_token'))))
    data_headers = (('Created', 'datetime'), ('First Seen', 'datetime'), 'UID', 'Username', 'First Name',
                    'Last Name', 'Phone', ('Username Last Updated', 'datetime'),
                    ('Last Friends Change', 'datetime'), 'Invite Token')
    return data_headers, data_list, store


@artifact_processor
def locketFriends(context):
    files = _locket_files(context)
    documents = _firestore_documents(files)
    friends, source = _friends_cache(files)
    uid, _, _ = _account(documents)
    friend_docs = {path.rsplit('/', 1)[-1] for path, (exists, _, _, _) in documents.items()
                   if exists and path.startswith(f'users/{uid}/friends/')} if uid else set()
    data_list = []
    for entry in friends:
        if not isinstance(entry, dict):
            continue
        data_list.append((
            _blank(entry.get('uid')), _blank(entry.get('username')), _blank(entry.get('first_name')),
            _blank(entry.get('last_name')), _blank(entry.get('phone')), _yes_no(entry.get('friend')),
            _yes_no(entry.get('temp')), _yes_no(entry.get('celebrity')),
            'Yes' if entry.get('uid') in friend_docs else 'No'))
    data_headers = ('UID', 'Username', 'First Name', 'Last Name', 'Phone', 'Friend', 'Temp', 'Celebrity',
                    'In Friends Collection')
    return data_headers, data_list, source


@artifact_processor
def locketFriendRequests(context):
    files = _locket_files(context)
    documents = _firestore_documents(files)
    friends, _ = _friends_cache(files)
    names = _names(documents, friends)
    data_list = []
    sources = set()
    for path, (exists, fields, when, store) in sorted(documents.items()):
        parts = path.split('/')
        if len(parts) != 4 or parts[0] != 'users' or parts[2] not in (
                'incoming_friend_requests', 'outgoing_friend_requests'):
            continue
        direction = 'Incoming' if parts[2].startswith('incoming') else 'Outgoing'
        other = parts[3]
        if exists:
            requesting = fields.get('requesting_user') or ''
            requested = fields.get('requested_user') or ''
            data_list.append((
                fields.get('created_at'), direction, 'Exists', _blank(requesting), names.get(requesting, ''),
                _blank(requested), names.get(requested, ''), _blank(fields.get('source')),
                _blank(fields.get('messenger')), _blank(fields.get('platform')),
                _yes_no(fields.get('share_history_eligible'))))
        else:
            requesting, requested = (other, parts[1]) if direction == 'Incoming' else (parts[1], other)
            data_list.append((
                when, direction, 'No Longer Exists', requesting, names.get(requesting, ''), requested,
                names.get(requested, ''), '', '', '', ''))
        sources.add(store)
    data_headers = (('Created', 'datetime'), 'Direction', 'State', 'Requesting User', 'Requesting Name',
                    'Requested User', 'Requested Name', 'Source', 'Messenger', 'Platform',
                    'Share History Eligible')
    return data_headers, data_list, '\n'.join(sorted(sources))


@artifact_processor
def locketMessages(context):
    files = _locket_files(context)
    documents = _firestore_documents(files)
    friends, _ = _friends_cache(files)
    names = _names(documents, friends)
    members = {}
    for path, (exists, fields, _, _) in documents.items():
        parts = path.split('/')
        if exists and len(parts) == 4 and parts[0] == 'users' and parts[2] == 'conversations':
            member_list = fields.get('members') or []
            members[parts[3]] = ', '.join(
                f'{m} ({names[m]})' if names.get(m) else str(m) for m in member_list)
    data_list = []
    sources = set()
    for path, (exists, fields, _, store) in sorted(documents.items()):
        parts = path.split('/')
        if not exists or len(parts) != 4 or parts[0] != 'conversations' or parts[2] != 'messages':
            continue
        sender = fields.get('sender') or ''
        data_list.append((
            fields.get('created_at'), parts[1], members.get(parts[1], ''), _blank(sender),
            names.get(sender, ''), _blank(fields.get('body')), _blank(fields.get('reply_moment')),
            _blank(fields.get('thumbnail_url')), parts[3]))
        sources.add(store)
    data_list.sort(key=lambda row: (row[1], row[0] or _EPOCH))
    data_headers = (('Created', 'datetime'), 'Conversation ID', 'Members', 'Sender', 'Sender Name', 'Body',
                    'Reply Moment', 'Thumbnail URL', 'Message ID')
    return data_headers, data_list, '\n'.join(sorted(sources))


@artifact_processor
def locketMoments(context):
    files = _locket_files(context)
    documents = _firestore_documents(files)
    friends, _ = _friends_cache(files)
    names = _names(documents, friends)
    account_uid, _, _ = _account(documents)
    images = {os.path.basename(inner).split('.', 1)[0]: path for (_, inner), path in files.items()
              if inner.startswith('com.locket.imgcache/') and inner.count('/') == 1}
    data_list = []
    sources = set()
    for path, (exists, fields, _, store) in sorted(documents.items()):
        parts = path.split('/')
        if not exists or len(parts) != 4 or parts[0] != 'history' or parts[2] != 'entries':
            continue
        user = fields.get('user') or ''
        url = fields.get('thumbnail_url') or ''
        thumbnail = ''
        cached = images.get(hashlib.md5(url.encode('utf-8')).hexdigest()) if url else None
        if cached:
            try:
                with open(cached, 'rb') as handle:
                    head = handle.read(12)
                if head.startswith(_IMAGE_SIGNATURES) or (head[:4] == b'RIFF' and head[8:12] == b'WEBP'):
                    thumbnail = check_in_media(cached, os.path.basename(cached))
            except OSError as ex:
                logfunc(f'Locket: could not read {cached}: {ex}')
        data_list.append((
            fields.get('date'), 'Sent' if account_uid and user == account_uid else 'Received', _blank(user),
            names.get(user, ''), thumbnail, _yes_no(fields.get('sent_to_all')),
            _yes_no(fields.get('sent_to_self_only')), _blank(fields.get('md5')), url, parts[3]))
        sources.add(store)
    data_list.sort(key=lambda row: row[0] or _EPOCH)
    data_headers = (('Date', 'datetime'), 'Direction', 'User', 'User Name', ('Thumbnail', 'media'),
                    'Sent To All', 'Sent To Self Only', 'MD5', 'Thumbnail URL', 'Moment ID')
    return data_headers, data_list, '\n'.join(sorted(sources))
