__artifacts_v2__ = {
    "pingertextfree": {
        "name": "Text Free - Pinger",
        "description": "Text Free (Pinger) messages",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-11-18",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Pinger",
        "notes": "The Messaging_*.sqlite store is attributed to Text Free by this module; no test "
                 "image, row count or sample data is recorded for that attribution. None of the "
                 "27 registered iOS test images holds a file the pattern matches on a "
                 "case-sensitive system, so the query has been exercised only on a constructed "
                 "database, not on a real store. The Messaging_*.sqlite glob is not "
                 "bundle-specific. Every matching database that holds a ZCOMMUNICATIONCD table "
                 "is read, and the Source File column names the database a row came from. A "
                 "matching database without that table is skipped and named in the run log. "
                 "Each row is one ZCOMMUNICATIONCD record. Other Party is ZDISPLAYNAME of the "
                 "ZCONVERSATIONCD row whose Z_PK equals the message's ZCONVERSATION value, and "
                 "it is blank when no such row exists. Timestamp is ZTIMECREATED read as Unix "
                 "seconds in UTC; that reading is not confirmed against a test image here. "
                 "Direction, Status and Type are reported as stored and their values are not "
                 "decoded.",
        "paths": ('*/Messaging_*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message"
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, does_table_exist_in_db, \
    get_sqlite_db_records, logfunc


@artifact_processor
def pingertextfree(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Conversation ID',
        'Directionality to from Other Party',
        'Other Party',
        'Status',
        'Text',
        'Type',
        'Source File')
    data_list = []
    source_paths = []

    query = '''
    SELECT
        datetime(ZCOMMUNICATIONCD.ZTIMECREATED, 'unixepoch'),
        ZCOMMUNICATIONCD.ZCONVERSATION,
        ZCOMMUNICATIONCD.ZDIRECTION,
        ZCONVERSATIONCD.ZDISPLAYNAME,
        ZCOMMUNICATIONCD.ZMYSTATUS,
        ZCOMMUNICATIONCD.ZTEXT,
        ZCOMMUNICATIONCD.ZTYPE
    FROM ZCOMMUNICATIONCD
    LEFT JOIN ZCONVERSATIONCD ON ZCONVERSATIONCD.Z_PK = ZCOMMUNICATIONCD.ZCONVERSATION
    ORDER BY ZCOMMUNICATIONCD.ZCONVERSATION, ZCOMMUNICATIONCD.ZTIMECREATED
    '''

    for file_found in sorted({str(found) for found in context.get_files_found()}):
        if not file_found.endswith('.sqlite'):
            continue
        relative_path = context.get_relative_path(file_found)
        if not does_table_exist_in_db(file_found, 'ZCOMMUNICATIONCD'):
            logfunc(f'Text Free: {relative_path} holds no ZCOMMUNICATIONCD table, skipped')
            continue
        try:
            rows = [tuple(row) for row in get_sqlite_db_records(file_found, query)]
        except sqlite3.Error as ex:
            logfunc(f'Error reading Text Free messages from {relative_path}: {ex}')
            continue
        source_paths.append(file_found)
        for row in rows:
            data_list.append(row + (relative_path,))

    return data_headers, data_list, '\n'.join(source_paths)
