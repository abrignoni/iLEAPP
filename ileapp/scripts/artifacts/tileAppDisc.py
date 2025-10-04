__artifacts_v2__ = {
    'tileAppDisc': {
        'name': 'Tile App Discovered Tiles',
        'description': 'Tile IDs seen from other users',
        'author': '@AlexisBrignoni',
        'creation_date': '2020-09-03',
        'last_update_date': '2025-04-05',
        'requirements': 'none',
        'category': 'Tile App',
        'notes': '',
        'paths': (
            '*/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-DiscoveredTileDB.sqlite*', ),
        'output_types': 'standard',
        'artifact_icon': 'user'
    }
}


from ileapp.scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, \
    convert_cocoa_core_data_ts_to_utc


@artifact_processor
def tileAppDisc(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(
        files_found, 'com.thetileapp.tile-DiscoveredTileDB.sqlite')
    data_list = []

    query = '''
    SELECT
        ZLAST_MODIFIED_TIMESTAMP,
        ZTILE_UUID
    FROM ZTILENTITY_DISCOVEREDTILE
    '''

    data_headers = (('Last Modified Timestamp', 'datetime'), 'Tile UUID')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        last_modified_timestamp = convert_cocoa_core_data_ts_to_utc(
            record['ZLAST_MODIFIED_TIMESTAMP'])
        data_list.append((last_modified_timestamp, record[1]))

    return data_headers, data_list, source_path
