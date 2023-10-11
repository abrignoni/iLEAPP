import glob
import os
import pathlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, kmlgen, timeline, is_platform_windows, open_sqlite_db_readonly


def get_quickLook(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('cloudthumbnails.db'):
            break
    
    if file_found.endswith('cloudthumbnails.db'):
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select 
        datetime("last_hit_date", 'unixepoch') as lasthitdate,
        last_seen_path, 
        size
        from thumbnails
        ''')
    
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2]))
            
                description = 'Listing of iCloud files accessed by the Quick Look function.'
                report = ArtifactHtmlReport('iCloud Quick Look')
                report.start_artifact_report(report_folder, 'iCloud Quick Look', description)
                report.add_script()
                data_headers = ('Last Hit Date','Last Seen Path','Size')     
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
            tsvname = 'iCloud Quick Look'
            tsv(report_folder, data_headers, data_list, tsvname)
        
            tlactivity = 'iCloud Quick Look'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No iCloud Quick Look DB data available')
    
        db.close()
        
    else:
        logfunc('No Quicklook DB file found. Check -wal files for possible data remnants.')
__artifacts__ = {
    "quickLook": (
        "iCloud Quick Look",
        ('*/Quick Look/cloudthumbnails.db*'),
        get_quickLook)
}