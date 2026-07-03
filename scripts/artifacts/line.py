__artifacts_v2__ = {
    "line": {
        "name": "Line Artifacts",
        "description": "Line messages including message direction and associated usernames",
        "author": "Elliot Glendye",
        "creation_date": "2023-11-22",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Line",
        "notes": "",
        "paths": ('**/Line.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Username",
                "textColumn": "Message",
                "directionColumn": "Sent / Received",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Username",
                "sentMessageStaticLabel": "Local User"
            }
        },
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc


@artifact_processor
def line(context):
    data_headers = (('Timestamp', 'datetime'), 'Sent / Received', 'Username', 'Message')
    data_list = []
    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('Line.sqlite'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(ZMESSAGE.ZTIMESTAMP / 1000, 'unixepoch'),
        CASE WHEN ZMESSAGE.ZSENDER IS NULL THEN 'Outgoing' ELSE 'Incoming' END,
        ZUSER.ZNAME,
        ZMESSAGE.ZTEXT
    FROM ZMESSAGE
    LEFT JOIN ZUSER ON ZMESSAGE.ZSENDER = ZUSER.Z_PK
    ORDER BY ZMESSAGE.ZTIMESTAMP DESC
    '''
    try:
        rows = get_sqlite_db_records(source_path, query)
    except sqlite3.Error as ex:
        logfunc(f'Error reading Line messages: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for row in rows:
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)
