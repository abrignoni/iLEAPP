__artifacts_v2__ = {
    "get_bluetoothPairedLE": {
        "name": "Bluetooth Paired LE",
        "description": "",
        "author": "@JohnHyla",
        "creation_date": "2024-10-21",
        "last_update_date": "2024-10-21",
        "requirements": "none",
        "category": "Bluetooth",
        "notes": "",
        "paths": ('*/com.apple.MobileBluetooth.ledevices.paired.db'),
        "output_types": "standard"
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
                data_list.append((row[0], row[1], row[2], row[3], row[4],row[6], file_found))

            db.close()

    data_headers = ('UUID','Name','Name Origin','Address','Resolved Address','Last Connection Time', 'Source File')

    return data_headers, data_list, ''

