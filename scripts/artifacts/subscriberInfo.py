# pylint: disable=W0613
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
        "artifact_icon": "settings",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 3 rows",
            "fsfull002_ios17": "iOS 17.1 | 3 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
        }
    }
}


from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, convert_cocoa_core_data_ts_to_utc, device_info

@artifact_processor
def subscriberInfo(context):
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

    for file_found in context.get_files_found():
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
