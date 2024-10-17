__artifacts_v2__ = {
    "get_sms": {  # This should match the function name exactly
        "name": "SMS",
        "description": "Parses sms and iMessage chats",
        "author": "@KevinPagano",
        "version": "0.1",
        "date": "2023-03-28",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "",
        "paths": ('**/sms.db*',),
        "output_types": "all",  # or ["html", "tsv", "timeline", "lava"]
        "data_views": {
            "chat": {
                "threadDiscriminatorColumn": "Chat ID",
                "threadLabelColumn": "Chat Contact ID",
                "textColumn": "Message",
                "directionColumn": "From Me",
                "directionSentValue": 1,
                "timeColumn": "Message Timestamp",
                "senderColumn": "Chat Contact ID",
                "sentMessageLabelColumn": "Account",
                "mediaColumn": "Attachment Path"
            }
        }
    }
}

import os
import pandas as pd
import shutil

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import is_platform_windows, open_sqlite_db_readonly, sanitize_file_name, logfunc, convert_ts_human_to_timezone_offset
from scripts.chat_rendering import render_chat, chat_HTML
from scripts.ilapfuncs import artifact_processor

@artifact_processor
def get_sms(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_name = str(file_found)
        
        if file_name.endswith('sms.db'):
            break
        else:
            continue
    
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute(
        '''
        select
        case
            when LENGTH(message.date) = 9 then 
            datetime(message.date + 978307200,'unixepoch')
            when LENGTH(message.date) = 18 then 
            datetime(message.date/1000000000 + 978307200,'unixepoch')
            else ''
        end as "Message Timestamp",
        case
            when LENGTH(message.date_read) = 9 then
            datetime(message.date_read + 978307200,'unixepoch')
            when LENGTH(message.date_read) = 18 then
            datetime(message.date_read/1000000000 + 978307200,'unixepoch')
            else ''
        end as "Read Timestamp",
        message.text as "Message",
        message.service as "Service",
        case
            when message.is_from_me = 0
            then 'Incoming'
            when message.is_from_me = 1
            then 'Outgoing'
        end as "Message Direction",
        case 
            when message.is_sent = 0
            then ''
            when message.is_sent = 1
            then 'Yes'
        end as "Message Sent",
        case
            when message.is_delivered = 0
            then ''
            when message.is_delivered = 1
            then 'Yes'
        end as "Message Delivered",
        case
            when message.is_read = 0
            then ''
            when message.is_read = 1
            then 'Yes'
        end as "Message Read",
        message.account as "Account",
        chat.account_login as "Account Login",
        chat.chat_identifier as "Chat Contact ID",
        attachment.transfer_name as "Attachment Name",
        attachment.filename as "Attachment Path",
        case
            when LENGTH(attachment.created_date) = 9 then 
            datetime(attachment.created_date + 978307200,'unixepoch')
            when LENGTH(attachment.created_date) = 18 then 
            datetime(attachment.created_date/1000000000 + 978307200,'unixepoch')
        end as "Attachment Timestamp",
        attachment.mime_type as "Attachment Mimetype",
        attachment.total_bytes as "Attachment Size",
        message.rowid as "Message Row ID",
        chat_message_join.chat_id as "Chat ID",
        message.is_from_me as "From Me"
        from message
        left join message_attachment_join on message.ROWID = message_attachment_join.message_id
        left join attachment on message_attachment_join.attachment_id = attachment.ROWID
        left join chat_message_join on message.ROWID = chat_message_join.message_id
        left join chat on chat_message_join.chat_id = chat.ROWID 
        ''')
    all_rows = cursor.fetchall()

    data_headers = (('Message Timestamp', 'datetime'), ('Read Timestamp', 'datetime'), 'Message', 'Service', 'Message Direction', 'Message Sent',
                    'Message Delivered', 'Message Read', 'Account', 'Account Login', 'Chat Contact ID',
                    'Attachment Name', 'Attachment Path', ('Attachment Timestamp', 'datetime'), 'Attachment Mimetype',
                    'Attachment Size (Bytes)', 'Message Row ID', 'Chat ID', 'From Me')

    data_list = []
    for row in all_rows:
        message_timestamp = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
        read_timestamp = convert_ts_human_to_timezone_offset(row[1], timezone_offset)
        attachment_timestamp = convert_ts_human_to_timezone_offset(row[13], timezone_offset)
        data_list.append((message_timestamp, read_timestamp, row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                          row[9], row[10], row[11], row[12], attachment_timestamp, row[14], row[15], row[16], row[17],
                          row[18]))

    def copyAttachments(rec):
        pathToAttachment = None
        if rec[12]:
            attachment = seeker.search('**'+rec[12].replace('~', '', 1), return_on_first_hit=True)
            if not attachment:
                logfunc(' [!] Unable to extract attachment file: "{}"'.format(rec[12]))
                return
            if is_platform_windows():
                destFileName = sanitize_file_name(os.path.basename(rec[12]))
            else:
                destFileName = os.path.basename(rec[12])
            pathToAttachment = os.path.join((os.path.basename(os.path.abspath(report_folder))), destFileName)
            shutil.copy(attachment[0], os.path.join(report_folder, destFileName))
        return pathToAttachment

    sms_df = pd.DataFrame(data_list,
                          columns=['data-time', 'Read Timestamp', 'message', 'Service', 'Message Direction',
                                   'Message Sent',
                                   'Message Delivered', 'Message Read', 'Account', 'Account Login', 'data-name',
                                   'Attachment Name', 'Attachment Path', 'Attachment Timestamp', 'content-type',
                                   'Attachment Size (Bytes)', 'message-id', 'Chat ID', 'from_me'])

    sms_df["file-path"] = sms_df.apply(lambda rec: copyAttachments(rec), axis=1)

    if file_found.startswith('\\\\?\\'):
        file_found = file_found[4:]

    db.close()

    report = ArtifactHtmlReport('SMS & iMessage - Messages (Threaded)')
    report.start_artifact_report(report_folder, 'SMS & iMessage - Messages (Threaded)')
    report.add_script()
    report.write_lead_text(f'SMS & iMessage Messages (Threaded) located at: {file_found}')
    report.write_raw_html(chat_HTML)
    report.add_script(render_chat(sms_df))
    report.end_artifact_report()

    return data_headers, data_list, file_found

