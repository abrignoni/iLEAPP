import glob
import os
import pathlib
import sqlite3
from datetime import datetime, timezone

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone 



def get_tileAppNetDb(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('tile-TileNetworkDB.sqlite'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(ZREGISTRATION_TIMESTAMP,'unixepoch','31 years'),
    ZEMAIL,
    ZFULL_NAME,
    ZMOBILE_PHONE
    FROM
    ZTILENTITY_USER
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []    
    if usageentries > 0:
        for row in all_rows:
            timestamp = row[0]
            if timestamp is None:
                pass
            else:
                timestamp = convert_ts_human_to_utc(timestamp)
                timestamp = convert_utc_human_to_timezone(timestamp,timezone_offset)
                
            data_list.append((timestamp, row[1], row[2], row[3]))
            
            description = ''
            report = ArtifactHtmlReport('Tile App - Account Information')
            report.start_artifact_report(report_folder, 'Tile App Account Information', description)
            report.add_script()
            data_headers = ('Registration Timestamp','Email','Full Name','Mobile Phone Number')     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
        tsvname = 'Tile App Account Information'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Tile App Account Information'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Tile App DB account data available')
    
    db.close()
    return 

__artifacts__ = {
    "tileAppNetDb": (
        "Accounts",
        ('*/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-TileNetworkDB.sqlite*'),
        get_tileAppNetDb)
}