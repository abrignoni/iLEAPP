__artifacts_v2__ = {
    "Oops": {
        "name": "Oops: Make New Friends",
        "description": "Parses Oops Message Database",
        "author": "Heather Charpentier",
        "creation_date": "2024-06-26",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Oops",
        "notes": "message_direction is reported as stored. RongCloud's SDK defines MessageDirection SEND=1, RECEIVE=2; the previous Incoming/Outgoing mapping did not match the SDK and was removed pending verification. Reference: RongCloud RCStatusDefine.h, https://github.com/rongcloud/callkit-ios/blob/5e10415805a1202ce0f19543509fe58ea7418a6f/ios-rongcallkit/framework/RongIMLibCore.framework/Headers/RCStatusDefine.h",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/RongCloud/*/storage*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "User ID",
                "textColumn": "Message",
                "timeColumn": "Date Sent",
                "senderColumn": "Sender Name"
            }
        },
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc

_QUERY = '''
SELECT
    datetime(send_time/1000, 'unixepoch'),
    datetime(receive_time/1000, 'unixepoch'),
    json_extract(RCT_MESSAGE.content, '$.user.name'),
    json_extract(RCT_Message.content, '$.content'),
    clazz_name,
    sender_id,
    message_direction,
    json_extract(json_extract(RCT_Message.content, '$.extra'), '$.nickName'),
    json_extract(json_extract(RCT_Message.content, '$.extra'), '$.userId')
FROM RCT_MESSAGE
WHERE json_valid(json_extract(RCT_Message.content, '$.extra'))
'''


@artifact_processor
def Oops(context):
    data_headers = (
        ('Date Sent', 'datetime'), ('Date Received', 'datetime'), 'Sender Name', 'Message',
        'Message Type', 'Sender ID', 'Direction (as stored)', 'Nickname', 'User ID')
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
