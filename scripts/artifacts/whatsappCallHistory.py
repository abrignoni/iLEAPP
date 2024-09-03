__artifacts_v2__ = {
    "whatsappCallHistory": {
        "name": "WhatsappCallHistory",
        "description": "",
        "author": "",
        "version": "",
        "date": "",
        "requirements": "",
        "category": "Whatsapp",
        "notes": "",
        "paths": ('*/var/mobile/Containers/Shared/AppGroup/*/CallHistory.sqlite*',
                  '*/var/mobile/Containers/Shared/AppGroup/*/ContactsV2.sqlite*',),
        "function": "get_whatsappCallHistory"
    }
}


import sqlite3
import io
import json
import os
import shutil
import nska_deserialize as nd
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly


def get_whatsappCallHistory(files_found, report_folder, seeker, wrap_text, timezone_offset):

    CallHistory_db = ""
    ContactsV2_db = ""

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('CallHistory.sqlite'):
            CallHistory_db = file_found
        elif file_found.endswith('ContactsV2.sqlite'):
            ContactsV2_db = file_found

        #if file_found.endswith('.sqlite'):
            #break
    data_list =[]

    if CallHistory_db and not ContactsV2_db:
        db = open_sqlite_db_readonly(CallHistory_db)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(ZWACDCALLEVENT.ZDATE+978307200,'unixepoch') as Datetime_begin,
        CASE
            WHEN ((datetime(ZWACDCALLEVENT.ZDATE+978307200,'unixepoch')) = (datetime(((ZWACDCALLEVENT.ZDATE) + (ZWACDCALLEVENT.ZDURATION))+978307200,'unixepoch'))) then 'No Call Duration'
            ELSE (datetime(((ZWACDCALLEVENT.ZDATE) + (ZWACDCALLEVENT.ZDURATION))+978307200,'unixepoch'))
        END Datetime_end, 
        time(ZWACDCALLEVENT.ZDURATION+978307200,'unixepoch') as Duration,
        CASE
            WHEN ZWACDCALLEVENT.ZGROUPCALLCREATORUSERJIDSTRING = ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING then "Incoming" 
            ELSE "Outgoing"
        END Direction,
        CASE ZWACDCALLEVENT.ZOUTCOME
            WHEN 0 THEN 'Ended'
            WHEN 1 THEN 'Missed'
            WHEN 4 THEN 'Rejected'
            ELSE ZWACDCALLEVENT.ZOUTCOME
        END Disconnected_cause,
        ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING as 'Contact ID'
        FROM ZWACDCALLEVENT, ZWACDCALLEVENTPARTICIPANT
        WHERE ZWACDCALLEVENT.Z1CALLEVENTS = ZWACDCALLEVENTPARTICIPANT.Z1PARTICIPANTS
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
           
            description = 'Whatsapp - Call History'
            report = ArtifactHtmlReport('Whatsapp - Call History')
            report.start_artifact_report(report_folder, 'Whatsapp - Call History')
            report.add_script()
            data_headers = (
                'Starting Timestamp', 'Ending Timestamp', 'Duration H:M:S', 'Direction', 'Disconnected cause', 'Contact ID')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()    
            
            
            tsvname = f'Whatsapp - Call History'
            tsv(report_folder, data_headers, data_list, tsvname)
        else:
            logfunc('Whatsapp - Call History data available')

    if CallHistory_db and ContactsV2_db:
        db_CallHistory = open_sqlite_db_readonly(CallHistory_db)
        cursor = db_CallHistory.cursor()
        # To avoid modifying the code too much, I'm working on the path string
        if is_platform_windows():
            ContactsV2_db = ContactsV2_db.split('?\\')[1]
        # Attach ContactsV2 database in read only for contact information number and name
        cursor.execute(f'ATTACH DATABASE "file:{ContactsV2_db}?mode=ro" AS ContactsV2;')
        cursor.execute('''
            SELECT
            datetime(ZWACDCALLEVENT.ZDATE+978307200,'unixepoch') as Datetime_begin,
            CASE
                WHEN ((datetime(ZWACDCALLEVENT.ZDATE+978307200,'unixepoch')) = (datetime(((ZWACDCALLEVENT.ZDATE) + (ZWACDCALLEVENT.ZDURATION))+978307200,'unixepoch'))) then 'No Call Duration'
                ELSE (datetime(((ZWACDCALLEVENT.ZDATE) + (ZWACDCALLEVENT.ZDURATION))+978307200,'unixepoch'))
            END Datetime_end, 
            time(ZWACDCALLEVENT.ZDURATION+978307200,'unixepoch') as Duration,
            CASE
                WHEN ZWACDCALLEVENT.ZGROUPCALLCREATORUSERJIDSTRING = ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING then "Incoming" 
                ELSE "Outgoing"
            END Direction,
            CASE ZWACDCALLEVENT.ZOUTCOME
                WHEN 0 THEN 'Ended'
                WHEN 1 THEN 'Missed'
                WHEN 4 THEN 'Rejected'
                ELSE ZWACDCALLEVENT.ZOUTCOME
            END Disconnected_cause,
            ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING as 'Contact ID',
            base2.ZFULLNAME,
            base2.ZPHONENUMBER
            FROM ZWACDCALLEVENT, ZWACDCALLEVENTPARTICIPANT
            INNER JOIN ContactsV2.ZWAADDRESSBOOKCONTACT base2 ON ZWACDCALLEVENTPARTICIPANT.ZJIDSTRING = base2.ZWHATSAPPID
            WHERE ZWACDCALLEVENT.Z1CALLEVENTS = ZWACDCALLEVENTPARTICIPANT.Z1PARTICIPANTS
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        
        if usageentries > 0:
            for row in all_rows:
                
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7] ))
           
            description = 'Whatsapp - Call History'
            report = ArtifactHtmlReport('Whatsapp - Call History')
            report.start_artifact_report(report_folder, 'Whatsapp - Call History')
            report.add_script()
            data_headers = (
                'Starting Timestamp', 'Ending Timestamp', 'Duration H:M:S', 'Direction', 'Disconnected cause', 'Contact ID', 'Contact Fullname', 'Phone Number')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()            
            
            tsvname = f'Whatsapp - Call History'
            tsv(report_folder, data_headers, data_list, tsvname)
        else:
            logfunc('Whatsapp - Call History data available')
        
    else:
        logfunc('Whatsapp - Call History data available')
