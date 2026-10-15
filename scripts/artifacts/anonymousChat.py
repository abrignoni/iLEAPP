__artifacts_v2__ = {
    'anonymousChat_appInfo': {
        'name': 'Anonymous Chat & Fun - Application Info',
        'description': 'Bundle and data containers of the iOS app "Anonymous Chat & Fun" '
                       '(bundle ID com.anonimchat.app), identified from the container metadata plist, the '
                       'app\'s own plists or the backup domain name.',
        'author': '@darren33',
        'creation_date': '2026-09-11',
        'last_update_date': '2026-10-15',
        'requirements': 'none',
        'category': 'Anonymous Chat & Fun',
        'notes': 'One row per container that names com.anonimchat.app: a bundle or data '
                 'container whose .com.apple.mobile_container_manager.metadata.plist holds '
                 'the bundle ID in MCMMetadataIdentifier, a data container holding '
                 'Library/Preferences/com.anonimchat.app.plist, a bundle container whose '
                 'Info.plist or iTunesMetadata.plist names the bundle ID, or an iTunes backup '
                 'AppDomain, where the bundle ID takes the place of the container UUID. '
                 'In an iTunes backup, the app database path can identify its AppDomain even '
                 'when container metadata and preference plists are absent; this artifact does '
                 'not read the database contents. The AppDomain fallback is covered by a '
                 'generated synthetic iTunes backup regression test; no device-derived case '
                 'data is committed. '
                 'Application name, version, build and store fields come from the bundle container\'s Info.plist '
                 'and iTunesMetadata.plist and are blank for data containers.',
        'paths': (
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.anonimchat.app.plist',
            '*/Containers/Data/Application/*/Library/LocalDatabase/anonimchat.db*',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/*.app/Info.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/iTunesMetadata.plist',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'package',
        'sample_data': {
            'anonymous_chat_synthetic': 'Synthetic test case built by '
                                        'admin/test/scripts/build_anonymous_chat_fixture.py, '
                                        'not a device extraction | 2 rows',
        },
    },
    'anonymousChat_accounts': {
        'name': 'Anonymous Chat & Fun - Accounts',
        'description': 'Usernames that take part in the conversations stored by the iOS app '
                       '"Anonymous Chat & Fun" (bundle ID com.anonimchat.app), with message '
                       'counts and any signed-in username found in the app\'s AsyncStorage.',
        'author': '@darren33',
        'creation_date': '2026-09-11',
        'last_update_date': '2026-10-14',
        'requirements': 'none',
        'category': 'Anonymous Chat & Fun',
        'notes': 'Rows are built from the from_username and to_username of each message\'s '
                 'conversation in anonimchat.db. A username is marked as the signed-in account '
                 'only when the same data container\'s React Native AsyncStorage manifest.json '
                 '(or the MD5-named file beside it that holds a long value) names exactly one '
                 'username under one of these keys: signedInUsername, loggedInUsername, '
                 'currentUsername, accountUsername, localUsername, or a username field inside '
                 'a session, auth, account, currentUser, signedInUser or loggedInUser object. '
                 'These key names are not confirmed from the app on a real device. When none '
                 'is found, every participant is reported as not confirmed and the outgoing '
                 'and incoming counts stay blank. A matching username does not establish who '
                 'owned or used the device.',
        'paths': (
            '*/Containers/Data/Application/*/Library/LocalDatabase/anonimchat.db*',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.anonimchat.app.plist',
            '*/Containers/Data/Application/*/Library/Application Support/'
            'com.anonimchat.app/RCTAsyncLocalStorage_V1/*',
            '*/Containers/Data/Application/*/Documents/RCTAsyncLocalStorage_V1/*',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'user',
        'sample_data': {
            'anonymous_chat_synthetic': 'Synthetic test case built by '
                                        'admin/test/scripts/build_anonymous_chat_fixture.py, '
                                        'not a device extraction | 2 rows',
        },
    },
    'anonymousChat_conversations': {
        'name': 'Anonymous Chat & Fun - Conversations',
        'description': 'Conversations stored by the iOS app "Anonymous Chat & Fun" '
                       '(bundle ID com.anonimchat.app).',
        'author': '@darren33',
        'creation_date': '2026-09-11',
        'last_update_date': '2026-10-14',
        'requirements': 'none',
        'category': 'Anonymous Chat & Fun',
        'notes': 'Rows come from the conversations table of anonimchat.db. Message, outgoing '
                 'and incoming counts and the observed last message time are computed from '
                 'the messages table. Columns marked (raw) are reported as stored because '
                 'their meaning is not established. Numeric times are read as Unix time: a '
                 'value of ten digits or fewer as seconds, a longer one scaled down from '
                 'milliseconds, microseconds or nanoseconds by its size. Neither the unit nor '
                 'the epoch is confirmed on a real device. A conversation_time held as '
                 'text with no timezone is left in the raw column only. Other Party names the '
                 'opposite participant only when the Accounts artifact found one signed-in '
                 'username; otherwise it lists both participants. Conversation Key joins the '
                 'source database path and the stored conversation ID, so two databases with '
                 'the same ID stay apart.',
        'paths': (
            '*/Containers/Data/Application/*/Library/LocalDatabase/anonimchat.db*',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.anonimchat.app.plist',
            '*/Containers/Data/Application/*/Library/Application Support/'
            'com.anonimchat.app/RCTAsyncLocalStorage_V1/*',
            '*/Containers/Data/Application/*/Documents/RCTAsyncLocalStorage_V1/*',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'message-circle',
        'sample_data': {
            'anonymous_chat_synthetic': 'Synthetic test case built by '
                                        'admin/test/scripts/build_anonymous_chat_fixture.py, '
                                        'not a device extraction | 1 row',
        },
    },
    'anonymousChat_messages': {
        'name': 'Anonymous Chat & Fun - Messages',
        'description': 'Messages stored by the iOS app "Anonymous Chat & Fun" '
                       '(bundle ID com.anonimchat.app), with the cached image on the message '
                       'row when a file in the app\'s image cache is named for its stored URL.',
        'author': '@darren33',
        'creation_date': '2026-09-11',
        'last_update_date': '2026-10-14',
        'requirements': 'none',
        'category': 'Anonymous Chat & Fun',
        'notes': 'Rows come from the messages table of anonimchat.db, joined to conversations '
                 'for the participants. Direction is Outgoing when the sender flag is 0 and the '
                 'sender name is the signed-in username from the Accounts artifact, Incoming '
                 'when the flag is 1 and the sender name is the other participant, and blank '
                 'otherwise. Neither the flag values nor the account keys are confirmed on a '
                 'real device, so a blank direction is expected. Numeric times are read as '
                 'Unix time: a value of ten digits or fewer as seconds, a longer one scaled '
                 'down from milliseconds, microseconds or nanoseconds by its size. Neither the '
                 'unit nor the epoch is confirmed on a real device. Media: SDWebImage 5 keeps '
                 'cached images in Library/Caches/com.hackemist.SDImageCache/<namespace>/ '
                 '(5.19.0 source) and SDWebImage 4 in Library/Caches/default/'
                 'com.hackemist.SDWebImageCache.default/ (4.4.8 source). Both name each file '
                 'by the MD5 of its cache key plus the URL\'s extension, and the default cache '
                 'key is the URL itself. A '
                 'cached file is shown on a message only when its name equals that value for '
                 'the message\'s stored media_url, in the same data container. A custom cache '
                 'key, image transformer or thumbnail changes the key and leaves the message '
                 'without a link. Files are never matched by name alone, size or time. Local '
                 'paths in media_url, message_info fields and Photos library originals are '
                 'not followed, because no real extraction has confirmed how the app records '
                 'them. Media Link Method says why a media message has no file.',
        'paths': (
            '*/Containers/Data/Application/*/Library/LocalDatabase/anonimchat.db*',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.anonimchat.app.plist',
            '*/Containers/Data/Application/*/Library/Application Support/'
            'com.anonimchat.app/RCTAsyncLocalStorage_V1/*',
            '*/Containers/Data/Application/*/Documents/RCTAsyncLocalStorage_V1/*',
            '*/Containers/Data/Application/*/Library/Caches/com.hackemist.SDImageCache/*',
            '*/Containers/Data/Application/*/Library/Caches/default/com.hackemist.SDWebImageCache.*',
        ),
        'output_types': ['html', 'tsv', 'timeline', 'lava'],
        'data_views': {
            'conversation': {
                'directionSentValue': 'Outgoing',
                'conversationDiscriminatorColumn': 'Conversation Key',
                'conversationLabelColumn': 'Other Party',
                'directionColumn': 'Direction',
                'senderColumn': 'Sender Name',
                'textColumn': 'Message Text',
                'mediaColumn': 'Media',
                'timeColumn': 'Message Timestamp',
            }
        },
        'artifact_icon': 'message-square',
        'sample_data': {
            'anonymous_chat_synthetic': 'Synthetic test case built by '
                                        'admin/test/scripts/build_anonymous_chat_fixture.py, '
                                        'not a device extraction | 3 rows',
        },
    },
    'anonymousChat_blocked': {
        'name': 'Anonymous Chat & Fun - Blocked Users',
        'description': 'Blocked-user rows stored by the iOS app "Anonymous Chat & Fun" '
                       '(bundle ID com.anonimchat.app).',
        'author': '@darren33',
        'creation_date': '2026-09-11',
        'last_update_date': '2026-10-14',
        'requirements': 'none',
        'category': 'Anonymous Chat & Fun',
        'notes': 'Rows come from the blocked table of anonimchat.db and are reported as '
                 'stored. Which of the two usernames did the blocking is not established.',
        'paths': (
            '*/Containers/Data/Application/*/Library/LocalDatabase/anonimchat.db*',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.anonimchat.app.plist',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'slash',
        'sample_data': {
            'anonymous_chat_synthetic': 'Synthetic test case built by '
                                        'admin/test/scripts/build_anonymous_chat_fixture.py, '
                                        'not a device extraction | 1 row',
        },
    },
    'anonymousChat_media': {
        'name': 'Anonymous Chat & Fun - Media',
        'description': 'Media referenced by messages, the media table and the image cache of '
                       'the iOS app "Anonymous Chat & Fun" (bundle ID com.anonimchat.app).',
        'author': '@darren33',
        'creation_date': '2026-09-11',
        'last_update_date': '2026-10-14',
        'requirements': 'none',
        'category': 'Anonymous Chat & Fun',
        'notes': 'Three kinds of row. Message Media: a message with a stored media URL, type, '
                 'size or duration, with its cached image when one is linked (the Messages '
                 'artifact notes give the SDWebImage naming rule that makes the link). Media '
                 'Table: a row of the media table of anonimchat.db; media_data is not read, '
                 'and these rows are not linked to messages or files because no stored join '
                 'between them is confirmed. Cached Image: a file in the app\'s SDImageCache '
                 'folder that no message row was linked to. It can be an image the app '
                 'showed outside a message, or one whose message is no longer in the '
                 'database; which one is not established. Size on a Cached Image row is the '
                 'file size; on a Message Media row it is the stored media_size.',
        'paths': (
            '*/Containers/Data/Application/*/Library/LocalDatabase/anonimchat.db*',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.anonimchat.app.plist',
            '*/Containers/Data/Application/*/Library/Application Support/'
            'com.anonimchat.app/RCTAsyncLocalStorage_V1/*',
            '*/Containers/Data/Application/*/Documents/RCTAsyncLocalStorage_V1/*',
            '*/Containers/Data/Application/*/Library/Caches/com.hackemist.SDImageCache/*',
            '*/Containers/Data/Application/*/Library/Caches/default/com.hackemist.SDWebImageCache.*',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'image',
        'sample_data': {
            'anonymous_chat_synthetic': 'Synthetic test case built by '
                                        'admin/test/scripts/build_anonymous_chat_fixture.py, '
                                        'not a device extraction | 4 rows',
        },
    },
}


import hashlib
import json
import os
import posixpath
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, \
    does_table_exist_in_db, get_plist_file_content, get_sqlite_db_records, logfunc, \
    null_absent_columns


_BUNDLE_ID = 'com.anonimchat.app'
_DB_NAME = 'anonimchat.db'
_MCM_PLIST = '.com.apple.mobile_container_manager.metadata.plist'
_PREFS_PLIST = 'com.anonimchat.app.plist'
_MAX_JSON_BYTES = 1024 * 1024

# A container is its folder: the source path up to and including the UUID (or, in an
# iTunes backup, the bundle ID) after Data/Application or Bundle/Application. Two
# containers, or one container in two extractions, never share a folder.
_CONTAINER_RE = re.compile(r'^(.*?/containers/(data|bundle)/application/([^/]+))(?:/|$)',
                           re.IGNORECASE)
# SDWebImage 5 and SDWebImage 4 disk-cache folders.
_SDIMAGECACHE_RE = re.compile(r'/library/caches/(?:com\.hackemist\.sdimagecache/|'
                              r'default/com\.hackemist\.sdwebimagecache\.[^/]+/)',
                              re.IGNORECASE)

# AsyncStorage keys that may hold the signed-in username. Not confirmed on a device.
_ACCOUNT_KEYS = {'signedinusername', 'loggedinusername', 'currentusername',
                 'accountusername', 'localusername'}
_ACCOUNT_OBJECTS = {'session', 'auth', 'account', 'currentuser', 'signedinuser', 'loggedinuser'}
_MAX_DEPTH = 8


# ---------------------------------------------------------------- containers

def _source(context, path):
    """Evidence-relative path of a staged file."""
    return context.get_relative_path(str(path)).replace('\\', '/').lstrip('/')


def _container(source):
    """(container folder, kind) for a source path, or (None, None)."""
    match = _CONTAINER_RE.match('/' + source)
    if not match:
        return None, None
    return match.group(1).lstrip('/'), match.group(2).lower()


def _read_plist(path):
    content = get_plist_file_content(path)
    return content if isinstance(content, dict) else {}


def _containers(context):
    """Map each container folder that names the app to (kind, how it was identified)."""
    found = {}
    for path in context.get_files_found():
        source = _source(context, path)
        folder, kind = _container(source)
        if not folder:
            continue
        name = posixpath.basename(source)
        if kind == 'data' and folder.rsplit('/', 1)[1].casefold() == _BUNDLE_ID:
            found[folder] = (kind, 'iTunes backup AppDomain')
        elif name == _MCM_PLIST:
            if _read_plist(path).get('MCMMetadataIdentifier') == _BUNDLE_ID:
                found[folder] = (kind, 'MCMMetadataIdentifier')
        elif kind == 'data' and name == _PREFS_PLIST:
            found.setdefault(folder, (kind, 'Preferences plist name'))
        elif kind == 'bundle' and name == 'Info.plist':
            if _read_plist(path).get('CFBundleIdentifier') == _BUNDLE_ID:
                found.setdefault(folder, (kind, 'Info.plist CFBundleIdentifier'))
        elif kind == 'bundle' and name == 'iTunesMetadata.plist':
            if _read_plist(path).get('softwareVersionBundleId') == _BUNDLE_ID:
                found.setdefault(folder, (kind, 'iTunesMetadata.plist'))
    return found


def _app_files(context):
    """Staged files inside the app's data containers, as (path, source, folder)."""
    data_folders = {folder for folder, (kind, _) in _containers(context).items()
                    if kind == 'data'}
    result = []
    for path in context.get_files_found():
        source = _source(context, path)
        folder, _kind = _container(source)
        # '._<name>' is a macOS AppleDouble sidecar an archiver added, not app data.
        if posixpath.basename(source).startswith('._'):
            continue
        if folder in data_folders and os.path.isfile(path):
            result.append((str(path), source, folder))
    return sorted(result, key=lambda item: item[1])


def _databases(app_files):
    return [item for item in app_files if posixpath.basename(item[1]) == _DB_NAME]


# ---------------------------------------------------------------- accounts

def _read_json(path):
    try:
        with open(path, 'rb') as handle:
            payload = handle.read(_MAX_JSON_BYTES + 1)
        if len(payload) > _MAX_JSON_BYTES:
            logfunc(f'Anonymous Chat: skipped AsyncStorage file over 1 MiB: {path}')
            return None
        return json.loads(payload.decode('utf-8'))
    except (OSError, UnicodeError, ValueError, RecursionError) as ex:
        logfunc(f'Anonymous Chat: could not read AsyncStorage file {path}: {ex}')
        return None


def _key(value):
    return re.sub(r'[^a-z0-9]', '', str(value).casefold())


def _decode(value):
    if isinstance(value, str) and value.strip()[:1] in ('{', '[', '"'):
        try:
            return json.loads(value)
        except (ValueError, RecursionError):
            return None
    return value


def _usernames(value, depth=0):
    """Usernames under the account keys. Usernames anywhere else are ignored."""
    names = set()
    value = _decode(value)
    if depth > _MAX_DEPTH or not isinstance(value, dict):
        return names
    for child_key, child in value.items():
        key = _key(child_key)
        if key in _ACCOUNT_KEYS or (depth and key == 'username'):
            child = _decode(child)
            if isinstance(child, str) and 0 < len(child.strip()) <= 256:
                names.add(child.strip())
        elif key in _ACCOUNT_OBJECTS:
            names |= _usernames(child, depth + 1)
    return names


def _accounts(app_files):
    """{data container folder: {username: AsyncStorage files it came from}}."""
    by_source = {source: path for path, source, _ in app_files}
    accounts = {}
    for path, source, folder in app_files:
        if (posixpath.basename(source) != 'manifest.json' or
                '/RCTAsyncLocalStorage_V1/' not in '/' + source):
            continue
        manifest = _read_json(path)
        if not isinstance(manifest, dict):
            continue
        for storage_key, value in manifest.items():
            evidence = [source]
            if value is None and _key(storage_key) in _ACCOUNT_KEYS | _ACCOUNT_OBJECTS:
                # AsyncStorage keeps a long value in a file named by the MD5 of its key.
                sidecar = posixpath.join(posixpath.dirname(source), hashlib.md5(
                    str(storage_key).encode('utf-8'), usedforsecurity=False).hexdigest())
                if sidecar not in by_source:
                    continue
                try:
                    with open(by_source[sidecar], 'rb') as handle:
                        value = handle.read(_MAX_JSON_BYTES).decode('utf-8')
                except (OSError, UnicodeError):
                    continue
                evidence.append(sidecar)
            for name in _usernames({storage_key: value}):
                accounts.setdefault(folder, {}).setdefault(name, set()).update(evidence)
    return accounts


def _participants(row):
    return [str(row.get(key) or '').strip() for key in ('from_username', 'to_username')]


def _local_name(row, local_accounts):
    """The participant that is the one signed-in username, or ''."""
    if len(local_accounts) != 1:
        return ''
    local = next(iter(local_accounts)).casefold()
    matches = [name for name in _participants(row) if name and name.casefold() == local]
    return matches[0] if len(matches) == 1 else ''


def _other_party(row, local_accounts):
    local = _local_name(row, local_accounts)
    if local:
        return next((name for name in _participants(row) if name != local), '')
    names = sorted(set(filter(None, _participants(row))))
    return 'Participants: ' + ', '.join(names) if names else ''


def _direction(row, local_accounts):
    local = _local_name(row, local_accounts)
    if not local:
        return ''
    sender = str(row.get('sender_name') or '').strip().casefold()
    if row.get('sender_flag') == 0 and sender == local.casefold():
        return 'Outgoing'
    if row.get('sender_flag') == 1 and sender == _other_party(row, local_accounts).casefold():
        return 'Incoming'
    return ''


# ---------------------------------------------------------------- database

_MESSAGE_QUERY = '''
    SELECT m.message_id, m.conversation_id, m.msg_id, m.message, m.media_url,
           m.media_mime_type, m.media_ac_type, m.media_size, m.media_duration,
           m.media_origin, m.media_show, m.media_spotify, m.anonymous_reveal,
           m.message_reaction, m.message_reply, m.message_info,
           m.message_verified_profile_link, m.message_time, m.sender AS sender_flag,
           m.sender_name, m.send_time, c.from_username, c.to_username
    FROM messages AS m
    LEFT JOIN conversations AS c ON c.conversation_id = m.conversation_id
    ORDER BY m.message_time, m.message_id
'''

_MESSAGE_QUERY_NO_CONVERSATIONS = (
    _MESSAGE_QUERY
    .replace('c.from_username, c.to_username', 'NULL AS from_username, NULL AS to_username')
    .replace('LEFT JOIN conversations AS c ON c.conversation_id = m.conversation_id', ''))

_CONVERSATION_QUERY = '''
    SELECT conversation_id, from_username, to_username, anonymous_status, anonymous_color,
           anonymous_reveal, anonymous_alert, anonymous_alias, trusted_media, pin_status,
           unread_count, last_message_time, seen_message_id, seen_message_time,
           conversation_time
    FROM conversations
    ORDER BY conversation_id
'''

# media_data is not selected: its content is not needed to report the row.
_MEDIA_TABLE_QUERY = 'SELECT media_id, media_name, media_time FROM media ORDER BY media_time, media_id'

_BLOCKED_QUERY = 'SELECT block_id, from_username, to_username FROM blocked ORDER BY block_id'


def _rows(path, query):
    """Rows as dicts. A missing column reads as empty; a missing table yields none."""
    if query is _MESSAGE_QUERY and not does_table_exist_in_db(path, 'conversations'):
        query = _MESSAGE_QUERY_NO_CONVERSATIONS
    return [dict(row) for row in
            get_sqlite_db_records(path, null_absent_columns(path, query)) or []]


def _time(value):
    """A numeric value read as Unix seconds, or ''."""
    if value in (None, '') or isinstance(value, bool):
        return ''
    converted = convert_unix_ts_to_utc(value)
    return converted if isinstance(converted, datetime) else ''


def _text_time(value):
    """A numeric time, or a text time that carries its own timezone, or ''."""
    if isinstance(value, (int, float)):
        return _time(value)
    text = str(value or '').strip()
    if not re.search(r'(?:Z|[+-]\d{2}:?\d{2})$', text, re.IGNORECASE):
        return ''
    try:
        return datetime.fromisoformat(text.replace('Z', '+00:00')).astimezone(timezone.utc)
    except ValueError:
        return ''


def _conversation_key(source, conversation_id, message_id=''):
    identity = (['conversation', str(conversation_id)] if conversation_id not in (None, '')
                else ['unassigned message', str(message_id)])
    return json.dumps([source, *identity], separators=(',', ':'))


def _has_media(message):
    return any(message.get(column) not in (None, '') for column in (
        'media_url', 'media_mime_type', 'media_size', 'media_duration'))


# ---------------------------------------------------------------- media

def _cache_name(url):
    """The SDImageCache file name for an http(s) URL used as its own cache key, or ''.

    SDWebImage names the file by the MD5 of the key, then '.' and the URL path's
    extension unless that extension would not fit in a file name.
    """
    url = str(url or '').strip()
    try:
        parts = urlsplit(url)
    except ValueError:
        return ''
    if parts.scheme.casefold() not in ('http', 'https') or not parts.netloc:
        return ''
    digest = hashlib.md5(url.encode('utf-8'), usedforsecurity=False).hexdigest()
    extension = posixpath.splitext(parts.path)[1][1:]
    return f'{digest}.{extension}' if extension and len(extension) <= 255 - 33 else digest


def _cache_files(app_files):
    """{(data container folder, file name): [(path, source)]} for SDImageCache files."""
    files = {}
    for path, source, folder in app_files:
        if _SDIMAGECACHE_RE.search('/' + source):
            files.setdefault((folder, posixpath.basename(source)), []).append((path, source))
    return files


def _check_in(path, source):
    try:
        return check_in_media(path, name=posixpath.basename(source)) or ''
    except (OSError, RuntimeError, TypeError, ValueError) as ex:
        logfunc(f'Anonymous Chat: could not add {source} to the report: {ex}')
        return ''


def _message_media(message, folder, cache_files):
    """(media reference, cache file source, link method) for one message."""
    if not _has_media(message):
        return '', '', ''
    url = message.get('media_url')
    name = _cache_name(url)
    if not name:
        return '', '', ('No link: media_url is not an http(s) URL' if url
                        else 'No link: no media_url stored')
    matches = cache_files.get((folder, name), [])
    if len(matches) != 1:
        return '', '', ('No link: no SDImageCache file named for this URL' if not matches
                        else 'No link: more than one SDImageCache file has this name')
    path, source = matches[0]
    return _check_in(path, source), source, 'SDImageCache file named for the stored media_url'


# ---------------------------------------------------------------- artifacts

@artifact_processor
def anonymousChat_appInfo(context):
    containers = _containers(context)
    plists = {}
    for path in context.get_files_found():
        source = _source(context, path)
        folder, kind = _container(source)
        name = posixpath.basename(source)
        if folder in containers and kind == 'bundle' and name in ('Info.plist',
                                                                  'iTunesMetadata.plist'):
            plists.setdefault(folder, {})[name] = (_read_plist(path), source)
    rows, sources = [], []
    for folder, (kind, method) in sorted(containers.items()):
        info, info_source = plists.get(folder, {}).get('Info.plist', ({}, ''))
        store, store_source = plists.get(folder, {}).get('iTunesMetadata.plist', ({}, ''))
        sources.extend(filter(None, (info_source, store_source)))
        rows.append((
            'Bundle' if kind == 'bundle' else 'Data',
            folder.rsplit('/', 1)[1],
            _BUNDLE_ID,
            info.get('CFBundleDisplayName') or info.get('CFBundleName') or '',
            info.get('CFBundleShortVersionString') or store.get('bundleShortVersionString', ''),
            info.get('CFBundleVersion') or store.get('bundleVersion', ''),
            store.get('itemName', ''),
            store.get('artistName', ''),
            str(store.get('purchaseDate', '')),
            method,
            folder,
        ))
    data_headers = ('Container Type', 'Container ID', 'Bundle ID', 'Application Name', 'Version',
                    'Build', 'Store Item Name', 'Store Artist Name', 'Purchase Date', 'Identified By',
                    'Container Path')
    return data_headers, rows, '\n'.join(sorted(set(sources)) or sorted(containers))


@artifact_processor
def anonymousChat_accounts(context):
    app_files = _app_files(context)
    accounts = _accounts(app_files)
    databases = _databases(app_files)
    totals = {}
    for path, source, folder in databases:
        local_accounts = accounts.get(folder, {})
        for message in _rows(path, _MESSAGE_QUERY):
            for name in set(filter(None, _participants(message))):
                item = totals.setdefault((folder, name), {
                    'conversations': set(), 'messages': 0, 'Outgoing': 0, 'Incoming': 0,
                    'times': [], 'sources': set()})
                item['conversations'].add(str(message.get('conversation_id')))
                item['messages'] += 1
                item['sources'].add(source)
                direction = _direction(message, local_accounts)
                if direction and _local_name(message, local_accounts) == name:
                    item[direction] += 1
                sent = _time(message.get('message_time'))
                if sent:
                    item['times'].append(sent)
    rows = []
    for (folder, name), item in sorted(totals.items()):
        evidence = accounts.get(folder, {})
        local = len(evidence) == 1 and name in evidence
        rows.append((
            min(item['times']) if item['times'] else '',
            max(item['times']) if item['times'] else '',
            name,
            'Username under an account key in AsyncStorage' if local else 'Participant, not confirmed '
                                                               'as the signed-in account',
            len(item['conversations']),
            item['messages'],
            item['Outgoing'] if local else '',
            item['Incoming'] if local else '',
            '\n'.join(sorted(evidence[name])) if local else '',
            '\n'.join(sorted(item['sources'])),
        ))
    data_headers = (('First Message Timestamp', 'datetime'), ('Last Message Timestamp', 'datetime'),
                    'Username', 'Account Status', 'Conversation Count', 'Message Count',
                    'Outgoing Count', 'Incoming Count', 'AsyncStorage Evidence', 'Source')
    return data_headers, rows, '\n'.join(source for _, source, _ in databases)


@artifact_processor
def anonymousChat_conversations(context):
    app_files = _app_files(context)
    accounts = _accounts(app_files)
    databases = _databases(app_files)
    rows = []
    for path, source, folder in databases:
        local_accounts = accounts.get(folder, {})
        counts = {}
        for message in _rows(path, _MESSAGE_QUERY):
            item = counts.setdefault(str(message.get('conversation_id')),
                                     {'total': 0, 'Outgoing': 0, 'Incoming': 0, 'last': ''})
            item['total'] += 1
            direction = _direction(message, local_accounts)
            if direction:
                item[direction] += 1
            sent = _time(message.get('message_time'))
            if sent and (not item['last'] or sent > item['last']):
                item['last'] = sent
        for conversation in _rows(path, _CONVERSATION_QUERY):
            count = counts.get(str(conversation.get('conversation_id')),
                               {'total': 0, 'Outgoing': 0, 'Incoming': 0, 'last': ''})
            rows.append((
                _time(conversation.get('last_message_time')),
                count['last'],
                _time(conversation.get('seen_message_time')),
                _text_time(conversation.get('conversation_time')),
                conversation.get('conversation_id'),
                conversation.get('from_username'),
                conversation.get('to_username'),
                _other_party(conversation, local_accounts),
                count['total'],
                count['Outgoing'],
                count['Incoming'],
                conversation.get('seen_message_id'),
                conversation.get('anonymous_status'),
                conversation.get('anonymous_color'),
                conversation.get('anonymous_reveal'),
                conversation.get('anonymous_alert'),
                conversation.get('anonymous_alias'),
                conversation.get('trusted_media'),
                conversation.get('pin_status'),
                conversation.get('unread_count'),
                conversation.get('conversation_time'),
                source,
                _conversation_key(source, conversation.get('conversation_id')),
            ))
    data_headers = (('Stored Last Message Timestamp', 'datetime'),
                    ('Observed Last Message Timestamp', 'datetime'),
                    ('Seen Message Timestamp', 'datetime'), ('Conversation Timestamp', 'datetime'),
                    'Conversation ID', 'From Username', 'To Username', 'Other Party',
                    'Message Count', 'Outgoing Count', 'Incoming Count', 'Seen Message ID',
                    'Anonymous Status (raw)', 'Anonymous Color', 'Anonymous Reveal (raw)',
                    'Anonymous Alert (raw)', 'Anonymous Alias', 'Trusted Media (raw)',
                    'Pin Status (raw)', 'Unread Count (raw)', 'Conversation Time (raw)', 'Source',
                    'Conversation Key')
    return data_headers, rows, '\n'.join(source for _, source, _ in databases)


@artifact_processor
def anonymousChat_messages(context):
    app_files = _app_files(context)
    accounts = _accounts(app_files)
    cache_files = _cache_files(app_files)
    databases = _databases(app_files)
    rows = []
    for path, source, folder in databases:
        local_accounts = accounts.get(folder, {})
        for message in _rows(path, _MESSAGE_QUERY):
            media, _cache_source, link = _message_media(message, folder, cache_files)
            rows.append((
                _time(message.get('message_time')),
                _time(message.get('send_time')),
                _direction(message, local_accounts),
                message.get('sender_name'),
                _other_party(message, local_accounts),
                message.get('message'),
                media,
                message.get('conversation_id'),
                message.get('message_id'),
                message.get('msg_id'),
                message.get('sender_flag'),
                message.get('from_username'),
                message.get('to_username'),
                message.get('media_url'),
                message.get('media_mime_type'),
                message.get('media_size'),
                message.get('media_duration'),
                message.get('media_ac_type'),
                message.get('media_origin'),
                message.get('media_show'),
                message.get('media_spotify'),
                message.get('anonymous_reveal'),
                message.get('message_reaction'),
                message.get('message_reply'),
                message.get('message_info'),
                message.get('message_verified_profile_link'),
                link,
                source,
                _conversation_key(source, message.get('conversation_id'),
                                  message.get('message_id')),
            ))
    data_headers = (('Message Timestamp', 'datetime'), ('Send Timestamp', 'datetime'), 'Direction',
                    'Sender Name', 'Other Party', 'Message Text', ('Media', 'media'),
                    'Conversation ID', 'Message ID', 'Msg ID (raw)', 'Sender Flag (raw)',
                    'From Username', 'To Username', 'Media URL', 'Media MIME Type', 'Media Size',
                    'Media Duration', 'Media AC Type (raw)', 'Media Origin (raw)',
                    'Media Show (raw)', 'Media Spotify (raw)', 'Anonymous Reveal (raw)',
                    'Message Reaction (raw)', 'Message Reply (raw)', 'Message Info (raw)',
                    'Verified Profile Link (raw)', 'Media Link Method', 'Source',
                    'Conversation Key')
    return data_headers, rows, '\n'.join(source for _, source, _ in databases)


@artifact_processor
def anonymousChat_blocked(context):
    databases = _databases(_app_files(context))
    rows = []
    for path, source, _folder in databases:
        for row in _rows(path, _BLOCKED_QUERY):
            rows.append((row.get('block_id'), row.get('from_username'),
                         row.get('to_username'), source))
    data_headers = ('Block ID', 'From Username', 'To Username', 'Source')
    return data_headers, rows, '\n'.join(source for _, source, _ in databases)


@artifact_processor
def anonymousChat_media(context):
    app_files = _app_files(context)
    accounts = _accounts(app_files)
    cache_files = _cache_files(app_files)
    databases = _databases(app_files)
    linked = set()
    rows = []
    for path, source, folder in databases:
        local_accounts = accounts.get(folder, {})
        for message in _rows(path, _MESSAGE_QUERY):
            if not _has_media(message):
                continue
            media, cache_source, link = _message_media(message, folder, cache_files)
            linked.add(cache_source)
            rows.append((_time(message.get('message_time')), '', 'Message Media', media,
                         message.get('conversation_id'), message.get('message_id'),
                         _direction(message, local_accounts), message.get('sender_name'), '',
                         message.get('media_url'), message.get('media_mime_type'),
                         message.get('media_size'), message.get('media_duration'),
                         message.get('media_origin'), message.get('media_show'),
                         cache_source, link, source))
        for row in _rows(path, _MEDIA_TABLE_QUERY):
            rows.append(('', _time(row.get('media_time')), 'Media Table', '', '', '', '', '',
                         row.get('media_id'), row.get('media_name'), '', '', '', '', '', '',
                         'Not linked: no confirmed join to a message or file', source))
    for _name, matches in sorted(cache_files.items()):
        for path, cache_source in matches:
            if cache_source in linked:
                continue
            rows.append(('', '', 'Cached Image', _check_in(path, cache_source), '', '', '', '',
                         '', '', '', os.path.getsize(path), '', '', '', cache_source,
                         'Not linked: no message row was linked to this file', ''))
    data_headers = (('Message Timestamp', 'datetime'), ('Media Timestamp', 'datetime'), 'Record Type',
                    ('Media', 'media'), 'Conversation ID', 'Message ID', 'Direction', 'Sender Name',
                    'Media ID', 'Media URL or Name', 'Media MIME Type', 'Size', 'Media Duration',
                    'Media Origin (raw)', 'Media Show (raw)', 'Cache File', 'Link Method',
                    'Source Database')
    sources = [source for _, source, _ in databases] + sorted(
        source for matches in cache_files.values() for _, source in matches)
    return data_headers, rows, '\n'.join(sources)
