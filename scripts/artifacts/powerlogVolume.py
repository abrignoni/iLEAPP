import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_powerlogVolume(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
    VOLUME,
    CASE MUTED 
        WHEN "0" THEN "NO" 
        WHEN "1" THEN "YES" 
    END "MUTED", 
    ID AS "PLAUDIOAGENT_EVENTFORWARD_OUTPUT TABLE ID" 
    FROM
    PLAUDIOAGENT_EVENTFORWARD_OUTPUT
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:    
            data_list.append((row[0],row[1],row[2],row[3]))

        report = ArtifactHtmlReport('Powerlog Volume')
        report.start_artifact_report(report_folder, 'Volume')
        report.add_script()
        data_headers = ('Timestamp','Volume','Muted','Event Forward Output Table ID')   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No data available in table')

    db.close()
    return   