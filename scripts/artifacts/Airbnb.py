# Airbnb App (com.airbnb.app)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# 
# Tested with the following versions:
# 2025-04-23: iOS 18.4.1, App: 24.50.2

# Requirements: -

__artifacts_v2__ = {

    
    "get_airbnb_messages": {
        "name": "Airbnb - Messages",
        "description": "Messages sent and received in the Airbnb App",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creatin_date": "2024-04-29",
        "last_update_date": "2025-04-29",
        "requirements": "",
        "category": "Airbnb",
        "notes": "",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/user_*_messaging_core.sqlite3*'),
        "output_types": "standard",
        "artifact_icon": "message-square"
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records

@artifact_processor
def get_airbnb_messages(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    query = ('''
        SELECT
        strftime('%Y-%m-%d %H:%M:%S.', "messages__created_at"/1000, 'unixepoch') || ("messages__created_at"%1000) [Created Timestamp],
        strftime('%Y-%m-%d %H:%M:%S.', "messages__updated_at"/1000, 'unixepoch') || ("messages__updated_at"%1000) [Updated Timestamp],
        strftime('%Y-%m-%d %H:%M:%S.', "messages__fetched_at"/1000, 'unixepoch') || ("messages__fetched_at"%1000) [Fetched Timestamp],
        m.messages__thread_id [Thread ID],
        m.messages__user_id [Sender User ID],
        m.messages__user_type [Sender User Type],
        u.users__display_name [Sender User Display Name],
        json_extract(m.messages__content, '$.body') [Original Message],
        json_extract(m.messages__trasnlated_content, '$.body') [Translated Message]
        FROM messages m
        LEFT JOIN users u ON m.messages__user_id = u.users__user_id
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        created = row[0]
        updated = row[1]
        fetched = row[2]
        thread_id = row[3]
        sender_user_id = row[4]
        sender_user_type = row[5]
        sender_display_name = row[6]
        orig_message = row[7]
        trans_message = row[8]

        data_list.append((created, updated, fetched, thread_id, sender_user_id, sender_user_type, sender_display_name, orig_message, trans_message))

    data_headers = ('Created Date', 'Updated Date', 'Fetched Date', 'Thread ID', 'Sender User ID', 'Sender User Type', 'Sender Display Name', 'Original Message', 'Translated Message')
    
    return data_headers, data_list, files_found[0]

