import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_powerlogProcessdatausage(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
            DATETIME(TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
            DATETIME(TIMESTAMPEND + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_END_TIMESTAMP,
            BUNDLENAME AS 'BUNDLE ID',
            PROCESSNAME AS 'PROCESS NAME',
            CELLIN AS 'CELL IN',
            CELLOUT AS 'CELL OUT',
            WIFIIN AS 'WIFI IN',
            WIFIOUT AS 'WIFI OUT',
            DATETIME(TIMESTAMP, 'UNIXEPOCH') AS ORIGINAL_TIMESTAMP,
            DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
            SYSTEM AS TIME_OFFSET,
            TABLE_ID AS "PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF TABLE ID"
        FROM
        (
        SELECT
            TABLE_ID,
            TIMESTAMP,
            TIME_OFFSET_TIMESTAMP,
            MAX(TIME_OFFSET_ID) AS MAX_ID,
            TIMESTAMPEND,
            BUNDLENAME,
            PROCESSNAME,
            CELLIN,
            CELLOUT,
            WIFIIN,
            WIFIOUT,
            SYSTEM
        FROM
        (
        SELECT
            PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.TIMESTAMP,
            PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.TIMESTAMPEND,
            PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.BUNDLENAME,
            PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.PROCESSNAME,
            PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.CELLIN,
            PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.CELLOUT,
            PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.WIFIIN,
            PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.WIFIOUT,
            PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF.ID AS "TABLE_ID",
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
        FROM
            PLPROCESSNETWORKAGENT_EVENTINTERVAL_USAGEDIFF 
        LEFT JOIN
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
        )
        GROUP BY
        TABLE_ID 
             )
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:    
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))

        report = ArtifactHtmlReport('Powerlog Process Data Usage')
        report.start_artifact_report(report_folder, 'Process Data Usage')
        report.add_script()
        data_headers = ('Adjusted Timestamp','Adjusted End Timestamp','Bundle ID','Process Name','Cell In','Cell Out','WiFI In','WiFi Out','Original Timestamp','Offset Timestamp','Time Offset','Usage Diff Table ID')   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Powerlog Process Data Usage'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Powerlog Process Data Usage'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return   