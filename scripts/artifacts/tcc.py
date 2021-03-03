import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf
from packaging import version #use to search per version number

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_tcc(files_found, report_folder, seeker):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('TCC.db'):
            break
        
    db = open_sqlite_db_readonly(file_found)
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        select client,
        service,
        datetime(last_modified,'unixepoch')
        from access
        order by client
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list =[]
            for row in all_rows: 
                data_list.append((row[0], row[1], row[2]))

        if usageentries > 0:
            report = ArtifactHtmlReport('TCC - Permissions')
            report.start_artifact_report(report_folder, 'TCC - Permissions')
            report.add_script()
            data_headers = ('Bundle ID','Permissions','Last Modified Timestamp')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            '''
            tsvname = 'InteractionC Contacts'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'InteractonC Contacts'
            timeline(report_folder, tlactivity, data_list, data_headers)
            '''
        else:
            logfunc('No data available in TCC database.')

        db.close()
        return      
    
    
    