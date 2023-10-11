import sqlite3
import io
import json
import os
import shutil
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly


def get_serialNumber(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
    data_list =[]
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    SerialNumber
    FROM TableInfo
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0],))
            logdevinfo(f"Serial Number: {row[0]}")
            break
            
        description = 'Serial Number'
        report = ArtifactHtmlReport('Serial Number')
        report.start_artifact_report(report_folder, 'Serial Number')
        report.add_script()
        data_headers = ('Serial Number',)
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Serial Number'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Serial Number available in consolidated.db')
        
__artifacts__ = {
    "serialNumber": (
        "Identifiers",
        ('*/Library/Caches/locationd/consolidated.db'),
        get_serialNumber)
}