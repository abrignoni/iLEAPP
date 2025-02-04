__artifacts_v2__ = {
    "get_DataUsage": {
        "name": "Data Usage",
        "description": "Parses application network data usage",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "creation_date": "2023-10-10",
        "last_update_date": "2025-02-04",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "",
        "paths": ('*/wireless/Library/Databases/DataUsage.sqlite*',),
        "output_types": ["html", "tsv", "timeline", "lava"]
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, does_column_exist_in_db, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def get_DataUsage(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            if does_column_exist_in_db(file_found,'ZLIVEUSAGE','ZWIFIIN'):
                cursor.execute('''
                select
                ZLIVEUSAGE.ZTIMESTAMP,
                ZPROCESS.ZFIRSTTIMESTAMP,
                ZPROCESS.ZTIMESTAMP,
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
                where ZLIVEUSAGE.ZKIND != 257
                ''')

                all_rows = cursor.fetchall()
                
                for row in all_rows:
                    firstused = convert_cocoa_core_data_ts_to_utc(row[0])
                    lastused = convert_cocoa_core_data_ts_to_utc(row[1])
                    lastconnected = convert_cocoa_core_data_ts_to_utc(row[2])
                    
                    process_split = row[4].split('/')
                    data_list.append((lastconnected,firstused,lastused,row[3],process_split[0],row[5],row[6],row[7],row[8],row[9]))
                
                data_headers = ((('Last Connect Timestamp','datetime'),('First Usage Timestamp','datetime'),('Last Usage Timestamp','datetime'),'Bundle Name','Process Name','Entry Type','Wifi In (Bytes)','Wifi Out (Bytes)','Mobile/WWAN In (Bytes)','Mobile/WWAN Out (Bytes)'))
                return data_headers, data_list, file_found
                 
            else:
                cursor.execute('''
                select
                ZLIVEUSAGE.ZTIMESTAMP,
                ZPROCESS.ZFIRSTTIMESTAMP,
                ZPROCESS.ZTIMESTAMP,
                ZPROCESS.ZBUNDLENAME,
                ZPROCESS.ZPROCNAME,
                case ZLIVEUSAGE.ZKIND
                    when 0 then 'Process'
                    when 1 then 'App'
                    else ZLIVEUSAGE.ZKIND
                end,
                ZLIVEUSAGE.ZWWANIN,
                ZLIVEUSAGE.ZWWANOUT
                from ZLIVEUSAGE
                left join ZPROCESS on ZPROCESS.Z_PK = ZLIVEUSAGE.ZHASPROCESS
                where ZLIVEUSAGE.ZKIND != 257
                ''')

                all_rows = cursor.fetchall()
                
                for row in all_rows:
                    firstused = convert_cocoa_core_data_ts_to_utc(row[0])
                    lastused = convert_cocoa_core_data_ts_to_utc(row[1])
                    lastconnected = convert_cocoa_core_data_ts_to_utc(row[2])
                    
                    process_split = row[4].split('/')
                    data_list.append((lastconnected,firstused,lastused,row[3],process_split[0],row[5],row[6],row[7]))
                    
                data_headers = ((('Last Connect Timestamp','datetime'),('First Usage Timestamp','datetime'),('Last Usage Timestamp','datetime'),'Bundle Name','Process Name','Entry Type','Mobile/WWAN In (Bytes)','Mobile/WWAN Out (Bytes)'))
                return data_headers, data_list, file_found
                    
            db.close()
            
        else:
            continue
            
    if not data_list:
        logfunc('No Network Usage (DataUsage) - App Data available')