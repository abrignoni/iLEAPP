""" This module contains artifacts related to the Files app and iCloud Drive. """

__artifacts_v2__ = {
    "icloud_sync_device_names": {
        "name": "Files App - iCloud Sync Device Names",
        "description": "Device names recorded in the CloudDocs server.db devices table",
        "author": "@JohannPLW",
        "creation_date": "2024-02-05",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": (
            '*/mobile/Library/Application Support/CloudDocs/session/db/server.db*',
            ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-mobile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 4 rows",
            "abe_ios16": "iOS 16.5 | 3 rows",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 3 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
        }
    },
    "icloud_application_list": {
        "name": "Files App - iCloud Application List",
        "description": "Rows of the app_libraries table in the CloudDocs client.db",
        "author": "@JohannPLW",
        "creation_date": "2024-02-02",
        "last_update_date": "2026-10-10",
        "requirements": "none",
        "category": "Files App",
        "notes": "Application Bundle ID is app_library_name. Below iOS 18, Number of files is "
                 "auto_document_count, Number of folders is auto_client_item_count minus "
                 "auto_document_count and Total size in bytes is auto_aggregate_size; what the "
                 "system counts in each is not established. On iOS 18 and later only the library "
                 "name is reported. Nothing is reported when no iOS version has been read.",
        "paths": (
            '*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',
            ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 12 rows",
            "dexter_ios18": "iOS 18.3.2 | 34 rows",
            "felix_ios17": "iOS 17.6.1 | 36 rows",
            "fsfull002_ios17": "iOS 17.1 | 35 rows",
            "hc_ios18_7": "iOS 18.7.8 | 31 rows",
            "iphone11_ios17": "iOS 17.3 | 43 rows",
            "iphone12_ios18": "iOS 18.7 | 44 rows",
            "iphone14plus_ios18": "iOS 18.0 | 28 rows",
            "otto_ios17": "iOS 17.5.1 | 32 rows",
            "abe_ios16": "iOS 16.5 | 28 rows",
            "felix23_ios16": "iOS 16.5 | 24 rows",
            "hickman_ios13": "iOS 13.3.1 | 23 rows",
            "hickman_ios14": "iOS 14.3 | 30 rows",
            "jess_ios15": "iOS 15.0.2 | 15 rows",
            "magnet_ios16": "iOS 16.1.1 | 21 rows",
        }
    },
    "icloud_drive_stored_files": {
        "name": "Files App - Files stored in iCloud Drive",
        "description": "Items (files and folders) listed in the client_items table of the "
                       "CloudDocs client.db, with their stored times, size and library",
        "author": "@JohannPLW",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-09-30",
        "requirements": "none",
        "category": "Files App",
        "notes": "Every client_items row is reported. A row shows the item is listed in the "
                 "device's CloudDocs database; it does not by itself show where the file's content "
                 "is held. A row whose size is not an integer is treated as a folder: its name is "
                 "added to Path and Filename is left blank. Created, Modified and Last opened are "
                 "item_birthtime, version_mtime and item_lastusedtime converted from Unix time to "
                 "UTC; values of 0 or below are left blank. Shared? reads Yes when "
                 "item_sharing_options is above 4, a threshold with no cited source. Recently "
                 "Deleted reads Yes when item_trash_put_back_path holds a value. From Device Name "
                 "is the server.db devices name for version_device.",
        "paths": (
            '*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',
            '*/mobile/Library/Application Support/CloudDocs/session/db/server.db*',
            ),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 30 rows",
            "dexter_ios18": "iOS 18.3.2 | 55 rows",
            "felix_ios17": "iOS 17.6.1 | 63 rows",
            "fsfull002_ios17": "iOS 17.1 | 40 rows",
            "hc_ios18_7": "iOS 18.7.8 | 31 rows",
            "iphone11_ios17": "iOS 17.3 | 99 rows",
            "iphone12_ios18": "iOS 18.7 | 54 rows",
            "iphone14plus_ios18": "iOS 18.0 | 39 rows",
            "otto_ios17": "iOS 17.5.1 | 56 rows",
            "abe_ios16": "iOS 16.5 | 67 rows",
            "felix23_ios16": "iOS 16.5 | 50 rows",
            "hickman_ios13": "iOS 13.3.1 | 38 rows",
            "hickman_ios14": "iOS 14.3 | 74 rows",
            "jess_ios15": "iOS 15.0.2 | 15 rows",
            "magnet_ios16": "iOS 16.1.1 | 27 rows",
        }
    },
    "icloud_drive_shared_files": {
        "name": "Files App - Shared files stored in iCloud Drive",
        "description": "Shared files stored in iCloud Drive with their metadata",
        "author": "@JohannPLW",
        "creation_date": "2024-02-02",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Files App",
        "notes": "A row is reported when item_sharing_options is above 4; that threshold and "
                 "the Permissions labels assigned to values 8 and 12, 24 and 28, and 64 and 68 "
                 "have no vendor source, and other values are reported as stored. Shared by is "
                 "the name decoded from the server.db users row for item_creator_id, or 'an "
                 "unknown user' where no name decodes. Where the item has no creator id the "
                 "column reads 'local account (no creator ID)'; that wording is this report's "
                 "and who shared the item is not established for those rows.",
        "paths": (
            '*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',
            '*/mobile/Library/Application Support/CloudDocs/session/db/server.db*',
            ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "share",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "icloud_drive_tagged_files": {
        "name": "Files App - Tagged files",
        "description": "Tagged files in iCloud Drive with their metadata",
        "author": "@JohannPLW",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-09-30",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": (
            '*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',
            '*/mobile/Library/Application Support/CloudDocs/session/db/server.db*',
            ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "tag",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "icloud_drive_favourite_files": {
        "name": "Files App - Favourite files",
        "description": "Favourite files in iCloud Drive with their metadata",
        "author": "@JohannPLW",
        "creation_date": "2024-02-02",
        "last_update_date": "2025-09-30",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": (
            '*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',
            '*/mobile/Library/Application Support/CloudDocs/session/db/server.db*',
            ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "star",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "files_ios_updates": {
        "name": "Files App - OS Build History (boot_history)",
        "description": "OS builds and dates recorded in the CloudDocs client.db boot_history table",
        "author": "@JohannPLW",
        "creation_date": "2024-02-02",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Files App",
        "notes": "",
        "paths": (
            '*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',
            ),
        "output_types": "standard",
        "artifact_icon": "refresh",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 3 rows",
            "fsfull002_ios17": "iOS 17.1 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
            "abe_ios16": "iOS 16.5 | 3 rows",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
        }
    },
    "icloud_drive_server_files": {
        "name": "Files App - iCloud Drive server files",
        "description": "Rows of the server_items table of the CloudDocs server.db, with the stored times, size, zone "
                       "name and the device name matched on version_device.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-12",
        "last_update_date": "2026-11-12",
        "requirements": "none",
        "category": "Files App",
        "notes": (
                 "Source is the server_items table of the CloudDocs server.db at "
                 "/private/var/mobile/Library/Application Support/CloudDocs/session/db. Rows can live in the "
                 "write-ahead log, which is read with the database; on iphone11_ios17 the file alone held 56 "
                 "of 58 rows. Created, Modified and Last opened are item_birthtime, version_mtime and "
                 "item_lastusedtime, read as Unix epoch seconds and shown in UTC; every non-zero value in "
                 "the tested images was a 10-digit integer and the epoch is not sourced. A zero, empty or "
                 "negative value reads blank. Path is rebuilt from the item_parent_id chain in server_items, "
                 "outermost first, following only a 16-byte parent id; a parent id of another length ends "
                 "the chain even when the table holds a row with that id (4 rows on felix_ios17), so Path "
                 "can be incomplete or blank. A row whose version_size is not stored as an integer is "
                 "treated as a folder: its name is appended to Path and Filename is left blank. Item type "
                 "and Item state are the stored integer codes, reported as stored; their meanings are not "
                 "sourced. Version name is version_name as stored. Size in bytes is version_size as stored; "
                 "Size is the same value in 1024-based units, blank when the size is 0 or absent. Zone is "
                 "server_zones.zone_name. From device name is devices.name matched on version_device, blank "
                 "when version_device is empty or has no devices row. Item state held 0 on all 145 rows of "
                 "the eight images. server_items had no account or user name column in the eight schemas "
                 "read. Run against eight images, iOS 12 to 18; row counts 1 to 58 matched the table at "
                 "every output. "
        ),
        "paths": ('*/mobile/Library/Application Support/CloudDocs/session/db/server.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud",
        "sample_data": {
            'iphone11_ios17': 'iOS 17 | 58 rows',
            'ctf2020_ios12': 'iOS 12 | 19 rows',
            'jess_ios15': 'iOS 15 | 1 row',
            'magnet_ios16': 'iOS 16 | 7 rows',
            'felix_ios17': 'iOS 17 | 32 rows',
            'iphone12_ios18': 'iOS 18 | 11 rows',
            'hc_ios18_7': 'iOS 18.7 | 1 row',
            'hickman_ios13': 'iOS 13 | 16 rows',
        },
    },
    "icloud_drive_download_queue": {
        "name": "Files App - iCloud Drive download queue",
        "description": "Rows of the client_downloads table of the CloudDocs client.db, with the client_items row "
                       "matched on throttle_id and the stored stamps.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-12",
        "last_update_date": "2026-11-12",
        "requirements": "none",
        "category": "Files App",
        "notes": (
                 "Source is the client_downloads table of the CloudDocs client.db at "
                 "/private/var/mobile/Library/Application Support/CloudDocs/session/db. Rows can live in the "
                 "write-ahead log, which is read with the database; on iphone11_ios17 the single row was "
                 "present only in the -wal. throttle_id is matched to client_items.rowid to take the file "
                 "name (item_filename) and rebuild Path from that row's item_parent_id chain; this link is "
                 "not sourced, and on the rows tested each matched one client_items row whose zone and "
                 "library agreed. Path follows only a 16-byte parent id, so it is blank when the parent id "
                 "is another length, as on the iphone11_ios17 row. Last try, Request time, Next retry and "
                 "Expires are last_try_stamp, download_request_stamp, next_retry_stamp and expire_stamp; the "
                 "headers follow the column names and what each records is not sourced. Each is read as Unix "
                 "nanoseconds and shown in whole seconds, UTC, dropping any sub-second part; the stored "
                 "values were 19-digit integers resolving to 2024 and the unit and epoch are not sourced. A "
                 "zero, empty or negative value reads blank. Transfer size in bytes is transfer_size as "
                 "stored; Transfer size is the same value in units, blank when 0. Transfer queue, Transfer "
                 "stage and Download kind are reported as stored; a queue or stage value stored as a blob "
                 "would show as its byte length, which did not occur (the stored values were text). App "
                 "library name is app_libraries.app_library_name; Zone is client_zones.zone_name. Run "
                 "against eight images, iOS 12 to 18: 1 row on iphone11_ios17 (in the write-ahead log) and 0 "
                 "rows on seven where the table was present and empty; one row is the whole tested "
                 "population and the queue, stage and kind values were not sourced. "
        ),
        "paths": ('*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "download-cloud",
        "sample_data": {
            'iphone11_ios17': 'iOS 17 | 1 row (write-ahead log)',
            'ctf2020_ios12': 'iOS 12 | 0 rows',
            'jess_ios15': 'iOS 15 | 0 rows',
            'magnet_ios16': 'iOS 16 | 0 rows',
            'felix_ios17': 'iOS 17 | 0 rows',
            'iphone12_ios18': 'iOS 18 | 0 rows',
            'hc_ios18_7': 'iOS 18.7 | 0 rows',
            'hickman_ios13': 'iOS 13 | 0 rows',
        },
    },
    "icloud_drive_upload_queue": {
        "name": "Files App - iCloud Drive upload queue",
        "description": "Rows of the client_uploads table of the CloudDocs client.db, with the client_items row "
                       "matched on throttle_id and the stored stamps.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-12",
        "last_update_date": "2026-11-12",
        "requirements": "none",
        "category": "Files App",
        "notes": (
                 "Source is the client_uploads table of the CloudDocs client.db at "
                 "/private/var/mobile/Library/Application Support/CloudDocs/session/db. The write-ahead log "
                 "is read with the database, so the rows are the table's current state; on ctf2020_ios12 the "
                 "database file alone holds 2 rows the log removes. throttle_id is matched to "
                 "client_items.rowid to take the file name (item_filename) and rebuild Path from that row's "
                 "item_parent_id chain; this link is not sourced, and on the rows tested each matched one "
                 "client_items row whose zone and library agreed. Path follows only a 16-byte parent id, so "
                 "a file whose parent id is another length has a blank Path (both iphone12_ios18 rows); the "
                 "hickman_ios13 row had a 16-byte parent and its Path resolved to a folder. Last try, "
                 "Request time, Next retry and Expires are last_try_stamp, upload_request_stamp, "
                 "next_retry_stamp and expire_stamp; upload_request_stamp and next_retry_stamp held 0 on all "
                 "three rows and last_try_stamp held 0 on the hickman_ios13 row. Each stamp is read as Unix "
                 "nanoseconds and shown in whole seconds, UTC, dropping any sub-second part; the stored "
                 "values were 19-digit integers resolving to 2020 and 2025 and the unit and epoch are not "
                 "sourced. A zero, empty or negative value reads blank. Transfer size in bytes is "
                 "transfer_size as stored; Transfer size is the same value in units, blank when 0 (one row "
                 "on iphone12_ios18). Transfer queue and Transfer stage are reported as stored; a value "
                 "stored as a blob would show as its byte length, which did not occur, and Transfer stage "
                 "was empty on all three rows. App library name is app_libraries.app_library_name; Zone is "
                 "client_zones.zone_name. Run against eight images, iOS 12 to 18: 2 rows on iphone12_ios18 "
                 "and 1 row on hickman_ios13, and 0 rows on six others where the table was present and empty "
                 "as read with the write-ahead log; the queue and stage values were not sourced. "
        ),
        "paths": ('*/mobile/Library/Application Support/CloudDocs/session/db/client.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "upload-cloud",
        "sample_data": {
            'iphone11_ios17': 'iOS 17 | 0 rows',
            'ctf2020_ios12': 'iOS 12 | 0 rows',
            'jess_ios15': 'iOS 15 | 0 rows',
            'magnet_ios16': 'iOS 16 | 0 rows',
            'felix_ios17': 'iOS 17 | 0 rows',
            'iphone12_ios18': 'iOS 18 | 2 rows',
            'hc_ios18_7': 'iOS 18.7 | 0 rows',
            'hickman_ios13': 'iOS 13 | 1 row',
        },
    },
}

from packaging import version
from scripts.ilapfuncs import artifact_processor, get_file_path, \
    attach_sqlite_db_readonly, get_sqlite_db_records, get_plist_content, \
    convert_bytes_to_unit, convert_unix_ts_to_utc, logfunc


def get_tree_structure(source_path):
    """
    Builds a dictionary mapping item IDs to their full hierarchical paths
    in iCloud Drive.
    """

    query = '''
    SELECT
        client_items.item_id,
        client_items.item_parent_id,
        client_items.item_filename
    FROM client_items
    WHERE client_items.item_type != 1
    '''

    db_records = get_sqlite_db_records(source_path, query)

    tree_structure_dict = {}
    tree_structure_paths = {}

    for record in db_records:
        ts_id, ts_parent_id, ts_filename = record
        tree_structure_dict[ts_id] = (ts_parent_id, ts_filename)

    for ts_key, ts_value in tree_structure_dict.items():
        ts_p_id, ts_path = ts_value
        while len(ts_p_id) == 16:
            ts_p_id, ts_name = tree_structure_dict[ts_p_id]
            ts_path = ts_name + "/" + ts_path
        tree_structure_paths[ts_key] = f"{ts_path}/"

    return tree_structure_paths


@artifact_processor
def icloud_sync_device_names(context):
    """ See artifact description """
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "server.db")
    data_list = []

    query = '''
    SELECT
        devices.key,
        devices.name
    FROM devices
    '''

    data_headers = ('Device Number', 'Device Name')

    data_list = list( get_sqlite_db_records(source_path, query) )

    return data_headers, data_list, source_path


@artifact_processor
def icloud_application_list(context):
    """ See artifact description """
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "client.db")
    data_list = []

    os_version = context.get_installed_os_version()
    if not os_version:
        logfunc('No iOS version had been read when this artifact ran, client.db app libraries were not queried')
        return ('Application Bundle ID', ), data_list, source_path
    if version.parse(os_version) < version.parse('18'):
        query = '''
        SELECT
            app_libraries.app_library_name,
            app_libraries.auto_client_item_count - app_libraries.auto_document_count,
            app_libraries.auto_document_count,
            app_libraries.auto_aggregate_size
        FROM app_libraries
        '''
        data_headers = (
            'Application Bundle ID', 'Number of folders', 'Number of files',
            'Total size in bytes'
            )
    else:
        query = '''
        SELECT
            app_libraries.app_library_name
        FROM app_libraries
        '''
        data_headers = ('Application Bundle ID', )

    data_list = list( get_sqlite_db_records(source_path, query) )

    return data_headers, data_list, source_path


@artifact_processor
def icloud_drive_stored_files(context):
    """ See artifact description """
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "client.db")
    server_db_path = get_file_path(files_found, "server.db")
    data_list = []

    attach_query = attach_sqlite_db_readonly(server_db_path, 'server')
    query = '''
    SELECT
        client_items.item_birthtime AS 'Created',
        client_items.version_mtime AS 'Modified',
        client_items.item_lastusedtime AS 'Last opened',
        app_libraries.app_library_name AS 'App Bundle ID',
        client_items.item_parent_id AS 'Parent ID',
        client_items.item_filename AS 'Filename',
        CASE client_items.item_hidden_ext
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        END AS 'Hidden Extension',
        client_items.version_size AS 'Size',
        server.devices.name AS 'Device',
        client_items.item_sharing_options AS 'Is Shared?',
        CASE client_items.item_user_visible
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        END AS 'Is Visible?',
        client_items.item_trash_put_back_path AS 'Recently Deleted'
    FROM client_items
    LEFT JOIN app_libraries ON client_items.app_library_rowid = app_libraries.rowid
    LEFT JOIN server.devices ON client_items.version_device = server.devices.key
    '''

    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'),
        ('Last opened', 'datetime'), 'Application Bundle ID', 'Path',
        'Filename', 'Hidden extension', 'Size in bytes', 'Size',
        'From Device Name', 'Shared?', 'Visible?', 'Recently Deleted')

    db_records = get_sqlite_db_records(source_path, query, attach_query)

    parents = get_tree_structure(source_path) if db_records else {}

    for record in db_records:
        cdate, mdate, lodate, app_id, parent_id, filename, ext, \
            size_in_bytes, device, sharing_options, visible, \
            trash_back_path = record

        path = ''
        if len(parent_id) == 16:
            path = parents.get(parent_id, '')

        if not isinstance(size_in_bytes, int):
            path += f"{filename}/"
            filename = ""

        size = size_in_bytes
        if size:
            size = convert_bytes_to_unit(size_in_bytes)

        cdate = convert_unix_ts_to_utc(cdate) if cdate and cdate > 0 else ''
        mdate = convert_unix_ts_to_utc(mdate) if mdate and mdate > 0 else ''
        lodate = convert_unix_ts_to_utc(lodate) if lodate and lodate > 0 else ''

        shared = 'No' if sharing_options <= 4 else 'Yes'
        recently_deleted = 'Yes' if trash_back_path else 'No'

        data_list.append((
            cdate, mdate, lodate, app_id, path, filename, ext, size_in_bytes,
            size, device, shared, visible, recently_deleted))

    return data_headers, data_list, source_path


@artifact_processor
def icloud_drive_shared_files(context):
    """ See artifact description """
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "client.db")
    server_db_path = get_file_path(files_found, "server.db")
    data_list = []

    attach_query = attach_sqlite_db_readonly(server_db_path, 'server')
    query = '''
    SELECT
        client_items.item_birthtime AS 'Created',
        client_items.version_mtime AS 'Modified',
        client_items.item_lastusedtime AS 'Last opened',
        app_libraries.app_library_name AS 'App Bundle ID',
        client_items.item_parent_id AS 'Parent ID',
        client_items.item_filename AS 'Filename',
        CASE client_items.item_hidden_ext
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        END AS 'Hidden Extension',
        client_items.version_size AS 'Size',
        server.devices.name AS 'Device',
        client_items.item_sharing_options AS 'Is Shared?',
        client_items.item_creator_id AS 'Creator ID?',
        server.users.user_plist,
        client_items.item_trash_put_back_path AS 'Recently Deleted'
    FROM client_items
    LEFT JOIN app_libraries ON client_items.app_library_rowid = app_libraries.rowid
    LEFT JOIN server.devices ON client_items.version_device = server.devices.key
    LEFT JOiN server.users ON client_items.item_creator_id = server.users.user_key
    WHERE client_items.item_sharing_options > 4
    '''

    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'),
        ('Last opened', 'datetime'), 'Application Bundle ID', 'Path', 'Filename',
        'Hidden extension', 'Size in bytes', 'Size', 'From Device Name',
        'Shared by', 'Permissions', 'Recently Deleted')

    db_records = get_sqlite_db_records(source_path, query, attach_query)
    parents = get_tree_structure(source_path) if db_records else {}

    for record in db_records:
        cdate, mdate, lodate, app_id, parent_id, filename, ext, \
            size_in_bytes, device, sharing_options, creator_id, user_plist, \
            trash_back_path = record

        path = ''
        if len(parent_id) == 16:
            path = parents.get(parent_id, '')

        if not isinstance(size_in_bytes, int):
            path += f"{filename}/"
            filename = ""

        size = size_in_bytes
        if size:
            size = convert_bytes_to_unit(size_in_bytes)

        cdate = convert_unix_ts_to_utc(cdate) if cdate and cdate > 0 else ''
        mdate = convert_unix_ts_to_utc(mdate) if mdate and mdate > 0 else ''
        lodate = convert_unix_ts_to_utc(lodate) if lodate and lodate > 0 else ''

        if sharing_options in (8, 12):
            sharing_permissions = "Anyone with the link can make changes"
        elif sharing_options in (24, 28):
            sharing_permissions = "Anyone with the link can view only"
        elif sharing_options in (64, 68):
            sharing_permissions = "Only invited people"
        else:
            sharing_permissions = sharing_options

        user_full_name = ''
        if user_plist:
            deserialized_user_plist = get_plist_content(user_plist[3:])
            user = deserialized_user_plist.get('NS.nameComponentsPrivate')
            if user:
                user_given_name = user.get('NS.givenName', '')
                user_family_name = user.get('NS.familyName', '')
                user_full_name = f"{user_given_name + ' ' if user_given_name else ''}" +\
                    f"{user_family_name}"
        creator_name = user_full_name if user_full_name else 'an unknown user'
        shared_by = creator_name if creator_id else 'local account (no creator ID)'

        recently_deleted = 'Yes' if trash_back_path else 'No'

        data_list.append((cdate, mdate, lodate, app_id, path, filename, ext,
                          size_in_bytes, size, device, shared_by,
                          sharing_permissions, recently_deleted))

    return data_headers, data_list, source_path


@artifact_processor
def icloud_drive_tagged_files(context):
    """ See artifact description """
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "client.db")
    server_db_path = get_file_path(files_found, "server.db")
    data_list = []

    attach_query = attach_sqlite_db_readonly(server_db_path, 'server')
    query = '''
    SELECT
        client_items.item_birthtime AS 'Created',
        client_items.version_mtime AS 'Modified',
        client_items.item_lastusedtime AS 'Last opened',
        app_libraries.app_library_name AS 'App Bundle ID',
        client_items.item_parent_id AS 'Parent ID',
        client_items.item_filename AS 'Filename',
        CASE client_items.item_hidden_ext
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        END AS 'Hidden Extension',
        client_items.item_finder_tags AS 'Tags',
        client_items.version_size AS 'Size',
        server.devices.name AS 'Device',
        client_items.item_trash_put_back_path AS 'Recently Deleted'
    FROM client_items
    LEFT JOIN app_libraries ON client_items.app_library_rowid = app_libraries.rowid
    LEFT JOIN server.devices ON client_items.version_device = server.devices.key
    WHERE client_items.item_finder_tags IS NOT NULL
    '''

    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'), ('Last opened', 'datetime'),
        'Application Bundle ID', 'Path', 'Filename', 'Hidden extension', 'Tags',
        'Size in bytes', 'Size', 'From Device Name', 'Recently Deleted')

    db_records = get_sqlite_db_records(source_path, query, attach_query)
    parents = get_tree_structure(source_path) if db_records else {}

    for record in db_records:
        cdate, mdate, lodate, app_id, parent_id, filename, ext, tags, \
            size_in_bytes, device, trash_back_path = record

        path = ''
        if len(parent_id) == 16:
            path = parents.get(parent_id, '')

        if not isinstance(size_in_bytes, int):
            path += f"{filename}/"
            filename = ""

        size = size_in_bytes
        if size:
            size = convert_bytes_to_unit(size_in_bytes)

        cdate = convert_unix_ts_to_utc(cdate) if cdate and cdate > 0 else ''
        mdate = convert_unix_ts_to_utc(mdate) if mdate and mdate > 0 else ''
        lodate = convert_unix_ts_to_utc(lodate) if lodate and lodate > 0 else ''

        if tags:
            tags = ', '.join(tags.decode('utf-8').split())

        recently_deleted = 'Yes' if trash_back_path else 'No'

        data_list.append((cdate, mdate, lodate, app_id, path, filename, ext,
                          tags, size_in_bytes, size, device, recently_deleted))

    return data_headers, data_list, source_path


@artifact_processor
def icloud_drive_favourite_files(context):
    """ See artifact description """
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "client.db")
    server_db_path = get_file_path(files_found, "server.db")
    data_list = []

    attach_query = attach_sqlite_db_readonly(server_db_path, 'server')
    query = '''
    SELECT
        client_items.item_birthtime AS 'Created',
        client_items.version_mtime AS 'Modified',
        client_items.item_lastusedtime AS 'Last opened',
        app_libraries.app_library_name AS 'App Bundle ID',
        client_items.item_parent_id AS 'Parent ID',
        client_items.item_filename AS 'Filename',
        CASE client_items.item_hidden_ext
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        END AS 'Hidden Extension',
        client_items.version_size AS 'Size',
        server.devices.name AS 'Device',
        client_items.item_trash_put_back_path AS 'Recently Deleted',
        client_items.item_favoriterank AS 'Favourite'
    FROM client_items
    LEFT JOIN app_libraries ON client_items.app_library_rowid = app_libraries.rowid
    LEFT JOIN server.devices ON client_items.version_device = server.devices.key
    WHERE client_items.item_favoriterank != 0
    '''

    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'), ('Last opened', 'datetime'),
        'Application Bundle ID', 'Path', 'Filename', 'Hidden extension',
        'Size in bytes', 'Size', 'From Device Name', 'Recently Deleted')

    db_records = get_sqlite_db_records(source_path, query, attach_query)
    parents = get_tree_structure(source_path) if db_records else {}

    for record in db_records:
        cdate, mdate, lodate, app_id, parent_id, filename, ext, \
            size_in_bytes, device, trash_back_path, _ = record

        path = ''
        if len(parent_id) == 16:
            path = parents.get(parent_id, '')

        if not isinstance(size_in_bytes, int):
            path += f"{filename}/"
            filename = ""

        size = size_in_bytes
        if size:
            size = convert_bytes_to_unit(size_in_bytes)

        cdate = convert_unix_ts_to_utc(cdate) if cdate and cdate > 0 else ''
        mdate = convert_unix_ts_to_utc(mdate) if mdate and mdate > 0 else ''
        lodate = convert_unix_ts_to_utc(lodate) if lodate and lodate > 0 else ''

        recently_deleted = 'Yes' if trash_back_path else 'No'

        data_list.append((cdate, mdate, lodate, app_id, path, filename, ext,
                          size_in_bytes, size, device, recently_deleted))

    return data_headers, data_list, source_path


@artifact_processor
def files_ios_updates(context):
    """ See artifact description """
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "client.db")
    data_list = []

    query = '''
    SELECT
        boot_history.date,
        boot_history.os
    FROM boot_history
    '''
    data_headers = (('Date and Time', 'datetime'), 'OS Build', 'OS Version')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        os_date, os_os = record
        os_date = convert_unix_ts_to_utc(os_date)
        os_version = context.get_apple_os_version(os_os)

        data_list.append((os_date, os_os, os_version))

    return data_headers, data_list, source_path


def _cloud_stamp(value):
    """A CloudDocs stamp as Unix seconds: a value above 10**14 is nanoseconds, else seconds; 0/None -> None."""
    if not isinstance(value, (int, float)) or value == 0:
        return None
    return value / 1_000_000_000 if abs(value) > 10 ** 14 else value


def get_server_tree_structure(server_db_path):
    """item_id -> full path, built from the server_items table of server.db (mirrors get_tree_structure)."""
    query = '''
    SELECT item_id, item_parent_id, item_filename
    FROM server_items
    WHERE item_type != 1
    '''
    records = get_sqlite_db_records(server_db_path, query)
    nodes = {}
    for item_id, parent_id, filename in records:
        nodes[item_id] = (parent_id, filename)
    paths = {}
    for key, (parent_id, name) in nodes.items():
        path = name
        seen = {key}
        while isinstance(parent_id, (bytes, bytearray)) and len(parent_id) == 16 and parent_id in nodes and parent_id not in seen:
            seen.add(parent_id)
            parent_id, parent_name = nodes[parent_id]
            path = parent_name + "/" + path
        paths[key] = f"{path}/"
    return paths


@artifact_processor
def icloud_drive_server_files(context):
    """ See artifact description """
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "server.db")
    data_list = []
    query = '''
    SELECT
        server_items.item_birthtime,
        server_items.version_mtime,
        server_items.item_lastusedtime,
        server_items.item_parent_id,
        server_items.item_filename,
        server_items.version_name,
        server_items.item_type,
        server_items.item_state,
        server_items.version_size,
        server_zones.zone_name,
        devices.name
    FROM server_items
    LEFT JOIN server_zones ON server_items.zone_rowid = server_zones.rowid
    LEFT JOIN devices ON server_items.version_device = devices.key
    '''
    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'), ('Last opened', 'datetime'),
        'Filename', 'Path', 'Version name', 'Item type', 'Item state', 'Size in bytes', 'Size',
        'Zone', 'From device name')
    db_records = get_sqlite_db_records(source_path, query)
    parents = get_server_tree_structure(source_path) if db_records else {}
    for (cdate, mdate, lodate, parent_id, filename, version_name, item_type, item_state,
         size_in_bytes, zone, device) in db_records:
        path = parents.get(parent_id, '') if isinstance(parent_id, (bytes, bytearray)) and len(parent_id) == 16 else ''
        if not isinstance(size_in_bytes, int):
            path += f"{filename}/"
            filename = ""
        size = convert_bytes_to_unit(size_in_bytes) if size_in_bytes else ''
        cdate = convert_unix_ts_to_utc(cdate) if cdate and cdate > 0 else ''
        mdate = convert_unix_ts_to_utc(mdate) if mdate and mdate > 0 else ''
        lodate = convert_unix_ts_to_utc(lodate) if lodate and lodate > 0 else ''
        data_list.append((cdate, mdate, lodate, filename, path, version_name, item_type, item_state,
                          size_in_bytes, size, zone, device))
    return data_headers, data_list, source_path


def _transfer_rows(context, table, extra_select, data_headers):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "client.db")
    data_list = []
    query = f'''
    SELECT
        {table}.last_try_stamp,
        {table}.{extra_select[0]},
        {table}.next_retry_stamp,
        {table}.expire_stamp,
        client_items.item_parent_id,
        client_items.item_filename,
        {table}.transfer_size,
        {table}.transfer_queue,
        {table}.transfer_stage,
        app_libraries.app_library_name,
        client_zones.zone_name,
        {table}.throttle_id{extra_select[1]}
    FROM {table}
    LEFT JOIN client_items ON client_items.rowid = {table}.throttle_id
    LEFT JOIN app_libraries ON {table}.app_library_rowid = app_libraries.rowid
    LEFT JOIN client_zones ON {table}.zone_rowid = client_zones.rowid
    '''
    def _t(value):
        secs = _cloud_stamp(value)
        return convert_unix_ts_to_utc(secs) if secs and secs > 0 else ''

    def _blob(value):
        if isinstance(value, (bytes, bytearray)):
            return f"({len(value)} bytes)"
        return value

    db_records = get_sqlite_db_records(source_path, query)
    parents = get_tree_structure(source_path) if db_records else {}
    for record in db_records:
        (last_try, request, next_retry, expire, parent_id, filename, size_in_bytes, queue, stage,
         app_id, zone, throttle_id, *rest) = record
        path = parents.get(parent_id, '') if isinstance(parent_id, (bytes, bytearray)) and len(parent_id) == 16 else ''
        stage = _blob(stage)
        queue = _blob(queue)
        size = convert_bytes_to_unit(size_in_bytes) if size_in_bytes else ''
        data_list.append((_t(last_try), _t(request), _t(next_retry), _t(expire), filename, path,
                          size_in_bytes, size, queue, stage, app_id, zone, throttle_id, *rest))
    return data_headers, data_list, source_path


@artifact_processor
def icloud_drive_download_queue(context):
    """ See artifact description """
    data_headers = (
        ('Last try', 'datetime'), ('Request time', 'datetime'), ('Next retry', 'datetime'),
        ('Expires', 'datetime'), 'Filename', 'Path', 'Transfer size in bytes', 'Transfer size',
        'Transfer queue', 'Transfer stage', 'App library name', 'Zone', 'Throttle ID', 'Download kind')
    return _transfer_rows(context, 'client_downloads',
                          ('download_request_stamp', ', client_downloads.download_kind'),
                          data_headers)


@artifact_processor
def icloud_drive_upload_queue(context):
    """ See artifact description """
    data_headers = (
        ('Last try', 'datetime'), ('Request time', 'datetime'), ('Next retry', 'datetime'),
        ('Expires', 'datetime'), 'Filename', 'Path', 'Transfer size in bytes', 'Transfer size',
        'Transfer queue', 'Transfer stage', 'App library name', 'Zone', 'Throttle ID')
    return _transfer_rows(context, 'client_uploads',
                          ('upload_request_stamp', ''), data_headers)
