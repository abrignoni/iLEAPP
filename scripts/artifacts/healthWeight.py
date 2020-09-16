import glob
import os
import pathlib
import plistlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_healthWeight(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "DATE",
        QUANTITY AS "WEIGHT (IN KG)",
        QUANTITY*2.20462 AS "WEIGHT (IN LBS)",
        SAMPLES.DATA_ID AS "SAMPLES TABLE ID" 
    FROM
        SAMPLES 
        LEFT OUTER JOIN QUANTITY_SAMPLES ON SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID 
    WHERE
        SAMPLES.DATA_TYPE = 3 
        AND "DATE" IS  NOT NULL
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3]))

        report = ArtifactHtmlReport('Health Weight')
        report.start_artifact_report(report_folder, 'Weight')
        report.add_script()
        data_headers = ('Date','Weight in KG','Weight in LBS','Samples Table ID' )   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Health Weight'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Health Weight'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return      
    
    
