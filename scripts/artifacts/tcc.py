import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf
from packaging import version #use to search per version number

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_tcc(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('TCC.db'):
            break
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select datetime(last_modified,'unixepoch'),
    client,
    service,
    case auth_value
        when 0 then 'Not allowed'
        when 2 then 'Allowed'
        when 3 then 'Limited'
        else auth_value
    end
    from access
    order by client
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list =[]
        for row in all_rows: 
            data_list.append((row[0], row[1], row[2].replace("kTCCService",""), row[3]))

    if usageentries > 0:
        report = ArtifactHtmlReport('TCC - Permissions')
        report.start_artifact_report(report_folder, 'TCC - Permissions')
        report.add_script()
        data_headers = ('Last Modified Timestamp','Bundle ID','Service','Access')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'TCC - Permissions'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'TCC - Permissions'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No data available in TCC database.')
    
__artifacts__ = {
    "tcc": (
        "App Permissions",
        ('*TCC.db*'),
        get_tcc)
}
    