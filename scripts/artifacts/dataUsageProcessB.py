import glob
import os
import pathlib
import plistlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_dataUsageProcessB(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    DATETIME(ZPROCESS.ZTIMESTAMP+ 978307200, 'UNIXEPOCH') AS "TIMESTAMP",
    DATETIME(ZPROCESS.ZFIRSTTIMESTAMP + 978307200, 'UNIXEPOCH') AS "PROCESS FIRST TIMESTAMP",
    ZPROCESS.ZPROCNAME AS "PROCESS NAME",
    ZPROCESS.ZBUNDLENAME AS "BUNDLE ID",
    ZPROCESS.Z_PK AS "ZPROCESS TABLE ID" 
    FROM ZPROCESS
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4]))

        report = ArtifactHtmlReport('Data Usage')
        report.start_artifact_report(report_folder, 'Data Usage Process')
        report.add_script()
        data_headers = ('Timestamp','Process First Timestamp','Process Name','Bundle ID','Table ID' )   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Data Usage Process'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Data Usage Process'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Data Usage available')

    db.close()
    return      
    
    
