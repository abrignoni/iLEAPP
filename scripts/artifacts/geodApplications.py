__artifacts_v2__ = {
    "geodapplications": {
        "name": "Geolocation - Applications",
        "description": "Per-application location count entries from the geod AP.db (mkcount/dailycounts)",
        "author": "",
        "version": "2.0",
        "date": "2026-06-23",
        "requirements": "none",
        "category": "Location",
        "notes": "createtime assumed to be Mac absolute time (Cocoa, seconds since 2001-01-01 UTC).",
        "paths": ('**/AP.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin"
    }
}

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, does_table_exist_in_db,
                               convert_cocoa_core_data_ts_to_utc)


@artifact_processor
def geodapplications(context):
    data_headers = (('Creation Time', 'datetime'), 'Count ID', 'Application')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('.db'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    table = ''
    if does_table_exist_in_db(source_path, 'mkcount'):
        table = 'mkcount'
    elif does_table_exist_in_db(source_path, 'dailycounts'):
        table = 'dailycounts'

    if table:
        for row in get_sqlite_db_records(source_path, f'SELECT count_type, app_id, createtime FROM {table}'):
            data_list.append((convert_cocoa_core_data_ts_to_utc(row[2]), row[0], row[1]))

    return data_headers, data_list, context.get_relative_path(source_path)
