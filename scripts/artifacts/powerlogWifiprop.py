import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_powerlogWifiprop(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    DATETIME(WIFIPROPERTIES_TIMESTAMP + SYSTEM, 'UNIXEPOCH') AS ADJUSTED_TIMESTAMP,
    CURRENTSSID,
    CURRENTCHANNEL,
    DATETIME(TIME_OFFSET_TIMESTAMP, 'UNIXEPOCH') AS OFFSET_TIMESTAMP,
    SYSTEM AS TIME_OFFSET,
    WIFIPROPERTIES_ID AS "PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES TABLE ID" 
	FROM
    (
    SELECT
        WIFIPROPERTIES_ID,
        WIFIPROPERTIES_TIMESTAMP,
        TIME_OFFSET_TIMESTAMP,
        MAX(TIME_OFFSET_ID) AS MAX_ID,
        CURRENTSSID,
        CURRENTCHANNEL,
        SYSTEM
    FROM
        (
        SELECT
            PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES.TIMESTAMP AS WIFIPROPERTIES_TIMESTAMP,
            CURRENTSSID,
            CURRENTCHANNEL,
            PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES.ID AS "WIFIPROPERTIES_ID" ,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.TIMESTAMP AS TIME_OFFSET_TIMESTAMP,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.ID AS TIME_OFFSET_ID,
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET.SYSTEM
        FROM
            PLWIFIAGENT_EVENTBACKWARD_CUMULATIVEPROPERTIES
        LEFT JOIN
            PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET 
        )
        AS WIFIPROPERTIES_STATE 
    GROUP BY
        WIFIPROPERTIES_ID 
    )    
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:    
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

        report = ArtifactHtmlReport('Powerlog WiFi Network Connections')
        report.start_artifact_report(report_folder, 'WiFi Network Connections')
        report.add_script()
        data_headers = ('Adjusted Timestamp','Current SSID','Current Channel','Offset Timestamp','Time Offset','Cummilative Prop. Table ID')   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Powerlog Wifi Prop'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Powerlog Wifi Prop'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return   