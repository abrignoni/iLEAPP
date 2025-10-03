__artifacts_v2__ = {
    "sms": {  # This should match the function name exactly
        "name": "SMS",
        "description": "Parses SMS and iMessage chats",
        "author": "@AlexisBrignoni, @XperyLab, @ydkhatri, @tobraha, @snoop168",
        "creation_date": "2020-04-30",
        "last_update_date": "2025-03-24",
        "requirements": "none",
        "category": "SMS & iMessage",
        "notes": "",
        "paths": ('*/mobile/Library/SMS/sms.db*',),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
        "artifact_icon": "message-square",
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

from ileapp.scripts.artifact_report import ArtifactHtmlReport
from ileapp.scripts.ilapfuncs import is_platform_windows, open_sqlite_db_readonly, sanitize_file_name, logfunc, convert_ts_human_to_timezone_offset
from ileapp.scripts.chat_rendering import render_chat, chat_HTML
from ileapp.scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records

@artifact_processor
def sms(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "sms.db")
    data_list = []
    
    query = '''
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
    '''

    data_headers = (('Message Timestamp', 'datetime'), ('Read Timestamp', 'datetime'), 'Message', 'Service', 'Message Direction', 'Message Sent',
                    'Message Delivered', 'Message Read', 'Account', 'Account Login', 'Chat Contact ID',
                    'Attachment Name', 'Attachment Path', ('Attachment Timestamp', 'datetime'), 'Attachment Mimetype',
                    'Attachment Size (Bytes)', 'Message Row ID', 'Chat ID', 'From Me')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        message_timestamp = convert_ts_human_to_timezone_offset(record[0], timezone_offset)
        read_timestamp = convert_ts_human_to_timezone_offset(record[1], timezone_offset)
        attachment_timestamp = convert_ts_human_to_timezone_offset(record[13], timezone_offset)
        data_list.append((message_timestamp, read_timestamp, record[2], record[3], record[4], record[5], record[6], record[7], record[8],
                          record[9], record[10], record[11], record[12], attachment_timestamp, record[14], record[15], record[16], record[17],
                          record[18]))

    def copyAttachments(rec):
        pathToAttachment = None
        if rec["Attachment Path"]:
            pathToAttachment = seeker.search('*'+rec["Attachment Path"].replace('~', '', 1), return_on_first_hit=True)
            if not pathToAttachment:
                logfunc(' [!] Unable to extract attachment file: "{}"'.format(rec["Attachment Path"]))
                return
        return pathToAttachment

    sms_df = pd.DataFrame(data_list,
                          columns=['data-time', 'Read Timestamp', 'message', 'Service', 'Message Direction',
                                   'Message Sent',
                                   'Message Delivered', 'Message Read', 'Account', 'Account Login', 'data-name',
                                   'Attachment Name', 'Attachment Path', 'Attachment Timestamp', 'content-type',
                                   'Attachment Size (Bytes)', 'message-id', 'Chat ID', 'from_me'])

    sms_df["file-path"] = sms_df.apply(lambda rec: copyAttachments(rec), axis=1)

    report = ArtifactHtmlReport('SMS & iMessage - Messages (Threaded)')
    report.start_artifact_report(report_folder, 'SMS & iMessage - Messages (Threaded)')
    report.add_script()
    report.write_lead_text(f'SMS & iMessage Messages (Threaded) located at: {source_path}')
    report.write_raw_html(chat_HTML)
    report.add_script(render_chat(sms_df))
    report.end_artifact_report()

    return data_headers, data_list, source_path
