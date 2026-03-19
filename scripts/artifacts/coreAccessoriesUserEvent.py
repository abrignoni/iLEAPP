# Core Accessories - UserEventAgent
# Author:  John Hyla
# Version: 1.0.0
#
#   Description:
#   Parses records found in the plists located in the UserEventAgent database found in CoreAccessories
#

__artifacts_v2__ = {
    "get_coreAccessoriesUserEvent": {
        "name": "Core Accessories - UserEventAgent",
        "description": "Parses records found in the plists located in the UserEventAgent \
            database found in CoreAccessories",
        "author": "John Hyla",
        "creation_date": "2023-08-01",
        "last_update_date": "2025-10-01",
        "requirements": "none",
        "category": "Core Accessories",
        "notes": "",
        "paths": ('*/mobile/Library/CoreAccessories/Analytics/acc_analytics_UserEventAgent_v3.db*',),
        "output_types": "standard",
    }
}

from scripts.ilapfuncs import open_sqlite_db_readonly, artifact_processor, get_plist_content, convert_unix_ts_to_utc

@artifact_processor
def get_coreAccessoriesUserEvent(context):

    for file_found in context.get_files_found():
        file_name = str(file_found)
        if file_name.endswith('acc_analytics_UserEventAgent_v3.db'):
            db_file = str(file_found)
            break
    

    db = open_sqlite_db_readonly(db_file)

    cursor = db.cursor()
    cursor.execute('''
        SELECT
        data from all_events
        ''')

    all_rows = cursor.fetchall()

    # Initialize the list to store dictionaries from each iteration
    temp_data = []

    # Set to store all possible keys found during iterations
    all_keys = set()
    event_time_key = 'eventTime'
    for row in all_rows:
        pl = get_plist_content(row[0])
        temp_data.append(pl)
        all_keys.update(pl.keys())

    all_keys.remove(event_time_key)
    all_keys_list = [event_time_key] + list(all_keys)
    data_list = []
    for row in temp_data:
        row_values = []
        for key in all_keys_list:
            if key == event_time_key:
                event_time_value = row.get(event_time_key, None)
                event_time_value = convert_unix_ts_to_utc(event_time_value)
                row_values.append(event_time_value)
            elif key == "lightningDigitalID":
                value = row.get(key, None)
                if value.upper() == "100C00000000":
                    value = value + ' (Official Normal Cable)'
                elif value.upper() == "10C000000000":
                    value = value + ' (MFi Certified Common Cable)'
                elif value.upper() == "101908000000":
                    value = value + ' (Official Quick Charge Cable)'
                elif value.upper() == "100908000000":
                    value = value + ' (MFi Certified Quick Charge Cable)'
                elif value.upper() == "04F100000000":
                    value = value + ' (Audio Cable)'
                elif value.upper() == "0BF000000000":
                    value = value + ' (Official to HDMI Cable)'
                elif value.upper() == "100100000000":
                    value = value + ' (Research, non official maybe?)'
                row_values.append(value)
            else:
                row_values.append(row.get(key, None))
        data_list.append(row_values)
        
    all_keys_list[0] = (all_keys_list[0], 'datetime')


    return all_keys_list, data_list, db_file
