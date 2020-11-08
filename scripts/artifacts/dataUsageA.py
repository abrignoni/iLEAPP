import glob
import os
import pathlib
import plistlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_dataUsageA(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        DATETIME(ZPROCESS.ZTIMESTAMP + 978307200, 'unixepoch') AS "PROCESS TIMESTAMP",
        DATETIME(ZPROCESS.ZFIRSTTIMESTAMP + 978307200, 'unixepoch') AS "PROCESS FIRST TIMESTAMP",
        DATETIME(ZLIVEUSAGE.ZTIMESTAMP + 978307200, 'unixepoch') AS "LIVE USAGE TIMESTAMP",
        ZBUNDLENAME AS "BUNDLE ID",
        ZPROCNAME AS "PROCESS NAME",
        ZWIFIIN AS "WIFI IN",
        ZWIFIOUT AS "WIFI OUT",
        ZWWANIN AS "WWAN IN",
        ZWWANOUT AS "WWAN OUT",
        ZLIVEUSAGE.Z_PK AS "ZLIVEUSAGE TABLE ID" 
    FROM ZLIVEUSAGE 
    LEFT JOIN ZPROCESS ON ZPROCESS.Z_PK = ZLIVEUSAGE.ZHASPROCESS
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))

        report = ArtifactHtmlReport('Data Usage')
        report.start_artifact_report(report_folder, 'Data Usage')
        report.add_script()
        data_headers = ('Process Timestamp','Process First Timestamp','Live Usage Timestamp','Bundle ID','Process Name','WIFI In','WIFI Out','WWAN IN','WWAN Out','Table ID' )   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Data Usage'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Data Usage'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Data Usage available')

    db.close()
    return      
    
    
