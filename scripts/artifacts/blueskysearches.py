__artifacts_v2__ = {
    "blueskysearches": {
        "name": "Bluesky",
        "description": "User generated searches",
        "author": "DFIRcon 2025 Miami",
        "version": "0.0.1",
        "date": "2024-11-15",
        "requirements": "none",
        "category": "Bluesky",
        "notes": "",
        "paths": ('*/xyz.blueskyweb.app/databases/RKStorage*'),
        "function": "get_blueskysearches"
    }
}

import sqlite3
import json 

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_blueskysearches(files_found, report_folder, seeker, wrap_text, time_offset):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('RKStorage'):
            db = open_sqlite_db_readonly(file_found)
            #SQL QUERY TIME!
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            key, value
            FROM catalystLocalStorage
            WHERE key like 'searchHistory'
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            
            if usageentries > 0:
                for row in all_rows:
            
                    searches = row[1]
                    searches = json.loads(searches)
                    for item in searches:
                        data_list.append((item,))
            db.close()
                    
        else:
            continue
        
    if data_list:
        description = 'Bluesky'
        report = ArtifactHtmlReport('Bluesky user generated searches')
        report.start_artifact_report(report_folder, 'Bluesky Searches', description)
        report.add_script()
        data_headers = ('Searches',)
        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Bluesky Searches'
        tsv(report_folder, data_headers, data_list, tsvname)
    
    
    else:
        logfunc('No Bluesky searches available')
        