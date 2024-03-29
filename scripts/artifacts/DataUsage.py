__artifacts_v2__ = {
    "datausage": {
        "name": "Data Usage",
        "description": "Parses application network data usage",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "date": "2023-10-10",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "",
        "paths": ('*/wireless/Library/Databases/DataUsage.sqlite*',),
        "function": "get_DataUsage"
    }
}

import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_DataUsage(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(ZLIVEUSAGE.ZTIMESTAMP + 978307200,'unixepoch'),
            datetime(ZPROCESS.ZFIRSTTIMESTAMP + 978307200,'unixepoch'),
            datetime(ZPROCESS.ZTIMESTAMP + 978307200,'unixepoch'),
            ZPROCESS.ZBUNDLENAME,
            ZPROCESS.ZPROCNAME,
            case ZLIVEUSAGE.ZKIND
                when 0 then 'Process'
                when 1 then 'App'
                else ZLIVEUSAGE.ZKIND
            end,
            ZLIVEUSAGE.ZWIFIIN,
            ZLIVEUSAGE.ZWIFIOUT,
            ZLIVEUSAGE.ZWWANIN,
            ZLIVEUSAGE.ZWWANOUT
            from ZLIVEUSAGE
            left join ZPROCESS on ZPROCESS.Z_PK = ZLIVEUSAGE.ZHASPROCESS
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                
                report = ArtifactHtmlReport('Network Usage (DataUsage) - App Data')
                report.start_artifact_report(report_folder, 'Network Usage (DataUsage) - App Data')
                report.add_script()
                data_headers = ('Last Connect Timestamp','First Usage Timestamp','Last Usage Timestamp','Bundle Name','Process Name','Type','Wifi In (Bytes)','Wifi Out (Bytes)','Mobile/WWAN In (Bytes)','Mobile/WWAN Out (Bytes)') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                
                data_list = []
                for row in all_rows:
                    firstused = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),timezone_offset)
                    lastused = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]),timezone_offset)
                    lastconnected = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[2]),timezone_offset)
                    
                    process_split = row[4].split('/')
                    data_list.append((lastconnected,firstused,lastused,row[3],process_split[0],row[5],row[6],row[7],row[8],row[9]))
                    
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Network Usage (DataUsage) - App Data'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Network Usage (DataUsage) - App Data'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Network Usage (DataUsage) - App Data available')
            db.close()
        else:
            continue