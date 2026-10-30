__artifacts_v2__ = {
    "get_bluetoothOtherLE": {
        "name": "Bluetooth Other LE",
        "description": "Parses Bluetooth Low Energy device records (name, address, UUID and raw LastSeenTime) from the OtherDevices table of com.apple.MobileBluetooth.ledevices.other.db, and the devices an earlier state of the database held and the current state does not.",
        "author": "@JohnHyla, @AlexisBrignoni, Codex",
        "creation_date": "2024-10-21",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "Bluetooth",
        "notes": "LastSeenTime is reported as stored without an assumed unit, epoch or timezone. "
                 "A record in OtherDevices does not by itself establish a Bluetooth connection "
                 "or a precisely timed encounter. Plain-text exports may serialize native SQLite "
                 "values; original database bytes remain separate evidence. "
                 "Record State is Current for a row of the database as SQLite reads it with its -wal, and Not in current state for a device (by UUID) that an earlier state holds and the current state does not: the database file before the log, a committed state of the log, or a left-over commit of the previous log generation. Each such device is listed once, with its values from the newest state holding it; a row with no UUID is compared by all its values. Read From names the first and last states holding it: the database file without its -wal, the log's committed states counted from its first commit, or a left-over commit of the previous log generation. Earlier versions of a current row are counted in the run log and not listed. Reading the log does not establish when or why a row left the current state. Of the 15 images listed, 13 have such rows, from 1 to 158 per image.",
        "paths": ('*/Library/Database/com.apple.MobileBluetooth.ledevices.other.db*'),
        "output_types": ["html","lava","tsv"],
        "artifact_icon": "bluetooth",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 50 rows",
            "dexter_ios18": "iOS 18.3.2 | 1054 rows",
            "felix_ios17": "iOS 17.6.1 | 1169 rows",
            "fsfull002_ios17": "iOS 17.1 | 1141 rows",
            "hc_ios18_7": "iOS 18.7.8 | 237 rows",
            "iphone11_ios17": "iOS 17.3 | 1115 rows",
            "iphone12_ios18": "iOS 18.7 | 132 rows",
            "iphone14plus_ios18": "iOS 18.0 | 39 rows",
            "otto_ios17": "iOS 17.5.1 | 1064 rows",
            "abe_ios16": "iOS 16.5 | 1063 rows",
            "felix23_ios16": "iOS 16.5 | 1061 rows",
            "hickman_ios13": "iOS 13.3.1 | 95 rows",
            "hickman_ios14": "iOS 14.3 | 125 rows",
            "jess_ios15": "iOS 15.0.2 | 1141 rows",
            "magnet_ios16": "iOS 16.1.1 | 1101 rows",
        }
    }
}

from scripts.bluetooth_le_wal import STATE_CURRENT, STATE_NOT_IN_CURRENT, rows_only_in_log
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

_QUERY = '''
SELECT
Name,
Address,
LastSeenTime,
Uuid
FROM
OtherDevices
order by Name desc, OtherDevices.rowid
'''

@artifact_processor
def get_bluetoothOtherLE(context):

    data_list = []
    source_paths = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('.db'):
            source_paths.add(file_found)
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute(_QUERY)

            all_rows = cursor.fetchall()

            for row in all_rows:
                data_list.append((row[2], row[0], row[1], row[3], STATE_CURRENT, '',
                                  context.get_relative_path(file_found)))

            db.close()

            for row, read_from in rows_only_in_log(file_found, _QUERY, 3, 'Bluetooth Other LE'):
                data_list.append((row[2], row[0], row[1], row[3], STATE_NOT_IN_CURRENT, read_from,
                                  context.get_relative_path(file_found)))

    data_headers = ('LastSeenTime (As Stored)', 'Name', 'Address', 'UUID', 'Record State', 'Read From',
                    'Source File')

    return data_headers, data_list, '\n'.join(sorted(source_paths))


