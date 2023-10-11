# Module Description: Parses missing ROWID values from the SMS.db, presents the number of missing rows, and provides timestamps for data rows before and after the missing data
# Author: @SQL_McGee
# Date: 2023-03-20
# Artifact version: 0.0.1
# Requirements: none

# This query was the product of research completed by James McGee, Metadata Forensics, LLC, for "Lagging for the Win", published by Belkasoft
# https://belkasoft.com/lagging-for-win

import sqlite3
import textwrap
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_SMS(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    sms = ''
    
    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('sms.db'):
            sms = str(file_found)
            source_file_sms = file_found.replace(seeker.directory, '')
   
    db = open_sqlite_db_readonly(sms)
    
    cursor = db.cursor()
    
    cursor.execute('''
    SELECT * FROM (
        SELECT 
        CASE -- This column is the same as the very first column but obtaining timestamp instead of the ROWID value. A CASE statement is used to capture data whether using seconds since Jan 1, 1970 or microseconds since Jan 1, 1970
            WHEN length(DATE) = 18 
            THEN LAG(DATETIME(DATE/1000000000 + 978307200, 'UNIXEPOCH'),1) OVER (ORDER BY ROWID) 
            WHEN length(DATE) = 9
            THEN LAG(DATETIME(DATE + 978307200, 'UNIXEPOCH'),1) OVER (ORDER BY ROWID)
            END AS "Beginning Timestamp",
        CASE -- Finally, this last column obtains the timestamp for the row following the missing row
            WHEN length(DATE) = 18 
            THEN DATETIME(DATE/1000000000 + 978307200, 'UNIXEPOCH') 
            WHEN length(DATE) = 9
            THEN DATETIME(DATE + 978307200, 'UNIXEPOCH')
            END  AS "Ending Timestamp",
		LAG (ROWID,1) OVER (ORDER BY ROWID) AS "Previous ROWID", -- This column uses the LAG function to obtain the ROWID value prior to a missing row
        ROWID AS "ROWID", -- This column obtains the ROWID value following the missing row
        (ROWID - (LAG (ROWID,1) OVER (ORDER BY ROWID)) - 1) AS "Number of Missing Rows" -- This column is a subtraction of the first two columns, minus one additional value, to obtain the number of missing rows
        FROM message) list
        WHERE ROWID - "Previous ROWID" > 1;
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append(
            (row[0], row[1], row[2], row[3], row[4]))
            
        report = ArtifactHtmlReport('SMS - Missing ROWIDs')
        report.start_artifact_report(report_folder, 'SMS - Missing ROWIDs')
        report.add_script()
        data_headers = (
            'Beginning Timestamp', 'Ending Timestamp','Previous ROWID', 'ROWID', 'Number of Missing Rows')
        report.write_artifact_data_table(data_headers, data_list, sms)
        report.end_artifact_report()

        tsvname = 'SMS - Missing ROWIDs'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'SMS - Missing ROWIDs'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in SMS - Missing ROWIDs')
        
__artifacts__ = {
    "SMS Missing ROWIDs": (
        "SMS & iMessage",
        ('*/mobile/Library/SMS/sms*'),
        get_SMS)
}
