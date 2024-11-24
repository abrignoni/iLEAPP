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


from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc, device_info

@artifact_processor
def subscriberInfo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    db_file = ''
    db_records = []

    query = '''
    SELECT
        last_update_time,
        slot_id,
        subscriber_id,
        subscriber_mdn
    FROM subscriber_info
    '''

    for file_found in files_found:
        if file_found.endswith('CellularUsage.db'):
            db_file = file_found
            db_records = get_sqlite_db_records(db_file, query)
            break

    for record in db_records:
        last_update_time = convert_cocoa_core_data_ts_to_utc(record[0])
        data_list.append((last_update_time, record[1], record[2], record[3]))
        device_info("Cellular", "SIM Cards", f"Slot {record[1]} -> ICCID: {record[2]} | MSISDN: {record[3]} | Last Update: {last_update_time}", db_file)

    data_headers = (
        ('Last update time', 'datetime'),
        'Slot ID',
        'ICCID', 
        'MSISDN', 
        )
    
    return data_headers, data_list, db_file
