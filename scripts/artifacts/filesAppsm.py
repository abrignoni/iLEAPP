__artifacts_v2__ = {
    "filesAppsm": {
        "name": "Files App Smart Folders",
        "description": "Items stored in iCloud Drive.",
        "author": "@AlexisBrignoni",
        "version": "0.1",
        "date": "2023-01-01",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/smartfolders.db*',),
        "function": "get_filesAppsm"
    }
}


import os
import nska_deserialize as nd
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_filesAppsm(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
            
            creationdate = contentmodificationdate = userinfo = childitemcount = flags = ''
            
            with open(os.path.join(report_folder, row[2]+'.bplist'), "rb") as f:
                deserialized_plist = nd.deserialize_plist(f)
            for x, y in deserialized_plist.items():
                if x == '_creationDate':
                    creationdate = y.strftime('%Y-%m-%d %H:%M:%S')
                if x == '_contentModificationDate':
                    contentmodificationdate = y.strftime('%Y-%m-%d %H:%M:%S')
                if x == '_flags':
                    flags = y
                if x == '_userInfo':
                    userinfo = y
                if x == '_childItemCount':
                    childitemcount = y
            
            lasthitdate = datetime.datetime.utcfromtimestamp(row[3]).strftime('%Y-%m-%d %H:%M:%S')
            lasthitdate = convert_ts_human_to_utc(lasthitdate)
            lasthitdate = convert_utc_human_to_timezone(lasthitdate,timezone_offset)

            creationdate = convert_ts_human_to_utc(creationdate)
            creationdate = convert_utc_human_to_timezone(creationdate,timezone_offset)

            contentmodificationdate = convert_ts_human_to_utc(contentmodificationdate)
            contentmodificationdate = convert_utc_human_to_timezone(contentmodificationdate,timezone_offset)

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
    
