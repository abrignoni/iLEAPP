__artifacts_v2__ = {
    "nsurlsessiondTasks": {
        "name": "Background URL Session Tasks",
        "description": "Rows of the session_tasks table in nsurlsessiond's tasks.sqlite: the "
                       "creation time, the bundle ID, the request URL, the task kind and state, "
                       "and four of the byte counts each row stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "One row per row of session_tasks in tasks.sqlite under "
                 "Library/com.apple.nsurlsessiond. The meaning of the columns is not sourced here, "
                 "so the column names are the only labels used. Apart from Creation Time and the "
                 "three URL columns, values are reported as stored, with NULL shown as empty. "
                 "Creation Time is creation_time read as seconds since 2001 UTC; read that way it "
                 "falls between March and October 2026 on wilkerson_iphone16_ios26, between August "
                 "and October 2026 on hill_iphone15pro_ios26 and between March and July 2024 on "
                 "iphone11_ios17, and no source for the epoch was found. Request URL is read from "
                 "the task's original_request, an NSKeyedArchiver archive of the request, with "
                 "nska_deserialize: it is the NS.relative value of "
                 "__nsurlrequest_proto_prop_obj_1, and it was found on every row of the three "
                 "tested images (62, 62 and 23). File URL and Download File URL are file_url and "
                 "download_file_url, each an NSKeyedArchiver archive of a URL, read the same way "
                 "from their own NS.relative value; that gave a file URL on every row that holds "
                 "one (10 and 36 on hill_iphone15pro_ios26, 18 and 40 on wilkerson_iphone16_ios26, "
                 "1 and 1 on iphone11_ios17). NS.base was empty on every archive of the three "
                 "tested images, so the code that would prepend a base URL was not exercised. "
                 "Bundle ID is the bundle_id column as stored. Task Kind and State are integers "
                 "with no names given here. Bytes Received, Bytes Sent, Bytes Expected To Receive "
                 "and Bytes Expected To Send held 0, and Has Started held 1, on every row of the "
                 "three tested images, and Discretionary held 1 on every row of iphone11_ios17. "
                 "earliest_begin_date held 0 on every row of the three tested images and is not "
                 "shown. Only the columns shown are read: the current_request, response, error and "
                 "task_metrics blobs are among those not read, and so is the sessions table "
                 "(absent on iphone11_ios17). The write-ahead log is read with the database: "
                 "without it, hill_iphone15pro_ios26 holds 60 of the 62 rows, iphone11_ios17 holds "
                 "24 rows where 23 remain with it, and wilkerson_iphone16_ios26 holds 62 rows with "
                 "and without it, with some values different.",
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


def _url(blob, in_request):
    '''The URL in an archived NSURLRequest (NS.relative of __nsurlrequest_proto_prop_obj_1) or
    an archived NSURL (its own NS.relative), joined to NS.base when that is a URL, or ''.'''
    if not blob:
        return ''
    try:
        archive = nd.deserialize_plist_from_string(blob)
    except _ARCHIVE_ERRORS as error:
        logfunc(f'Background URL Session Tasks: could not read an archived URL: {error}')
        return ''
    if not isinstance(archive, dict):
        return ''
    url = archive.get('__nsurlrequest_proto_prop_obj_1') if in_request else archive
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
            data_list.append((_cocoa(row[0]), _value(row[1]), _url(row[2], True))
                             + tuple(_value(value) for value in row[3:12])
                             + (_url(row[12], False), _url(row[13], False))
                             + tuple(_value(value) for value in row[14:]))
    data_headers = (
        ('Creation Time', 'datetime'), 'Bundle ID', 'Request URL', 'Task Kind (as stored)',
        'State (as stored)', 'Task Description', 'Bytes Received', 'Bytes Sent',
        'Bytes Expected To Receive', 'Bytes Expected To Send', 'Has Started (as stored)',
        'Discretionary (as stored)', 'File URL', 'Download File URL', 'Session ID', 'Identifier')
    return data_headers, data_list, '\n'.join(sources)
