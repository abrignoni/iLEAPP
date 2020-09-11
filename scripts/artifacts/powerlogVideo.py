import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_powerlogVideo(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    DATETIME(VIDEO_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
    CLIENTDISPLAYID AS "CLIENT DISPLAY ID",
    STATE,
    CLIENTPID AS "CLIENT PID",
    DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
    SYSTEM AS TIME_OFFSET,
    VIDEO_ID AS "PLVIDEOAGENT_EVENTFORWARD_VIDEO TABLE ID" 
	FROM
    (
    SELECT
        VIDEO_ID,
        VIDEO_TIMESTAMP,
        TIME_OFFSET_TIMESTAMP,
        MAX(TIME_OFFSET_ID) AS MAX_ID,
        CLIENTDISPLAYID,
        STATE,
        CLIENTPID,
        SYSTEM
    FROM
        (
        SELECT
            PLVIDEOAGENT_EVENTFORWARD_VIDEO.TIMESTAMP AS VIDEO_TIMESTAMP,
            CLIENTDISPLAYID,
            STATE,
            CLIENTPID,
            PLVIDEOAGENT_EVENTFORWARD_VIDEO.ID AS "VIDEO_ID" ,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
        FROM
            PLVIDEOAGENT_EVENTFORWARD_VIDEO
        LEFT JOIN
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET
        )
        AS VIDEO_STATE 
    GROUP BY
        VIDEO_ID 
    )
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:    
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

        report = ArtifactHtmlReport('Powerlog App Playing Video')
        report.start_artifact_report(report_folder, 'App Playing Video')
        report.add_script()
        data_headers = ('Adjusted Timestamp','Client Display ID','State','Client PID','Offset Timestamp','Time Offset','Event Forward Video Table ID')   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Powerlog Video'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Powerlog Video'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return   