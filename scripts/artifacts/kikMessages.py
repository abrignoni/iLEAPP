import os
import shutil
import sqlite3
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, media_to_html


def get_kikMessages(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(ZKIKMESSAGE.ZRECEIVEDTIMESTAMP +978307200,'UNIXEPOCH') AS RECEIVEDTIME,
    datetime(ZKIKMESSAGE.ZTIMESTAMP +978307200,'UNIXEPOCH') as TIMESTAMP,
    ZKIKMESSAGE.ZBODY,
    case ZKIKMESSAGE.ZTYPE
        when 1 then 'Received'
        when 2 then 'Sent'
        when 3 then 'Group Admin'
        when 4 then 'Group Message'
        else 'Unknown' end as 'Type',
    ZKIKMESSAGE.ZUSER,
    ZKIKUSER.ZDISPLAYNAME,
    ZKIKUSER.ZUSERNAME,
    ZKIKATTACHMENT.ZCONTENT
    from ZKIKMESSAGE
    left join ZKIKUSER on ZKIKMESSAGE.ZUSER = ZKIKUSER.Z_PK
    left join ZKIKATTACHMENT on ZKIKMESSAGE.Z_PK = ZKIKATTACHMENT.ZMESSAGE
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []  
    
    if usageentries > 0:
        for row in all_rows:
        
            attachmentName = str(row[7])
            thumb = media_to_html(attachmentName, files_found, report_folder)
            
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], thumb))

        description = 'Kik Messages'
        report = ArtifactHtmlReport('Kik Messages')
        report.start_artifact_report(report_folder, 'Kik Messages', description)
        report.add_script()
        data_headers = ('Received Time', 'Timestamp', 'Message', 'Type', 'User', 'Display Name', 'User Name','Attachment Name','Attachment')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Attachment'])
        report.end_artifact_report()
        
        tsvname = 'Kik Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Kik Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Kik Messages data available')
        
    cursor.execute('''
    SELECT
    Z_PK,
    ZDISPLAYNAME,
    ZUSERNAME,
    ZEMAIL,
    ZJID,
    ZFIRSTNAME,
    ZLASTNAME,
    datetime(ZPPTIMESTAMP/1000,'unixepoch'),
    ZPPURL
    FROM ZKIKUSER
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []  
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

        description = 'Kik Users'
        report = ArtifactHtmlReport('Kik Users')
        report.start_artifact_report(report_folder, 'Kik Users', description)
        report.add_script()
        data_headers = ('PK','Display Name','User Name','Email','JID','First Name','Last Name','Profile Pic Timestamp','Profile Pic URL')     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Kik Users'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Kik Users'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Kik Users data available')
    
    db.close()
    return 

__artifacts__ = {
    "kikMessages": (
        "Kik",
        ('**/kik.sqlite*','*/mobile/Containers/Shared/AppGroup/*/cores/private/*/content_manager/data_cache/*'),
        get_kikMessages)
}