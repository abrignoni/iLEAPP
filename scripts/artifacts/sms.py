import os
import pandas as pd
import shutil

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, sanitize_file_name
from scripts.chat_rendering import render_chat, chat_HTML


def get_sms(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    sms_df = pd.read_sql_query('''
    SELECT
    CASE
        WHEN LENGTH(MESSAGE.DATE)=18 THEN DATETIME(MESSAGE.DATE/1000000000+978307200,'UNIXEPOCH')
        WHEN LENGTH(MESSAGE.DATE)=9 THEN DATETIME(MESSAGE.DATE + 978307200,'UNIXEPOCH')
        ELSE "N/A"
    END "MESSAGE DATE",
    MESSAGE.ROWID as "MESSAGE ID",
    CASE 
        WHEN LENGTH(MESSAGE.DATE_DELIVERED)=18 THEN DATETIME(MESSAGE.DATE_DELIVERED/1000000000+978307200,"UNIXEPOCH")
        WHEN LENGTH(MESSAGE.DATE_DELIVERED)=9 THEN DATETIME(MESSAGE.DATE_DELIVERED+978307200,"UNIXEPOCH")
        ELSE "N/A"
    END "DATE DELIVERED",
    CASE 
        WHEN LENGTH(MESSAGE.DATE_READ)=18 THEN DATETIME(MESSAGE.DATE_READ/1000000000+978307200,"UNIXEPOCH")
        WHEN LENGTH(MESSAGE.DATE_READ)=9 THEN DATETIME(MESSAGE.DATE_READ+978307200,"UNIXEPOCH")
        ELSE "N/A"
    END "DATE READ",
    MESSAGE.TEXT as "MESSAGE",
    HANDLE.ID AS "CONTACT ID",
    MESSAGE.SERVICE AS "SERVICE",
    MESSAGE.ACCOUNT AS "ACCOUNT",
    MESSAGE.IS_DELIVERED AS "IS DELIVERED",
    MESSAGE.IS_FROM_ME AS "IS FROM ME",
    ATTACHMENT.FILENAME AS "FILENAME",
    ATTACHMENT.MIME_TYPE AS "MIME TYPE",
    ATTACHMENT.TRANSFER_NAME AS "TRANSFER TYPE",
    ATTACHMENT.TOTAL_BYTES AS "TOTAL BYTES"
    FROM MESSAGE
    LEFT OUTER JOIN MESSAGE_ATTACHMENT_JOIN ON MESSAGE.ROWID = MESSAGE_ATTACHMENT_JOIN.MESSAGE_ID
    LEFT OUTER JOIN ATTACHMENT ON MESSAGE_ATTACHMENT_JOIN.ATTACHMENT_ID = ATTACHMENT.ROWID
    LEFT OUTER JOIN HANDLE ON MESSAGE.HANDLE_ID = HANDLE.ROWID 
    ''', db)

    usageentries = sms_df.shape[0]
    if usageentries > 0:
        data_list = sms_df.to_records(index=False)
        
        report = ArtifactHtmlReport('SMS - iMessage')
        report.start_artifact_report(report_folder, 'SMS - iMessage')
        report.add_script()

        sms_df = sms_df.rename(
                columns={"MESSAGE DATE": "data-time", 'MESSAGE ID': "message-id", "MESSAGE": "message", "CONTACT ID": "data-name", "IS FROM ME": "from_me", "MIME TYPE": "content-type"}
                )
        sms_df["data-time"] = pd.to_datetime(sms_df["data-time"])

        def copyAttachments(rec):
            pathToAttachment = None
            if rec["FILENAME"]:
                attachment = seeker.search('**'+rec["FILENAME"].replace('~', '', 1), return_on_first_hit=True)
                if not attachment:
                    logfunc(' [!] Unable to extract attachment file: "{}"'.format(rec['FILENAME']))
                    return
                if is_platform_windows():
                    destFileName = sanitize_file_name(os.path.basename(rec["FILENAME"]))
                else:
                    destFileName = os.path.basename(rec["FILENAME"])
                pathToAttachment = os.path.join((os.path.basename(os.path.abspath(report_folder))), destFileName)
                shutil.copy(attachment[0], os.path.join(report_folder, destFileName))
            return pathToAttachment
        
        sms_df["file-path"] = sms_df.apply(lambda rec: copyAttachments(rec), axis=1)

        num_entries = sms_df.shape[0]
        report.write_minor_header(f'Total number of entries: {num_entries}', 'h6')
    
        if file_found.startswith('\\\\?\\'):
            file_found = file_found[4:]
        report.write_lead_text(f'SMS - iMessage located at: {file_found}')
        report.write_raw_html(chat_HTML)
        report.add_script(render_chat(sms_df))

        data_headers = ('Message Date', 'Message ID', 'Date Delivered', 'Date Read', 'Message', 'Contact ID', 'Service', 'Account', 'Is Delivered', 'Is from Me', 'Filename', 'MIME Type', 'Transfer Type', 'Total Bytes')
        report.write_artifact_data_table(data_headers, data_list, file_found, write_total=False, write_location=False)
        report.end_artifact_report()
        
        tsvname = 'SMS - iMessage'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'SMS - iMessage'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No SMS & iMessage data available')

    db.close()
    return
