"""
Extracts and processes device synchronization information from the
    Biome Device Sync database.
"""

__artifacts_v2__ = {
    "biome_sync": {
        "name": "Biome - Device Syncs",
        "description": "Parses Biome Device Sync records",
        "author": "@JohnHyla",
        'creation_date': '2023-03-22',
        'last_update_date': '2025-03-05',
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/sync/sync.db*'),
        "output_types": "standard",
        'artifact_icon': 'eye'
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, \
    get_sqlite_db_records, convert_unix_ts_to_utc


@artifact_processor
def biome_sync(context):
    """
    Extracts and processes device synchronization information from the
    'sync.db' SQLite database.
    """

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'sync.db')
    data_list = []

    query = '''
        SELECT
            last_sync_date,
            device_identifier,
            name,
            CASE platform
                WHEN 1 THEN 'iPad'
                WHEN 2 THEN 'iPhone'
                WHEN 3 THEN 'Mac'
                WHEN 4 THEN 'Mac'
                WHEN 5 THEN 'AppleTV'
                WHEN 6 THEN 'Watch'
                WHEN 7 THEN 'AppleTV'
                ELSE 'Unknown'
            END,
            model,
            CASE me
                WHEN 0 THEN ''
                WHEN 1 THEN 'Yes'
            END AS 'Local Device'
        FROM DevicePeer
    '''

    data_headers = (('Last Sync Timestamp', 'datetime'), 'Device ID', 'Name',
                    'Device Type', 'OS Build', 'OS Version', 'Local Device')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        timestamp = convert_unix_ts_to_utc(record[0])
        os_version = context.get_os_version(record[4], record[3])

        data_list.append((timestamp, record[1], record[2], record[3],
                          record[4], os_version, record[5]))

    return data_headers, data_list, source_path
