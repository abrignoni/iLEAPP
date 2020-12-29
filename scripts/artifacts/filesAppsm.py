import glob
import os
import nska_deserialize as nd
import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly


def get_filesAppsm(files_found, report_folder, seeker):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('smartfolders.db'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT * 
    FROM
    FILENAMES
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    if usageentries > 0:

        for row in all_rows:
            
            output_file = open(os.path.join(report_folder, row[2]+'.bplist'), "wb") 
            output_file.write(row[1])
            output_file.close()
            
            with open(os.path.join(report_folder, row[2]+'.bplist'), "rb") as f:
                deserialized_plist = nd.deserialize_plist(f)
            for x, y in deserialized_plist.items():
                if x == '_creationDate':
                    creationdate = y
                if x == '_contentModificationDate':
                    contentmodificationdate = y
                if x == '_flags':
                    flags = y
                if x == '_userInfo':
                    userinfo = y
                if x == '_childItemCount':
                    childitemcount = y
            lasthitdate = datetime.datetime.fromtimestamp(row[3])
            
            data_list.append((lasthitdate, row[0], row[2],row[4], creationdate, contentmodificationdate, userinfo, childitemcount, flags))
            
            description = 'Files App - Files stored in the "On my iPad" area.'
            report = ArtifactHtmlReport('Files App - Filenames')
            report.start_artifact_report(report_folder, 'Files App - Filenames', description)
            report.add_script()
            data_headers = ('Last Hit Date','Folder ID','Filename','Frequency at Las Hit Date','Creation Date','Modification Date','User Info','Child Item Count','Flags' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Files App - Filenames'
            tsv(report_folder, data_headers, data_list, tsvname)
        
            tlactivity = 'Files App - Filenames'
            timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Files App - Filenames data available')

    db.close()
    
