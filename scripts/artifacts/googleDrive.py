__artifacts_v2__ = {
    "google_drive_accounts": {
        "name": "Google Drive - Accounts",
        "description": "Google accounts signed in to the Google Drive app, with the account id, "
                       "email, display name and profile image URL recorded in each account's "
                       "cello.db cache",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-15",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Google Drive",
        "notes": "One row per cello.db under Documents/drivekit/users/<account id>/. Identity "
                 "fields come from the undocumented protobuf stored in the properties table under "
                 "the key driveway_account, or account in older app versions; fields are selected "
                 "by shape and, in every tested store, the decoded account id equals the account "
                 "directory name in the path. The root folder title is the items row named by the "
                 "root_id property. Reference for the older gdx-cello path: Mattia Epifani, 'iOS 15 "
                 "Image Forensics Analysis and Tools Comparison - Browsers, Mail Clients, and "
                 "Productivity apps', blog.digital-forensics.it.",
        "paths": ('*/Documents/drivekit/users/*/*cello/cello.db*',),
        "output_types": "standard",
        "artifact_icon": "user-circle",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 2 rows",
            "hickman_ios15": "iOS 15 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 4 rows",
            "abe_ios16": "iOS 16.5 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
        },
    },
    "google_drive_items": {
        "name": "Google Drive - Items",
        "description": "Files and folders cached in the Google Drive app's cello.db, with Drive "
                       "timestamps, the reconstructed folder path, trash and ownership flags, and "
                       "the locally stored copy of the file where one exists on the device",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-15",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Google Drive",
        "notes": "One row per row of the items table of each cello.db under "
                 "Documents/drivekit/users/<account id>/. Timestamps are Unix milliseconds as "
                 "stored. The folder path is reconstructed by walking the stable_parents table; "
                 "every tested store had at most one parent per item. Offline Status is reported "
                 "as stored because no value list ships in the file. The Local File column shows "
                 "the file saved under files/<item id>/ when the extraction carries one; the "
                 "cache is a partial view of the account's Drive, not a complete listing. Column "
                 "drift across app versions (trashed_date and the spam columns are absent in "
                 "older stores) is reported as empty.",
        "paths": ('*/Documents/drivekit/users/*/*cello/cello.db*',
                  '*/Documents/drivekit/users/*/files/*/*'),
        "output_types": "standard",
        "artifact_icon": "brand-google-drive",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 59 rows",
            "hickman_ios15": "iOS 15 | 21 rows",
            "magnet_ios16": "iOS 16.1.1 | 10 rows",
            "abe_ios16": "iOS 16.5 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 21 rows",
            "otto_ios17": "iOS 17.5.1 | 26 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "hc_ios18_7": "iOS 18.7.8 | 20 rows",
        },
    },
    "google_drive_local_files": {
        "name": "Google Drive - Local Files",
        "description": "Drive file content stored on the device under the Google Drive app's "
                       "files directory, each shown with the Drive item it belongs to when the "
                       "account's cello.db still lists it",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-15",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Google Drive",
        "notes": "One row per file under Documents/drivekit/users/<account id>/files/<item id>/. "
                 "A file whose item id has no row in that account's cello.db is still listed, "
                 "with the Drive metadata columns empty; in tested samples such files exist. "
                 "Offline Last Modified is the offlineLastModifiedDate value the app records for "
                 "the item, in Unix milliseconds as stored. The newer gdx-content sibling "
                 "directory was empty in every tested image and is not covered.",
        "paths": ('*/Documents/drivekit/users/*/*cello/cello.db*',
                  '*/Documents/drivekit/users/*/files/*/*'),
        "output_types": "standard",
        "artifact_icon": "file-download",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows, files directories present but empty",
            "hickman_ios15": "iOS 15 | 0 rows, gdx layout without a files directory",
            "magnet_ios16": "iOS 16.1.1 | 0 rows, files directories present but empty",
            "abe_ios16": "iOS 16.5 | 0 rows, files directory present but empty",
            "iphone11_ios17": "iOS 17.3 | 0 rows, gdx layout without a files directory",
            "otto_ios17": "iOS 17.5.1 | 3 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows, files directory present but empty",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows, files directories present but empty",
        },
    },
    "google_drive_thumbnails": {
        "name": "Google Drive - Thumbnails",
        "description": "Thumbnail images cached by the Google Drive app, each shown with the "
                       "Drive item it belongs to when the account's cello.db still lists it",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-15",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Google Drive",
        "notes": "One row per file under Documents/drivekit/users/<account id>/thumbnails/"
                 "<item id>/. Files are stored without an extension; the image type is read from "
                 "the file content (PNG and JPEG observed). Thumbnail filenames end in an "
                 "undocumented number, reported as stored; in tested samples it parses as Unix "
                 "milliseconds inside the account's activity window. A thumbnail whose item id "
                 "has no row in cello.db is still listed. The newer gdx-thumbnails sibling "
                 "directory was empty in every tested image and is not covered.",
        "paths": ('*/Documents/drivekit/users/*/*cello/cello.db*',
                  '*/Documents/drivekit/users/*/thumbnails/*/*'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 29 rows",
            "hickman_ios15": "iOS 15 | 0 rows, gdx layout without a thumbnails directory",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 0 rows, thumbnails directory present but empty",
            "iphone11_ios17": "iOS 17.3 | 0 rows, gdx layout without a thumbnails directory",
            "otto_ios17": "iOS 17.5.1 | 13 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows, thumbnails directory present but empty",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
        },
    },
    "google_drive_comments": {
        "name": "Google Drive - Comments",
        "description": "Document comments cached by the Google Drive app, with the comment text, "
                       "author display name, quoted document text and anchor position",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-15",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Google Drive",
        "notes": "Read from comments_snapshot_<account id>.db under Documents/<account id>/. "
                 "Each comments row carries an NSKeyedArchiver blob whose entries hold the "
                 "comment; keys are reported under their stored names (content, author, postId, "
                 "origin, actionStateString). In every tested row the blob's publishedMs equals "
                 "the row's published_date, and every tested blob held exactly one entry, so "
                 "multi-entry threads are handled but unexercised. The anchor value is reported "
                 "as stored. Dates are Unix seconds. The is_content_reaction column is absent in "
                 "older stores and reported empty. The stored item_identifier reads "
                 "<mime type>:<item id> in tested samples; the Drive Title column is filled only "
                 "when the id part resolves to an items row in the same account's cello.db. "
                 "Populated comment rows, including text, author and the title join, were "
                 "verified on a private sample; every registered corpus store carried an empty "
                 "comments table.",
        "paths": ('*/Documents/*/comments_snapshot_*.db*',
                  '*/Documents/drivekit/users/*/*cello/cello.db*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows, comments table empty",
            "magnet_ios16": "iOS 16.1.1 | 0 rows, comments tables empty",
            "abe_ios16": "iOS 16.5 | 0 rows, comments table empty",
            "otto_ios17": "iOS 17.5.1 | 0 rows, comments table empty",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows, comments tables empty",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows, comments tables empty",
        },
    },
}

import os
import re
import struct

from google.protobuf.message import DecodeError

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    get_plist_content,
    get_sqlite_db_records,
    check_in_media,
    null_absent_columns,
    logfunc,
)
from scripts import blackboxprotobuf

_ACCOUNT_DIR_RE = re.compile(r'[/\\]drivekit[/\\]users[/\\]([^/\\]+)[/\\]')
_CONTENT_FILE_RE = re.compile(
    r'[/\\]drivekit[/\\]users[/\\][^/\\]+[/\\]files[/\\]([^/\\]+)[/\\][^/\\]+$')
_THUMBNAIL_FILE_RE = re.compile(
    r'[/\\]drivekit[/\\]users[/\\][^/\\]+[/\\]thumbnails[/\\]([^/\\]+)[/\\]([^/\\]+)$')
_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)


def _account_from_path(path):
    match = _ACCOUNT_DIR_RE.search(str(path))
    return match.group(1) if match else ''


def _yes_no(value):
    '''Render a stored boolean, keeping absence empty.

    NULL means the store does not carry the column (or the row has no value),
    so rendering it as No would turn absence into a negative finding.
    '''
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return '' if value is None else str(value)


def _when(value):
    '''Convert a stored Unix timestamp, keeping 0 and NULL empty.

    The items table stores 0 in date columns such as viewed_by_me_date; 0 is
    not an observed event, so it is reported empty rather than as 1970.
    '''
    return convert_unix_ts_to_utc(value) if value else ''


def _cello_dbs(files_found):
    return [str(f) for f in files_found if str(f).endswith('cello.db')]


def _decode_account_proto(blob):
    '''Pick the account identity fields out of the cello.db account protobuf.

    Newer stores keep the account message under driveway_account at field 2.1,
    older ones under account at field 1, and the display name has been seen at
    field 3 in older stores and field 9 in newer ones. The message is
    undocumented, so each candidate is accepted only if its shape matches:
    digits for the account id, an address shape for the email, a URL shape for
    the image. Anything that does not match is reported empty.
    '''
    result = {'id': '', 'email': '', 'name': '', 'image': ''}
    try:
        message, _ = blackboxprotobuf.decode_message(blob)
    except _DECODE_ERRORS as ex:
        logfunc(f'Google Drive account protobuf did not decode: {ex}')
        return result

    account = message.get('2', {})
    if isinstance(account, dict):
        account = account.get('1', {})
    if not isinstance(account, dict) or '2' not in account:
        account = message.get('1', {})
    if not isinstance(account, dict):
        return result

    candidate = _text(account.get('2'))
    if candidate.isdigit():
        result['id'] = candidate
    candidate = _text(account.get('8'))
    if _EMAIL_RE.match(candidate):
        result['email'] = candidate
    candidate = _text(account.get('5'))
    if candidate.startswith(('http://', 'https://', '//')):
        result['image'] = candidate
    for field in ('9', '3'):
        candidate = account.get(field)
        if isinstance(candidate, bytes):
            name = _text(candidate)
            if name and '\x00' not in name:
                result['name'] = name
                break
    return result


@artifact_processor
def google_drive_accounts(context):
    data_list = []
    for db_path in _cello_dbs(context.get_files_found()):
        account_id = _account_from_path(db_path)
        rows = get_sqlite_db_records(
            db_path,
            "SELECT property, value FROM properties "
            "WHERE property IN ('driveway_account', 'account', 'root_id')")
        values = {record[0]: record[1] for record in rows}
        blob = values.get('driveway_account') or values.get('account')
        decoded = _decode_account_proto(blob) if blob else {
            'id': '', 'email': '', 'name': '', 'image': ''}

        root_title = ''
        root_id = _text(values.get('root_id'))
        if root_id:
            escaped = root_id.replace("'", "''")
            for record in get_sqlite_db_records(
                    db_path, f"SELECT title FROM items WHERE id = '{escaped}'"):
                root_title = record[0]
        data_list.append((
            account_id,
            decoded['email'],
            decoded['name'],
            decoded['image'],
            root_title,
            context.get_relative_path(db_path),
        ))

    data_headers = (
        'Account ID',
        'Email',
        'Display Name',
        'Profile Image URL',
        'Root Folder Title',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


def _local_file_index(files_found):
    '''Map (account id, item id) to the content files stored on the device.'''
    index = {}
    for found in files_found:
        found = str(found)
        match = _CONTENT_FILE_RE.search(found)
        if match:
            account_id = _account_from_path(found)
            index.setdefault((account_id, match.group(1)), []).append(found)
    return index


def _parent_paths(db_path):
    '''Folder title chain per stable_id, walked up through stable_parents.'''
    titles = {}
    parents = {}
    for record in get_sqlite_db_records(
            db_path, 'SELECT stable_id, title FROM items'):
        titles[record[0]] = record[1]
    for record in get_sqlite_db_records(
            db_path, 'SELECT item_stable_id, parent_stable_id FROM stable_parents'):
        parents.setdefault(record[0], record[1])

    def path_for(stable_id):
        chain = []
        current = parents.get(stable_id)
        seen = set()
        while current is not None and current not in seen and len(chain) < 50:
            seen.add(current)
            chain.append(titles.get(current, ''))
            current = parents.get(current)
        return '/'.join(reversed(chain))

    return path_for


@artifact_processor
def google_drive_items(context):
    files_found = context.get_files_found()
    local_files = _local_file_index(files_found)
    data_list = []

    query = '''
    SELECT created_date, modified_date, modified_by_me_date, viewed_by_me_date,
           shared_with_me_date, trashed_date, title, is_folder, mime_type,
           quota_bytes, starred, is_owner, trashed, explicitly_trashed, hidden,
           id, stable_id,
           (SELECT value FROM item_properties
            WHERE key = 'offlineStatus' AND item_stable_id = stable_id) AS offline_status
    FROM items
    ORDER BY created_date
    '''
    for db_path in _cello_dbs(files_found):
        account_id = _account_from_path(db_path)
        path_for = _parent_paths(db_path)
        for record in get_sqlite_db_records(db_path, null_absent_columns(db_path, query)):
            media_ref = ''
            stored = local_files.get((account_id, record[15]), [])
            if stored:
                media_ref = check_in_media(stored[0], record[6] or '') or ''
            data_list.append((
                _when(record[0]),
                _when(record[1]),
                _when(record[2]),
                _when(record[3]),
                _when(record[4]),
                _when(record[5]),
                record[6],
                _yes_no(record[7]),
                record[8],
                record[9],
                _yes_no(record[10]),
                _yes_no(record[11]),
                _yes_no(record[12]),
                _yes_no(record[13]),
                _yes_no(record[14]),
                path_for(record[16]),
                record[15],
                record[17],
                media_ref,
                account_id,
                context.get_relative_path(db_path),
            ))

    data_headers = (
        ('Created', 'datetime'),
        ('Modified', 'datetime'),
        ('Modified By Me', 'datetime'),
        ('Viewed By Me', 'datetime'),
        ('Shared With Me', 'datetime'),
        ('Trashed Date', 'datetime'),
        'Title',
        'Folder',
        'Mime Type',
        'Quota Bytes',
        'Starred',
        'User is Owner',
        'Trashed',
        'Explicitly Trashed',
        'Hidden',
        'Folder Path',
        'Item ID',
        'Offline Status (as stored)',
        ('Local File', 'media'),
        'Account ID',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def google_drive_local_files(context):
    files_found = context.get_files_found()
    local_files = _local_file_index(files_found)
    data_list = []

    item_query = '''
    SELECT id, title, mime_type, modified_date, trashed,
           (SELECT value FROM item_properties
            WHERE key = 'offlineLastModifiedDate' AND item_stable_id = stable_id)
           AS offline_last_modified
    FROM items
    '''
    items_by_key = {}
    for db_path in _cello_dbs(files_found):
        account_id = _account_from_path(db_path)
        for record in get_sqlite_db_records(db_path, null_absent_columns(db_path, item_query)):
            items_by_key[(account_id, record[0])] = record

    for (account_id, item_id), paths in sorted(local_files.items()):
        item = items_by_key.get((account_id, item_id))
        for stored in sorted(paths):
            media_ref = check_in_media(stored, os.path.basename(stored)) or ''
            data_list.append((
                _when(item[5]) if item else '',
                _when(item[3]) if item else '',
                os.path.basename(stored),
                item[1] if item else '',
                item[2] if item else '',
                _yes_no(item[4]) if item else '',
                'Yes' if item else 'No',
                item_id,
                media_ref,
                account_id,
                context.get_relative_path(stored),
            ))

    data_headers = (
        ('Offline Last Modified', 'datetime'),
        ('Item Modified', 'datetime'),
        'Local Name',
        'Drive Title',
        'Mime Type',
        'Trashed',
        'In cello.db',
        'Item ID',
        ('File', 'media'),
        'Account ID',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def google_drive_thumbnails(context):
    files_found = context.get_files_found()
    data_list = []

    titles_by_key = {}
    for db_path in _cello_dbs(files_found):
        account_id = _account_from_path(db_path)
        for record in get_sqlite_db_records(db_path, 'SELECT id, title FROM items'):
            titles_by_key[(account_id, record[0])] = record[1]

    for found in files_found:
        found = str(found)
        match = _THUMBNAIL_FILE_RE.search(found)
        if not match:
            continue
        account_id = _account_from_path(found)
        item_id = match.group(1)
        filename = match.group(2)
        suffix = filename.rsplit('-', 1)[-1] if '-' in filename else ''

        extension = None
        try:
            with open(found, 'rb') as handle:
                magic = handle.read(8)
            if magic.startswith(b'\x89PNG'):
                extension = 'png'
            elif magic.startswith(b'\xff\xd8'):
                extension = 'jpg'
        except OSError:
            pass
        media_ref = check_in_media(
            found, titles_by_key.get((account_id, item_id), item_id),
            force_extension=extension) or ''

        data_list.append((
            titles_by_key.get((account_id, item_id), ''),
            item_id,
            suffix,
            media_ref,
            account_id,
            context.get_relative_path(found),
        ))

    data_headers = (
        'Drive Title',
        'Item ID',
        'Filename Number (as stored)',
        ('Thumbnail', 'media'),
        'Account ID',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'


@artifact_processor
def google_drive_comments(context):
    files_found = context.get_files_found()
    data_list = []

    titles_by_key = {}
    for db_path in _cello_dbs(files_found):
        cello_account = _account_from_path(db_path)
        for record in get_sqlite_db_records(db_path, 'SELECT id, title FROM items'):
            titles_by_key[(cello_account, record[0])] = record[1]

    query = '''
    SELECT published_date, updated_date, item_identifier, quote, anchor,
           deleted, is_content_reaction, discussion_blob_data
    FROM comments
    ORDER BY published_date
    '''
    for db_path in files_found:
        db_path = str(db_path)
        if not os.path.basename(db_path).startswith('comments_snapshot_') \
                or not db_path.endswith('.db'):
            continue
        account_id = os.path.basename(db_path).replace(
            'comments_snapshot_', '').replace('.db', '')
        for record in get_sqlite_db_records(db_path, null_absent_columns(db_path, query)):
            entries = get_plist_content(record[7]) if record[7] else []
            if not isinstance(entries, list) or not entries:
                entries = [{}]
            identifier = record[2] or ''
            id_part = identifier.split(':', 1)[-1]
            drive_title = titles_by_key.get((account_id, id_part), '')
            for entry in entries:
                if not isinstance(entry, dict):
                    entry = {}
                author = entry.get('author') or {}
                data_list.append((
                    _when(record[0]),
                    _when(record[1]),
                    entry.get('content', ''),
                    author.get('KeyActorEncoderName', ''),
                    author.get('kKeyActorEmailAddress', ''),
                    record[3],
                    drive_title,
                    identifier,
                    entry.get('postId', ''),
                    entry.get('origin', ''),
                    entry.get('actionStateString', ''),
                    _yes_no(record[5]),
                    _yes_no(record[6]),
                    record[4],
                    account_id,
                    context.get_relative_path(db_path),
                ))

    data_headers = (
        ('Published', 'datetime'),
        ('Updated', 'datetime'),
        'Comment',
        'Author Name',
        'Author Email',
        'Quoted Text',
        'Drive Title',
        'Item Identifier (as stored)',
        'Post ID',
        'Origin (as stored)',
        'Action State (as stored)',
        'Deleted',
        'Content Reaction',
        'Anchor (as stored)',
        'Account ID',
        'Source Path',
    )
    return data_headers, data_list, 'See Source Path column'
