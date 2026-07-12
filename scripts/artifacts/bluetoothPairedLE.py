__artifacts_v2__ = {
    "get_bluetoothPairedLE": {
        "name": "Bluetooth Paired LE",
        "description": "Parses paired Bluetooth Low Energy devices, including name, address and last connection time, from com.apple.MobileBluetooth.ledevices.paired.db.",
        "author": "@JohnHyla",
        "creation_date": "2024-10-21",
        "last_update_date": "2025-11-03",
        "requirements": "none",
        "category": "Bluetooth",
        "notes": "",
        "paths": ('*/com.apple.MobileBluetooth.ledevices.paired.db*'),
        "output_types": "standard",
        "artifact_icon": "bluetooth-connected",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 2 rows",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 5 rows",
            "hickman_ios14": "iOS 14.3 | 3 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

@artifact_processor
def get_bluetoothPairedLE(context):

    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute("""
            select 
            Uuid,
            Name,
            NameOrigin,
            Address,
            ResolvedAddress,
            LastSeenTime,
            LastConnectionTime
            from 
            PairedDevices
            """)

            all_rows = cursor.fetchall()
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4],row[6], context.get_relative_path(file_found)))

            db.close()

    data_headers = ('UUID','Name','Name Origin','Address','Resolved Address','Last Connection Time', 'Source File')

    return data_headers, data_list, 'see Source File for more info'

