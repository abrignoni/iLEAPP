import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_powerlogVolumePercentage(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    DATETIME(VOLUME_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
    VOLUME AS "VOLUME PERCENTAGE",
    CASE MUTED 
        WHEN "0" THEN "NO" 
        WHEN "1" THEN "YES" 
    END AS "MUTED",
    DATETIME(VOLUME_TIMESTAMP, 'UNIXEPOCH') AS ORIGINAL_VOLUME_TIMESTAMP,
    DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
    SYSTEM AS TIME_OFFSET,
    VOLUME_ID AS "PLAUDIOAGENT_EVENTFORWARD_OUTPUT TABLE ID" 
    FROM
    (
    SELECT
        VOLUME_ID,
        VOLUME_TIMESTAMP,
        TIME_OFFSET_TIMESTAMP,
        MAX(TIME_OFFSET_ID) AS MAX_ID,
        VOLUME,
        MUTED,
        SYSTEM
    FROM
        (
        SELECT
            PLAUDIOAGENT_EVENTFORWARD_OUTPUT.TIMESTAMP AS VOLUME_TIMESTAMP,
            VOLUME,
            MUTED,
            PLAUDIOAGENT_EVENTFORWARD_OUTPUT.ID AS "VOLUME_ID" ,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
        FROM
            PLAUDIOAGENT_EVENTFORWARD_OUTPUT
        LEFT JOIN
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET
        )
        AS VOLUME_STATE 
    GROUP BY
        VOLUME_ID 
    )
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:    
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

        report = ArtifactHtmlReport('Powerlog Volume Percentage')
        report.start_artifact_report(report_folder, 'Volume Percentage')
        report.add_script()
        data_headers = ('Adjusted Timestamp','Volume Percentage','Muted','Original Volume Timestamp','Offset Timestamp','Time Offset','Event Forward Output Table ID')   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Powerlog Volume Percentage'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Powerlog Volume Percentage'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return   