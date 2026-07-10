__artifacts_v2__ = {
    "get_bluetoothOtherLE": {
        "name": "Bluetooth Other LE",
        "description": "Parses non-paired (other) Bluetooth Low Energy devices seen by the device from com.apple.MobileBluetooth.ledevices.other.db.",
        "author": "@JohnHyla",
        "creation_date": "2024-10-21",
        "last_update_date": "2025-11-03",
        "requirements": "none",
        "category": "Bluetooth",
        "notes": "",
        "paths": ('*/Library/Database/com.apple.MobileBluetooth.ledevices.other.db*'),
        "output_types": "standard",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 50 rows",
            "dexter_ios18": "iOS 18.3.2 | 1003 rows",
            "felix_ios17": "iOS 17.6.1 | 1011 rows",
            "fsfull002_ios17": "iOS 17.1 | 1013 rows",
            "hc_ios18_7": "iOS 18.7.8 | 237 rows",
            "iphone11_ios17": "iOS 17.3 | 1056 rows",
            "iphone12_ios18": "iOS 18.7 | 131 rows",
            "iphone14plus_ios18": "iOS 18.0 | 38 rows",
            "otto_ios17": "iOS 17.5.1 | 1021 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

@artifact_processor
def get_bluetoothOtherLE(context):

    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute(
            """
            SELECT
            Name,
            Address,
            LastSeenTime,
            Uuid
            FROM
            OtherDevices
            order by Name desc
            """)

            all_rows = cursor.fetchall()

            for row in all_rows:
                data_list.append((row[0], row[1], row[3], context.get_relative_path(file_found)))

            db.close()

    data_headers = ('Name','Address','UUID', 'Source File')

    return data_headers, data_list, 'see Source File for more info'


