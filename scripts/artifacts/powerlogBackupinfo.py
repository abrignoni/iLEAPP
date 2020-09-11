import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf
from packaging import version #use to search per version number

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_powerlogBackupinfo(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("11"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
            DATETIME(START, 'UNIXEPOCH') AS "START",
            DATETIME(END, 'UNIXEPOCH') AS "END",
            STATE AS "STATE",
            FINISHED AS "FINISHED",
            HASERROR AS "HAS ERROR",
            ID AS "PLXPCAGENT_EVENTPOINT_MOBILEBACKUPEVENTS TABLE ID" 
        FROM
            PLXPCAGENT_EVENTPOINT_MOBILEBACKUPEVENTS
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            if version.parse(iOSversion) >= version.parse("11"):
                for row in all_rows:    
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

                report = ArtifactHtmlReport('Powerlog Backup Info')
                report.start_artifact_report(report_folder, 'Backup Info')
                report.add_script()
                data_headers = ('Timestamp','Start','End','State','Finished','Has error','Table ID' )   
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Powerlog Backup Info'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Powerlog Backup Info'
                timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available in Powerlog Backup Info')

        db.close()
        return      
    
    
