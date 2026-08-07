__artifacts_v2__ = {
    "AMDSQLiteDB_UsageEvents": {
        "name": "App Usage Events (AMDSQLiteDB)",
        "description": "Apple App Store application foreground events",
        "author": "@stark4n6",
        "creation_date": "2025-07-21",
        "last_update_date": "2026-08-04",
        "requirements": "none",
        "category": "App Usage",
        "notes": "App names, bundle IDs and vendors are resolved from the extraction itself: "
                 "storeUser.db current_apps (installed apps) and purchase_history_apps (the "
                 "account's purchase history, which retains uninstalled apps). Events whose "
                 "adamId appears in neither table are labeled Unknown. Earlier versions queried "
                 "itunes.apple.com per adamId; the online lookup was removed so processing stays "
                 "offline. Reference: Kevin Pagano, 'iOS App Storage Usage via AMDSQLite.db', "
                 "https://www.stark4n6.com/2025/07/ios-app-storage-usage-via-amdsqlite-db.html",
        "paths": (
            '*/mobile/Containers/Data/PluginKitPlugin/*/Documents/AMDSQLite.db.0*',
            '*/mobile/Library/Caches/com.apple.appstored/storeUser.db*'
            ),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 1343 rows",
            "felix_ios17": "iOS 17.6.1 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 475 rows",
            "fsfull002_ios17": "iOS 17.1 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 294 rows",
            "hc_ios18_7": "iOS 18.7.8 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 484 rows",
            "iphone11_ios17": "iOS 17.3 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 1891 rows",
            "iphone12_ios18": "iOS 18.7 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 413 rows",
            "iphone14plus_ios18": "iOS 18.0 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 21 rows",
            "otto_ios17": "iOS 17.5.1 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 3064 rows",
            "abe_ios16": "iOS 16.5 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 6065 rows",
            "felix23_ios16": "iOS 16.5 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 1119 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 167 rows",
        }
    },
    "AMDSQLiteDB_StorageCapacity": {
        "name": "Device Storage Capacity",
        "description": "Shows storage capacity size over time",
        "author": "@stark4n6",
        "creation_date": "2025-07-21",
        "last_update_date": "2025-10-08",
        "requirements": "none",
        "category": "Device Information",
        "notes": "",
        "paths": (
            '*/mobile/Containers/Data/PluginKitPlugin/*/Documents/AMDSQLite.db.0*'
            ),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 0 rows",
            "felix_ios17": "iOS 17.6.1 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 13 rows",
            "fsfull002_ios17": "iOS 17.1 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 17 rows",
            "hc_ios18_7": "iOS 18.7.8 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 0 rows",
            "iphone11_ios17": "iOS 17.3 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 36 rows",
            "iphone12_ios18": "iOS 18.7 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 0 rows",
            "otto_ios17": "iOS 17.5.1 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 49 rows",
            "abe_ios16": "iOS 16.5 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 15 rows",
            "felix23_ios16": "iOS 16.5 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 20 rows",
            "magnet_ios16": "iOS 16.1.1 | com.apple.AppleMediaDiscovery.AMDEngagementExtension | 2 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, \
    attach_sqlite_db_readonly, does_table_exist_in_db, logfunc, convert_unix_ts_to_utc

def get_purchase_history(store_user_db):
    """Map adamId -> (title, bundle_id, developer_name) from purchase_history_apps.

    The account's purchase history covers apps that were uninstalled and are no
    longer in current_apps, so usage events for removed apps can still be named
    from the extraction itself. The table is absent in some older storeUser.db
    schemas, hence the existence check.
    """
    history = {}
    if not store_user_db or not does_table_exist_in_db(store_user_db, 'purchase_history_apps'):
        return history
    query = '''
    select
    store_item_id,
    title,
    bundle_id,
    developer_name
    from purchase_history_apps
    '''
    for row in get_sqlite_db_records(store_user_db, query):
        if row[0] is not None and row[0] not in history:
            history[row[0]] = (row[1], row[2], row[3])
    return history

@artifact_processor
def AMDSQLiteDB_UsageEvents(context):
    data_list = []
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "AMDSQLite.db.0")

    storeUserDB = get_file_path(files_found, "storeUser.db")
    purchase_history = get_purchase_history(storeUserDB)
    
    if storeUserDB:
        logfunc("storeUser.db found. Running combined database query.")
        attach_query = attach_sqlite_db_readonly(storeUserDB, 'storeUser')
        query = '''
        select
        AMDAppStoreUsageEvents.time,
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
        AMDAppStoreUsageEvents.userId,
        storeUser.current_apps.item_name,
        storeUser.current_apps.vendor_name
        from AMDAppStoreUsageEvents
        left join storeUser.current_apps on AMDAppStoreUsageEvents.adamId = storeUser.current_apps.item_id
        left join storeUser.account_events on AMDAppStoreUsageEvents.userId = storeUser.account_events.account_id
        '''
        db_records = get_sqlite_db_records(source_path, query, attach_query)
    else:
        logfunc("storeUser.db NOT found. Adjusting query to skip storeUser database references.")
        query = '''
        select
        AMDAppStoreUsageEvents.time,
        case AMDAppStoreUsageEvents.type
            when "0" then "Install/Update"
            when "1" then "Uninstall"
            when "2" then "Open"
            else AMDAppStoreUsageEvents.type
        end as "App Action",
        NULL as bundle_id,
        AMDAppStoreUsageEvents.adamId,
        AMDAppStoreUsageEvents.appVersion,
        AMDAppStoreUsageEvents.foregroundDuration,
        NULL as apple_id,
        AMDAppStoreUsageEvents.userId,
        NULL as item_name,
        NULL as vendor_name
        from AMDAppStoreUsageEvents
        '''
        db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        time = convert_unix_ts_to_utc(record[0])

        local_bundle_id = record[2]
        adam_id = record[3]
        local_item_name = record[8]
        local_vendor_name = record[9]

        # Resolve name/bundle/vendor from the extraction only: current_apps
        # first (installed apps), then the account's purchase history
        # (uninstalled apps). Values recorded on the device at the time of the
        # events beat a live store lookup, whose listings can be renamed or
        # delisted after the fact.
        history_title, history_bundle_id, history_vendor = purchase_history.get(
            adam_id, (None, None, None))

        final_bundle_id = local_bundle_id or history_bundle_id or ''
        final_vendor_name = local_vendor_name or history_vendor or ''

        if local_item_name:
            final_app_name = local_item_name
        elif history_title:
            final_app_name = history_title
        else:
            final_app_name = f"Unknown ({final_bundle_id or adam_id})"

        data_list.append((time, record[1], final_app_name, final_bundle_id, record[3], record[4], final_vendor_name, record[5], record[6], record[7]))
                            
    data_headers = (('Timestamp', 'datetime'),'App Action','App Name','Bundle ID','AdamID','App Version','Vendor Name','Foreground Duration (as stored)','Apple ID','User ID')
    return data_headers, data_list, source_path
    
@artifact_processor
def AMDSQLiteDB_StorageCapacity(context):
    data_list = []
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "AMDSQLite.db.0")
    
    query = '''
    select
    time,
    availableDeviceCapacityGB,
    totalDeviceCapacityGB
    from DeviceStorageUsage
    '''

    db_records = get_sqlite_db_records(source_path, query)
    for record in db_records:
        time = convert_unix_ts_to_utc(record[0])
        data_list.append((time, record[1], record[2]))
                            
    data_headers = (('Timestamp', 'datetime'),'Available Capacity (GB)','Total Capacity (GB)')
    return data_headers, data_list, source_path