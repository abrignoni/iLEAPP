import glob
import os
import pathlib
import plistlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_callHistory(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT 
    ZADDRESS AS "ADDRESS", 
    ZANSWERED AS "WAS ANSWERED", 
    ZCALLTYPE AS "CALL TYPE", 
    ZORIGINATED AS "ORIGINATED", 
    ZDURATION AS "DURATION (IN SECONDS)",
    ZISO_COUNTRY_CODE as "ISO COUNTY CODE",
    ZLOCATION AS "LOCATION", 
    ZSERVICE_PROVIDER AS "SERVICE PROVIDER",
    DATETIME(ZDATE+978307200,'UNIXEPOCH') AS "TIMESTAMP"
    FROM ZCALLRECORD  
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            an = str(row[0])
            an = an.replace("b'", "")
            an = an.replace("'", "")
            data_list.append((row[8],an,row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

        report = ArtifactHtmlReport('Call Logs')
        report.start_artifact_report(report_folder, 'Call Logs')
        report.add_script()
        data_headers = ('Timestamp','Address','Was Answered','Call Type','Originated','Duration in Secs','ISO County Code','Location','Service Provider' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Call History'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Call History'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Call History data available')

    db.close()
    return      
    
    
