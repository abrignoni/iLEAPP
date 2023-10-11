import glob
import os
import pathlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_tileAppDisc(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('tile-DiscoveredTileDB.sqlite'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(ZLAST_MODIFIED_TIMESTAMP,'unixepoch','31 years'),
    ZTILE_UUID
    FROM
    ZTILENTITY_DISCOVEREDTILE
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1]))
            
            description = 'Tile IDs seen from other users'
            report = ArtifactHtmlReport('Tile App - Discovered Tiles')
            report.start_artifact_report(report_folder, 'Tile App Discovered Tiles', description)
            report.add_script()
            data_headers = ('Last Modified Timestamp','Tile UUID')     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
        tsvname = 'Tile App Discovered Tiles'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Tile Discovered Tiles'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Tile App Discovered Tiles data available')
    
    db.close()
    return 

__artifacts__ = {
    "tileAppDisc": (
        "Accounts",
        ('*/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-DiscoveredTileDB.sqlite*'),
        get_tileAppDisc)
}