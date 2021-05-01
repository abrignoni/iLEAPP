import sqlite3
import io
import json
import os
import shutil
import nska_deserialize as nd
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly


def get_whatsappContacts(files_found, report_folder, seeker):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
    data_list =[]
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    ZFULLNAME,
    ZABOUTTEXT,
    datetime(ZABOUTTIMESTAMP+978307200, 'UNIXEPOCH'),
    ZPHONENUMBER,
    ZPHONENUMBERLABEL,
    ZWHATSAPPID,
    ZIDENTIFIER
    FROM ZWAADDRESSBOOKCONTACT
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    
    if usageentries > 0:
        for row in all_rows:
            
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5],row[6]))
            
        
        
        description = 'Whatsapp - Contacts'
        report = ArtifactHtmlReport('Whatsapp - Contacts')
        report.start_artifact_report(report_folder, 'Whatsapp - Contacts')
        report.add_script()
        data_headers = (
            'Fullname', 'About Text', 'About Text Timestamp', 'Phone Number', 'Phone Number Label', 'Whatsapp ID', 'Identifier')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()    
        
        
        tsvname = f'Whatsapp - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('Whatsapp - Contacts data available')
        
    