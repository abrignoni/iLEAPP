import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_powerlogAggnotifications(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        DATETIME(TIMESTAMP, 'UNIXEPOCH') AS TIMESTAMP,
        NOTIFICATIONBUNDLEID AS "BULLETIN BUNDLE ID",
        TIMEINTERVAL / 60 AS "TIME INTERVAL IN SECONDS",
        COUNT AS "COUNT",
        NOTIFICATIONTYPE AS "NOTIFICATION TYPE",
        ID AS "PLSPRINGBOARDAGENT_AGGREGATE_SBNOTIFICATIONS_AGGREGATE TABLE ID" 
    FROM
        PLSPRINGBOARDAGENT_AGGREGATE_SBNOTIFICATIONS_AGGREGATE 
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:    
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

        report = ArtifactHtmlReport('Powerlog Aggregate Notifications')
        report.start_artifact_report(report_folder, 'Aggregate Notifications')
        report.add_script()
        data_headers = ('Timestamp','Notification Bundle ID','Time Interval in Seconds','Count','Notification Type','Aggregate Table ID')   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Powerlog Agg Notifications'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Powerlog Agg Notifications'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return   