__artifacts_v2__ = {
    "datausage": {
        "name": "Data Usage",
        "description": "Parses application network data usage",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "date": "2023-10-10",
        "requirements": "none",
        "category": "Data Usage",
        "notes": "",
        "paths": ('*/wireless/Library/Databases/DataUsage.sqlite*',),
        "function": "get_DataUsage"
    }
}

import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_DataUsage(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(zprocess.zfirsttimestamp + 978307200, 'unixepoch') as "First Used",
            datetime(zprocess.ztimestamp + 978307200, 'unixepoch') as "Last Used",
            datetime(zliveusage.ztimestamp + 978307200, 'unixepoch') as "Last Connected",
            zprocess.zbundlename as "Bundle Name",
            zprocess.zprocname as "Process Name",
            zliveusage.zwifiin as "Wifi Data In (Bytes)",
            zliveusage.zwifiout as "Wifi Data Out (Bytes)",
            zliveusage.zwwanin as "Cellular Data In (Bytes)",
            zliveusage.zwwanout as "Cellular Data Out (Bytes)"
            from zliveusage, zprocess
            where zprocess.z_pk = zliveusage.zhasprocess
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Data Usage')
                report.start_artifact_report(report_folder, 'Data Usage')
                report.add_script()
                data_headers = ('Process First Used','Process Last Used','Process Last Connected','Bundle Name','Process Name','Wifi Data In (Bytes)','Wifi Data Out (Bytes)','Cellular Data In (Bytes)','Cellular Data Out (Bytes)')   
                
                data_list = []
                for row in all_rows:
                    process_split = row[4].split('/')
                    data_list.append((row[0],row[1],row[2],row[3],process_split[0],row[5],row[6],row[7],row[8]))
                    
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Data Usage'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Data Usage'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Data Usage available')

            db.close()