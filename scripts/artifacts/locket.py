__artifacts_v2__ = {
    "locketAccount": {
        "name": "Locket - Account",
        "description": "The Locket user's own account, from the user document in the app's Firestore cache.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Social Media",
        "notes": ("Read from the Firestore cache (LevelDB, read with Alex Caithness's ccl_leveldb) under "
                  "Library/Application Support/firestore in the Locket app container. The account is the "
                  "users/<uid> document whose uid also owns the cached conversations, history and friend "
                  "documents. A profile is reported only when live owner-scoped paths identify a single uid. Field names are as stored; Firestore timestamps are UTC. The cache holds only "
                  "documents the app fetched, so it is not a full copy of the server account. Only a "
                  "container that also holds Library/Preferences/com.locket.Locket.plist is read."),
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/firestore/*/*/main/*',
                  '*/Containers/Data/Application/*/Library/Preferences/com.locket.Locket.plist'),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "locketFriends": {
        "name": "Locket - Friends",
        "description": "Locket friends and contacts known to the app, from light_friends_cache in the shared "
                       "app group container, with the friend documents of the Firestore cache.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Social Media",
        "notes": ("One row per uid in light_friends_cache (a JSON list in the group.com.locket.Locket-Shared "
                  "container). Friend is the file's friend key as stored; Temp is its temp key as stored. "
                  "In Friends Collection is Yes when the Firestore cache holds a users/<uid>/friends/<friend uid> "
                  "document for that uid. Unknown means the owner could not be established. On the tested image Friend and In Friends Collection were identical on every row. Only a group container that also holds "
                  "Library/Preferences/group.com.locket.Locket-Shared.plist, and an app container that also "
                  "holds Library/Preferences/com.locket.Locket.plist, are read."),
        "paths": ('*/Containers/Shared/AppGroup/*/light_friends_cache',
                  '*/Containers/Shared/AppGroup/*/Library/Preferences/group.com.locket.Locket-Shared.plist',
                  '*/Containers/Data/Application/*/Library/Application Support/firestore/*/*/main/*',
                  '*/Containers/Data/Application/*/Library/Preferences/com.locket.Locket.plist'),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "locketFriendRequests": {
        "name": "Locket - Friend Requests",
        "description": "Incoming and outgoing Locket friend requests from the app's Firestore cache.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Social Media",
        "notes": ("Documents under users/<uid>/incoming_friend_requests and outgoing_friend_requests. A Firestore no-document entry records "
                  "an observation of absence. Observed Absent holds its read time and Created is blank. "
                  "Event Time is the observation time for those rows and the creation time for live requests. "
                  "Direction and UIDs on absent rows come from the document path. Source, Messenger "
                  "and Platform are stored only on some requests and are blank where absent. Names are resolved "
                  "from light_friends_cache and the account document. Only containers that hold the Locket "
                  "preference files are read."),
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/firestore/*/*/main/*',
                  '*/Containers/Data/Application/*/Library/Preferences/com.locket.Locket.plist',
                  '*/Containers/Shared/AppGroup/*/light_friends_cache',
                  '*/Containers/Shared/AppGroup/*/Library/Preferences/group.com.locket.Locket-Shared.plist'),
        "output_types": "standard",
        "artifact_icon": "user-plus",
    },
    "locketMessages": {
        "name": "Locket - Messages",
        "description": "Locket chat messages from the app's Firestore cache.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Social Media",
        "notes": ("Documents under conversations/<conversation id>/messages. Members are taken from the "
                  "matching users/<uid>/conversations/<conversation id> document. Sender is the sender uid, "
                  "with the name resolved from light_friends_cache and the account document. Reply Moment and "
                  "Thumbnail URL were null on every tested message and are shown blank where null. The cache "
                  "holds only messages the app fetched. On the tested image every message was in one conversation, so Conversation ID and Members held one value on every row. Only containers "
                  "that hold the Locket preference files are read."),
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/firestore/*/*/main/*',
                  '*/Containers/Data/Application/*/Library/Preferences/com.locket.Locket.plist',
                  '*/Containers/Shared/AppGroup/*/light_friends_cache',
                  '*/Containers/Shared/AppGroup/*/Library/Preferences/group.com.locket.Locket-Shared.plist'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
    },
    "locketMoments": {
        "name": "Locket - Moments",
        "description": "Locket moments (shared photos) from the history entries of the app's Firestore cache, "
                       "with the cached thumbnail where the app's image cache holds it.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Social Media",
        "notes": ("Documents under history/<uid>/entries. Direction is Sent when the entry's user is the account "
                  "uid, Received when both uids are known and differ, and Unknown when either is unresolved. This reading matched known activity on one tested image and is not sourced from app documentation. Sent To All "
                  "and Sent To Self Only are stored only on some entries and are blank where absent. On the "
                  "tested image Sent To All and Sent To Self Only were identical on every row. Thumbnail is "
                  "the file in com.locket.imgcache of the shared app group container named with the MD5 of the "
                  "entry's thumbnail_url; that naming was measured, not sourced: on the tested image every entry had such a file. On the tested image the cached thumbnail's MD5 equalled the stored md5 on some entries and not on others. What md5 is computed over is not established. "
                  "Only a file starting with a WebP, JPEG or PNG signature is attached. Only containers that "
                  "hold the Locket preference files are read."),
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/firestore/*/*/main/*',
                  '*/Containers/Data/Application/*/Library/Preferences/com.locket.Locket.plist',
                  '*/Containers/Shared/AppGroup/*/com.locket.imgcache/*',
                  '*/Containers/Shared/AppGroup/*/light_friends_cache',
                  '*/Containers/Shared/AppGroup/*/Library/Preferences/group.com.locket.Locket-Shared.plist'),
        "output_types": "standard",
        "artifact_icon": "image",
    },
}

from dataclasses import dataclass
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


@dataclass
class _Document:
    parts: tuple
    exists: bool
    fields: dict
    read_time: datetime.datetime | None
    source: str


def _firestore_documents(files):
    """Resolve each remote key within the sequence space of its own LevelDB."""
    stores = {os.path.dirname(path) for (_, inner), path in files.items()
              if inner.startswith('Library/Application Support/firestore/')
              and (inner.endswith('/CURRENT') or
                   re.fullmatch(ccl_leveldb.RawLevelDb.DATA_FILE_PATTERN, os.path.basename(inner)))}
    documents = []
    for store in sorted(stores):
        if not os.path.isfile(os.path.join(store, 'CURRENT')):
            logfunc(f'Locket: CURRENT missing in {store}, reading available LevelDB records')
        latest = {}
        try:
            with ccl_leveldb.RawLevelDb(store) as database:
                for record in database.iterate_records_raw():
                    key = record.user_key
                    if key.startswith(_REMOTE_DOCUMENT) and (key not in latest or record.seq > latest[key].seq):
                        latest[key] = record
        except Exception as ex:  # pylint: disable=broad-except
            logfunc(f'Locket: could not read Firestore cache {store}: {ex}')
        for record in latest.values():
            if record.state != ccl_leveldb.KeyState.Live or not record.value:
                continue
            try:
                exists, path, fields, when = _maybe_document(record.value)
            except (ValueError, IndexError, struct.error, UnicodeDecodeError, OverflowError) as ex:
                logfunc(f'Locket: could not decode a document in {store}: {ex}')
                continue
            if exists is not None and path:
                parts = tuple(path.split('/documents/', 1)[-1].split('/'))
                documents.append(_Document(parts, exists, fields, when, str(record.origin_file)))
    return documents


def _containers(context):
    """Pair app and shared data only when the two markers identify a unique pair."""
    files = _locket_files(context)
    apps = [root for root, inner in files if inner == _APP_MARKER]
    groups = [root for root, inner in files if inner == _GROUP_MARKER]
    if len(apps) == len(groups) == 1:
        yield files
    else:
        for root in sorted(set(apps + groups)):
            yield {key: path for key, path in files.items() if key[0] == root}


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


def _account_uid(documents):
    owners = set()
    profiles = set()
    for doc in documents:
        parts = doc.parts
        if not doc.exists:
            continue
        if len(parts) == 2 and parts[0] == 'users':
            profiles.add(parts[1])
        if len(parts) == 4 and (parts[0], parts[2]) in {
                ('history', 'entries'), ('users', 'conversations'), ('users', 'friends'),
                ('users', 'incoming_friend_requests'), ('users', 'outgoing_friend_requests')}:
            owners.add(parts[1])
    if len(owners) == 1 and owners.issubset(profiles):
        return next(iter(owners))
    return ''


def _names(documents, friends):
    names = {}
    for entry in friends:
        if isinstance(entry, dict) and entry.get('uid'):
            names[entry['uid']] = ' '.join(x for x in (entry.get('first_name'), entry.get('last_name')) if x)
    uid = _account_uid(documents)
    owner_names = {' '.join(x for x in (doc.fields.get('first_name'), doc.fields.get('last_name')) if x)
                   for doc in documents if doc.exists and doc.parts == ('users', uid)}
    if len(owner_names) == 1:
        names[uid] = owner_names.pop()
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

def _result(context, headers, rows):
    """The artifact location lists all sources. Disambiguate individual rows when necessary."""
    sources = sorted({row[-1] for row in rows})
    if len(sources) > 1:
        return (*headers, 'Source File'), [(*r[:-1], context.get_relative_path(r[-1])) for r in rows], '\n'.join(sources)
    return headers, [r[:-1] for r in rows], '\n'.join(sources)


@artifact_processor
def locketAccount(context):
    rows = []
    for files in _containers(context):
        documents = _firestore_documents(files)
        uid = _account_uid(documents)
        for doc in documents:
            if not uid or not doc.exists or doc.parts != ('users', uid):
                continue
            f = doc.fields
            rows.append((f.get('created_at'), f.get('first_seen_at'), f.get('username_last_updated'),
                         f.get('last_friends_change'), uid, _blank(f.get('username')), _blank(f.get('first_name')),
                         _blank(f.get('last_name')), _blank(f.get('phone')), _blank(f.get('invite_token')), doc.source))
    headers = (('Created', 'datetime'), ('First Seen', 'datetime'), ('Username Last Updated', 'datetime'),
               ('Last Friends Change', 'datetime'), 'UID', 'Username', 'First Name', 'Last Name', 'Phone', 'Invite Token')
    return _result(context, headers, rows)


@artifact_processor
def locketFriends(context):
    rows = []
    for files in _containers(context):
        friends, source = _friends_cache(files)
        if not friends:
            continue
        documents = _firestore_documents(files)
        uid = _account_uid(documents)
        friend_uids = {doc.parts[3] for doc in documents if doc.exists and len(doc.parts) == 4
                       and doc.parts[:3] == ('users', uid, 'friends')}
        for entry in friends:
            if isinstance(entry, dict):
                membership = _yes_no(entry.get('uid') in friend_uids) if uid else 'Unknown'
                rows.append((_blank(entry.get('uid')), _blank(entry.get('username')), _blank(entry.get('first_name')),
                             _blank(entry.get('last_name')), _blank(entry.get('phone')), _yes_no(entry.get('friend')),
                             _yes_no(entry.get('temp')), _yes_no(entry.get('celebrity')), membership, source))
    headers = ('UID', 'Username', 'First Name', 'Last Name', 'Phone', 'Friend', 'Temp', 'Celebrity',
               'In Friends Collection')
    return _result(context, headers, rows)


@artifact_processor
def locketFriendRequests(context):
    rows = []
    for files in _containers(context):
        documents = _firestore_documents(files)
        friends, _ = _friends_cache(files)
        names = _names(documents, friends)
        for doc in documents:
            parts = doc.parts
            if len(parts) != 4 or parts[0] != 'users' or parts[2] not in (
                    'incoming_friend_requests', 'outgoing_friend_requests'):
                continue
            incoming = parts[2] == 'incoming_friend_requests'
            fields = doc.fields
            if doc.exists:
                requesting = fields.get('requesting_user') or ''
                requested = fields.get('requested_user') or ''
            else:
                requesting, requested = (parts[3], parts[1]) if incoming else (parts[1], parts[3])
            created = fields.get('created_at')
            rows.append((created if doc.exists else doc.read_time, created, doc.read_time,
                         'Incoming' if incoming else 'Outgoing', 'Exists' if doc.exists else 'Observed Absent',
                         requesting, names.get(requesting, ''), requested, names.get(requested, ''),
                         _blank(fields.get('source')), _blank(fields.get('messenger')), _blank(fields.get('platform')),
                         _yes_no(fields.get('share_history_eligible')), doc.source))
    # The timeline uses the first column as its event timestamp.
    headers = (('Event Time', 'datetime'), ('Created', 'datetime'), ('Observed Absent', 'datetime'),
               'Direction', 'State', 'Requesting User', 'Requesting Name', 'Requested User', 'Requested Name',
               'Source', 'Messenger', 'Platform', 'Share History Eligible')
    rows.sort(key=lambda row: row[0] or _EPOCH)
    return _result(context, headers, rows)


@artifact_processor
def locketMessages(context):
    rows = []
    for files in _containers(context):
        documents = _firestore_documents(files)
        friends, _ = _friends_cache(files)
        names = _names(documents, friends)
        members = {}
        for doc in documents:
            parts = doc.parts
            if doc.exists and len(parts) == 4 and parts[0] == 'users' and parts[2] == 'conversations':
                key = (os.path.dirname(doc.source), parts[3])
                member_list = doc.fields.get('members') or []
                members.setdefault(key, set()).add(', '.join(
                    f'{m} ({names[m]})' if names.get(m) else str(m) for m in member_list))
        for doc in documents:
            parts = doc.parts
            if not doc.exists or len(parts) != 4 or parts[0] != 'conversations' or parts[2] != 'messages':
                continue
            fields = doc.fields
            sender = fields.get('sender') or ''
            candidates = members.get((os.path.dirname(doc.source), parts[1]), set())
            rows.append((fields.get('created_at'), parts[1], next(iter(candidates)) if len(candidates) == 1 else '',
                         sender, names.get(sender, ''), _blank(fields.get('body')), _blank(fields.get('reply_moment')),
                         _blank(fields.get('thumbnail_url')), parts[3], doc.source))
    rows.sort(key=lambda row: (row[1], row[0] or _EPOCH))
    headers = (('Created', 'datetime'), 'Conversation ID', 'Members', 'Sender', 'Sender Name', 'Body',
               'Reply Moment', 'Thumbnail URL', 'Message ID')
    return _result(context, headers, rows)


def _thumbnail(url, images):
    cached = images.get(hashlib.md5(url.encode('utf-8')).hexdigest()) if url else None
    if cached:
        try:
            with open(cached, 'rb') as handle:
                head = handle.read(12)
            if head.startswith(_IMAGE_SIGNATURES) or (head[:4] == b'RIFF' and head[8:12] == b'WEBP'):
                return check_in_media(cached, os.path.basename(cached))
        except OSError as ex:
            logfunc(f'Locket: could not read {cached}: {ex}')
    return ''


@artifact_processor
def locketMoments(context):
    rows = []
    for files in _containers(context):
        documents = _firestore_documents(files)
        friends, _ = _friends_cache(files)
        names = _names(documents, friends)
        owner = _account_uid(documents)
        images = {os.path.basename(inner).split('.', 1)[0]: path for (_, inner), path in files.items()
                  if inner.startswith('com.locket.imgcache/') and inner.count('/') == 1}
        for doc in documents:
            parts = doc.parts
            if not doc.exists or len(parts) != 4 or parts[0] != 'history' or parts[2] != 'entries':
                continue
            fields = doc.fields
            user = fields.get('user') or ''
            url = fields.get('thumbnail_url') or ''
            direction = 'Unknown'
            if owner and user:
                direction = 'Sent' if owner == user else 'Received'
            rows.append((fields.get('date'), direction, user, names.get(user, ''), _thumbnail(url, images),
                         _yes_no(fields.get('sent_to_all')), _yes_no(fields.get('sent_to_self_only')),
                         _blank(fields.get('md5')), url, parts[3], doc.source))
    rows.sort(key=lambda row: row[0] or _EPOCH)
    headers = (('Date', 'datetime'), 'Direction', 'User', 'User Name', ('Thumbnail', 'media'),
               'Sent To All', 'Sent To Self Only', 'MD5', 'Thumbnail URL', 'Moment ID')
    return _result(context, headers, rows)
