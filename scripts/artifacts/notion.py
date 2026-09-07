__artifacts_v2__ = {
    "notion_ios_blocks": {
        "name": "Notion - Blocks",
        "description": "The content blocks Notion held on the device, with the text of each and "
                       "the times it was created and last edited.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Notion",
        "notes": "One row per row of the block table in Library/LocalDatabase/notion.db. In the "
                 "block table a page and each paragraph, heading, list item or image inside it "
                 "are separate rows joined by Parent ID, and Type says which kind a row is. Text "
                 "is read from the row's properties field, which holds the block's rich text as "
                 "nested JSON arrays; the text segments are joined and the formatting is "
                 "dropped. 760 of the 949 rows on the tested image carried properties; a blank "
                 "Text is a row whose properties field held no text, and whether such a block "
                 "holds content elsewhere is not established. Created Time, Last Edited Time and "
                 "Last Access Time are Unix milliseconds. Created By and Last Edited By are "
                 "resolved against the notion_user table in the same store and fall back to the "
                 "stored identifier when no user row matches; 890 of the rows recorded a "
                 "creating user. Alive is the flag the row carries and was 0 on 3 rows of the "
                 "tested image, and Moved To Trash Time was set on 1; the meaning of a 0 Alive "
                 "value is not sourced. A row is not evidence that the content was authored on "
                 "this device, and Created By names the account the record credits rather than "
                 "the person at the keyboard. The store keeps a write-ahead log that is "
                 "load-bearing in both directions on the tested image: reading with the log "
                 "gives 949 blocks and reading the database alone gives 945, while the "
                 "transactions table holds 5 rows without the log and none with it, so the log "
                 "must travel with the database. Deleted From Trash Time held no value on any "
                 "row of the tested image.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/LocalDatabase/notion.db*',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "file-text",
        "sample_data": {
            "iphone12_ios18": "iOS 18.7 | Notion | 949 rows",
        },
    },
    "notion_ios_page_activity": {
        "name": "Notion - Page Activity",
        "description": "Page visits and exits Notion recorded, with the page each one names.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Notion",
        "notes": "One row per row of the records table whose record_table field is page_visit or "
                 "page_exit. Timestamp is the row's own timestamp in Unix milliseconds and Event "
                 "Time is a second time the record's JSON carries, present on the page_visit "
                 "rows. Page Title is joined from the block the record's parent_id names, so a "
                 "visit to a page whose block row is absent still reports its identifier with "
                 "the title left blank; that join resolved on 12 of the 12 visits and 11 of the "
                 "16 exits on the tested image. User is resolved against the notion_user table "
                 "in the same store. A page_visit row is a record the app wrote naming a page; "
                 "what it establishes about a person is not sourced. Whether the table is pruned "
                 "is not established, so absence of a row is not evidence that a page was not "
                 "visited. Space ID held one value on all 28 rows of the tested image.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/LocalDatabase/notion.db*',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "eye",
        "sample_data": {
            "iphone12_ios18": "iOS 18.7 | Notion | 28 rows",
        },
    },
    "notion_ios_users": {
        "name": "Notion - Users",
        "description": "The Notion accounts the device cached for the workspace, with the email "
                       "address held against each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Notion",
        "notes": "One row per row of the notion_user table. Every one of the 16 rows on the "
                 "tested image carried an email address and a display name; the separate given "
                 "name and family name fields were empty on all of them, and 9 carried a profile "
                 "photo address. A row is not evidence that the person used this device, and the "
                 "signed-in account is not distinguished here from the others; the space_user "
                 "and user_root tables in the same store are not reported by this artifact. "
                 "Profile Photo is the address the record holds and is not fetched. Banned (as "
                 "stored) and Suspended Time held no value on any of the 16 rows.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/LocalDatabase/notion.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users",
        "sample_data": {
            "iphone12_ios18": "iOS 18.7 | Notion | 16 rows",
        },
    },
    "notion_ios_collections": {
        "name": "Notion - Collections",
        "description": "The Notion databases the device cached, with the name and description of "
                       "each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Notion",
        "notes": "One row per row of the collection table. Name and Description hold rich text "
                 "in the same nested JSON arrays the blocks use and are joined into plain text "
                 "here. 15 of the 17 rows on the tested image carried a name. Column Names is "
                 "read from the row's schema field, which maps an internal column key to that "
                 "column's name and type; the names are listed and the types are not, and a "
                 "collection whose schema does not parse reports a blank. The rows of a "
                 "collection are blocks and are reported by the Blocks artifact, where the "
                 "collection is named by Parent ID, so this artifact describes the containers "
                 "rather than their contents. Alive (as stored) held the single value 1 and "
                 "Parent Table the single value block on all 17 rows of the tested image.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/LocalDatabase/notion.db*',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "database",
        "sample_data": {
            "iphone12_ios18": "iOS 18.7 | Notion | 17 rows",
        },
    },
}

import json
import os
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db, get_sqlite_db_records,
                               logfunc)

_STORE_NAME = 'notion.db'
_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _stores(files_found):
    '''Every Notion database among the matched files, directories skipped.'''
    seen = []
    for found in files_found:
        path = str(found)
        if os.path.isdir(path):
            continue
        if os.path.basename(path) == _STORE_NAME and path not in seen:
            seen.append(path)
    return seen


def _rows(path, table, columns, where=''):
    '''Rows of a table, or nothing when the store does not have it.'''
    if not does_table_exist_in_db(path, table):
        logfunc(f'Notion: {table} is not in this notion.db')
        return []
    statement = f'SELECT {columns} FROM {table}' + (f' WHERE {where}' if where else '')
    try:
        return list(get_sqlite_db_records(path, statement))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'Notion: could not read {table}: {error}')
        return []


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _ms_to_utc(value):
    '''Unix milliseconds to an aware UTC datetime, or ''.'''
    if value in (None, '', 0):
        return ''
    try:
        return _UNIX_EPOCH_UTC + timedelta(milliseconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _rich_text(value):
    '''Notion rich text, stored as nested arrays, joined into plain text.

    The outer list holds segments and each segment's first element is its text, so the
    formatting that follows it is dropped rather than rendered.
    '''
    if value in (None, ''):
        return ''
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            return ''
    if not isinstance(value, list):
        return ''
    parts = []
    for segment in value:
        if isinstance(segment, list) and segment and isinstance(segment[0], str):
            parts.append(segment[0])
        elif isinstance(segment, str):
            parts.append(segment)
    return ''.join(parts)


def _title(properties):
    '''The title text a block stores in its properties field.'''
    if properties in (None, ''):
        return ''
    try:
        parsed = json.loads(properties)
    except (TypeError, ValueError):
        return ''
    if not isinstance(parsed, dict):
        return ''
    return _rich_text(parsed.get('title'))


def _users(path):
    '''{user id: display name or email} for resolving the identifiers rows carry.'''
    people = {}
    for user_id, name, email in _rows(path, 'notion_user', 'id, name, email'):
        people[user_id] = _text(name) or _text(email)
    return people


@artifact_processor
def notion_ios_blocks(context):
    data_list = []
    sources = _stores(context.get_files_found())

    for source_path in sources:
        people = _users(source_path)
        for (block_id, kind, properties, created, edited, accessed, created_by, edited_by,
             parent_id, parent_table, alive, trashed, deleted, space_id) in _rows(
                source_path, 'block',
                'id, type, properties, created_time, last_edited_time, '
                'meta_last_access_timestamp, created_by_id, last_edited_by_id, parent_id, '
                'parent_table, alive, moved_to_trash_time, deleted_from_trash_time, space_id'):
            data_list.append((
                _ms_to_utc(created), _ms_to_utc(edited), _text(kind), _title(properties),
                people.get(created_by, _text(created_by)),
                people.get(edited_by, _text(edited_by)), _text(alive),
                _ms_to_utc(trashed), _ms_to_utc(deleted), _ms_to_utc(accessed),
                _text(parent_table), _text(parent_id), _text(space_id), _text(block_id),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Created Time', 'datetime'), ('Last Edited Time', 'datetime'), 'Type', 'Text',
        'Created By', 'Last Edited By', 'Alive (as stored)', ('Moved To Trash Time', 'datetime'),
        ('Deleted From Trash Time', 'datetime'), ('Last Access Time', 'datetime'),
        'Parent Table', 'Parent ID', 'Space ID', 'Block ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def notion_ios_page_activity(context):
    data_list = []
    sources = _stores(context.get_files_found())

    for source_path in sources:
        people = _users(source_path)
        titles = {}
        for block_id, properties in _rows(source_path, 'block', 'id, properties'):
            titles[block_id] = _title(properties)
        for (kind, record_id, value, stamp, parent_id, user_id, space_id) in _rows(
                source_path, 'records',
                'record_table, record_id, record_value, timestamp, parent_id, user_id, space_id',
                "record_table IN ('page_visit', 'page_exit')"):
            visited = ''
            try:
                inner = json.loads(value).get('value', {}) if value else {}
                visited = inner.get('visited_at', '') if isinstance(inner, dict) else ''
            except (TypeError, ValueError):
                inner = {}
            data_list.append((
                _ms_to_utc(stamp), _text(kind), titles.get(parent_id, ''),
                _ms_to_utc(visited), people.get(user_id, _text(user_id)),
                _text(parent_id), _text(space_id), _text(record_id),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Timestamp', 'datetime'), 'Event', 'Page Title', ('Event Time', 'datetime'), 'User',
        'Page ID', 'Space ID', 'Record ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def notion_ios_users(context):
    data_list = []
    sources = _stores(context.get_files_found())

    for source_path in sources:
        for (user_id, email, name, given_name, family_name, photo, banned,
             suspended) in _rows(
                source_path, 'notion_user',
                'id, email, name, given_name, family_name, profile_photo, is_banned, '
                'suspended_time'):
            data_list.append((
                _text(name), _text(email), _text(given_name), _text(family_name),
                _text(photo), _text(banned), _ms_to_utc(suspended), _text(user_id),
            ))

    data_list.sort(key=lambda row: str(row[0]))

    data_headers = (
        'Name', 'Email', 'Given Name', 'Family Name', 'Profile Photo', 'Banned (as stored)',
        ('Suspended Time', 'datetime'), 'User ID',
    )
    return data_headers, data_list, '\n'.join(sources)


def _schema_columns(value):
    '''The column names a collection's schema field declares, joined for display.'''
    if value in (None, ''):
        return ''
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return ''
    if not isinstance(parsed, dict):
        return ''
    names = [str(entry['name']) for entry in parsed.values()
             if isinstance(entry, dict) and entry.get('name')]
    return '; '.join(names)


@artifact_processor
def notion_ios_collections(context):
    data_list = []
    sources = _stores(context.get_files_found())

    for source_path in sources:
        people = _users(source_path)
        for (collection_id, name, description, schema, created, edited, created_by, alive,
             parent_id, parent_table, space_id) in _rows(
                source_path, 'collection',
                'id, name, description, schema, created_time, last_edited_time, created_by_id, '
                'alive, parent_id, parent_table, space_id'):
            data_list.append((
                _ms_to_utc(created), _ms_to_utc(edited), _rich_text(name),
                _rich_text(description), _schema_columns(schema),
                people.get(created_by, _text(created_by)), _text(alive), _text(parent_table),
                _text(parent_id), _text(space_id), _text(collection_id),
            ))

    data_list.sort(key=lambda row: str(row[0]), reverse=True)

    data_headers = (
        ('Created Time', 'datetime'), ('Last Edited Time', 'datetime'), 'Name', 'Description',
        'Column Names', 'Created By', 'Alive (as stored)', 'Parent Table', 'Parent ID',
        'Space ID', 'Collection ID',
    )
    return data_headers, data_list, '\n'.join(sources)
