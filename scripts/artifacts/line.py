__artifacts_v2__ = {
    "line": {
        "name": "Line Artifacts",
        "description": "Get Line",
        "author": "Elliot Glendye",
        "version": "0.0.1",
        "date": "2023-11-22",
        "requirements": "",
        "category": "Line",
        "notes": "No notes at present.",
        "paths": ('**/Line.sqlite*'),
        "function": "get_line"
    }
}

import scripts.artifacts.artGlobals
import sqlite3
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, open_sqlite_db_readonly

def get_line(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        iOSversion = scripts.artifacts.artGlobals.versionf
        if version.parse(iOSversion) < version.parse('15'):
            logfunc('Line parsing has not been tested on iOS version ' + iOSversion)
            
        if file_found.endswith('Line.sqlite'):
            break
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select datetime(ZMESSAGE.ZTIMESTAMP / 1000, 'unixepoch') AS Timestamp,
    CASE 
    WHEN ZMESSAGE.ZSENDER IS NULL THEN "Outgoing"
     ELSE "Incoming" END AS "Sent / Received",
    ZUSER.ZNAME AS "Username",
    ZMESSAGE.ZTEXT AS "Message Content"
    From ZMESSAGE
    LEFT Join ZUSER On ZMESSAGE.ZSENDER = ZUSER.Z_PK
    ORDER BY ZMESSAGE.ZTIMESTAMP Desc;
    ''')
        
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
        
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3]))
            
        description = 'A report of Line Messages, including message direction and associated usernames.'
        report = ArtifactHtmlReport('Line Messages')
        report.start_artifact_report(report_folder, 'Line Messages', description)
        report.add_script()
        data_headers = ('Timestamp', 'Sent / Received', 'Username', 'Message',)
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        tsvname = 'Line Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
    
    else:
        logfunc('No Line messages present')
    db.close()
    return