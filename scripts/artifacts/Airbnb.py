# Airbnb App (com.airbnb.app)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# 
# Tested with the following versions:
# 2025-04-23: iOS 18.4.1, App: 24.50.2

__artifacts_v2__ = {
    "airbnb_messages": {
        "name": "Airbnb - Messages",
        "description": "Messages sent and received in the Airbnb App",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-04-29",
        "last_update_date": "2026-05-18",
        "requirements": "Path, re",
        "category": "Airbnb",
        "notes": "",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/user_*_messaging_core.sqlite3*'),
        "output_types": "standard",
        "artifact_icon": "message-square",
        'data_views': {
            'conversation': {
                'conversationDiscriminatorColumn': 'Thread ID',
                'conversationLabelColumn': 'Thread ID',
                'textColumn': 'Original Message',
                'directionColumn': 'Sent',
                'directionSentValue': 1,
                'timeColumn': 'Created Timestamp',
                'senderColumn': 'Sender Display Name'
                }
        }
    }
}

from pathlib import Path
import re

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, convert_unix_ts_to_utc

@artifact_processor
def airbnb_messages(context):
    files_found = [x for x in context.get_files_found() if not x.endswith('wal') and not x.endswith('shm')]
    
    stem = Path(files_found[0]).stem
    user_account_id = int(re.search(r'(?<=_)\d+(?=_)', stem).group())

    query = ('''
        SELECT
        messages__created_at [Created Timestamp],
        messages__updated_at [Updated Timestamp],
        messages__fetched_at [Fetched Timestamp],
        m.messages__thread_id [Thread ID],
        m.messages__user_id [Sender User ID],
        m.messages__user_type [Sender User Type],
        u.users__display_name [Sender User Display Name],
        CASE messages__type
                WHEN 'multipart' THEN json_extract(m.messages__content, '$.sub_messages[0].content.body')
                WHEN 'text' THEN json_extract(m.messages__content, '$.body')
        END [Original Message],
        CASE messages__type
                WHEN 'multipart' THEN json_extract(m.messages__trasnlated_content, '$.sub_messages[0].content.body')
                WHEN 'text' THEN json_extract(m.messages__trasnlated_content, '$.body')
        END [Translated Message]
        FROM messages m
        LEFT JOIN users u ON m.messages__user_id = u.users__user_id
        LEFT JOIN threads t ON m.messages__thread_id = t.threads__id
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        created = convert_unix_ts_to_utc(row[0])
        updated = convert_unix_ts_to_utc(row[1])
        fetched = convert_unix_ts_to_utc(row[2])
        thread_id = row[3]
        sender_user_id = row[4]
        sender_user_type = row[5]
        sender_display_name = row[6]
        orig_message = row[7]
        trans_message = row[8]
        # check if it was sent by local account or received
        if sender_user_id == user_account_id:
            sent = 1
        else:
            sent = 0

        data_list.append(   (created,
                            updated,
                            fetched,
                            thread_id,
                            sender_user_id,
                            sender_user_type,
                            sender_display_name,
                            orig_message,
                            trans_message,
                            sent)
                        )

    data_headers = (    ('Created Timestamp', 'datetime'),
                        ('Updated Timestamp', 'datetime'),
                        ('Fetched Timestamp', 'datetime'),
                        'Thread ID',
                        'Sender User ID',
                        'Sender User Type',
                        'Sender Display Name',
                        'Original Message',
                        'Translated Message',
                        'Sent'
                    )

    return data_headers, data_list, files_found[0]
