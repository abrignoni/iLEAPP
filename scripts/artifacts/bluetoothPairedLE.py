__artifacts_v2__ = {
    "get_bluetoothPairedLE": {
        "name": "Bluetooth Paired LE",
        "description": "Parses paired Bluetooth Low Energy devices, including name, address and the LastConnectionTime and LastSeenTime values as stored (not converted to dates), from com.apple.MobileBluetooth.ledevices.paired.db, and the devices an earlier state of the database held and the current state does not.",
        "author": "@JohnHyla, @AlexisBrignoni, Codex",
        "creation_date": "2024-10-21",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "Bluetooth",
        "notes": "Record State is Current for a row of the database as SQLite reads it with its -wal, and Not in current state for a device (by UUID) that an earlier state holds and the current state does not: the database file before the log, a committed state of the log, or a left-over commit of the previous log generation. Each such device is listed once, with its values from the newest state holding it; a row with no UUID is compared by all its values. Read From names the first and last states holding it: the database file without its -wal, the log's committed states counted from its first commit, or a left-over commit of the previous log generation. Earlier versions of a current row are counted in the run log and not listed. Reading the log does not establish when or why a row left the current state. Of the 15 images listed, 3 have such a row, one each.",
        "paths": ('*/com.apple.MobileBluetooth.ledevices.paired.db*'),
        "output_types": ["html","lava","tsv"],
        "artifact_icon": "bluetooth-connected",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 3 rows",
            "abe_ios16": "iOS 16.5 | 3 rows",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 5 rows",
            "hickman_ios14": "iOS 14.3 | 3 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
        }
    }
}

from scripts.bluetooth_le_wal import STATE_CURRENT, STATE_NOT_IN_CURRENT, rows_only_in_log
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

_QUERY = '''
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
'''

@artifact_processor
def get_bluetoothPairedLE(context):

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
                data_list.append((row[6], row[5], row[0], row[1], row[2], row[3], row[4], STATE_CURRENT, '',
                                  context.get_relative_path(file_found)))

            db.close()

            for row, read_from in rows_only_in_log(file_found, _QUERY, 0, 'Bluetooth Paired LE'):
                data_list.append((row[6], row[5], row[0], row[1], row[2], row[3], row[4], STATE_NOT_IN_CURRENT,
                                  read_from, context.get_relative_path(file_found)))

    data_headers = ('LastConnectionTime (as stored)', 'LastSeenTime (as stored)',
                    'UUID', 'Name', 'Name Origin', 'Address', 'Resolved Address', 'Record State', 'Read From',
                    'Source File')

    return data_headers, data_list, '\n'.join(sorted(source_paths))

