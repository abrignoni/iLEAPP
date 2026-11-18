__artifacts_v2__ = {
    "nsurlsessiondTasks": {
        "name": "Background URL Session Tasks",
        "description": "Rows of the session_tasks table in nsurlsessiond's tasks.sqlite: the "
                       "creation time, the bundle ID, the request URL, the task kind and state, "
                       "and the byte counts each row stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "One row per row of session_tasks in tasks.sqlite under "
                 "Library/com.apple.nsurlsessiond. No Apple documentation of this database was "
                 "found, so the column names are the only labels used here and values are reported "
                 "as stored apart from the two below. Creation Time is creation_time read as "
                 "seconds since 2001 UTC; read that way it falls between March and October 2026 on "
                 "the two iOS 26 images and between March and July 2024 on iphone11_ios17, and no "
                 "source for the epoch was found. Request URL is read from the task's "
                 "original_request, an NSKeyedArchiver archive of the request, with "
                 "nska_deserialize: it is the NS.relative value of "
                 "__nsurlrequest_proto_prop_obj_1, joined to NS.base when the archive has one, and "
                 "it was found on every row of the three tested images (62, 62 and 23). Bundle ID "
                 "is the bundle_id column as stored. Task Kind and State are "
                 "integers with no names given here. Bytes Received, Bytes Sent, Bytes Expected To "
                 "Receive and Bytes Expected To Send held 0, and Has Started held 1, on every row "
                 "of the three tested images, and Discretionary held 1 on every row of "
                 "iphone11_ios17. earliest_begin_date held 0 on every row and is not shown. The "
                 "current_request, response, error and task_metrics blobs and the sessions table "
                 "are not read here. On hill_iphone15pro_ios26 the database without its "
                 "write-ahead log holds 60 of the 62 rows, so the sidecar is read.",
        "paths": ('*/mobile/Library/com.apple.nsurlsessiond/tasks.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 62 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 62 rows",
            "iphone11_ios17": "iOS 17.3 | 23 rows",
        },
    }
}


import os
import plistlib
from datetime import datetime, timedelta, timezone

import nska_deserialize as nd

from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db, get_sqlite_db_records,
                               is_sqlite_sidecar, logfunc, null_absent_columns)

_EPOCH_2001 = datetime(2001, 1, 1, tzinfo=timezone.utc)
_ARCHIVE_ERRORS = (nd.DeserializeError, plistlib.InvalidFileException, ValueError, TypeError,
                   KeyError, IndexError)


def _cocoa(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return ''
    try:
        return _EPOCH_2001 + timedelta(seconds=value)
    except OverflowError:
        return ''


def _url(blob):
    '''The URL of an archived NSURLRequest: NS.relative of __nsurlrequest_proto_prop_obj_1,
    joined to NS.base when the archive carries one, or ''.'''
    if not blob:
        return ''
    try:
        request = nd.deserialize_plist_from_string(blob)
    except _ARCHIVE_ERRORS as error:
        logfunc(f'Background URL Session Tasks: could not read a request: {error}')
        return ''
    url = request.get('__nsurlrequest_proto_prop_obj_1') if isinstance(request, dict) else None
    if not isinstance(url, dict) or not isinstance(url.get('NS.relative'), str):
        return ''
    base = url.get('NS.base')
    if isinstance(base, dict) and isinstance(base.get('NS.relative'), str):
        return base['NS.relative'] + url['NS.relative']
    return url['NS.relative']


def _value(value):
    return '' if value is None else value


@artifact_processor
def nsurlsessiondTasks(context):
    data_list, sources = [], []
    for found in sorted(str(path) for path in context.get_files_found()):
        if os.path.basename(found) != 'tasks.sqlite' or is_sqlite_sidecar(found):
            continue
        if not does_table_exist_in_db(found, 'session_tasks'):
            continue
        sources.append(found)
        query = null_absent_columns(found, '''
            SELECT creation_time, bundle_id, original_request, task_kind, state, task_description,
                   count_of_bytes_received, count_of_bytes_sent,
                   count_of_bytes_expected_to_receive, count_of_bytes_expected_to_send,
                   has_started, discretionary, file_url, download_file_url, session_id,
                   identifier
            FROM session_tasks
            ORDER BY creation_time, identifier
        ''')
        for row in get_sqlite_db_records(found, query):
            data_list.append((_cocoa(row[0]), _value(row[1]), _url(row[2]))
                             + tuple(_value(value) for value in row[3:]))
    data_headers = (
        ('Creation Time', 'datetime'), 'Bundle ID', 'Request URL', 'Task Kind (as stored)',
        'State (as stored)', 'Task Description', 'Bytes Received', 'Bytes Sent',
        'Bytes Expected To Receive', 'Bytes Expected To Send', 'Has Started (as stored)',
        'Discretionary (as stored)', 'File URL', 'Download File URL', 'Session ID', 'Identifier')
    return data_headers, data_list, '\n'.join(sources)
