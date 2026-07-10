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
        "output_types": "none",
        "artifact_icon": "hash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | files found",
            "dexter_ios18": "iOS 18.3.2 | files found",
            "felix_ios17": "iOS 17.6.1 | files found",
            "fsfull002_ios17": "iOS 17.1 | files found",
            "hc_ios18_7": "iOS 18.7.8 | files found",
            "iphone11_ios17": "iOS 17.3 | files found",
            "iphone12_ios18": "iOS 18.7 | files found",
            "iphone14plus_ios18": "iOS 18.0 | files found",
            "otto_ios17": "iOS 17.5.1 | files found",
        }
    }
}


from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, device_info

@artifact_processor
def serialNumber(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    db_file = ''

    for file_found in files_found:
        if file_found.endswith('consolidated.db'):
            db_file = file_found
            break
    
    with open_sqlite_db_readonly(db_file) as db:
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
