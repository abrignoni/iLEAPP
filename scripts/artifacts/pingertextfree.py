__artifacts_v2__ = {
    "pingertextfree": {
        "name": "Text Free - Pinger",
        "description": "Text Free (Pinger) messages",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-11-18",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Pinger",
        "notes": "",
        "paths": ('*/Messaging_*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-square"
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc


@artifact_processor
def pingertextfree(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Conversation ID',
        'Directionality to from Other Party',
        'Other Party',
        'Status',
        'Text',
        'Type')
    data_list = []
    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('.sqlite'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

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
    JOIN ZCONVERSATIONCD ON ZCONVERSATIONCD.Z_PK = ZCOMMUNICATIONCD.ZCONVERSATION
    ORDER BY ZCOMMUNICATIONCD.ZCONVERSATION, ZCOMMUNICATIONCD.ZTIMECREATED
    '''
    try:
        rows = get_sqlite_db_records(source_path, query)
    except sqlite3.Error as ex:
        logfunc(f'Error reading Text Free messages: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for row in rows:
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)
