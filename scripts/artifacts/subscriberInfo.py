__artifacts_v2__ = {
    "subscriberInfo": {
        "name": "Subscriber Info",
        "description": "Information about inserted SIM Cards",
        "author": "@Johann-PLW",
        "version": "0.1",
        "date": "2024-11-19",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/wireless/Library/Databases/CellularUsage.db*',),
        "output_types": "standard",
        "artifact_icon": "settings"
    }
}


from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_ts_human_to_timezone_offset, device_info

@artifact_processor
def subscriberInfo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    db_file = ''

    for file_found in files_found:
        if file_found.endswith('CellularUsage.db'):
            db_file = file_found
            break
    
    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            datetime(last_update_time+978307200,'unixepoch'),
            slot_id,
            subscriber_id,
            subscriber_mdn
        FROM subscriber_info
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            last_update_time = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            data_list.append((last_update_time, row[1], row[2], row[3]))
            device_info("Cellular", "SIM Cards", f"Slot {row[1]} -> ICCID: {row[2]} | MSISDN: {row[3]} | Last Update: {last_update_time}", db_file)

    data_headers = (
        ('Last update time', 'datetime'),
        'Slot ID',
        'ICCID', 
        'MSISDN', 
        )
    return data_headers, data_list, db_file
