import os
import sqlite3
import pandas as pd
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows
from scripts.chat_rendering import render_chat

def get_sms(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    sms_df = pd.read_sql_query('''
    SELECT
    CASE
        WHEN LENGTH(MESSAGE.DATE)=18 THEN DATETIME(MESSAGE.DATE/1000000000+978307200,'UNIXEPOCH')
        WHEN LENGTH(MESSAGE.DATE)=9 THEN DATETIME(MESSAGE.DATE + 978307200,'UNIXEPOCH')
        ELSE "N/A"
		END "MESSAGE DATE",			
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
                columns={"MESSAGE DATE":"data-time","MESSAGE":"message","CONTACT ID":"data-name","IS FROM ME":"from_me"}
                )
        sms_df["ts"] = pd.to_datetime(sms_df["data-time"])
        latest_mess = sms_df.groupby("data-name", as_index=False)["ts"].max()
        sms_df = pd.merge(
                    sms_df, 
                    latest_mess, 
                    on=["data-name"], 
                    how='right', 
                    suffixes=["","_latest"]
                    ).sort_values(by=['ts_latest','data-name'], ascending=[False, True])

        chats = {}
        for c in sms_df["data-name"].unique():
            chats[c] = sms_df[sms_df["data-name"] == c][["data-name","from_me","message","data-time"]].reset_index(drop=True).to_dict(orient='index')
        
        rendering = render_chat(json.dumps(chats))
        num_entries = sms_df.shape[0]
        report.write_minor_header(f'Total number of entries: {num_entries}', 'h6')
    
        if file_found.startswith('\\\\?\\'):
            file_found = file_found[4:]
        report.write_lead_text(f'SMS - iMessage located at: {file_found}')
        report.write_raw_html(rendering['HTML'])
        report.add_script(rendering['js'])

        data_headers = ('Message Date','Date Delivered','Date Read','Message','Contact ID','Service','Account','Is Delivered','Is from Me','Filename','MIME Type','Transfer Type','Total Bytes' )
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
    
    
