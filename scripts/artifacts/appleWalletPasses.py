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
        "output_types": "standard"
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
        "output_types": "standard"
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
            with open(file_found, 'r') as f:
                data = json.load(f)
                for x, y in data.items():
                    data_list.append((x,str(y), file_found))
    
    data_headers = ['Identidicator','Data Value', 'Source File']
            
    return data_list, data_headers, 'see Source File for more info'
        
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
                encoded_pass = get_plist_content(row[6])
                for x in encoded_pass:
                    if isinstance(x, list):
                        for a in x:
                            agg = agg + f'{a}<br><br>'
                    elif isinstance(x, dict):
                        for y,z in x.items():
                            agg = agg + f'{y}: {z}<br><br>'
                    else:
                        agg = agg + f'{x}<br>'
                encoded_pass = agg + f'<br>'
                
                agg = ''
                front_field = get_plist_content(row[7])
                for x in front_field:
                    if isinstance(x, list):
                        for a in x:
                            agg = agg + f'{a}<br><br>'
                    elif isinstance(x, dict):
                        for y,z in x.items():
                            agg = agg + f'{y}: {z}<br><br>'
                    else:
                        agg = agg + f'{x}<br>'
                front_field = agg + f'<br>'
                
                agg = ''
                back_field = get_plist_content(row[8])
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
                
                data_list.append((timestamp, row[0], row[1], row[2], row[3], row[5], front_field, back_field, encoded_pass, file_found))
    
    data_headers = [('Pass Added', 'datetime'),'Unique ID', 'Organization Name', 'Type', 'Localized Description',
        'Pending Delete', 'Front Fields Content', 'Back Fields Content', 'Encoded Pass', 'Source File']
            
    return data_headers, data_list, 'see Source File for more info'
