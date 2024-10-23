__artifacts_v2__ = {
    "get_biomeSync": {
        "name": "Biome Sync - Devices",
        "description": "Parses Biome Device Sync records",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-17",
        "requirements": "none",
        "category": "Biome Sync",
        "notes": "",
        "paths": ('**/Biome/sync/sync.db*'),
        "output_types": "standard"
    }
}


from scripts.builds_ids import OS_build
from scripts.ilapfuncs import open_sqlite_db_readonly, convert_ts_human_to_utc
from scripts.ilapfuncs import artifact_processor, convert_utc_human_to_timezone

@artifact_processor
def get_biomeSync(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_list = []
    report_file = 'Unknown'
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.db'):
            continue # Skip all other files
        report_file = file_found
        db = open_sqlite_db_readonly(file_found)

        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(last_sync_date,'unixepoch'),
        device_identifier,
        name,
        case platform
            when 1 then 'iPad'
            when 2 then 'iPhone'
            when 4 then 'macOS'
            when 6 then 'watchOS'
            else 'Unknown'
        end,
        model,
        case me
            when 0 then ''
            when 1 then 'Yes'
        end as 'Local Device'
        from DevicePeer
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            if row[0] == ' ':
                timestamp = ''
            elif row[0] is None:
                timestamp = row[0]
            else:
                timestamp = row[0]
                timestamp = convert_ts_human_to_utc(timestamp)
                timestamp = convert_utc_human_to_timezone(timestamp, timezone_offset)

            os_build = 'Unknown'
            for key, value in OS_build.items():
                if str(row[4]) == key:
                    os_build = value
                    break

            data_list.append((timestamp, row[1], row[2], row[3], row[4], os_build, row[5]))

        db.close()

    data_headers = (('Last Sync Timestamp', 'datetime'), 'Device ID', 'Name', 'Device Type', 'OS Build', 'OS Version', 'Local Device')

    return data_headers, data_list, report_file
