__artifacts_v2__ = {
    "get_appleWalletPKPasses": {
        "name": "PK Passes",
        "description": "Apple wallet passes PK",
        "author": "@any333",
        "creation_date": "2021-02-17",
        "last_update_date": "2025-10-22",
        "requirements": "none",
        "category": "Apple Wallet",
        "notes": "",
        "paths": ('*/Cards/*.pkpass/pass.json'),
        "output_types": "standard",
        "artifact_icon": "credit-card",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 107 rows",
            "dexter_ios18": "iOS 18.3.2 | 92 rows",
            "felix_ios17": "iOS 17.6.1 | 45 rows",
            "fsfull002_ios17": "iOS 17.1 | 24 rows",
            "hc_ios18_7": "iOS 18.7.8 | 25 rows",
            "iphone11_ios17": "iOS 17.3 | 24 rows",
            "iphone12_ios18": "iOS 18.7 | 25 rows",
            "iphone14plus_ios18": "iOS 18.0 | 25 rows",
            "otto_ios17": "iOS 17.5.1 | 35 rows",
            "abe_ios16": "iOS 16.5 | 32 rows",
            "hickman_ios13": "iOS 13.3.1 | 24 rows",
            "hickman_ios14": "iOS 14.3 | 24 rows",
            "jess_ios15": "iOS 15.0.2 | 25 rows",
            "magnet_ios16": "iOS 16.1.1 | 25 rows",
        }
    },
    "get_appleWalletNanoPasses": {
        "name": "Nano Passes",
        "description": "Apple wallet Nano passes",
        "author": "@any333",
        "creation_date": "2021-02-17",
        "last_update_date": "2025-10-22",
        "requirements": "none",
        "category": "Apple Wallet",
        "notes": "",
        "paths": ('*/nanopasses.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "device-watch",
        "sample_data": {
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
        }
    }
}

import json
from scripts.ilapfuncs import open_sqlite_db_readonly, artifact_processor, convert_cocoa_core_data_ts_to_utc, \
    get_plist_content

@artifact_processor
def get_appleWalletPKPasses(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)

        if file_found.endswith('pass.json'):
            with open(file_found, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for x, y in data.items():
                    data_list.append((x,str(y), context.get_relative_path(file_found)))
    
    data_headers = ['Identifier','Items', 'Source File']
    return data_headers, data_list, 'see Source File for more info'
                    
@artifact_processor
def get_appleWalletNanoPasses(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)

        if file_found.endswith('.sqlite3'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''SELECT 
                            UNIQUE_ID, 
                            ORGANIZATION_NAME, 
                            TYPE_ID, 
                            LOCALIZED_DESCRIPTION, 
                            INGESTED_DATE,
                            DELETE_PENDING,
                            ENCODED_PASS, 
                            FRONT_FIELD_BUCKETS,
                            BACK_FIELD_BUCKETS
                            FROM PASS
                            ''')

            all_rows = cursor.fetchall()
    
            for row in all_rows:
                #typeID = row[2]
                
                agg = ''
                encoded_pass = get_plist_content(row[6]) or []
                for x in encoded_pass:
                    if isinstance(x, list):
                        for a in x:
                            agg = agg + f'{a}<br><br>'
                    elif isinstance(x, dict):
                        for y,z in x.items():
                            agg = agg + f'{y}: {z}<br><br>'
                    else:
                        agg = agg + f'{x}<br>'
                encoded_pass = agg + '<br>'
                
                agg = ''
                front_field = get_plist_content(row[7]) or []
                for x in front_field:
                    if isinstance(x, list):
                        for a in x:
                            agg = agg + f'{a}<br><br>'
                    elif isinstance(x, dict):
                        for y,z in x.items():
                            agg = agg + f'{y}: {z}<br><br>'
                    else:
                        agg = agg + f'{x}<br>'
                front_field = agg + '<br>'
                
                agg = ''
                back_field = get_plist_content(row[8]) or []
                for x in back_field:
                    if isinstance(x, list):
                        for a in x:
                            agg = agg + f'{a}<br><br>'
                    elif isinstance(x, dict):
                        for y,z in x.items():
                            agg = agg + f'{y}: {z}<br>'
                    else:
                        agg = agg + f'{x}<br>'
                        
                back_field = agg
                
                timestamp = convert_cocoa_core_data_ts_to_utc(row[4])
                
                data_list.append((timestamp, row[0], row[1], row[2], row[3], row[5], front_field, back_field, encoded_pass, context.get_relative_path(file_found)))
    
    data_headers = [('Pass Added', 'datetime'),'Unique ID', 'Organization Name', 'Type', 'Localized Description',
        'Pending Delete', 'Front Fields Content', 'Back Fields Content', 'Encoded Pass', 'Source File']
            
    return data_headers, data_list, 'see Source File for more info'
