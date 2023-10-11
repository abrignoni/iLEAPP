import io
import nska_deserialize as nd
import sqlite3
import json
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, media_to_html

def relative_paths(source, splitter):
    splitted_a = source.split(splitter)
    for x in splitted_a:
        if 'LEAPP_Reports_' in x:
            report_folder = x
            
    splitted_b = source.split(report_folder)
    return '.'+ splitted_b[1]


def get_vippsContacts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
    
    data_list = []
    
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    
    cursor.execute('''
    SELECT 
    ZNAME,
    ZPHONENUMBERS,
    ZPROFILEIMAGEDATA,
    ZCONTACTSTOREIDENTIFIER
    FROM ZCONTACTMODEL

    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    
    if usageentries > 0:
        for row in all_rows:
            name = row[0]
            phonenumbers = row[1]
            image = row[2]
            pathing = os.path.join(report_folder, f'{row[3]}')
            if image is not None:
                with open(pathing, 'wb') as f:
                    f.write(image)
                
                platform = is_platform_windows()
                if platform:
                    pathing = pathing.replace('/', '\\')
                    splitter = '\\'
                else:
                    splitter = '/'
                    
                source = relative_paths(pathing, splitter)

                thumb = f'<img src="{source}"width="300"></img>'
                
            else:
                thumb = ''
           
            data_list.append((thumb, name, phonenumbers))
        
        report = ArtifactHtmlReport('Vipps - Contacts')
        report.start_artifact_report(report_folder, 'Vipps - Contacts')
        report.add_script()
        data_headers = ('Profile Image', 'Name', 'Telephones')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Profile Image'])
        report.end_artifact_report()
        
        tsvname = 'Vipps Contacts'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        
        db.close()
    else:
        logfunc('No data available for Vipps Contacts')
        
__artifacts__ = {
    "vippsContacts": (
        "Vipps",
        ('*/Vipps.sqlite*'),
        get_vippsContacts)
}