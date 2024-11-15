__artifacts_v2__ = {
    "serialNumber": {
        "name": "Serial Number",
        "description": "Serial Number of the device",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2023-09-30",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/Library/Caches/locationd/consolidated.db*'),
        "output_types": "none"
    }
}


from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, device_info

@artifact_processor
def serialNumber(files_found, report_folder, seeker, wrap_text, timezone_offset):
    db_file = ''

    for file_found in files_found:
        if file_found.endswith('consolidated.db'):
            db_file = file_found
            break
    
    with open_sqlite_db_readonly(file_found) as db:
        cursor = db.cursor()
        
        cursor.execute('''
        SELECT DISTINCT SerialNumber
        FROM TableInfo
        ''')
        
        all_rows = cursor.fetchall()

        for row in all_rows:
            device_info("Device Information", "Serial Number", row[0], db_file)
                
    # Return empty data since this artifact only collects device info
    return (), [], db_file
