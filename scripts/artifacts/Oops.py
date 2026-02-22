from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_OopsMessages(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('storage'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(send_time/1000, 'unixepoch') as 'Date Sent',
            datetime(receive_time/1000, 'unixepoch') as 'Date Received',
            clazz_name as 'Message Type',
            json_extract(RCT_MESSAGE.content, '$.user.name') as 'Sender Name',
            sender_id as 'Sender ID',
            CASE message_direction
                WHEN 1 THEN 'Incoming'
                WHEN 0 THEN 'Outgoing'
                ELSE 'Unknown'
            END as Direction,
            json_extract(RCT_Message.content, '$.content') as 'Message',
            json_extract(json_extract(RCT_Message.content, '$.extra'), '$.nickName') AS 'Nickname',
            json_extract(json_extract(RCT_Message.content, '$.extra'), '$.userId') AS 'User ID'
            FROM RCT_MESSAGE
            WHERE
            json_valid(json_extract(RCT_Message.content, '$.extra'))
            ''')

            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
            db.close()

        else:
            continue

    data_headers = ('Date Sent', 'Date Received', 'Message Type', 'Sender Name', 'Sender ID',
                    'Direction', 'Message', 'Nickname', 'User ID')
    return data_headers, data_list, str(files_found[0])

__artifacts_v2__ = {
    "get_OopsMessages": {
        "name": "Oops: Make New Friends",
        "description": "Parses Oops Message Database",
        "author": "Heather Charpentier",
        "version": "0.0.1",
        "date": "2024-06-26",
        "requirements": "none",
        "category": "Oops",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/RongCloud/*/storage*',),
        "output_types": "standard",
        "artifact_icon": "message-square"
    }
}
