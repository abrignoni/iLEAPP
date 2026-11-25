__artifacts_v2__ = {
    "googleTasks": {
        "name": "Google Tasks",
        "description": "One row per task in the tasks.db that several Google apps keep under a Tasks "
                       "or tasks folder in their app container or app group, read from the Tasks table and its "
                       "EffectiveTask protobuf, with the task list's EffectiveTaskList text. App is the "
                       "identifier the container's metadata plist records.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Google Tasks",
        "notes": "The store was seen under five container identifiers: com.google.Keep and com.google.Gmail at"
                 " Library/Application Support/Tasks/<account folder>/tasks.db in the app container, "
                 "group.com.google.Gmail and group.com.google.Dynamite at tasks/<account folder>/tasks.db in "
                 "the app group, and group.com.google.calendar at Library/Application "
                 "Support/Tasks/tasks/<account folder>/tasks.db in the app group. A tasks.db is read only when"
                 " its container's metadata plist names an identifier starting with com.google. or "
                 "group.com.google. and the store has a Tasks table with an EffectiveTask column; any other "
                 "tasks.db is logged and skipped. On one image two app groups each held a store under the same"
                 " folder number, both with no tasks. A task present in two stores is reported once per store;"
                 " rows are not de-duplicated. Account Folder is the name of the folder holding tasks.db, as "
                 "stored: a 21-digit number, with a _tdl suffix in the Gmail and Dynamite app groups. That it "
                 "identifies an account is not established. Due Date and the ids are Tasks table columns as "
                 "stored. Completed is the Tasks.Completed column, stored as 0 or 1 and shown as No or Yes. No"
                 " published definition of the protobuf is known to the author, so the columns are named by "
                 "field position and what each field records is not established. Fields 11, 3 and 2.5 hold "
                 "seconds in field 1 and nanoseconds in field 2, the shape of google.protobuf.Timestamp, and "
                 "are converted to UTC on that basis. Field 9.1.6.1 is an integer converted as Unix seconds to"
                 " UTC; on the one row seen that held it, it equalled the date in field 9.1.2 and the hour and"
                 " minute in field 9.1.3 read in the zone named by field 9.1.4, and field 2.4 held the same "
                 "date as Due Date. On the 77 task rows seen, field 11 was earlier than field 3, and field 2.5"
                 " was present on every row whose Completed column was set and on no other row. On the one "
                 "Gmail row field 2.2 was absent and field 2.3 held text. Fields 2.2, 2.3 and 9.1.4 and the "
                 "task list's field 2.1 are read as bytes and decoded as UTF-8 text. A protobuf blob starting "
                 "with the bytes FE FF is not decoded, leaving that row's protobuf columns blank; no such blob"
                 " was seen. The task list is joined by Tasks.TaskListId to TaskLists.TaskListIdWithoutShard "
                 "within the same ShardId; a task list with no tasks gets no row. The task's fields 1, 2.1, "
                 "2.4, 4, 8, 9.1.2, 9.1.3 and 13, the task list's fields other than 2.1, and the Task and "
                 "OriginalTask blobs are not reported. Not reported: TaskRecurrenceId and TaskRecurrences "
                 "(empty), HasDirtyState (0 on every row seen), Operations, UserActions, Rooms, RoomsTable, "
                 "DocumentsTable and GlobalMetadata (no rows seen), and ClientSyncState, UserMetadata, "
                 "UserPrefs, UserExperimental and GlobalMetadataTable (not decoded; GlobalMetadataTable has an"
                 " ObfuscatedGaiaId column in eight of the ten stores seen, empty in all eight). In six of the"
                 " ten tasks.db stores seen, including both that held tasks, the tables were only in the -wal;"
                 " without the -wal such a store reads as having no tables. Only two stores seen held tasks, "
                 "so the com.google.Gmail, group.com.google.Dynamite and group.com.google.calendar stores were"
                 " exercised only with empty Tasks tables. The com.google.Keep field shapes were mapped from a"
                 " private sample.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/Tasks/*/tasks.db*',
                  '*/Containers/Shared/AppGroup/*/Library/Application Support/Tasks/*/tasks.db*',
                  '*/Containers/Shared/AppGroup/*/tasks/*/tasks.db*',
                  '*/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "checklist",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 1 row (group.com.google.Gmail)",
            "dexter_ios18": "iOS 18.3.2 | 0 rows (group.com.google.Gmail and group.com.google.calendar"
                            " stores, one task list and no tasks in each)",
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 0 rows (com.google.Gmail store, Tasks and TaskLists"
                                      " empty)",
            "magnet_ios16": "iOS 16.1.1 | 0 rows (group.com.google.Gmail store, Tasks and TaskLists empty)",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows (group.com.google.Gmail store, Tasks and TaskLists "
                                  "empty)",
            "iphone11_ios17": "iOS 17.3 | 0 rows (group.com.google.Dynamite store, Tasks and TaskLists "
                              "empty)",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows (group.com.google.Dynamite store, Tasks and TaskLists "
                          "empty)",
            "hickman_ios15": "iOS 15.3.1 | 0 rows (group.com.google.Dynamite store, Tasks and TaskLists "
                             "empty)",
        },
    },
}


import copy
import os
import plistlib
import re
import sqlite3
import struct

from google.protobuf.message import DecodeError

from scripts import blackboxprotobuf
from scripts.ilapfuncs import (artifact_processor, convert_unix_ts_to_utc, logfunc,
                               open_sqlite_db_readonly)

_METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'
_GOOGLE_PREFIXES = ('com.google.', 'group.com.google.')
_CONTAINER_RE = re.compile(r'^(.*/Containers/(?:Data/Application|Shared/AppGroup)/[^/]+)/')
_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)
# The decoder guesses a field's type from its bytes, and short UTF-8 text can also parse as a
# nested message. The text fields the artifact reports are pinned to bytes; the rest are guessed.
_BYTES = {'type': 'bytes', 'name': ''}
_TASK_TYPES = {
    '2': {'type': 'message', 'name': '', 'message_typedef': {'2': _BYTES, '3': _BYTES}},
    '9': {'type': 'message', 'name': '', 'message_typedef': {
        '1': {'type': 'message', 'name': '', 'message_typedef': {'4': _BYTES}}}},
}
_TASK_LIST_TYPES = {'2': {'type': 'message', 'name': '', 'message_typedef': {'1': _BYTES}}}


def _norm(path):
    return str(path).replace('\\', '/')


def _container_root(path):
    match = _CONTAINER_RE.match(_norm(path))
    return match.group(1) if match else ''


def _container_apps(files_found):
    '''Map each container folder to the identifier its metadata plist records.'''
    apps = {}
    for found in files_found:
        found = _norm(found)
        if os.path.basename(found) != _METADATA_NAME:
            continue
        try:
            with open(found, 'rb') as handle:
                plist = plistlib.load(handle)
        except (plistlib.InvalidFileException, OSError, ValueError) as error:
            logfunc(f'Google Tasks: could not read a container metadata plist: {error}')
            continue
        bundle_id = plist.get('MCMMetadataIdentifier') if isinstance(plist, dict) else None
        if isinstance(bundle_id, str) and bundle_id:
            apps[os.path.dirname(found)] = bundle_id
    return apps


def _tasks_dbs(files_found):
    '''(tasks.db, app identifier) for stores in a container whose plist names a Google app.

    A container without a readable metadata plist identifier, or naming another vendor's app,
    is not read.
    '''
    apps = _container_apps(files_found)
    dbs = set()
    for found in files_found:
        found = str(found)
        if os.path.basename(found) != 'tasks.db' or os.path.isdir(found):
            continue
        bundle_id = apps.get(_container_root(found))
        if not bundle_id or not bundle_id.startswith(_GOOGLE_PREFIXES):
            owner = bundle_id or 'an unidentified app'
            logfunc(f'Google Tasks: skipping a tasks.db in a container of {owner}')
            continue
        dbs.add((found, bundle_id))
    return sorted(dbs)


def _yes_no(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _fetch(cursor, query, app):
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as error:
        logfunc(f'Google Tasks: query failed on the {app} tasks.db: {error}')
        return []


def _tables(cursor, app):
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return {row[0] for row in cursor.fetchall()}
    except sqlite3.Error as error:
        logfunc(f'Google Tasks: could not read the schema of the {app} tasks.db: {error}')
        return set()


def _columns(cursor, table):
    try:
        cursor.execute(f"PRAGMA table_info('{table}')")
        return {row[1] for row in cursor.fetchall()}
    except sqlite3.Error:
        return set()


def _pb(message, *keys):
    value = message
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _pb_text(message, *keys):
    value = _pb(message, *keys)
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    if isinstance(value, str):
        return value
    if value is not None:
        field = '.'.join(keys)
        logfunc(f'Google Tasks: task protobuf field {field} did not decode as text; left blank')
    return ''


def _pb_time(message, *keys):
    '''A seconds/nanoseconds pair (google.protobuf.Timestamp shape) to UTC.'''
    value = _pb(message, *keys)
    if not isinstance(value, dict) or not isinstance(value.get('1'), int):
        return ''
    nanos = value.get('2') if isinstance(value.get('2'), int) else 0
    return convert_unix_ts_to_utc(value['1'] + nanos / 1e9)


def _pb_seconds(message, *keys):
    value = _pb(message, *keys)
    if not isinstance(value, int) or isinstance(value, bool):
        return ''
    return convert_unix_ts_to_utc(value)


def _decode(blob, label, typedef):
    if not isinstance(blob, (bytes, bytearray)) or not blob or blob.startswith(b'\xfe\xff'):
        return {}
    try:
        message, _types = blackboxprotobuf.decode_message(bytes(blob), copy.deepcopy(typedef))
        return message
    except _DECODE_ERRORS as error:
        logfunc(f'Google Tasks: could not decode a {label} protobuf: {error}')
        return {}


@artifact_processor
def googleTasks(context):
    data_list = []
    sources = []
    for store, app in _tasks_dbs(context.get_files_found()):
        db = open_sqlite_db_readonly(store)
        if db is None:
            continue
        cursor = db.cursor()
        tables = _tables(cursor, app)
        if 'Tasks' not in tables or 'EffectiveTask' not in _columns(cursor, 'Tasks'):
            logfunc(f'Google Tasks: no Tasks table with an EffectiveTask column in the {app} tasks.db')
            db.close()
            continue
        sources.append(store)
        account_folder = os.path.basename(os.path.dirname(_norm(store)))
        lists = {}
        if 'TaskLists' in tables:
            for shard, list_id, blob in _fetch(
                    cursor, 'SELECT ShardId, TaskListIdWithoutShard, EffectiveTaskList FROM TaskLists',
                    app):
                lists[(shard, list_id)] = _pb_text(_decode(blob, 'task list', _TASK_LIST_TYPES), '2', '1')
        rows = _fetch(cursor, '''
            SELECT TaskId, TaskListId, DueDate, Completed, EffectiveTask, ShardId
            FROM Tasks ORDER BY rowid''', app)
        db.close()
        for task_id, list_id, due, completed, blob, shard in rows:
            message = _decode(blob, 'task', _TASK_TYPES)
            data_list.append((
                _pb_time(message, '11'), _pb_time(message, '3'), _pb_time(message, '2', '5'),
                _pb_seconds(message, '9', '1', '6', '1'), _pb_text(message, '9', '1', '4'),
                due or '', _yes_no(completed), _pb_text(message, '2', '2'), _pb_text(message, '2', '3'),
                lists.get((shard, list_id), ''), app, account_folder, task_id or '', list_id or ''))

    data_headers = (
        ('Time (field 11)', 'datetime'), ('Time (field 3)', 'datetime'), ('Time (field 2.5)', 'datetime'),
        ('Time (field 9.1.6.1)', 'datetime'), 'Zone (field 9.1.4)', 'Due Date (as stored)', 'Completed',
        'Text (field 2.2)', 'Text (field 2.3)', 'Task List Text (field 2.1)', 'App', 'Account Folder',
        'Task ID', 'Task List ID')
    return data_headers, data_list, '\n'.join(sources)
