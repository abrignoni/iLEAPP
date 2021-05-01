import glob
import os
import pathlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_tileAppNetDb(files_found, report_folder, seeker):
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
            data_list.append((row[0], row[1], row[2], row[3]))
            
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
