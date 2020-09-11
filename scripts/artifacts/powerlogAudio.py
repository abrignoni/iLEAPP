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

def get_powerlogAudio(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
            DATETIME(TIMESTAMPLOGGED, 'UNIXEPOCH') AS "TIMESTAMP LOGGED",
            APPLICATIONNAME AS "APPLICATION NAME / BUNDLE ID",
            ASSERTIONID AS "ASERTION ID",
            ASSERTIONNAME AS "ASSERTION NAME",
            AUDIOROUTE AS "AUDIO ROUTE",
            MIRRORINGSTATE AS "MIRRORING STATE",
            OPERATION,
            PID,
            ID AS "PLAUDIOAGENT_EVENTPOINT_AUDIOAPP TABLE ID" 
            FROM
            PLAUDIOAGENT_EVENTPOINT_AUDIOAPP
        ''')
        
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            if version.parse(iOSversion) >= version.parse("9"):
                for row in all_rows:    
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

                report = ArtifactHtmlReport('Powerlog Audio Routing via App')
                report.start_artifact_report(report_folder, 'Audio Routing')
                report.add_script()
                data_headers = ('Timestamp','Timestamped Logged','Bundle ID','Assertion Name','Audio Route','Mirroring State','Operation','PID', 'Audio App Table ID' )   
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Powerlog Audio Routing App'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Powerlog Audio Routing App'
                timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available in Airdop Connection Info')

        db.close()
        return      
    
    
