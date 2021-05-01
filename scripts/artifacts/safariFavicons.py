import sqlite3
import os
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows, open_sqlite_db_readonly


def get_safariFavicons(files_found, report_folder, seeker):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('Favicons.db'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select 
    datetime('2001-01-01', "timestamp" || ' seconds') as icon_timestamp,
    page_url.url,
    icon_info.url,
    icon_info.width,
    icon_info.height,
    icon_info.has_generated_representations
    FROM icon_info
    LEFT JOIN page_url
    on icon_info.uuid = page_url.uuid
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

        description = 'Safari Favicons'
        report = ArtifactHtmlReport('Favicons')
        report.start_artifact_report(report_folder, 'Favicons', description)
        report.add_script()
        data_headers = ('Timestamp', 'Page URL', 'Icon URL', 'Width', 'Height', 'Generated Representations?' )
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Safari Favicons'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Safari Favicons'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Safari Favicons data available')
    
    db.close()

        
        