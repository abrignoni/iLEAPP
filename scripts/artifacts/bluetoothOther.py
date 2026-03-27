__artifacts_v2__ = {
    "get_bluetoothOtherLE": {
        "name": "Bluetooth Other LE",
        "description": "",
        "author": "@JohnHyla",
        "creation_date": "2024-10-21",
        "last_update_date": "2025-11-03",
        "requirements": "none",
        "category": "Bluetooth",
        "notes": "",
        "paths": ('*/Library/Database/com.apple.MobileBluetooth.ledevices.other.db*'),
        "output_types": "standard"
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
                data_list.append((row[0], row[1], row[3], file_found))

            db.close()

    data_headers = ('Name','Address','UUID', 'Source File')

    return data_headers, data_list, 'see Source File for more info'


