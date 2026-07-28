__artifacts_v2__ = {
    "cachev0": {
        "name": "Image cacheV0",
        "description": "Images cached in the SQLite database.",
        "author": "@AlexisBrignoni",
        "creation_date": "2024-02-06",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "Image cacheV0",
        "notes": "",
        "paths": ('*/cacheV0.db*',),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.google.Drive, com.google.Gmail | 36 rows",
            "dexter_ios18": "iOS 18.3.2 | Gmail - Email by Google 6.0.250915 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | Google Docs 1.2026.23106, Google Drive 4.2615.41600 | 1 row",
            "iphone11_ios17": "iOS 17.3 | Google Chat 0.390, Google Voice 23.47, Gmail - Email by Google 6.0.231127 | 79 rows",
            "otto_ios17": "iOS 17.5.1 | Google Drive 4.2430.11801 | 11 rows",
            "iphone14plus_ios18": "iOS 18.0 | Google Sheets 1.2025.49102 | 0 rows",
            "abe_ios16": "iOS 16.5 | Google Drive 4.2023.24204, Google Photos 6.22.0 | 269 rows",
            "magnet_ios16": "iOS 16.1.1 | Google Docs: Sync, Edit, Share 1.2022.48202, Google Drive 4.2022.48200, Google Photos 6.17.0 | 5 rows",
        },
    }
}

from scripts.ilapfuncs import (
    open_sqlite_db_readonly,
    check_in_embedded_media,
    artifact_processor,
)

@artifact_processor
def cachev0(context):
    data_headers = ('ID', ('Media', 'media'), 'Source DB')
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        
        if file_found.endswith('cacheV0.db'):
            
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            id,
            data 
            FROM cache
            ''')
        
            all_rows = cursor.fetchall()
            
            for row in all_rows:
                media_ref = check_in_embedded_media(
                    file_found, row[1], str(row[0]))
                if media_ref:
                    data_list.append((row[0], media_ref, context.get_relative_path(file_found)))
            
    return data_headers, data_list, 'see Source File for more info'
