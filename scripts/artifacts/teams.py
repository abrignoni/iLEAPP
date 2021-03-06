import sqlite3
import os
import re
import shutil
import nska_deserialize as nd
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows, open_sqlite_db_readonly


def get_teams(files_found, report_folder, seeker):
    CacheFile = 0
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            databasedata = file_found
        if file_found.endswith('CacheFile'):
            CacheFile = file_found
    
    if CacheFile != 0:
        with open(CacheFile ,'rb') as nsfile:
            nsplist = nd.deserialize_plist(nsfile)
    
    db = open_sqlite_db_readonly(databasedata)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime('2001-01-01', "ZARRIVALTIME" || ' seconds'),
    ZIMDISPLAYNAME,
    ZCONTENT
    from ZSMESSAGE
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []  
    
    if usageentries > 0:
        for row in all_rows:
            thumb =''
            if '<div><img src=' in row[2]:
                matches = re.search('"([^"]+)"',row[2])
                imageURL = (matches[0].strip('\"'))
                if imageURL in nsplist.keys():
                    data_file_real_path = nsplist[imageURL]
                    for match in files_found:
                        if data_file_real_path in match:
                            shutil.copy2(match, report_folder)
                            data_file_name = os.path.basename(match)
                            thumb = f'<img src="{report_folder}/{data_file_name}"></img>'
            data_list.append((row[0], row[1], row[2], thumb))

        description = 'Teams Messages'
        report = ArtifactHtmlReport('Teams Messages')
        report.start_artifact_report(report_folder, 'Teams Messages', description)
        report.add_script()
        data_headers = ('Timestamp', 'Name', 'Message', 'Shared Media')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Shared Media']
)
        report.end_artifact_report()
        
        tsvname = 'Teams Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Teams Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Teams Messages data available')
    
    cursor.execute('''
    SELECT
    ZDISPLAYNAME,
    zemail,
    ZPHONENUMBER
    from
    ZDEVICECONTACTHASH
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2]))
            
        description = 'Teams Contact'
        report = ArtifactHtmlReport('Teams Contact')
        report.start_artifact_report(report_folder, 'Teams Contact', description)
        report.add_script()
        data_headers = ('Display Name', 'Email', 'Phone Number')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Teams Contact'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Teams Contact data available')
    
    cursor.execute('''
    SELECT
    datetime('2001-01-01', "ZTS_LASTSYNCEDAT" || ' seconds'),
    ZDISPLAYNAME,
    ZTELEPHONENUMBER
    from zuser
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2]))
            
        description = 'Teams User'
        report = ArtifactHtmlReport('Teams User')
        report.start_artifact_report(report_folder, 'Teams User', description)
        report.add_script()
        data_headers = ('Timestamp Last Sync', 'Display Name', 'Phone Number')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Teams User'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Teams User'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Teams User data available')
        
    
    
    db.close()
    

        
        