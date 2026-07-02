__artifacts_v2__ = {
    "Oops": {
        "name": "Oops: Make New Friends",
        "description": "Parses Oops Message Database",
        "author": "Heather Charpentier",
        "creation_date": "2024-06-26",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Oops",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/RongCloud/*/storage*',),
        "output_types": "standard",
        "artifact_icon": "message-circle"
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc

_QUERY = '''
SELECT
    datetime(send_time/1000, 'unixepoch'),
    datetime(receive_time/1000, 'unixepoch'),
    clazz_name,
    json_extract(RCT_MESSAGE.content, '$.user.name'),
    sender_id,
    CASE message_direction
        WHEN 1 THEN 'Incoming'
        WHEN 0 THEN 'Outgoing'
        ELSE 'Unknown'
    END,
    json_extract(RCT_Message.content, '$.content'),
    json_extract(json_extract(RCT_Message.content, '$.extra'), '$.nickName'),
    json_extract(json_extract(RCT_Message.content, '$.extra'), '$.userId')
FROM RCT_MESSAGE
WHERE json_valid(json_extract(RCT_Message.content, '$.extra'))
'''


@artifact_processor
def Oops(context):
    data_headers = (
        ('Date Sent', 'datetime'), ('Date Received', 'datetime'), 'Message Type', 'Sender Name',
        'Sender ID', 'Direction', 'Message', 'Nickname', 'User ID')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('storage'):
            continue
        try:
            rows = get_sqlite_db_records(file_found, _QUERY)
        except sqlite3.Error as ex:
            logfunc(f'Error reading Oops messages from {file_found}: {ex}')
            continue
        for row in rows:
            data_list.append(tuple(row))
        sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
