__artifacts_v2__ = {
    "get_DataUsage": {
        "name": "Data Usage",
        "description": "Parses application network data usage",
        "author": "@KevinPagano3",
        "creation_date": "2023-10-10",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "ZKIND is reported as stored; rows with ZKIND 257 are excluded by the query, the meaning of these values is not documented.",
        "paths": ('*/wireless/Library/Databases/DataUsage.sqlite*',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "chart-bar",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 480 rows",
            "dexter_ios18": "iOS 18.3.2 | 689 rows",
            "felix_ios17": "iOS 17.6.1 | 781 rows",
            "fsfull002_ios17": "iOS 17.1 | 436 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1691 rows",
            "iphone11_ios17": "iOS 17.3 | 2402 rows",
            "iphone12_ios18": "iOS 18.7 | 510 rows",
            "iphone14plus_ios18": "iOS 18.0 | 228 rows",
            "otto_ios17": "iOS 17.5.1 | 2074 rows",
            "abe_ios16": "iOS 16.5 | 1463 rows",
            "felix23_ios16": "iOS 16.5 | 349 rows",
            "hickman_ios13": "iOS 13.3.1 | 624 rows",
            "hickman_ios14": "iOS 14.3 | 683 rows",
            "jess_ios15": "iOS 15.0.2 | 633 rows",
            "magnet_ios16": "iOS 16.1.1 | 5 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor
from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, does_column_exist_in_db, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def get_DataUsage(context):
    data_list = []
    
    for file_found in context.get_files_found():
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
                ZLIVEUSAGE.ZKIND,
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
                    usage_entry_ts = convert_cocoa_core_data_ts_to_utc(row[0])
                    process_first_ts = convert_cocoa_core_data_ts_to_utc(row[1])
                    process_ts = convert_cocoa_core_data_ts_to_utc(row[2])

                    process_split = row[4].split('/')
                    data_list.append((process_ts,process_first_ts,usage_entry_ts,row[3],process_split[0],row[5],row[6],row[7],row[8],row[9]))

                db.close()

                data_headers = (('Process Timestamp','datetime'), ('Process First Timestamp','datetime'), ('Usage Entry Timestamp','datetime'),
                                'Bundle Name', 'Process Name', 'ZKIND (as stored)', 'Wifi In (Bytes)', 'Wifi Out (Bytes)', 'Mobile/WWAN In (Bytes)',
                                'Mobile/WWAN Out (Bytes)')
                return data_headers, data_list, file_found
                 
            else:
                cursor.execute('''
                select
                ZLIVEUSAGE.ZTIMESTAMP,
                ZPROCESS.ZFIRSTTIMESTAMP,
                ZPROCESS.ZTIMESTAMP,
                ZPROCESS.ZBUNDLENAME,
                ZPROCESS.ZPROCNAME,
                ZLIVEUSAGE.ZKIND,
                ZLIVEUSAGE.ZWWANIN,
                ZLIVEUSAGE.ZWWANOUT
                from ZLIVEUSAGE
                left join ZPROCESS on ZPROCESS.Z_PK = ZLIVEUSAGE.ZHASPROCESS
                where ZLIVEUSAGE.ZKIND != 257
                ''')

                all_rows = cursor.fetchall()
                
                for row in all_rows:
                    usage_entry_ts = convert_cocoa_core_data_ts_to_utc(row[0])
                    process_first_ts = convert_cocoa_core_data_ts_to_utc(row[1])
                    process_ts = convert_cocoa_core_data_ts_to_utc(row[2])

                    process_split = row[4].split('/')
                    data_list.append((process_ts,process_first_ts,usage_entry_ts,row[3],process_split[0],row[5],row[6],row[7]))

                db.close()

                data_headers = (('Process Timestamp','datetime'), ('Process First Timestamp','datetime'), ('Usage Entry Timestamp','datetime'),
                                'Bundle Name', 'Process Name', 'ZKIND (as stored)', 'Mobile/WWAN In (Bytes)', 'Mobile/WWAN Out (Bytes)')
                return data_headers, data_list, file_found
            
    if not data_list:
        logfunc('No Network Usage (DataUsage) - App Data available')
        return (), [], ''