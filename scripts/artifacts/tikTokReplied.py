__artifacts_v2__ = {
    'tiktok_replied': {
        'name': 'TikTok - Replied Messages',
        'description': 'Extracts "Replied" message remnants left in the TikTok database which may no longer exist in '
                       'the native message table',
        'author': 'John Hyla http://www.bluecrewforensics.com/',
        'version': '0.2',
        'date': '2024-11-8',
        'requirements': 'none',
        'category': 'TikTok',
        'notes': 'This artifact is extracted from the TIMMessageKVORM table which appears to contain referenced '
                 'messages. It appears that a copy of the message being replied to is placed into this table. It also '
                 'appears that entries in this table may not be deleted when the actual referenced message or the new '
                 'reply is deleted. There may be unknown circumstances that cause records to be deleted from this table '
                 'and there may be reasons other than using the simple reply feature that may cause records to be '
                 'written here.',
        'paths': ('*/Application/*/Library/Application Support/ChatFiles/*/db.sqlite*', '*AwemeIM.db*'),
        "output_types": "standard"
    }
}

import sqlite3
from os.path import dirname, basename
from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, attach_sqlite_db_readonly, artifact_processor

@artifact_processor
def tiktok_replied(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    report_file = ''
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('AwemeIM.db'):
            report_file = file_found
            attachdb = file_found
            logfunc("FOUND AwemeIM.db")

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('db.sqlite'):
            report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found
            dir_path = dirname(file_found)
            account_id = basename(dir_path)

            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            attach_query = attach_sqlite_db_readonly(attachdb, 'AwemeIM')
            cursor.execute(attach_query)
            
            cursor.execute("SELECT name FROM AwemeIM.sqlite_master WHERE type='table' and name like 'AwemeContacts%';")
            table_results = cursor.fetchall()

            contacts_tables = [row[0] for row in table_results]

            if not contacts_tables:
                logfunc("No contacts tables found in AwemeIM.db, skipping tiktok_replied for this db.sqlite.")
                db.close()
                continue

            contacts_subqueries = []
            for table in contacts_tables:
                query_part = f'SELECT uid, customid, nickname, url1, "{table}" as t FROM AwemeIM.{table}'
                contacts_subqueries.append(query_part)

            contacts_union_query = '''
                        UNION ALL
                        '''.join(contacts_subqueries)

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            all_tables = [row[0] for row in cursor.fetchall()]
            required_tables = ['TIMMessageKVORM', 'TIMMessageORM']
            missing_tables = [tbl for tbl in required_tables if tbl not in all_tables]

            if missing_tables:
                if 'TIMMessageKVORM' in missing_tables:
                    logfunc("TIMMessageKVORM not found. Attempting to use TIMMessageNewPropertyORM instead.")
                    full_query = f'''
            WITH UniqueContacts AS (
                SELECT 
                    uid, customid, nickname, url1, t,
                    ROW_NUMBER() OVER (PARTITION BY uid ORDER BY t) AS rn
                FROM (
                    {contacts_union_query} -- Gunakan query union di sini
                ) AS CombinedContacts
            ),
            DeduplicatedContacts AS (
                SELECT uid, customid, nickname, url1, t
                FROM UniqueContacts
                WHERE rn = 1
            )
            select
                rowid,
                belongingMessageID,
                json_extract(value, '$.ref_msg_type') as ref_msg_type,
                json_extract(value, '$.ref_msg_id') as ref_msg_id,
                CASE WHEN
                    json_valid(json_extract(value, '$.hint')) 
                    AND json_valid(json_extract(json_extract(value, '$.hint'), '$.content')) 
                    THEN 
                        json_extract(json_extract(json_extract(value, '$.hint'), '$.content'), '$.text') 
                    ELSE 
                        NULL
                END AS referencedText,
                CASE WHEN
                    json_valid(json_extract(value, '$.hint'))  
                    THEN 
                        json_extract(json_extract(value, '$.hint'), '$.refmsg_uid') 
                    ELSE 
                        NULL
                END AS referencedMessageSender,
                ref_message_sender.customID as referenced_message_sender_customID,
                ref_message_sender.nickname as referenced_message_sender_nickname,
                NULL as replyText,
                NULL as deleted,
                belongingConversationID as belongingConversationIdentifier,
                sender as replySender,
                reply_sender.customID as reply_sender_customID,
                reply_sender.nickname as reply_sender_nickname,
                CASE 
                    WHEN createdTime > 1 THEN datetime(createdTime, 'unixepoch')
                    ELSE createdTime
                END replyServerCreatedAt
            from TIMMessageNewPropertyORM
            left join DeduplicatedContacts as ref_message_sender on json_extract(value, '$.hint.refmsg_uid') = ref_message_sender.uid
            left join DeduplicatedContacts as reply_sender on sender = reply_sender.uid
                    '''
                else:
                    logfunc(f"Required tables missing in db.sqlite: {missing_tables}. Skipping tiktok_replied for this db.sqlite.")
                    db.close()
                    continue
            else:
                full_query = f'''
            WITH UniqueContacts AS (
                SELECT 
                    uid, customid, nickname, url1, t,
                    ROW_NUMBER() OVER (PARTITION BY uid ORDER BY t) AS rn
                FROM (
                    {contacts_union_query} -- Gunakan query union di sini
                ) AS CombinedContacts
            ),
            DeduplicatedContacts AS (
                SELECT uid, customid, nickname, url1, t
                FROM UniqueContacts
                WHERE rn = 1
            )
            select
                TIMMessageKVORM.rowid,
                belongingMessageID,
                json_extract(value, '$.ref_msg_type') as ref_msg_type,
                json_extract(value, '$.ref_msg_id') as ref_msg_id,
                CASE WHEN
                    json_valid(json_extract(value, '$.hint')) 
                    AND json_valid(json_extract(json_extract(value, '$.hint'), '$.content')) 
                    THEN 
                        json_extract(json_extract(json_extract(value, '$.hint'), '$.content'), '$.text') 
                    ELSE 
                        NULL
                END AS referencedText,
                CASE WHEN
                    json_valid(json_extract(value, '$.hint'))  
                    THEN 
                        json_extract(json_extract(value, '$.hint'), '$.refmsg_uid') 
                    ELSE 
                        NULL
                END AS referencedMessageSender,
                ref_message_sender.customID as referenced_message_sender_customID,
                ref_message_sender.nickname as referenced_message_sender_nickname,
                CASE
                    WHEN json_valid(content) THEN json_extract(content, '$.text')
                ELSE NULL
                END replyText,
                CASE 
                    WHEN deleted = 0 THEN "False"
                    WHEN deleted = 1 THEN "True"
                    ELSE "Unknown"
                END deleted,
                belongingConversationIdentifier,
                sender as replySender,
                reply_sender.customID as reply_sender_customID,
                reply_sender.nickname as reply_sender_nickname,
                CASE 
                    WHEN servercreatedat > 1 THEN datetime(servercreatedat, 'unixepoch')
                    ELSE servercreatedat
                END replyServerCreatedAt
            from TIMMessageKVORM
            left join TIMMessageORM on TIMMessageKVORM.belongingMessageID = TIMMessageORM.identifier
            left join DeduplicatedContacts as ref_message_sender on referencedMessageSender = ref_message_sender.uid
            left join DeduplicatedContacts as reply_sender on replySender = reply_sender.uid
                '''

            try:
                cursor.execute(full_query)
            except sqlite3.OperationalError as e:
                logfunc(f"Reading tiktok_replied artifact had errors! Error was {str(e)}")
                db.close()
                continue

            all_rows = cursor.fetchall()

            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]))
            
            db.close()

    data_headers = (
        'RowID', 'BelongingMessageID', 'ref_msg_type', 'ref_msg_id', 'Referenced Text', 'Ref Msg Sender UID',
        'Ref Msg Sender CustomID', 'Ref Msg Sender Nickname', 'Reply Text', 'Deleted',
        'Belonging Conversation ID', 'Reply Sender UID', 'Reply Sender CustomID', 'Reply Sender Nickname',
        'Reply Server Created Date')

    return data_headers, data_list, report_file
