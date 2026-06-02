__artifacts_v2__ = {
    "cachev0": {
        "name": "Image cacheV0",
        "description": "Images cached in the SQLite database.",
        "author": "@AlexisBrignoni",
        "creation_date": "2024-02-06",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Image cacheV0",
        "notes": "",
        "paths": ('*/cacheV0.db*',),
        "output_types": "standard",
    }
}

from scripts.ilapfuncs import (
    open_sqlite_db_readonly,
    check_in_embedded_media,
    artifact_processor,
)

@artifact_processor
def cachev0(context):
    
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
                    data_list.append((row[0], media_ref, file_found))
            
    if not data_list:
        return

    data_headers = ('ID', ('Media', 'media'), 'Source DB')
    return data_headers, data_list, 'see Source File for more info'
