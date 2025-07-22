__artifacts_v2__ = {
    "AMDSQLiteDB_UsageEvents": {
        "name": "App Usage Events (AMDSQLiteDB)",
        "description": "Apple App Store application foreground events",
        "author": "@stark4n6",
        "date": "2025-07-21",
        "requirements": "none",
        "category": "App Usage",
        "notes": "",
        "paths": (
            '*/mobile/Containers/Data/PluginKitPlugin/*/Documents/AMDSQLite.db.0*',
            '*/mobile/Library/Caches/com.apple.appstored/storeUser.db*'
            ),
        "output_types": "standard",
        'artifact_icon': 'activity'
    },
    "AMDSQLiteDB_StorageCapacity": {
        "name": "Device Storage Capacity",
        "description": "Shows storage capacity size over time",
        "author": "@stark4n6",
        "date": "2025-07-21",
        "requirements": "none",
        "category": "Device Information",
        "notes": "",
        "paths": (
            '*/mobile/Containers/Data/PluginKitPlugin/*/Documents/AMDSQLite.db.0*'
            ),
        "output_types": "standard",
        'artifact_icon': 'hard-drive'
    }
}

import urllib.request
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, attach_sqlite_db_readonly, logfunc

def get_data_from_itunes(lookup_value, lookup_type):
    response_json_data = None
    base_url = "http://itunes.apple.com/lookup?"
    
    if lookup_type == "adamId":
        url = f"{base_url}id={lookup_value}"
    elif lookup_type == "bundleId":
        url = f"{base_url}bundleId={lookup_value}"
    else:
        return f"ERROR: Invalid lookup type '{lookup_type}'. Must be 'adamId' or 'bundleId'.", None

    try:
        with urllib.request.urlopen(url) as response:
            response_data = response.read()
            response_json_data = json.loads(response_data)
    except Exception as e:
        return f"\nERROR fetching data for {lookup_value} ({lookup_type})", None
    return None, response_json_data

def process_ids(item_record, data_dictionary, lookup_type):
    if item_record not in data_dictionary:
        error, result = get_data_from_itunes(item_record, lookup_type)
        if error:
            logfunc(error)
            data_dictionary[item_record] = ''
        else:
            data_dictionary[item_record] = result
    return data_dictionary

def results_for_id(item_record, data_dictionary):    
    if item_record in data_dictionary:
        app_name = bundle_name = ''
        data = data_dictionary[item_record]
        if data and data.get('resultCount', 0) > 0:
            if 'trackName' in data['results'][0]:
                app_name = data['results'][0].get('trackName','')
                bundle_name = data['results'][0].get('bundleId','')
                return app_name, bundle_name
        else:
            return app_name, bundle_name

@artifact_processor
def AMDSQLiteDB_UsageEvents(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    my_data_store = {}
    
    source_path = get_file_path(files_found, "AMDSQLite.db.0")
    
    storeUserDB = get_file_path(files_found, "storeUser.db")
    attach_query = attach_sqlite_db_readonly(storeUserDB, 'storeUser')
    
    query = '''
    select
    datetime(AMDAppStoreUsageEvents.time/1000,'unixepoch') as "Timestamp",
    case AMDAppStoreUsageEvents.type
        when "0" then "Install/Update"
        when "1" then "Uninstall"
        when "2" then "Open"
        else AMDAppStoreUsageEvents.type
    end as "App Action",
    storeUser.current_apps.bundle_id,
    AMDAppStoreUsageEvents.adamId,
    AMDAppStoreUsageEvents.appVersion,
    AMDAppStoreUsageEvents.foregroundDuration,
    storeUser.account_events.apple_id,
    AMDAppStoreUsageEvents.userId
    from AMDAppStoreUsageEvents
    left join storeUser.current_apps on AMDAppStoreUsageEvents.adamId = storeUser.current_apps.item_id
    left join storeUser.account_events on AMDAppStoreUsageEvents.userId = storeUser.account_events.account_id
    '''

    db_records = get_sqlite_db_records(source_path, query, attach_query)
    for record in db_records:
        app_name, bundle_name = results_for_id(record[3], process_ids(record[3], my_data_store, 'adamId'))
        data_list.append((record[0], record[1], app_name, record[2], record[3], record[4], record[5], record[6], record[7]))
                            
    data_headers = (('Timestamp', 'datetime'),'App Action','App Name','Bundle ID','AdamID','App Version','Foreground Duration (Secs)','Apple ID','User ID')
    return data_headers, data_list, source_path
    
@artifact_processor
def AMDSQLiteDB_StorageCapacity(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = get_file_path(files_found, "AMDSQLite.db.0")
    
    query = '''
    select
    datetime(time/1000,'unixepoch'),
    availableDeviceCapacityGB,
    totalDeviceCapacityGB
    from DeviceStorageUsage
    '''

    db_records = get_sqlite_db_records(source_path, query)
    for record in db_records:
        data_list.append((record[0], record[1], record[2]))
                            
    data_headers = (('Timestamp', 'datetime'),'Available Capacity (GB)','Total Capacity (GB)')
    return data_headers, data_list, source_path