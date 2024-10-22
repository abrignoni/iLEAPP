__artifacts_v2__ = {
    "get_bluetoothPairedLE": {
        "name": "Bluetooth Paired LE",
        "description": "",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-21",
        "requirements": "none",
        "category": "Bluetooth",
        "notes": "",
        "paths": ('**/com.apple.MobileBluetooth.ledevices.paired.db'),
        "output_types": "standard"
    }
}

from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly

@artifact_processor
def get_bluetoothPairedLE(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.db'):
            report_file = file_found
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
                data_list.append((row[0], row[1], row[2], row[3], row[4],row[6]))

            db.close()

    data_headers = ('UUID','Name','Name Origin','Address','Resolved Address','Last Connection Time')

    return data_headers, data_list, report_file

