import os
import pandas as pd
import shutil

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, sanitize_file_name
from scripts.chat_rendering import render_chat, chat_HTML

def get_sms(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_name = str(file_found)
        
        if file_name.endswith('sms.db'):
            break
        else:
            continue
    
    db = open_sqlite_db_readonly(file_found)
    sms_df = pd.read_sql_query('''
    select
    case
        when LENGTH(message.date) = 9 then 
        datetime(message.date + 978307200,'unixepoch')
        when LENGTH(message.date) = 18 then 
        datetime(message.date/1000000000 + 978307200,'unixepoch')
        else 'N/A'
    end as "Message Timestamp",
    case
        when LENGTH(message.date_read) = 9 then
        datetime(message.date_read + 978307200,'unixepoch')
        when LENGTH(message.date_read) = 18 then
        datetime(message.date_read/1000000000 + 978307200,'unixepoch')
        else 'N/A'
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
        when LENGTH(message.date) = 9 then 
        datetime(attachment.created_date + 978307200,'unixepoch')
        when LENGTH(message.date) = 18 then 
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
    ''', db)

    usageentries = sms_df.shape[0]
    if usageentries > 0:
        data_list = sms_df.to_records(index=False)
        
        report = ArtifactHtmlReport('SMS & iMessage - Messages (Threaded)')
        report.start_artifact_report(report_folder, 'SMS & iMessage - Messages (Threaded)')
        report.add_script()

        sms_df = sms_df.rename(
                columns={"Message Timestamp": "data-time", 'Message Row ID': "message-id", "Message": "message", "Chat Contact ID": "data-name", "From Me": "from_me", "Attachment Mimetype": "content-type"}
                )
        sms_df["data-time"] = pd.to_datetime(sms_df["data-time"])

        def copyAttachments(rec):
            pathToAttachment = None
            if rec["Attachment Path"]:
                attachment = seeker.search('**'+rec["Attachment Path"].replace('~', '', 1), return_on_first_hit=True)
                if not attachment:
                    logfunc(' [!] Unable to extract attachment file: "{}"'.format(rec['Attachment Path']))
                    return
                if is_platform_windows():
                    destFileName = sanitize_file_name(os.path.basename(rec["Attachment Path"]))
                else:
                    destFileName = os.path.basename(rec["Attachment Path"])
                pathToAttachment = os.path.join((os.path.basename(os.path.abspath(report_folder))), destFileName)
                shutil.copy(attachment[0], os.path.join(report_folder, destFileName))
            return pathToAttachment
        
        sms_df["file-path"] = sms_df.apply(lambda rec: copyAttachments(rec), axis=1)

        num_entries = sms_df.shape[0]
        report.write_minor_header(f'Total number of entries: {num_entries}', 'h6')
    
        if file_found.startswith('\\\\?\\'):
            file_found = file_found[4:]
        report.write_lead_text(f'SMS & iMessage Messages (Threaded) located at: {file_found}')
        report.write_raw_html(chat_HTML)
        report.add_script(render_chat(sms_df))
        report.end_artifact_report()
        
        report = ArtifactHtmlReport('SMS & iMessage - Messages')
        report.start_artifact_report(report_folder, 'SMS & iMessage - Messages')
        report.add_script()
        data_headers = ('Message Timestamp','Read Timestamp','Message','Service','Message Direction','Message Sent','Message Delivered','Message Read','Account','Account Login','Chat Contact ID','Attachment Name','Attachment Path','Attachment Timestamp','Attachment Mimetype','Attachment Size (Bytes)','Message Row ID','Chat ID','From Me')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'SMS & iMessage - Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'SMS & iMessage - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No SMS & iMessage - Messages data available')

    db.close()
    return
    
__artifacts__ = {
    "sms": (
        "SMS & iMessage",
        ('**/sms.db*'),
        get_sms)
}
