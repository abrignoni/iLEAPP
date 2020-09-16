import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_powerlogPushreceived(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        DATETIME(TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
        BUNDLEID AS 'BUNDLE ID',
        CONNECTIONTYPE AS 'CONNECTION TYPE',
        ISDROPPED AS 'IS DROPPED',
        LINKQUALITY AS 'LINK QUALITY',
        PRIORITY AS 'PRIORITY',
        TOPIC AS 'TOPIC',
        SERVERHOSTNAME AS 'SERVERHOSTNAME',
        SERVERIP AS 'SERVER IP',
        DATETIME(TIMESTAMP, 'UNIXEPOCH') AS ORIGINAL_TIMESTAMP,
        DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
        SYSTEM AS TIME_OFFSET,
        TABLE_ID AS "PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH TABLE ID"
    FROM
    (
    SELECT
        TABLE_ID,
        TIMESTAMP,
        TIME_OFFSET_TIMESTAMP,
        MAX(TIME_OFFSET_ID) AS MAX_ID,
        BUNDLEID,
        CONNECTIONTYPE,
        ISDROPPED,
        LINKQUALITY,
        PRIORITY,
        TOPIC,
        SERVERHOSTNAME,
        SERVERIP,
        SYSTEM
    FROM
    (
    SELECT
        PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.TIMESTAMP,
        PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.BUNDLEID,
        PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.CONNECTIONTYPE,
        PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.ISDROPPED,
        PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.LINKQUALITY,
        PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.PRIORITY,
        PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.TOPIC,
        PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.SERVERHOSTNAME,
        PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.SERVERIP,
        PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH.ID AS "TABLE_ID",
        PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
        PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
        PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
    FROM
        PLPUSHAGENT_EVENTPOINT_RECEIVEDPUSH 
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
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))

        report = ArtifactHtmlReport('Powerlog Push Message Received')
        report.start_artifact_report(report_folder, 'Push Message Received')
        report.add_script()
        data_headers = ('Adjusted Timestamp','Bundle ID','Connection Type','Is Dropped','Link Quality','Priority','Topic','Server Hostname','Server IP','Original Timestamp','Offset Timestamp','Time Offset','Aggregate Table ID')   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Powerlog Push Message Received'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Powerlog Push Message Received'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return   