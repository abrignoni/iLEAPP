import os
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 

def get_sms(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
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
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))

        
        report = ArtifactHtmlReport('SMS - iMessage')
        report.start_artifact_report(report_folder, 'SMS - iMessage')
        report.add_script()
        data_headers = ('Message Date','Date Delivered','Date Read','Message','Contact ID','Service','Account','Is Delivered','Is from Me','Filename','MIME Type','Transfer Type','Total Bytes' )
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'SMS - iMessage'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'SMS - iMessage'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No SMS & iMessage data available')

    db.close()
    return      
    
    
