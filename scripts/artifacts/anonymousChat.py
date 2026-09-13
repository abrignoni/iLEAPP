__artifacts_v2__ = {
    'anonymousChat_appInfo': {
        'name': 'Anonymous Chat & Fun - Application Info',
        'description': 'Application and container identity for the iOS app '
                       '"Anonymous Chat & Fun" (bundle ID com.anonimchat.app), '
                       'identified from bundle and container metadata.',
        'author': 'Darren Rooney',
        'creation_date': '2026-09-11',
        'last_update_date': '2026-09-13',
        'requirements': 'none',
        'category': 'Anonymous Chat & Fun',
        'notes': 'This module targets the iOS app "Anonymous Chat & Fun" identified by '
                 'bundle ID com.anonimchat.app. The bundle ID and container UUIDs are '
                 'verified from extraction metadata; no container UUID is hard-coded.',
        'paths': (
            '*/Containers/Data/Application/*/Library/LocalDatabase/anonimchat.db*',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.anonimchat.app.plist',
            '*/Containers/Data/Application/*/Library/Application Support/'
            'com.anonimchat.app/RCTAsyncLocalStorage_V1/manifest.json',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/*.app/Info.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/iTunesMetadata.plist',
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'package',
        'sample_data': {
            'anonymous_chat_synthetic': 'Synthetic metadata-only fixture for Anonymous Chat & Fun '
                                        '(bundle ID com.anonimchat.app); 1 row of application-info '
                                        'data; no casework or media payloads are included.',
            'examiner_case_metadata_counts': 'Metadata-only validation record from an examiner-run '
                                              'extraction: iOS 26.3; Application Info 1; Accounts 2; '
                                              'Conversations 479; Messages 5,837; Blocked Users 6; '
                                              'Media Files and Metadata 1,348. Aggregate counts only; '
                                              'no case files, identifiers, message content, paths, or '
                                              'media payloads are included.',
        },
    },
    'anonymousChat_accounts': {
        'name': 'Anonymous Chat & Fun - Accounts',
        'description': 'Account identifiers stored by the iOS app "Anonymous Chat & Fun" '
                       '(bundle ID com.anonimchat.app) as the '
                       'conversation from_username value, with message-direction evidence '
                       'and limits on owner attribution.',
        'author': 'Darren Rooney',
        'creation_date': '2026-09-11',
        'last_update_date': '2026-09-13',
        'requirements': 'none',
        'category': 'Anonymous Chat & Fun',
        'notes': 'This artifact is from the iOS app "Anonymous Chat & Fun" '
                 '(bundle ID com.anonimchat.app). The database does '
                 'not establish the legal or physical device owner.',
        'paths': (
            '*/Containers/Data/Application/*/Library/LocalDatabase/anonimchat.db*',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.anonimchat.app.plist',
            '*/Containers/Data/Application/*/Library/Application Support/'
            'com.anonimchat.app/RCTAsyncLocalStorage_V1/manifest.json',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/*.app/Info.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/iTunesMetadata.plist',
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'user',
        'sample_data': {
            'anonymous_chat_synthetic': 'Synthetic metadata-only fixture for Anonymous Chat & Fun '
                                        '(bundle ID com.anonimchat.app); 1 row of account data covering '
                                        '3 messages; no casework or media payloads are included.',
            'examiner_case_metadata_counts': 'Metadata-only validation record from an examiner-run '
                                              'extraction: iOS 26.3; Application Info 1; Accounts 2; '
                                              'Conversations 479; Messages 5,837; Blocked Users 6; '
                                              'Media Files and Metadata 1,348. Aggregate counts only; '
                                              'no case files, identifiers, message content, paths, or '
                                              'media payloads are included.',
        },
    },
    'anonymousChat_conversations': {
        'name': 'Anonymous Chat & Fun - Conversations',
        'description': 'Conversation records and raw status fields from the database of the iOS '
                       'app "Anonymous Chat & Fun" (bundle ID com.anonimchat.app).',
        'author': 'Darren Rooney',
        'creation_date': '2026-09-11',
        'last_update_date': '2026-09-13',
        'requirements': 'none',
        'category': 'Anonymous Chat & Fun',
        'notes': 'This artifact is from the iOS app "Anonymous Chat & Fun" '
                 '(bundle ID com.anonimchat.app). Unexplained integer '
                 'and boolean values are retained as raw values. Other Party repeats the stored '
                 'to_username participant as a display-friendly conversation label; it is not '
                 'an independent database field. Conversation Key combines the source database '
                 'and stored conversation ID; it is a report grouping key, not a stored field.',
        'paths': (
            '*/Containers/Data/Application/*/Library/LocalDatabase/anonimchat.db*',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.anonimchat.app.plist',
            '*/Containers/Data/Application/*/Library/Application Support/'
            'com.anonimchat.app/RCTAsyncLocalStorage_V1/manifest.json',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/*.app/Info.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/iTunesMetadata.plist',
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'message-circle',
        'sample_data': {
            'anonymous_chat_synthetic': 'Synthetic metadata-only fixture for Anonymous Chat & Fun '
                                        '(bundle ID com.anonimchat.app); 1 row of conversation data '
                                        'covering 3 messages; no casework or media payloads are included.',
            'examiner_case_metadata_counts': 'Metadata-only validation record from an examiner-run '
                                              'extraction: iOS 26.3; Application Info 1; Accounts 2; '
                                              'Conversations 479; Messages 5,837; Blocked Users 6; '
                                              'Media Files and Metadata 1,348. Aggregate counts only; '
                                              'no case files, identifiers, message content, paths, or '
                                              'media payloads are included.',
        },
    },
    'anonymousChat_messages': {
        'name': 'Anonymous Chat & Fun - Messages',
        'description': 'Message text, participants, timestamps, direction evidence, and Media '
                       'Manager references from the iOS app "Anonymous Chat & Fun" '
                       '(bundle ID com.anonimchat.app).',
        'author': 'Darren Rooney',
        'creation_date': '2026-09-11',
        'last_update_date': '2026-09-13',
        'requirements': 'none',
        'category': 'Anonymous Chat & Fun',
        'notes': 'This artifact is from the iOS app "Anonymous Chat & Fun" '
                 '(bundle ID com.anonimchat.app). Direction is populated only when the stored '
                 'sender/name relationship supports it; the signed-in username, when present in '
                 'the app manifest, is used as corroborating evidence rather than legal owner '
                 'attribution. Conversation Key scopes the stored conversation ID to its source '
                 'database. Media is populated only when the application records a relationship '
                 'to a local file: stored path, SDImageCache URL-derived key, explicit media ID, '
                 'or an equivalent stored join. Size, timestamps, MIME compatibility, and filename '
                 'similarity alone never link a file to a message. Unlinked media remains in the '
                 'media artifact with an explanatory correlation note. Photos originals are labelled '
                 'as originals and may differ from transmitted media. The examiner-run report uses '
                 'iLEAPP Media Manager for locally linked files; remote URLs are never followed.',
        'paths': (
            '*/Containers/Data/Application/*/Library/LocalDatabase/anonimchat.db*',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.anonimchat.app.plist',
            '*/Containers/Data/Application/*/Library/Application Support/'
            'com.anonimchat.app/RCTAsyncLocalStorage_V1/manifest.json',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/*.app/Info.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/iTunesMetadata.plist',
            '*/Media/PhotoData/Photos.sqlite*',
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
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
            'anonymous_chat_synthetic': 'Synthetic metadata-only fixture for Anonymous Chat & Fun '
                                        '(bundle ID com.anonimchat.app); 3 rows of message data with '
                                        'outgoing/incoming direction and database media metadata; '
                                        'Media Manager calls are mocked and no media payloads are included.',
            'examiner_case_metadata_counts': 'Metadata-only validation record from an examiner-run '
                                              'extraction: iOS 26.3; Application Info 1; Accounts 2; '
                                              'Conversations 479; Messages 5,837; Blocked Users 6; '
                                              'Media Files and Metadata 1,348. Aggregate counts only; '
                                              'no case files, identifiers, message content, paths, or '
                                              'media payloads are included.',
        },
    },
    'anonymousChat_blocked': {
        'name': 'Anonymous Chat & Fun - Blocked Users',
        'description': 'Raw blocked-user rows stored by the iOS app "Anonymous Chat & Fun" '
                       '(bundle ID com.anonimchat.app).',
        'author': 'Darren Rooney',
        'creation_date': '2026-09-11',
        'last_update_date': '2026-09-13',
        'requirements': 'none',
        'category': 'Anonymous Chat & Fun',
        'notes': 'This artifact is from the iOS app "Anonymous Chat & Fun" '
                 '(bundle ID com.anonimchat.app). The table is reported '
                 'as stored; no additional blocking semantics are inferred.',
        'paths': (
            '*/Containers/Data/Application/*/Library/LocalDatabase/anonimchat.db*',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.anonimchat.app.plist',
            '*/Containers/Data/Application/*/Library/Application Support/'
            'com.anonimchat.app/RCTAsyncLocalStorage_V1/manifest.json',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/*.app/Info.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/iTunesMetadata.plist',
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'slash',
        'sample_data': {
            'anonymous_chat_synthetic': 'Synthetic metadata-only fixture for Anonymous Chat & Fun '
                                        '(bundle ID com.anonimchat.app); 1 row of blocked-user data; '
                                        'no casework or media payloads are included.',
            'examiner_case_metadata_counts': 'Metadata-only validation record from an examiner-run '
                                              'extraction: iOS 26.3; Application Info 1; Accounts 2; '
                                              'Conversations 479; Messages 5,837; Blocked Users 6; '
                                              'Media Files and Metadata 1,348. Aggregate counts only; '
                                              'no case files, identifiers, message content, paths, or '
                                              'media payloads are included.',
        },
    },
    'anonymousChat_media': {
        'name': 'Anonymous Chat & Fun - Media Files and Metadata',
        'description': 'Application-container media inventory, Media Manager references, and '
                       'database attachment metadata from the iOS app "Anonymous Chat & Fun" '
                       '(bundle ID com.anonimchat.app).',
        'author': 'Darren Rooney',
        'creation_date': '2026-09-11',
        'last_update_date': '2026-09-13',
        'requirements': 'none',
        'category': 'Anonymous Chat & Fun',
        'notes': 'This artifact is from the iOS app "Anonymous Chat & Fun" '
                 '(bundle ID com.anonimchat.app). Media are identified and correlated by metadata. '
                 'A message is linked only when the application records a stored path, an exact '
                 'SDImageCache key derived from stored URL text, an explicit media ID, or another '
                 'stored join. Size, timestamps, MIME compatibility, and filename similarity alone '
                 'are not evidence of a message relationship. One filesystem row is reported per '
                 'association, or one inventory row for an unlinked file; unlinked rows explain why '
                 'no association was made. Only locally linked media are checked in through iLEAPP '
                 'Media Manager for report display; remote URLs are never followed. ZIP and TAR '
                 'inputs report blank Created/Access fields and preserve their source timestamp '
                 'limitations; ZIP modification output discloses when the timezone is unavailable. '
                 'Photos originals outside the app container are included only through app media_id '
                 '= ZASSET.ZUUID and a safe stored DCIM path. Original and transmitted media may differ.',
        'paths': (
            '*/Containers/Data/Application/*/Library/LocalDatabase/anonimchat.db*',
            '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/Containers/Data/Application/*/Library/Preferences/com.anonimchat.app.plist',
            '*/Containers/Data/Application/*/Library/Application Support/'
            'com.anonimchat.app/RCTAsyncLocalStorage_V1/manifest.json',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/.com.apple.mobile_container_manager.metadata.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/*.app/Info.plist',
            '*/[Cc]ontainers/[Bb]undle/[Aa]pplication/*/iTunesMetadata.plist',
            '*/Media/PhotoData/Photos.sqlite*',
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'image',
        'sample_data': {
            'anonymous_chat_synthetic': 'Synthetic metadata-only fixture for Anonymous Chat & Fun '
                                        '(bundle ID com.anonimchat.app); 3 rows of database metadata '
                                        '(2 message attachment references and 1 media-table row); '
                                        'filesystem media is intentionally absent and Media Manager '
                                        'calls are mocked.',
            'examiner_case_metadata_counts': 'Metadata-only validation record from an examiner-run '
                                              'extraction: iOS 26.3; Application Info 1; Accounts 2; '
                                              'Conversations 479; Messages 5,837; Blocked Users 6; '
                                              'Media Files and Metadata 1,348. Aggregate counts only; '
                                              'no case files, identifiers, message content, paths, or '
                                              'media payloads are included.',
        },
    },
}

# Container UUIDs are discovered from application metadata.  When the examiner runs
# the parser, locally correlated filesystem media is handed to iLEAPP's Media Manager
# so that the generated report can display it.  Development validation for this module
# deliberately does not run that media path against case material.


import hashlib
import json
import os
import plistlib
import re
import sqlite3
from datetime import datetime, timezone
from urllib.parse import urlsplit

from scripts.ilapfuncs import artifact_processor, check_in_media, \
    convert_unix_ts_to_utc, does_table_exist_in_db, open_sqlite_db_readonly, \
    logfunc, null_absent_columns


_BUNDLE_ID = 'com.anonimchat.app'
_APP_NAME = 'Anonymous Chat & Fun'
_DB_NAME = 'anonimchat.db'
_MAX_HEADER_BYTES = 4096
_SDIMAGECACHE_PATH = '/library/caches/com.hackemist.sdimagecache/default/'
_SDIMAGECACHE_KEY_RE = re.compile(r'^[0-9a-f]{32}$')
_CONTAINER_UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-'
    r'[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
_TARGET_GROUP_PREFIX = f'group.{_BUNDLE_ID}'
_MANIFEST_ACCOUNT_KEYS = {
    'username', 'signedinusername', 'loggedinusername', 'currentusername',
    'accountusername', 'localusername',
}
_MESSAGE_INFO_MEDIA_ID_KEYS = {
    'mediaid', 'mediauuid', 'assetid', 'assetuuid', 'attachmentid',
    'attachmentuuid',
}
_MESSAGE_INFO_PATH_KEYS = {
    'mediaurl', 'attachmenturl', 'localpath', 'filepath', 'storedpath',
    'cachekey', 'cachefilename',
}
_MESSAGE_INFO_JOIN_KEYS = _MESSAGE_INFO_MEDIA_ID_KEYS | _MESSAGE_INFO_PATH_KEYS | {
    'filename', 'mediafilename', 'storedfilename',
}

_CONTAINER_RE = re.compile(
    r'/containers/(bundle/application|data/application|shared/appgroup)'
    r'/([^/]+)(?=/|$)', re.IGNORECASE)

_MEDIA_EXTENSIONS = {
    '.jpg': ('JPEG', 'Image'),
    '.jpeg': ('JPEG', 'Image'),
    '.jpe': ('JPEG', 'Image'),
    '.png': ('PNG', 'Image'),
    '.gif': ('GIF', 'Image'),
    '.webp': ('WebP', 'Image'),
    '.heic': ('HEIC', 'Image'),
    '.heif': ('HEIF', 'Image'),
    '.bmp': ('BMP', 'Image'),
    '.tif': ('TIFF', 'Image'),
    '.tiff': ('TIFF', 'Image'),
    '.ico': ('ICO', 'Image'),
    '.avif': ('AVIF', 'Image'),
    '.dng': ('DNG', 'Image'),
    '.ktx': ('KTX texture', 'Image/Texture'),
    '.mov': ('MOV', 'Video'),
    '.mp4': ('MP4', 'Video'),
    '.m4v': ('M4V', 'Video'),
    '.avi': ('AVI', 'Video'),
    '.mkv': ('Matroska', 'Video'),
    '.webm': ('WebM', 'Video'),
    '.3gp': ('3GPP', 'Video'),
    '.mpeg': ('MPEG', 'Video'),
    '.mpg': ('MPEG', 'Video'),
    '.ts': ('MPEG transport stream', 'Video'),
    '.aac': ('AAC', 'Audio'),
    '.m4a': ('M4A', 'Audio'),
    '.mp3': ('MP3', 'Audio'),
    '.wav': ('WAV', 'Audio'),
    '.ogg': ('Ogg', 'Audio'),
    '.opus': ('Opus', 'Audio'),
}

_NON_MEDIA_EXTENSIONLESS_NAMES = {
    'anonimchat.db',
    'anonimchat.db-wal',
    'anonimchat.db-shm',
    'cache.db',
    'cache.db-wal',
    'cache.db-shm',
    'manifest.json',
    'info.plist',
    'itunesmetadata.plist',
    '.com.apple.mobile_container_manager.metadata.plist',
}

def _files_found(context):
    """Return staged safe inputs, tolerating a direct unit-test invocation."""
    try:
        return [str(path) for path in context.get_files_found()]
    except ValueError:
        return []


def _normalise_path(path):
    return str(path or '').replace('\\', '/')


def _relative_source(context, path):
    try:
        path = context.get_relative_path(str(path))
    except (AttributeError, ValueError):
        pass
    return _normalise_path(path)


def _container_location(path):
    match = _CONTAINER_RE.search(_normalise_path(path))
    if not match:
        return '', ''
    kind = match.group(1).lower()
    kind = {
        'bundle/application': 'bundle',
        'data/application': 'data',
        'shared/appgroup': 'group',
    }.get(kind, '')
    token = match.group(2)
    if _CONTAINER_UUID_RE.fullmatch(token):
        return kind, token.upper()
    # iTunes backup domains use the bundle identifier in place of the on-device
    # data-container UUID (for example AppDomain-com.anonimchat.app).  Accept
    # only this exact app identifier; arbitrary container names must not become
    # parser targets.
    if kind == 'data' and token.casefold() == _BUNDLE_ID.casefold():
        return kind, _BUNDLE_ID.upper()
    return '', ''


def _read_plist(path):
    try:
        with open(path, 'rb') as plist_file:
            value = plistlib.load(plist_file)
        return value if isinstance(value, dict) else {}
    except (OSError, plistlib.InvalidFileException, ValueError, TypeError) as ex:
        logfunc(f'Anonymous Chat: could not read plist {path}: {ex}')
        return {}


def _group_identifiers(plist):
    identifiers = set()
    for key in ('com.apple.security.application-groups', 'application-groups',
                'AppGroups'):
        values = plist.get(key, []) if isinstance(plist, dict) else []
        if isinstance(values, str):
            values = [values]
        if isinstance(values, (list, tuple, set)):
            identifiers.update(_text(value).strip().casefold() for value in values
                               if _text(value).strip())
    return identifiers


def _is_target_group_identifier(value, known_group_identifiers=()):
    identifier = _text(value).strip().casefold()
    prefix = _TARGET_GROUP_PREFIX.casefold()
    return (identifier in set(known_group_identifiers) or identifier == prefix or
            identifier.startswith(prefix + '.'))


def _target_containers(context, files=None):
    """Discover app containers from metadata, never from a fixed UUID."""
    files = _files_found(context) if files is None else files
    bundle_ids = set()
    data_ids = set()
    group_ids = set()
    app_plists = {}
    known_group_identifiers = set()

    # Bundle metadata is the best source for any app-group entitlement names;
    # collect it before evaluating shared-container metadata.
    for path in files:
        kind, uuid = _container_location(path)
        if kind != 'bundle' or not uuid or os.path.basename(path).lower() != 'info.plist':
            continue
        plist = _read_plist(path)
        if plist.get('CFBundleIdentifier') == _BUNDLE_ID:
            bundle_ids.add(uuid)
            app_plists.setdefault('bundles', {})[uuid] = plist
            known_group_identifiers.update(_group_identifiers(plist))

    for path in files:
        kind, uuid = _container_location(path)
        if not kind or not uuid:
            continue
        name = os.path.basename(path).lower()
        if name == '.com.apple.mobile_container_manager.metadata.plist':
            plist = _read_plist(path)
            identifiers = (plist.get('MCMMetadataIdentifier'),
                           plist.get('MCMMetadataContainerIdentifier'))
            if kind in ('bundle', 'data') and any(
                    _text(identifier).strip().casefold() == _BUNDLE_ID.casefold()
                    for identifier in identifiers):
                {'bundle': bundle_ids, 'data': data_ids}[kind].add(uuid)
            elif kind == 'group' and any(
                    _is_target_group_identifier(identifier, known_group_identifiers)
                    for identifier in identifiers):
                group_ids.add(uuid)
        elif name == 'com.anonimchat.app.plist' and kind == 'data':
            # The preference path itself is an app-specific identifier and is a
            # useful fallback when a partial extraction lacks MCM metadata.
            data_ids.add(uuid)
        elif name == 'itunesmetadata.plist' and kind == 'bundle':
            plist = _read_plist(path)
            if plist.get('softwareVersionBundleId') == _BUNDLE_ID:
                bundle_ids.add(uuid)
    return bundle_ids, data_ids, group_ids, app_plists


def _target_db_paths(context, files=None):
    files = _files_found(context) if files is None else files
    _bundle_ids, data_ids, _group_ids, _app_plists = _target_containers(context, files)
    result = []
    for path in files:
        kind, uuid = _container_location(path)
        if kind == 'data' and uuid in data_ids and os.path.basename(path).lower() == _DB_NAME:
            result.append(path)
    return sorted(set(result))


def _source_label(context, path):
    return _relative_source(context, path)


def _query_rows(path, table, query):
    """Run an explicit-column query against an existing table, including WAL data."""
    # The upstream test harness can provide paths relative to its temporary
    # extraction directory.  Resolve them before iLEAPP's Windows SQLite URI
    # helper adds an extended-length prefix; production seeker paths are
    # already absolute, so this is a no-op there.
    path = os.path.abspath(path)
    if not does_table_exist_in_db(path, table):
        return []
    db = None
    try:
        safe_query = null_absent_columns(path, query)
        db = open_sqlite_db_readonly(path)
        if db is None:
            return []
        db.row_factory = sqlite3.Row
        return [dict(row) for row in db.execute(safe_query)]
    except (sqlite3.DatabaseError, OSError, TypeError, ValueError) as ex:
        logfunc(f'Anonymous Chat: query failed for {path}, table {table}: {ex}')
        return []
    finally:
        if db is not None:
            db.close()


def _text(value):
    return '' if value is None else str(value)


def _raw(value):
    return '' if value is None else value


def _read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as json_file:
            value = json.load(json_file)
        return value
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as ex:
        logfunc(f'Anonymous Chat: could not read JSON metadata {path}: {ex}')
        return None


def _manifest_account_identifiers(context, files=None):
    """Return signed-in identifiers explicitly named in the app manifest."""
    files = _files_found(context) if files is None else files
    _bundle_ids, data_ids, _group_ids, _app_plists = _target_containers(context, files)
    identifiers = set()

    def collect(value, key=''):
        if isinstance(value, dict):
            for child_key, child in value.items():
                normalized_key = re.sub(r'[^a-z0-9]', '', _text(child_key).casefold())
                collect(child, normalized_key)
            return
        if isinstance(value, (list, tuple)):
            for child in value:
                collect(child, key)
            return
        if key not in _MANIFEST_ACCOUNT_KEYS or not isinstance(value, str):
            # Some React Native stores encode a nested object as a JSON string.
            if isinstance(value, str) and value[:1] in ('{', '['):
                try:
                    collect(json.loads(value), key)
                except (json.JSONDecodeError, TypeError, ValueError):
                    pass
            return
        value = value.strip()
        if value:
            identifiers.add(value.casefold())

    for path in files:
        kind, token = _container_location(path)
        if (kind != 'data' or token not in data_ids and
                token != _BUNDLE_ID.upper() or
                os.path.basename(path).casefold() != 'manifest.json'):
            continue
        manifest = _read_json(path)
        if manifest is not None:
            collect(manifest)
    return identifiers


def _unix_time(value):
    if value in (None, ''):
        return ''
    try:
        return convert_unix_ts_to_utc(value)
    except (TypeError, ValueError, OSError, OverflowError):
        return value


def _conversation_time(value):
    if value in (None, ''):
        return ''
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return _unix_time(value)
    if isinstance(value, datetime):
        return value if value.tzinfo else ''
    text = _text(value).strip()
    if not re.search(r'(?:Z|[+-]\d{2}:?\d{2})$', text, re.IGNORECASE):
        # A naive human timestamp carries no zone evidence. Keep it in the raw
        # field instead of silently labelling it UTC.
        return ''
    try:
        parsed = datetime.fromisoformat(text.replace('Z', '+00:00').replace('z', '+00:00'))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else ''
    except (TypeError, ValueError, OSError, OverflowError):
        return ''


def _message_rows(db_path):
    query = '''
        SELECT
            m.message_id AS message_id,
            m.conversation_id AS conversation_id,
            m.msg_id AS msg_uuid,
            m.message AS message_text,
            m.media_url AS media_url,
            m.media_mime_type AS media_mime_type,
            m.media_ac_type AS media_ac_type,
            m.media_size AS media_size,
            m.media_duration AS media_duration,
            m.media_origin AS media_origin,
            m.media_show AS media_show,
            m.media_spotify AS media_spotify,
            m.anonymous_reveal AS anonymous_reveal,
            m.message_reaction AS message_reaction,
            m.message_reply AS message_reply,
            m.message_info AS message_info,
            m.message_verified_profile_link AS verified_profile_link,
            m.message_time AS message_time,
            m.sender AS sender_flag,
            m.sender_name AS sender_name,
            m.send_time AS send_time,
            c.from_username AS from_username,
            c.to_username AS to_username
        FROM messages AS m
        LEFT JOIN conversations AS c ON c.conversation_id = m.conversation_id
        ORDER BY m.message_id
    '''
    if does_table_exist_in_db(os.path.abspath(db_path), 'conversations'):
        return _query_rows(db_path, 'messages', query)
    query = '''
        SELECT
            m.message_id AS message_id,
            m.conversation_id AS conversation_id,
            m.msg_id AS msg_uuid,
            m.message AS message_text,
            m.media_url AS media_url,
            m.media_mime_type AS media_mime_type,
            m.media_ac_type AS media_ac_type,
            m.media_size AS media_size,
            m.media_duration AS media_duration,
            m.media_origin AS media_origin,
            m.media_show AS media_show,
            m.media_spotify AS media_spotify,
            m.anonymous_reveal AS anonymous_reveal,
            m.message_reaction AS message_reaction,
            m.message_reply AS message_reply,
            m.message_info AS message_info,
            m.message_verified_profile_link AS verified_profile_link,
            m.message_time AS message_time,
            m.sender AS sender_flag,
            m.sender_name AS sender_name,
            m.send_time AS send_time,
            NULL AS from_username,
            NULL AS to_username
        FROM messages AS m
        ORDER BY message_id
    '''
    return _query_rows(db_path, 'messages', query)


def _direction(row, local_accounts=()):
    sender_flag = row.get('sender_flag')
    sender_name = _text(row.get('sender_name'))
    from_username = _text(row.get('from_username'))
    to_username = _text(row.get('to_username'))
    local_accounts = {(_text(account)).casefold() for account in local_accounts}
    if local_accounts:
        from_is_local = from_username.casefold() in local_accounts
        to_is_local = to_username.casefold() in local_accounts
        sender_is_from = sender_name.casefold() == from_username.casefold()
        sender_is_to = sender_name.casefold() == to_username.casefold()
        if sender_flag == 0 and from_is_local and sender_is_from:
            return 'Outgoing'
        if sender_flag == 1 and to_is_local and sender_is_to:
            return 'Incoming'
    if sender_flag == 0 and sender_name and sender_name == from_username:
        return 'Outgoing'
    if sender_flag == 1 and sender_name and sender_name == to_username:
        return 'Incoming'
    return ''


def _other_party(row):
    # In this database, from_username identifies the local account for the
    # conversation and to_username identifies the remote participant.  The
    # sender flag/name relationship changes with direction, but the endpoints
    # do not swap.  Returning from_username for incoming rows made one LAVA
    # conversation contain two competing labels and could display the owner as
    # the other party.
    other_party = _text(row.get('to_username'))
    if other_party:
        return other_party
    if _direction(row) == 'Incoming':
        return _text(row.get('sender_name'))
    return ''


def _recipient(row, local_accounts=()):
    direction = _direction(row, local_accounts)
    if direction == 'Incoming':
        return _text(row.get('from_username'))
    if direction == 'Outgoing':
        return _text(row.get('to_username'))
    return ''


def _message_key(source, message_id, conversation_id, message_uuid):
    return (source, _text(conversation_id), _text(message_id), _text(message_uuid))


def _conversation_key(source, conversation_id, message_id='', message_uuid=''):
    # IDs are local to a database. Preserve the stored ID separately in reports.
    identity = ['conversation', _text(conversation_id)] if conversation_id not in (
        None, '') else ['unassigned message', _text(message_id), _text(message_uuid)]
    return json.dumps([source, *identity], ensure_ascii=True, separators=(',', ':'))


def _source_paths(context, paths):
    return '\n'.join(sorted({_source_label(context, path) for path in paths if path}))


def _comparable_time(value):
    converted = _unix_time(value)
    return converted if isinstance(converted, datetime) else None


def _conversation_rows(db_path):
    query = '''
        SELECT
            c.conversation_id AS conversation_id,
            c.from_username AS from_username,
            c.to_username AS to_username,
            c.anonymous_status AS anonymous_status,
            c.anonymous_color AS anonymous_color,
            c.anonymous_reveal AS anonymous_reveal,
            c.anonymous_alert AS anonymous_alert,
            c.anonymous_alias AS anonymous_alias,
            c.trusted_media AS trusted_media,
            c.pin_status AS pin_status,
            c.unread_count AS unread_count,
            c.last_message_time AS last_message_time,
            c.seen_message_id AS seen_message_id,
            c.seen_message_time AS seen_message_time,
            c.conversation_time AS conversation_time
        FROM conversations AS c
        ORDER BY conversation_id
    '''
    return _query_rows(db_path, 'conversations', query)


def _blocked_rows(db_path):
    query = '''
        SELECT
            b.block_id AS block_id,
            b.from_username AS from_username,
            b.to_username AS to_username
        FROM blocked AS b
        ORDER BY block_id
    '''
    return _query_rows(db_path, 'blocked', query)


def _media_table_rows(db_path):
    # media_data is deliberately not selected.  It is an application field
    # whose contents are not needed for metadata reporting and may be binary or
    # encoded content despite its declared type.
    query = '''
        SELECT
            a.media_id AS media_id,
            a.media_name AS media_name,
            a.media_time AS media_time
        FROM media AS a
        ORDER BY media_time, media_id
    '''
    return _query_rows(db_path, 'media', query)


def _join_unique(values):
    seen = []
    for value in values:
        value = _text(value)
        if value and value not in seen:
            seen.append(value)
    return '; '.join(seen)


def _format_fs_time(timestamp):
    try:
        return datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    except (OSError, OverflowError, TypeError, ValueError):
        return ''


def _created_time(stat):
    # POSIX st_ctime is inode-change time, not creation time.
    return _format_fs_time(getattr(stat, 'st_birthtime',
                                   stat.st_ctime if os.name == 'nt' else None))


def _format_zip_time(date_time):
    return (f'{date_time[0]:04d}-{date_time[1]:02d}-{date_time[2]:02d} '
            f'{date_time[3]:02d}:{date_time[4]:02d}:{date_time[5]:02d} '
            '(ZIP timestamp; timezone not recorded)')


def _timestamp_datetime(timestamp):
    try:
        return datetime.fromtimestamp(timestamp, timezone.utc)
    except (OSError, OverflowError, TypeError, ValueError):
        return None


def _zip_modified_at(seeker, info):
    """Read a ZIP member's extended modification time, when present."""
    decoder = getattr(seeker, 'decode_extended_timestamp', None)
    if not callable(decoder):
        return None
    try:
        _creation_time, modification_time = decoder(info.extra)
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError, OverflowError):
        return None
    return _timestamp_datetime(modification_time)


def _iter_source_entries(context, include=None):
    """Yield listing/metadata records without staging or reading file contents."""
    try:
        seeker = context.get_seeker()
    except ValueError:
        return

    zip_file = getattr(seeker, 'zip_file', None)
    if zip_file is not None:
        for info in zip_file.infolist():
            if info.is_dir() or info.filename.startswith('__MACOSX'):
                continue
            if include is not None and not include(_normalise_path(info.filename)):
                continue
            yield {
                'path': _normalise_path(info.filename),
                'size': info.file_size,
                'created': '',
                'modified': _format_zip_time(info.date_time),
                'modified_at': _zip_modified_at(seeker, info),
                'accessed': '',
                'kind': 'zip',
                'info': info,
                'handle': zip_file,
            }
        return

    tar_file = getattr(seeker, 'tar_file', None)
    if tar_file is not None:
        for member in tar_file.getmembers():
            if not member.isfile():
                continue
            if include is not None and not include(_normalise_path(member.name)):
                continue
            mtime = _format_fs_time(member.mtime)
            yield {
                'path': _normalise_path(member.name),
                'size': member.size,
                'created': '',
                'modified': mtime,
                'modified_at': _timestamp_datetime(member.mtime),
                'accessed': '',
                'kind': 'tar',
                'info': member,
                'handle': tar_file,
            }
        return

    raw_names = getattr(seeker, 'name_list', None)
    raw_entries = getattr(seeker, '_entries', None)  # pylint: disable=protected-access
    if isinstance(raw_names, list) and isinstance(raw_entries, dict):
        # FileSeekerRaw lists members publicly but keeps their on-image size and
        # timestamps in its entry map. Read those metadata fields only; staging
        # remains deferred to _stage_media_entry and the normal seeker API.
        for member in raw_names:
            if member.endswith('/') or (include is not None and
                                        not include(_normalise_path(member))):
                continue
            raw_entry = raw_entries.get(member)
            if raw_entry is None:
                continue
            raw_mtime = getattr(raw_entry, 'mtime', 0)
            modified_at = (_timestamp_datetime(raw_mtime)
                           if raw_mtime not in (None, '', 0) else None)
            reading = _text(getattr(raw_entry, 'reading', '')).strip()
            modified = (_format_fs_time(raw_mtime) if modified_at
                         else (reading + ' (filesystem timestamp; timezone not recorded)'
                               if reading else ''))
            yield {
                'path': _normalise_path(member),
                'size': getattr(raw_entry, 'size', 0),
                'created': '',
                'modified': modified,
                'modified_at': modified_at,
                'accessed': '',
                'kind': 'raw',
                'info': member,
                'handle': seeker,
            }
        return

    all_files = getattr(seeker, '_all_files', None)
    if isinstance(all_files, list):
        directory = _normalise_path(getattr(seeker, 'directory', '')).rstrip('/')
        for item in all_files:
            item = str(item)
            if include is not None and not include(_normalise_path(item)):
                continue
            try:
                stat = os.stat(item)
            except OSError:
                continue
            if not os.path.isfile(item):
                continue
            source_path = _normalise_path(item)
            if directory and source_path.lower().startswith(directory.lower() + '/'):
                source_path = source_path[len(directory) + 1:]
            yield {
                'path': source_path,
                'size': stat.st_size,
                'created': _created_time(stat),
                'modified': _format_fs_time(stat.st_mtime),
                'modified_at': _timestamp_datetime(stat.st_mtime),
                'accessed': _format_fs_time(stat.st_atime),
                'kind': 'directory',
                'info': item,
                'handle': None,
            }
        return

    # A single-file seeker has no complete filesystem listing.  It can still
    # be handled without reading content, should the selected file be relevant.
    single_file = getattr(seeker, 'single_file_abs_path', '')
    if include is not None and not include(_normalise_path(single_file)):
        return
    if single_file and os.path.isfile(single_file):
        try:
            stat = os.stat(single_file)
        except OSError:
            return
        yield {
            'path': _normalise_path(single_file),
            'size': stat.st_size,
            'created': _created_time(stat),
            'modified': _format_fs_time(stat.st_mtime),
            'modified_at': _timestamp_datetime(stat.st_mtime),
            'accessed': _format_fs_time(stat.st_atime),
            'kind': 'directory',
            'info': single_file,
            'handle': None,
        }


def _signature_from_entry(entry):
    """Return a media signature after one bounded offset-zero read.

    This function is called only for extensionless candidates.  It never emits
    or logs the bytes and never reads past byte 4095.
    """
    try:
        if entry['kind'] == 'directory':
            with open(entry['info'], 'rb') as media_file:
                header = media_file.read(_MAX_HEADER_BYTES)
        elif entry['kind'] == 'zip':
            with entry['handle'].open(entry['info']) as media_file:
                header = media_file.read(_MAX_HEADER_BYTES)
        elif entry['kind'] == 'tar':
            media_file = entry['handle'].extractfile(entry['info'])
            if media_file is None:
                return None
            with media_file:
                header = media_file.read(_MAX_HEADER_BYTES)
        else:
            return None
    except (OSError, EOFError, KeyError, RuntimeError, ValueError) as ex:
        logfunc(f'Anonymous Chat: bounded signature read failed for {entry["path"]}: {ex}')
        return None
    return _signature_classification(header)


def _signature_classification(header):
    """Classify straightforward signatures without parsing media structure."""
    if header.startswith(b'\xff\xd8\xff'):
        return 'JPEG', 'Image', 'File Signature'
    if header.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'PNG', 'Image', 'File Signature'
    if header.startswith((b'GIF87a', b'GIF89a')):
        return 'GIF', 'Image', 'File Signature'
    if len(header) >= 12 and header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return 'WebP', 'Image', 'File Signature'
    if header.startswith(b'BM'):
        return 'BMP', 'Image', 'File Signature'
    if header.startswith((b'II*\x00', b'MM\x00*')):
        return 'TIFF', 'Image', 'File Signature'
    if header.startswith(b'\xabKTX 11\xbb\r\n\x1a\n'):
        return 'KTX texture', 'Image/Texture', 'File Signature'
    if len(header) >= 12 and header[:4] == b'RIFF' and header[8:12] == b'WAVE':
        return 'WAV', 'Audio', 'File Signature'
    if header.startswith(b'ID3'):
        return 'MP3', 'Audio', 'File Signature'
    if header.startswith(b'OggS'):
        return 'Ogg', 'Audio', 'File Signature'
    if header.startswith(b'fLaC'):
        return 'FLAC', 'Audio', 'File Signature'
    if header.startswith(b'\x1a\x45\xdf\xa3'):
        return 'WebM/Matroska', 'Video', 'File Signature'
    if len(header) >= 8 and header[4:8] == b'ftyp':
        brand = header[8:12]
        if brand == b'qt  ':
            return 'MOV', 'Video', 'File Signature'
        if brand in (b'heic', b'heix', b'hevc', b'hevx'):
            return 'HEIC/HEIF', 'Image', 'File Signature'
        if brand in (b'avif', b'avis'):
            return 'AVIF', 'Image', 'File Signature'
        if brand in (b'mp4 ', b'isom', b'iso2', b'mp41', b'mp42', b'M4V '):
            return 'MP4/ISO Base Media', 'Video', 'File Signature'
        return 'ISO Base Media', 'Media Container', 'File Signature'
    return None


def _extension_classification(path):
    extension = os.path.splitext(path)[1].lower()
    return extension, _MEDIA_EXTENSIONS.get(extension)


def _extensionless_candidate(path):
    normalized = _normalise_path(path).lower()
    basename = os.path.basename(normalized)
    if basename in _NON_MEDIA_EXTENSIONLESS_NAMES:
        return False
    if os.path.splitext(basename)[1]:
        return False
    return any(segment in normalized for segment in (
        '/library/caches/',
        '/tmp/',
        '/documents/',
        '/library/application support/',
    ))


def _mime_classification(mime):
    mime = _text(mime).lower()
    if mime in ('image', 'video', 'audio'):
        return '', mime.title()
    if mime.startswith('image/'):
        return mime, 'Image'
    if mime.startswith('video/'):
        return mime, 'Video'
    if mime.startswith('audio/'):
        return mime, 'Audio'
    return '', ''


def _media_size(value):
    if value in (None, ''):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return int(numeric) if numeric.is_integer() and numeric > 0 else None


def _media_categories_compatible(reference, category):
    """Return whether the stored MIME category is compatible with a file entry."""
    _mime, reference_category = _mime_classification(reference.get('mime'))
    if not reference_category:
        return True
    reference_family = reference_category.split('/', 1)[0]
    entry_family = _text(category).split('/', 1)[0]
    return bool(entry_family) and reference_family == entry_family


def _split_reference(reference):
    try:
        return urlsplit(_text(reference).strip())
    except ValueError:
        return None


def _reference_path(reference):
    """Return a textual reference path/basename without accessing its destination."""
    reference = _text(reference).strip()
    if not reference:
        return '', ''
    parsed = _split_reference(reference)
    if parsed is None:
        return '', ''
    if parsed.scheme and parsed.netloc:
        return _normalise_path(parsed.path), os.path.basename(parsed.path)
    normalized = _normalise_path(reference.split('?', 1)[0].split('#', 1)[0])
    return normalized, os.path.basename(normalized.rstrip('/'))


def _entry_matches_reference(entry_path, reference):
    entry_normalized = _normalise_path(entry_path).rstrip('/')
    reference_path, reference_basename = _reference_path(reference)
    if not reference_path:
        return False, ''
    parsed = _split_reference(reference)
    remote_url = bool(parsed and parsed.scheme and parsed.netloc)
    if remote_url and parsed.scheme.casefold() in ('http', 'https'):
        # A remote URL identifies the application resource, not a local copy.
        # Its only local-cache association is the separate SDImageCache key tier.
        return False, ''
    reference_without_root = reference_path.strip('/')
    if '/' in reference_without_root and (entry_normalized == reference_path or
            entry_normalized.endswith('/' + reference_path.lstrip('/')) or
            reference_path.endswith('/' + entry_normalized.lstrip('/'))):
        return True, 'Path/URL path'
    if (reference_basename and not remote_url and
            '/' not in reference_without_root and
            os.path.basename(entry_normalized) == reference_basename):
        return True, 'Filename'
    return False, ''


def _reference_path_values(reference):
    values = [reference.get('reference')]
    values.extend(reference.get('path_references', ()))
    result = []
    for value in values:
        value = _text(value).strip()
        if value and value not in result:
            result.append(value)
    return result


def _media_entry_indexes(media_entries):
    indexes = {'paths': {}, 'suffixes': {}, 'filenames': {}}
    for entry_index, media_entry in enumerate(media_entries):
        normalized = _normalise_path(media_entry['entry']['path']).strip('/').rstrip('/')
        if not normalized:
            continue
        indexes['paths'].setdefault(normalized, []).append(entry_index)
        parts = normalized.split('/')
        for offset in range(len(parts)):
            suffix = '/'.join(parts[offset:])
            indexes['suffixes'].setdefault(suffix, []).append(entry_index)
        indexes['filenames'].setdefault(parts[-1], []).append(entry_index)
    return indexes


def _reference_candidate_indices(indexes, reference):
    candidates = set()
    for value in _reference_path_values(reference):
        reference_path, reference_basename = _reference_path(value)
        stripped = reference_path.strip('/')
        parsed = _split_reference(value)
        remote_url = bool(parsed and parsed.scheme and parsed.netloc)
        if remote_url and parsed.scheme.casefold() in ('http', 'https'):
            continue
        if '/' in stripped:
            candidates.update(indexes['paths'].get(stripped, ()))
            candidates.update(indexes['suffixes'].get(stripped, ()))
        elif reference_basename and not remote_url:
            candidates.update(indexes['filenames'].get(reference_basename, ()))
    return sorted(candidates)


def _reference_in_scope(entry, reference):
    source_kind, source_uuid = _container_location(reference.get('source'))
    entry_kind, entry_uuid = _container_location(entry['path'])
    if source_kind and entry_kind:
        return source_kind == entry_kind and source_uuid == entry_uuid
    # Bundle/group ownership was established by container metadata. Photos entries
    # never reach the cache matchers; they have their own explicit UUID bridge.
    return True


def _direct_media_matches(media_entries, references, matched_reference_ids=(),
                          filenames_only=False):
    """Resolve explicit stored paths, or stored media-table names, only."""
    proposals = {}
    blocked = set()
    indexes = _media_entry_indexes(media_entries)
    for ref_index, reference in enumerate(references):
        if ref_index in matched_reference_ids:
            continue
        if filenames_only and reference.get('kind') != 'Media Table Metadata':
            # A message's filename, size, or timestamp is not an app-to-file
            # relationship. Message attachments must use their stored path/URL
            # or the dedicated SDImageCache key tier.
            continue
        if not _reference_path_values(reference):
            continue
        candidates = []
        for entry_index in _reference_candidate_indices(indexes, reference):
            media_entry = media_entries[entry_index]
            entry = media_entry['entry']
            if not _reference_in_scope(entry, reference):
                continue
            accepted = False
            for path_reference in _reference_path_values(reference):
                matched, method = _entry_matches_reference(entry['path'], path_reference)
                if matched and (method == 'Filename') == filenames_only:
                    accepted = True
                    break
            if accepted:
                candidates.append(entry_index)
        if not candidates:
            continue
        if len(candidates) != 1:
            blocked.add(ref_index)
            continue
        entry_index = candidates[0]
        media_entry = media_entries[entry_index]
        stored_size = _media_size(reference.get('size'))
        if (not _media_categories_compatible(reference, media_entry['category']) or
                (stored_size is not None and stored_size !=
                 _media_size(media_entry['entry'].get('size')))):
            blocked.add(ref_index)
            continue
        method = ('Direct: media-table stored filename' if filenames_only
                  else 'Direct: stored path/URL path')
        method += '; compatible MIME/category'
        if stored_size is not None:
            method += '; exact stored size'
        proposals.setdefault(entry_index, []).append((ref_index, reference, method))

    result = {}
    for entry_index, matches in proposals.items():
        identities = {row['reference'] for _, row, _ in matches
                      if row['kind'] == 'Message Attachment Reference'}
        if len(identities) > 1:
            # Distinct URLs with the same basename are not established copies.
            blocked.update(index for index, row, _ in matches
                           if row['kind'] == 'Message Attachment Reference')
            matches = [match for match in matches
                       if match[1]['kind'] != 'Message Attachment Reference']
        if matches:
            result[entry_index] = matches
    return result, blocked


def _sdimagecache_key(entry_path):
    """Return an SDImageCache filename key without reading the cached file."""
    normalized = _normalise_path(entry_path).lower()
    if _SDIMAGECACHE_PATH not in normalized:
        return ''
    stem = os.path.splitext(os.path.basename(normalized))[0]
    return stem if _SDIMAGECACHE_KEY_RE.fullmatch(stem) else ''


def _sdimagecache_url_matches(media_entries, references, direct_entry_indices,
                              matched_reference_ids, blocked_reference_ids=None):
    """Match SDImageCache files to the stored URL text used as their cache key.

    SDImageCache stores the MD5 of its textual cache key as the disk filename.  This
    hashes only the database URL string; no media bytes are opened or hashed.  A
    positive stored size must agree with the filesystem size.  Zero/absent sizes are
    treated as unavailable, while MIME/category compatibility remains required.
    """
    entries_by_key = {}
    for entry_index, media_entry in enumerate(media_entries):
        if entry_index in direct_entry_indices:
            continue
        key = _sdimagecache_key(media_entry['entry']['path'])
        if key:
            entries_by_key.setdefault(key, []).append(entry_index)

    references_by_key = {}
    urls_by_key = {}
    for reference_index, reference in enumerate(references):
        if (reference_index in matched_reference_ids or
                reference.get('kind') != 'Message Attachment Reference'):
            continue
        for stored_url in _reference_path_values(reference):
            parsed = _split_reference(stored_url)
            if (parsed is None or parsed.scheme not in ('http', 'https') or
                    not parsed.netloc):
                continue
            # MD5 is the application's cache-key naming algorithm here, not a security
            # digest and not a hash of media content.
            key = hashlib.md5(
                stored_url.encode('utf-8'), usedforsecurity=False).hexdigest()
            if key not in entries_by_key:
                continue
            references_by_key.setdefault(key, []).append((reference_index, reference))
            urls_by_key.setdefault(key, set()).add(stored_url)

    matches_by_entry = {}
    for key, keyed_references in references_by_key.items():
        entry_indices = entries_by_key[key]
        # Do not accept an MD5 collision or let a weaker timestamp tier override it.
        if len(urls_by_key[key]) != 1:
            if blocked_reference_ids is not None:
                blocked_reference_ids.update(index for index, _ in keyed_references)
            continue
        for reference_index, reference in keyed_references:
            scoped_entries = [index for index in entry_indices
                              if _reference_in_scope(media_entries[index]['entry'], reference)]
            if len(scoped_entries) != 1:
                if scoped_entries and blocked_reference_ids is not None:
                    blocked_reference_ids.add(reference_index)
                continue
            entry_index = scoped_entries[0]
            media_entry = media_entries[entry_index]
            entry_size = _media_size(media_entry['entry'].get('size'))
            if not _media_categories_compatible(reference, media_entry['category']):
                if blocked_reference_ids is not None:
                    blocked_reference_ids.add(reference_index)
                continue
            stored_size = _media_size(reference.get('size'))
            if stored_size is not None and stored_size > 0:
                if entry_size != stored_size:
                    if blocked_reference_ids is not None:
                        blocked_reference_ids.add(reference_index)
                    continue
                size_note = 'exact stored size'
            else:
                size_note = 'stored size unavailable/zero'
            method = (
                'Direct: SDImageCache URL-derived filename '
                f'(MD5 of stored URL text; {size_note})'
            )
            matches_by_entry.setdefault(entry_index, []).append(
                (reference_index, reference, method))
    return matches_by_entry


def _message_info_media_tokens(value):
    """Extract explicit media path/ID tokens from structured message metadata."""
    paths = []
    joins = []

    def add(target, item):
        item = _text(item).strip()
        if item and item not in target:
            target.append(item)

    def collect(item, key=''):
        if isinstance(item, dict):
            for child_key, child in item.items():
                normalized_key = re.sub(r'[^a-z0-9]', '', _text(child_key).casefold())
                collect(child, normalized_key)
            return
        if isinstance(item, (list, tuple)):
            for child in item:
                collect(child, key)
            return
        if not isinstance(item, str):
            return
        stripped = item.strip()
        if stripped[:1] in ('{', '['):
            try:
                collect(json.loads(stripped), key)
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
            return
        if key in _MESSAGE_INFO_JOIN_KEYS:
            add(joins, stripped)
        if key in _MESSAGE_INFO_PATH_KEYS:
            add(paths, stripped)

    collect(value)
    return paths, joins


def _attachment_references(db_paths, context):
    """Build safe textual/numeric attachment references; never select media_data."""
    refs = []
    media_rows = []
    local_accounts = _manifest_account_identifiers(context)
    for db_path in db_paths:
        source = _source_label(context, db_path)
        for row in _message_rows(db_path):
            stored_reference = row.get('media_url')
            info_paths, info_joins = _message_info_media_tokens(row.get('message_info'))
            path_references = []
            if _text(stored_reference).strip():
                path_references.append(_text(stored_reference).strip())
            path_references.extend(path for path in info_paths
                                   if path not in path_references)
            has_media_metadata = any(row.get(column) is not None for column in (
                'media_url', 'media_mime_type', 'media_size', 'media_duration'))
            has_media_metadata = has_media_metadata or bool(info_paths or info_joins)
            if not has_media_metadata:
                continue
            reference = _text(stored_reference).strip()
            refs.append({
                'kind': 'Message Attachment Reference',
                'reference': reference,
                'source': source,
                'message_timestamp': _unix_time(row.get('message_time')),
                'media_timestamp': '',
                'conversation_id': _raw(row.get('conversation_id')),
                'message_id': _raw(row.get('message_id')),
                'message_uuid': _text(row.get('msg_uuid')),
                'direction': _direction(row, local_accounts),
                'sender': _text(row.get('sender_name')),
                'recipient': _recipient(row, local_accounts),
                'media_id': '',
                'filename': _reference_path(reference)[1],
                'path_references': path_references,
                'join_tokens': info_joins,
                'mime': _text(row.get('media_mime_type')),
                'size': _raw(row.get('media_size')),
                'duration': _raw(row.get('media_duration')),
                'media_origin': _raw(row.get('media_origin')),
                'media_show': _raw(row.get('media_show')),
            })
        for row in _media_table_rows(db_path):
            media_rows.append({
                'kind': 'Media Table Metadata',
                'reference': _text(row.get('media_name')).strip(),
                'source': source,
                'message_timestamp': '',
                'media_timestamp': _unix_time(row.get('media_time')),
                'conversation_id': '',
                'message_id': '',
                'message_uuid': '',
                'direction': '',
                'sender': '',
                'recipient': '',
                'media_id': _text(row.get('media_id')),
                'filename': _text(row.get('media_name')),
                'path_references': [_text(row.get('media_name')).strip()],
                'join_tokens': [_text(row.get('media_id')).strip(),
                                _text(row.get('media_name')).strip()],
                'mime': '',
                'size': '',
                'duration': '',
                'media_origin': '',
                'media_show': '',
            })
    return refs + media_rows


def _target_media_entry(entry, _target_bundle_ids, target_data_ids, target_group_ids):
    kind, uuid = _container_location(entry['path'])
    # The app bundle is executable/package content; its icons and resources are
    # not user/chat media. Inventory only data and app-group containers.
    return ((kind == 'data' and uuid in target_data_ids) or
            (kind == 'group' and uuid in target_group_ids))


def _media_entry_type(entry, references):
    path = entry['path']
    extension, extension_type = _extension_classification(path)
    if extension_type:
        return extension, extension_type[0], extension_type[1], 'Extension'

    # A known database MIME can identify a non-standard filename without
    # inspecting bytes.  This is still a textual metadata classification.
    matched_refs = []
    for reference in references:
        if not _reference_in_scope(entry, reference):
            continue
        for path_reference in _reference_path_values(reference):
            matched, _method = _entry_matches_reference(path, path_reference)
            if matched:
                mime_type, category = _mime_classification(reference['mime'])
                if mime_type:
                    matched_refs.append((mime_type, category, 'Stored MIME Type'))
                break
    if matched_refs:
        if len(set(matched_refs)) != 1:
            return '', 'Unknown', 'Unknown', 'Conflicting stored MIME types'
        return '', matched_refs[0][0], matched_refs[0][1], matched_refs[0][2]

    if not _extensionless_candidate(path):
        return '', '', '', ''
    classification = _signature_from_entry(entry)
    if classification:
        return '', classification[0], classification[1], classification[2]
    return '', '', '', ''


_MEDIA_MIME_BY_TYPE = {
    'JPEG': 'image/jpeg',
    'PNG': 'image/png',
    'GIF': 'image/gif',
    'WebP': 'image/webp',
    'HEIC': 'image/heic',
    'HEIF': 'image/heif',
    'BMP': 'image/bmp',
    'TIFF': 'image/tiff',
    'ICO': 'image/x-icon',
    'AVIF': 'image/avif',
    'DNG': 'image/x-adobe-dng',
    'KTX texture': 'image/ktx',
    'MOV': 'video/quicktime',
    'MP4': 'video/mp4',
    'M4V': 'video/x-m4v',
    'AVI': 'video/x-msvideo',
    'Matroska': 'video/x-matroska',
    'WebM': 'video/webm',
    '3GPP': 'video/3gpp',
    'MPEG': 'video/mpeg',
    'MPEG transport stream': 'video/mp2t',
    'AAC': 'audio/aac',
    'M4A': 'audio/mp4',
    'MP3': 'audio/mpeg',
    'WAV': 'audio/wav',
    'Ogg': 'audio/ogg',
    'Opus': 'audio/opus',
    'WebM/Matroska': 'video/webm',
    'HEIC/HEIF': 'image/heic',
    'MP4/ISO Base Media': 'video/mp4',
    'ISO Base Media': 'application/octet-stream',
}

_MEDIA_EXTENSION_BY_TYPE = {
    'JPEG': 'jpg',
    'PNG': 'png',
    'GIF': 'gif',
    'WebP': 'webp',
    'HEIC': 'heic',
    'HEIF': 'heif',
    'MOV': 'mov',
    'MP4': 'mp4',
    'M4V': 'm4v',
    'AAC': 'aac',
    'M4A': 'm4a',
    'MP3': 'mp3',
    'WAV': 'wav',
    'Ogg': 'ogg',
    'Opus': 'opus',
    'WebM/Matroska': 'webm',
    'HEIC/HEIF': 'heic',
    'AVIF': 'avif',
    'MP4/ISO Base Media': 'mp4',
}


def _media_search_patterns(path):
    normalized = _normalise_path(path).lstrip('/')
    # The seeker accepts fnmatch patterns. Escape literal filename metacharacters.
    normalized = ''.join({'[': '[[]', '*': '[*]', '?': '[?]'}.get(char, char)
                         for char in normalized)
    return (normalized, f'*/{normalized}')


def _stage_media_entry(context, entry):
    """Stage one target media entry through iLEAPP's normal seeker API.

    The seeker owns archive extraction and directory copying.  This function does
    not inspect the staged bytes; Media Manager does that only during an examiner's
    actual report run.
    """
    try:
        seeker = context.get_seeker()
    except ValueError:
        return ''
    for pattern in _media_search_patterns(entry['path']):
        try:
            staged = seeker.search(pattern, return_on_first_hit=True)
        except (AttributeError, OSError, RuntimeError, ValueError):
            continue
        if staged:
            return str(staged)
    return ''


def _register_staged_media(context, staged):
    """Make a dynamically staged path visible to check_in_media()."""
    try:
        files_found = context.get_files_found()
    except ValueError:
        return False
    if not any(str(path) == staged for path in files_found):
        files_found.append(staged)
    # Context caches its basename lookup.  Invalidate it after adding a path.
    if hasattr(context, '_filename_lookup_map'):
        # Context exposes no public cache invalidation method.
        context._filename_lookup_map = {}  # pylint: disable=protected-access
    return True


def _media_cache(context):
    """Keep Media Manager references stable across the message/media artifacts."""
    try:
        seeker = context.get_seeker()
    except ValueError:
        return {}
    cache = getattr(seeker, '_anonymous_chat_media_cache', None)
    if cache is None:
        cache = {}
        setattr(seeker, '_anonymous_chat_media_cache', cache)
    return cache


def _media_force_type(detected_type, matches):
    identified_mime = _MEDIA_MIME_BY_TYPE.get(detected_type, '')
    if identified_mime:
        return identified_mime
    if _mime_classification(detected_type)[0]:
        return detected_type
    for _index, reference, _method in matches:
        mime, _category = _mime_classification(reference.get('mime'))
        if mime:
            return mime
    return ''


def _media_reference(context, entry, detected_type, matches):
    """Check in one filesystem media file using the iLEAPP Media Manager."""
    cache = _media_cache(context)
    try:
        artifact_name = context.get_artifact_name()
    except ValueError:
        artifact_name = ''
    cache_key = (artifact_name, entry['path'])
    if cache_key in cache:
        return cache[cache_key]

    staged = _stage_media_entry(context, entry)
    if not staged or not _register_staged_media(context, staged):
        cache[cache_key] = ''
        return ''

    extension = entry.get('extension') or _MEDIA_EXTENSION_BY_TYPE.get(detected_type, '')
    try:
        media_ref = check_in_media(
            staged,
            name=os.path.basename(entry['path']),
            force_type=(_MEDIA_MIME_BY_TYPE.get(detected_type, '')
                        if entry.get('photos_original')
                        else _media_force_type(detected_type, matches)) or None,
            force_extension=extension or None,
        ) or ''
    except (OSError, RuntimeError, TypeError, ValueError) as ex:
        logfunc(f'Anonymous Chat: Media Manager could not check in {entry["path"]}: {ex}')
        media_ref = ''
    cache[cache_key] = media_ref
    return media_ref


def _message_media_references(db_paths, context):
    """Scope each media association to its database, conversation and message."""
    candidates = {}
    for row in _media_rows(db_paths, context):
        if row['kind'] != 'Filesystem Media' or not row.get('media_ref'):
            continue
        key = row.get('_message_key')
        if key is None:
            continue
        method = row.get('correlation', '')
        rank = 3 if method.startswith('Direct:') else 2
        candidates.setdefault(key, []).append((rank, row['media_ref'], method))
    references = {}
    for key, items in candidates.items():
        best_rank = max(item[0] for item in items)
        best = {(ref, method) for rank, ref, method in items if rank == best_rank}
        media_refs = {ref for ref, _method in best}
        references[key] = {
            'media_ref': next(iter(media_refs)) if len(media_refs) == 1 else '',
            'correlation': ('; '.join(sorted({method for _, method in best}))
                            if len(media_refs) == 1 else
                            'Ambiguous: multiple equally supported local files; media not linked'),
        }
    return references


def _normalised_media_token(value):
    value = _text(value).strip()
    if not value:
        return ''
    return _normalise_path(value).rstrip('/').casefold()


def _explicit_media_table_message_matches(media_entries, references,
                                          direct_matches_by_entry,
                                          matched_reference_ids):
    """Propagate a media-table file to a message only through stored join data."""
    media_rows_by_token = {}
    for media_row_index, media_row in enumerate(references):
        if media_row.get('kind') != 'Media Table Metadata':
            continue
        tokens = list(media_row.get('join_tokens', ()))
        tokens.extend((media_row.get('media_id'), media_row.get('filename')))
        for token in {_normalised_media_token(item) for item in tokens} - {''}:
            media_rows_by_token.setdefault(token, set()).add(media_row_index)

    matches_by_entry = {}
    for message_index, message in enumerate(references):
        if (message_index in matched_reference_ids or
                message.get('kind') != 'Message Attachment Reference'):
            continue
        media_row_indices = set()
        for token in message.get('join_tokens', ()):
            media_row_indices.update(media_rows_by_token.get(
                _normalised_media_token(token), ()))
        media_row_indices = {
            index for index in media_row_indices
            if references[index].get('source') == message.get('source')
        }
        if len(media_row_indices) != 1:
            continue
        media_row_index = next(iter(media_row_indices))
        candidate_entries = []
        for entry_index, entry_matches in direct_matches_by_entry.items():
            if any(match[0] == media_row_index for match in entry_matches):
                candidate_entries.append(entry_index)
        if len(candidate_entries) != 1:
            continue
        entry_index = candidate_entries[0]
        media_row = references[media_row_index]
        linked_message = dict(message)
        linked_message['media_id'] = media_row.get('media_id', '')
        linked_message['media_timestamp'] = media_row.get('media_timestamp', '')
        method = ('Direct: explicit message_info media join -> media table row; '
                  'filesystem relationship established separately')
        if media_entries[entry_index]['entry'].get('photos_original'):
            method += '; Photos original via app media_id = ZASSET.ZUUID'
        matches_by_entry.setdefault(entry_index, []).append(
            (message_index, linked_message, method))
    return matches_by_entry


def _photos_asset_paths(context, references):
    """Resolve only app-referenced Photos UUIDs using safe SQLite text fields."""
    wanted = {}
    for index, reference in enumerate(references):
        if reference.get('kind') != 'Media Table Metadata':
            continue
        asset_id = _text(reference.get('media_id')).removeprefix('ph://')
        uuid = asset_id.split('/', 1)[0]
        if re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', uuid):
            wanted.setdefault(uuid.upper(), []).append((index, reference))
    if not wanted:
        return {}
    try:
        seeker = context.get_seeker()
        # Stage the database and WAL as known SQLite inputs, never any Photos
        # media. search without return_on_first_hit returns the staged path list.
        staged = seeker.search('*/Media/PhotoData/Photos.sqlite*')
    except (AttributeError, ValueError, OSError, RuntimeError) as ex:
        logfunc(f'Anonymous Chat: Photos metadata unavailable: {ex}')
        return {}
    if isinstance(staged, str):
        staged = [staged]
    db_paths = [str(path) for path in (staged or [])
                if os.path.basename(str(path)) == 'Photos.sqlite']
    if len(db_paths) != 1:
        return {}
    db_path = db_paths[0]
    rows = _query_rows(db_path, 'ZASSET',
                       'SELECT ZUUID AS uuid, ZDIRECTORY AS directory, '
                       'ZFILENAME AS filename FROM ZASSET')
    by_uuid = {}
    for row in rows:
        uuid = _text(row.get('uuid')).upper()
        if uuid in wanted:
            by_uuid.setdefault(uuid, []).append(row)
    paths = {}
    path_owners = {}
    ambiguous_paths = set()
    for uuid, assets in by_uuid.items():
        if len(assets) != 1:
            continue
        row = assets[0]
        directory = _text(row.get('directory'))
        filename = _text(row.get('filename'))
        # Restrict to relative DCIM paths stored in Photos, rejecting traversal.
        if (not directory.startswith('DCIM/') or not filename or
                '\\' in directory or '\\' in filename or '/' in filename or
                any(part in ('', '.', '..') for part in directory.split('/')) or
                filename in ('.', '..')):
            continue
        method = ('Photos original: app media_id = ZASSET.ZUUID; source ' +
                  _source_label(context, db_path))
        matches = [(index, reference, method) for index, reference in wanted[uuid]]
        path = directory + '/' + filename
        if path in path_owners and path_owners[path] != uuid:
            ambiguous_paths.add(path)
        path_owners[path] = uuid
        paths[path] = matches
    for path in ambiguous_paths:
        paths.pop(path, None)
    return paths


def _photos_relative_path(path):
    """Return a root-independent Photos DCIM path, or an empty string."""
    normalized = _normalise_path(path).lstrip('/')
    marker = re.search(r'(?:^|/)(?:private/)?var/mobile/Media/(DCIM/.+)$',
                       normalized, re.IGNORECASE)
    return marker.group(1) if marker else ''


def _media_rows(db_paths, context):
    files = _files_found(context)
    bundle_ids, data_ids, group_ids, _app_plists = _target_containers(context, files)
    if not (bundle_ids or data_ids or group_ids or db_paths):
        return []
    references = _attachment_references(db_paths, context)
    photos_paths = _photos_asset_paths(context, references)
    photos_entries = []
    media_entries = []
    def include(path):
        # Filter listing paths before stat calls on unrelated files in large inputs.
        if _target_media_entry({'path': path}, bundle_ids, data_ids, group_ids):
            return True
        return _photos_relative_path(path) in photos_paths

    for entry in _iter_source_entries(context, include=include):
        photo_matches = photos_paths.get(_photos_relative_path(entry['path']))
        if photo_matches:
            extension, classification = _extension_classification(entry['path'])
            if classification:
                entry['photos_original'] = True
                entry['photos_source'] = photo_matches[0][2]
                photos_entries.append(({
                    'entry': entry, 'extension': extension,
                    'detected_type': classification[0], 'category': classification[1],
                    'identification': 'Photos asset UUID + stored path + extension',
                }, photo_matches))
            continue
        if not _target_media_entry(entry, bundle_ids, data_ids, group_ids):
            continue
        extension, detected_type, category, identification = _media_entry_type(entry, references)
        if not detected_type:
            continue
        media_entries.append({
            'entry': entry,
            'extension': extension,
            'detected_type': detected_type,
            'category': category,
            'identification': identification,
        })

    direct_matches_by_entry, blocked_reference_ids = _direct_media_matches(
        media_entries, references)
    direct_entry_indices = set(direct_matches_by_entry)
    matched_reference_ids = {index for matches in direct_matches_by_entry.values()
                             for index, _reference, _method in matches}

    cache_key_matches_by_entry = _sdimagecache_url_matches(
        media_entries, references, direct_entry_indices,
        matched_reference_ids | blocked_reference_ids, blocked_reference_ids)
    for entry_index, matches in cache_key_matches_by_entry.items():
        direct_matches_by_entry.setdefault(entry_index, []).extend(matches)
        direct_entry_indices.add(entry_index)
        matched_reference_ids.update(match[0] for match in matches)

    filename_matches, filename_blocked = _direct_media_matches(
        media_entries, references, matched_reference_ids | blocked_reference_ids,
        filenames_only=True)
    blocked_reference_ids.update(filename_blocked)
    for entry_index, matches in filename_matches.items():
        direct_matches_by_entry.setdefault(entry_index, []).extend(matches)
        direct_entry_indices.add(entry_index)
        matched_reference_ids.update(match[0] for match in matches)

    # Use Photos originals only after the app-cache tiers, and only for media-table
    # references that have no surviving local app file. The media-table row is an
    # explicit app-to-asset relationship; it is not a message relationship by itself.
    photos_direct = {}
    for media_entry, photo_matches in photos_entries:
        matches = [match for match in photo_matches
                   if match[0] not in matched_reference_ids]
        if not matches:
            continue
        entry_index = len(media_entries)
        media_entries.append(media_entry)
        photos_direct[entry_index] = matches
        direct_matches_by_entry[entry_index] = matches
    for entry_index, matches in photos_direct.items():
        matched_reference_ids.update(match[0] for match in matches)

    explicit_message_matches = _explicit_media_table_message_matches(
        media_entries, references, direct_matches_by_entry,
        matched_reference_ids | blocked_reference_ids)
    for entry_index, matches in explicit_message_matches.items():
        direct_matches_by_entry[entry_index].extend(matches)
        matched_reference_ids.update(match[0] for match in matches)

    output = []
    for entry_index, media_entry in enumerate(media_entries):
        entry = media_entry['entry']
        extension = media_entry['extension']
        detected_type = media_entry['detected_type']
        category = media_entry['category']
        identification = media_entry['identification']
        matches = direct_matches_by_entry.get(entry_index, [])
        # Unmatched files remain in the metadata inventory but are not copied into
        # Media Manager.  Conversation display only needs locally correlated files.
        media_ref = _media_reference(context, entry, detected_type, matches) if matches else ''
        # One row per association preserves typed timestamps and participant pairs.
        # A file with no surviving reference still receives one inventory row.
        for _, reference, method in matches or [(None, {}, '')]:
            key = None
            if reference.get('kind') == 'Message Attachment Reference':
                key = _message_key(
                    reference['source'], reference['message_id'],
                    reference['conversation_id'], reference['message_uuid'])
            output.append({
                'kind': 'Filesystem Media',
                'message_timestamp': reference.get('message_timestamp', ''),
                'media_timestamp': reference.get('media_timestamp', ''),
                'conversation_id': _text(reference.get('conversation_id')),
                'message_id': _text(reference.get('message_id')),
                'message_uuid': reference.get('message_uuid', ''),
                'direction': reference.get('direction', ''),
                'sender': reference.get('sender', ''),
                'recipient': reference.get('recipient', ''),
                'media_id': reference.get('media_id', ''),
                'filename': os.path.basename(entry['path']),
                'media_ref': media_ref,
                'local_path': '',
                'remote_url': '',
                'mime': reference.get('mime', ''),
                'size': reference.get('size', ''),
                'duration': reference.get('duration', ''),
                'media_origin': reference.get('media_origin', ''),
                'media_show': reference.get('media_show', ''),
                'detected_type': detected_type,
                'category': category,
                'identification': identification,
                'extension': extension,
                'filesystem_path': entry['path'],
                'filesystem_size': entry['size'],
                'created': entry['created'],
                'modified': entry['modified'],
                'accessed': entry['accessed'],
                'database_referenced': 'Yes' if reference else 'No',
                'filesystem_present': 'Yes',
            'correlation': (method or
                            'Unlinked: no stored app-to-file relationship; '
                            'size/timestamp/name-only matching not used'),
                'source': '\n'.join(filter(None, (entry['path'], reference.get('source')))),
                '_message_key': key,
            })

    for index, reference in enumerate(references):
        if reference['kind'] == 'Message Attachment Reference':
            parsed_reference = _split_reference(reference['reference'])
            remote_url = reference['reference'] if (
                parsed_reference and parsed_reference.scheme) else ''
            local_path = '' if remote_url else reference['reference']
        else:
            remote_url = ''
            local_path = reference['reference']
        output.append({
            'kind': reference['kind'],
            'message_timestamp': reference['message_timestamp'],
            'media_timestamp': reference['media_timestamp'],
            'conversation_id': reference['conversation_id'],
            'message_id': reference['message_id'],
            'message_uuid': reference['message_uuid'],
            'direction': reference['direction'],
            'sender': reference['sender'],
            'recipient': reference['recipient'],
            'media_id': reference['media_id'],
            'filename': reference['filename'],
            'media_ref': '',
            'local_path': local_path,
            'remote_url': remote_url,
            'mime': reference['mime'],
            'size': reference['size'],
            'duration': reference['duration'],
            'media_origin': reference['media_origin'],
            'media_show': reference['media_show'],
            'detected_type': '',
            'category': '',
            'identification': 'Stored Database Metadata',
            'extension': os.path.splitext(reference['filename'])[1].lower(),
            'filesystem_path': '',
            'filesystem_size': '',
            'created': '',
            'modified': '',
            'accessed': '',
            'database_referenced': 'Yes',
            'filesystem_present': 'Correlated' if index in matched_reference_ids else 'No',
            'correlation': ('Unlinked: ambiguous or contradictory stored path metadata; '
                            'heuristic matching not used'
                            if index in blocked_reference_ids and
                            index not in matched_reference_ids else
                            '' if index in matched_reference_ids else
                            'Unlinked: no stored app-to-file relationship; '
                            'size/timestamp/name-only matching not used'),
            'source': reference['source'],
        })
    return output


def _common_media_headers():
    return (
        'Record Type',
        ('Message Timestamp', 'datetime'),
        ('Media Timestamp', 'datetime'),
        'Conversation ID',
        'Message ID',
        'Message UUID',
        'Direction',
        'Sender Username',
        'Recipient Username',
        'Attachment/Media ID',
        'Filename',
        ('Media', 'media'),
        'Local Path',
        'Remote URL',
        'Stored MIME Type',
        'Stored Size',
        'Media Duration',
        'Raw Media Origin',
        'Raw Media Show',
        'Detected File Type',
        'Media Category',
        'Identification Method',
        'Extension',
        'Filesystem Path',
        'Filesystem Size',
        'Created Timestamp',
        'Modified Timestamp',
        'Access Timestamp',
        'Database Referenced',
        'Filesystem Present',
        'Correlation Method',
        'Source',
    )


def _common_media_values(row):
    return (
        row['kind'],
        row['message_timestamp'],
        row['media_timestamp'],
        row['conversation_id'],
        row['message_id'],
        row['message_uuid'],
        row['direction'],
        row['sender'],
        row['recipient'],
        row['media_id'],
        row['filename'],
        row['media_ref'],
        row['local_path'],
        row['remote_url'],
        row['mime'],
        row['size'],
        row['duration'],
        row['media_origin'],
        row['media_show'],
        row['detected_type'],
        row['category'],
        row['identification'],
        row['extension'],
        row['filesystem_path'],
        row['filesystem_size'],
        row['created'],
        row['modified'],
        row['accessed'],
        row['database_referenced'],
        row['filesystem_present'],
        row['correlation'],
        row['source'],
    )


@artifact_processor
def anonymousChat_appInfo(context):
    files = _files_found(context)
    bundle_ids, data_ids, group_ids, app_plists = _target_containers(context, files)
    store_by_uuid = {}
    sources = []
    for path in files:
        kind, uuid = _container_location(path)
        if ((kind == 'bundle' and uuid in bundle_ids) or
                (kind == 'data' and uuid in data_ids) or
                (kind == 'group' and uuid in group_ids)) and path.lower().endswith('.plist'):
            sources.append(_source_label(context, path))
        if os.path.basename(path).lower() == 'itunesmetadata.plist':
            plist = _read_plist(path)
            if plist.get('softwareVersionBundleId') == _BUNDLE_ID:
                store_by_uuid[uuid] = plist
    rows = []
    for bundle_uuid in sorted(bundle_ids):
        info = app_plists.get('bundles', {}).get(bundle_uuid, {})
        iTunes_values = store_by_uuid.get(bundle_uuid, {})
        app_name = (info.get('CFBundleDisplayName') or info.get('CFBundleName') or
                    iTunes_values.get('itemName') or _APP_NAME)
        version = info.get('CFBundleShortVersionString') or iTunes_values.get(
            'bundleShortVersionString', '')
        build = info.get('CFBundleVersion') or iTunes_values.get('bundleVersion', '')
        rows.append((
            _BUNDLE_ID,
            app_name,
            version,
            build,
            bundle_uuid,
            '; '.join(sorted(data_ids)),
            '; '.join(sorted(group_ids)),
            iTunes_values.get('itemName', ''),
            iTunes_values.get('artistName', ''),
            iTunes_values.get('purchaseDate', ''),
            _source_paths(context, sources),
        ))
    if not rows and data_ids:
        rows.append((_BUNDLE_ID, _APP_NAME, '', '', '', '; '.join(sorted(data_ids)),
                     '; '.join(sorted(group_ids)), '', '', '', _source_paths(context, sources)))
    headers = (
        'Bundle ID', 'Application Name', 'Version', 'Build', 'Bundle Container UUID',
        'Data Container UUID(s)', 'App Group UUID(s)', 'Store Item Name', 'Developer',
        'Purchase Date', 'Source',
    )
    return headers, rows, _source_paths(context, sources)


@artifact_processor
def anonymousChat_accounts(context):
    db_paths = _target_db_paths(context)
    local_accounts = _manifest_account_identifiers(context)
    aggregate = {}
    source_by_account = {}
    for db_path in db_paths:
        source = _source_label(context, db_path)
        for row in _message_rows(db_path):
            account = _text(row.get('from_username'))
            if not account:
                continue
            item = aggregate.setdefault(account, {
                'conversations': set(), 'messages': 0, 'outgoing': 0, 'incoming': 0,
                'first': None, 'last': None, 'supported': 0, 'undetermined': 0,
            })
            item['conversations'].add((source, _text(row.get('conversation_id'))))
            item['messages'] += 1
            direction = _direction(row, local_accounts)
            if direction == 'Outgoing':
                item['outgoing'] += 1
                item['supported'] += 1
            elif direction == 'Incoming':
                item['incoming'] += 1
                item['supported'] += 1
            else:
                item['undetermined'] += 1
            timestamp = _comparable_time(row.get('message_time'))
            if timestamp is not None:
                item['first'] = timestamp if item['first'] is None else min(item['first'], timestamp)
                item['last'] = timestamp if item['last'] is None else max(item['last'], timestamp)
            source_by_account.setdefault(account, set()).add(source)
    rows = []
    for account in sorted(aggregate):
        item = aggregate[account]
        evidence = ('from_username; sender/name relationship supports direction for '
                    f'{item["supported"]} message(s)')
        if account.casefold() in local_accounts:
            evidence += '; app manifest signed-in username matches from_username'
        if item['undetermined']:
            evidence += f'; {item["undetermined"]} message(s) remain undetermined'
        rows.append((
            account,
            len([conversation for _source, conversation in item['conversations'] if conversation]),
            item['messages'],
            item['outgoing'],
            item['incoming'],
            item['first'] or '',
            item['last'] or '',
            'Candidate local account identifier; owner not established',
            evidence,
            '\n'.join(sorted(source_by_account[account])),
        ))
    headers = (
        'Account Identifier', 'Conversation Count', 'Message Count', 'Outgoing Count',
        'Incoming Count', ('First Message Timestamp', 'datetime'),
        ('Last Message Timestamp', 'datetime'), 'Owner Attribution', 'Evidence', 'Source',
    )
    return headers, rows, _source_paths(context, db_paths)


@artifact_processor
def anonymousChat_conversations(context):
    db_paths = _target_db_paths(context)
    local_accounts = _manifest_account_identifiers(context)
    rows = []
    for db_path in db_paths:
        source = _source_label(context, db_path)
        messages = _message_rows(db_path)
        counts = {}
        for message in messages:
            key = _text(message.get('conversation_id'))
            item = counts.setdefault(key, {'total': 0, 'outgoing': 0, 'incoming': 0, 'last': None})
            item['total'] += 1
            direction = _direction(message, local_accounts)
            if direction == 'Outgoing':
                item['outgoing'] += 1
            elif direction == 'Incoming':
                item['incoming'] += 1
            timestamp = _comparable_time(message.get('message_time'))
            if timestamp is not None:
                item['last'] = timestamp if item['last'] is None else max(item['last'], timestamp)
        for conversation in _conversation_rows(db_path):
            key = _text(conversation.get('conversation_id'))
            count = counts.get(key, {'total': 0, 'outgoing': 0, 'incoming': 0, 'last': None})
            rows.append((
                conversation.get('conversation_id'),
                _text(conversation.get('from_username')),
                _text(conversation.get('to_username')),
                _text(conversation.get('to_username')),
                count['total'],
                count['outgoing'],
                count['incoming'],
                _unix_time(conversation.get('last_message_time')),
                count['last'] or '',
                _text(conversation.get('seen_message_id')),
                _unix_time(conversation.get('seen_message_time')),
                conversation.get('anonymous_status'),
                _text(conversation.get('anonymous_color')),
                _text(conversation.get('anonymous_reveal')),
                conversation.get('anonymous_alert'),
                _text(conversation.get('anonymous_alias')),
                conversation.get('trusted_media'),
                conversation.get('pin_status'),
                conversation.get('unread_count'),
                _conversation_time(conversation.get('conversation_time')),
                _text(conversation.get('conversation_time')),
                source,
                _conversation_key(source, conversation.get('conversation_id')),
            ))
    headers = (
        'Conversation ID', 'From Username', 'To Username', 'Other Party', 'Message Count',
        'Outgoing Count', 'Incoming Count', ('Stored Last Message Timestamp', 'datetime'),
        ('Observed Last Message Timestamp', 'datetime'), 'Seen Message ID',
        ('Seen Message Timestamp', 'datetime'), 'Anonymous Status (raw)',
        'Anonymous Color', 'Anonymous Reveal', 'Anonymous Alert (raw)', 'Anonymous Alias',
        'Trusted Media (raw)', 'Pin Status (raw)', 'Unread Count (raw)',
        ('Conversation Timestamp', 'datetime'), 'Conversation Timestamp (raw)', 'Source',
        'Conversation Key',
    )
    return headers, rows, _source_paths(context, db_paths)


@artifact_processor
def anonymousChat_messages(context):
    db_paths = _target_db_paths(context)
    local_accounts = _manifest_account_identifiers(context)
    media_by_message = _message_media_references(db_paths, context)
    rows = []
    for db_path in db_paths:
        source = _source_label(context, db_path)
        for message in _message_rows(db_path):
            key = _message_key(source, message.get('message_id'),
                               message.get('conversation_id'), message.get('msg_uuid'))
            media_link = media_by_message.get(key, {})
            rows.append((
                _unix_time(message.get('message_time')),
                _unix_time(message.get('send_time')),
                _direction(message, local_accounts),
                _text(message.get('sender_name')),
                _other_party(message),
                _text(message.get('message_text')),
                media_link.get('media_ref', '') if isinstance(media_link, dict) else media_link,
                message.get('conversation_id'),
                message.get('message_id'),
                _text(message.get('msg_uuid')),
                message.get('sender_flag'),
                _text(message.get('from_username')),
                _text(message.get('to_username')),
                _text(message.get('media_url')),
                _text(message.get('media_mime_type')),
                message.get('media_size'),
                message.get('media_duration'),
                message.get('media_ac_type'),
                message.get('media_origin'),
                message.get('media_show'),
                _text(message.get('media_spotify')),
                _text(message.get('anonymous_reveal')),
                _text(message.get('message_reaction')),
                _text(message.get('message_reply')),
                _text(message.get('message_info')),
                message.get('verified_profile_link'),
                source,
                media_link.get('correlation', '') if isinstance(media_link, dict) else '',
                _conversation_key(source, message.get('conversation_id'),
                                  message.get('message_id'), message.get('msg_uuid')),
            ))
    data_headers = (
        ('Message Timestamp', 'datetime'), ('Send Timestamp', 'datetime'), 'Direction',
        'Sender Name', 'Other Party', 'Message Text', ('Media', 'media'), 'Conversation ID',
        'Message ID', 'Message UUID', 'Sender Flag (raw)', 'From Username', 'To Username',
        'Media URL', 'Media MIME Type', 'Media Size', 'Media Duration', 'Media AC Type (raw)',
        'Media Origin (raw)', 'Media Show (raw)', 'Media Spotify (raw)',
        'Anonymous Reveal (raw)', 'Message Reaction (raw)', 'Message Reply (raw)',
        'Message Info (raw)', 'Verified Profile Link (raw)', 'Source', 'Media Link Method',
        'Conversation Key',
    )
    return data_headers, rows, _source_paths(context, db_paths)


@artifact_processor
def anonymousChat_blocked(context):
    db_paths = _target_db_paths(context)
    rows = []
    for db_path in db_paths:
        source = _source_label(context, db_path)
        for row in _blocked_rows(db_path):
            rows.append((row.get('block_id'), _text(row.get('from_username')),
                         _text(row.get('to_username')), source))
    return ('Block ID', 'From Username', 'To Username', 'Source'), rows, _source_paths(context, db_paths)


@artifact_processor
def anonymousChat_media(context):
    db_paths = _target_db_paths(context)
    rows = [_common_media_values(row) for row in _media_rows(db_paths, context)]
    return _common_media_headers(), rows, _source_paths(context, db_paths)
