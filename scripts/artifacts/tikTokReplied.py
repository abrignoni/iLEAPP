from os.path import dirname, join, basename
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_tiktok_replied(files_found, report_folder, seeker, wrap_text, timezone_offset):


    # Find the AwemeIM.db
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('AwemeIM.db'):
            attachdb = file_found
            logfunc("FOUND AwemeIM.db")

    # Iterate all files again this time only targeting the db.sqlite files
    for file_found in files_found:
        file_found = str(file_found)


        if file_found.endswith('db.sqlite'):
            dir_path = dirname(file_found)
            account_id = basename(dir_path)
            data_list = []
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute(f'ATTACH DATABASE "file:{attachdb}?mode=ro" as AwemeIM;')
            cursor.execute("SELECT name FROM AwemeIM.sqlite_master WHERE type='table' and name like 'AwemeContactsV%';")
            table_results = cursor.fetchall()

            # There are sometimes more than one table that contacts are contained in. Need to union them all together
            contacts_tables = [row[0] for row in table_results]

            # create the contact subquery
            contacts_subqueries = []
            for table in contacts_tables:
                contacts_subqueries.append(f'SELECT uid, customid, nickname, url1 FROM {table}')

            contacts_subquery = '''
                        UNION ALL
                        '''.join(contacts_subqueries)

            cursor.execute(f'''
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
            left join ({contacts_subquery}) as ref_message_sender on referencedMessageSender = ref_message_sender.uid
            left join ({contacts_subquery}) as reply_sender on replySender = reply_sender.uid
            ''')

            all_rows = cursor.fetchall()
            logfunc(f'all rows length {len(all_rows)}')
            if len(all_rows) > 0:
                i = 0
                for row in all_rows:
                    i += 1
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                      row[10], row[11], row[12], row[13], row[14]))

            report = ArtifactHtmlReport(f'TikTok Referenced Replied - {account_id}')
            description = 'This artifact is extracted from the TIMMessageKVORM table which appears to contain ' \
                          'referenced messages. It appears that a copy of the message being replied to is placed ' \
                          'into this table. It also appears that entries in this table may not be deleted when the ' \
                          'actual referenced message or the new reply is deleted. There may be unknown circumstances ' \
                          'that cause records to be deleted from this table and there may be reasons other than ' \
                          'using the simple reply feature that may cause records to be written here.'
            report.start_artifact_report(report_folder, f'TikTok Referenced Replied - {account_id}',
                                         artifact_description=description)

            report.add_script()
            data_headers = (
                'RowID', 'BelongingMessageID', 'ref_msg_type', 'ref_msg_id', 'Referenced Text', 'Ref Msg Sender UID',
                'Ref Msg Sender CustomID', 'Ref Msg Sender Nickname', 'Reply Text', 'Deleted',
                'Belonging Conversation ID', 'Reply Sender UID', 'Reply Sender CustomID', 'Reply Sender Nickname',
                'Reply Server Created Date')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

    tsvname = 'Tiktok Messages'
    tsv(report_folder, data_headers, data_list, tsvname)

    tlactivity = 'TikTok Messages'
    timeline(report_folder, tlactivity, data_list, data_headers)


__artifacts_v2__ = {
    'tiktok_replied': {
        'name': 'TikTok - Replied Referenced Messages',
        'description': 'Extracts "Replied" message remnants left in the TikTok database which may no longer exist in '
                       'the native message table',
        'author': 'John Hyla http://www.bluecrewforensics.com/',
        'version': '0.1',
        'date': '2024-07-10',
        'requirements': 'none',
        'category': 'TikTok',
        'notes': 'There may be other reasons for these messages to exist in this table, but for now testing shows '
                 'that a copy is placed here when the reply feature is used',
        'paths': ('*/Application/*/Library/Application Support/ChatFiles/*/db.sqlite*', '*AwemeIM.db*'),
        'function': 'get_tiktok_replied'
    }
}
