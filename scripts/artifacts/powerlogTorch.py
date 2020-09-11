import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_powerlogTorch(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        DATETIME(TORCH_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
        BUNDLEID AS BUNDLE_ID,
        CASE LEVEL
        WHEN "0" THEN "OFF"
        WHEN "1" THEN "ON"
        END AS STATUS,
        DATETIME(TORCH_TIMESTAMP, 'UNIXEPOCH') AS ORIGINAL_TORCH_TIMESTAMP,
        DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
        SYSTEM AS TIME_OFFSET,
    TORCH_ID
    FROM
        (
        SELECT
            BUNDLEID,
            TORCH_ID,
            TORCH_TIMESTAMP,
            TIME_OFFSET_TIMESTAMP,
            MAX(TIME_OFFSET_ID) AS MAX_ID,
            SYSTEM,
            LEVEL
        FROM
                (
                SELECT
                    PLCAMERAAGENT_EVENTFORWARD_TORCH.TIMESTAMP AS TORCH_TIMESTAMP,
                    PLCAMERAAGENT_EVENTFORWARD_TORCH.BUNDLEID,
                    PLCAMERAAGENT_EVENTFORWARD_TORCH.LEVEL,
                    PLCAMERAAGENT_EVENTFORWARD_TORCH.ID AS "TORCH_ID",
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM,
                    BUNDLEID 
                FROM
                    PLCAMERAAGENT_EVENTFORWARD_TORCH 
                LEFT JOIN
                    PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
                ) 
                AS TORCHESTATE 
        GROUP BY
            TORCH_ID 
        )
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:    
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

        report = ArtifactHtmlReport('Powerlog Torch')
        report.start_artifact_report(report_folder, 'Torch')
        report.add_script()
        data_headers = ('Adjusted Timestamp','Bundle ID','Status','Original Torch Timestamp','Offset Timestamp','Time Offset','Torch ID')   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Powerlog Torch'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Powerlog Torch'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return   