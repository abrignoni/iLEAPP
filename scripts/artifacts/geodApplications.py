__artifacts_v2__ = {
    "geodapplications": {
        "name": "Geolocation - Applications",
        "description": "Per-application location count entries from the geod AP.db (mkcount/dailycounts)",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "Location",
        "notes": "createtime is stored either as Mac absolute time (Cocoa, seconds since 2001-01-01 UTC) or as a 'YYYY-MM-DD HH:MM:SS' text value assumed to be UTC.",
        "paths": ('**/AP.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 18 rows",
            "iphone11_ios17": "iOS 17.3 | 114 rows",
            "iphone12_ios18": "iOS 18.7 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
        }
    }
}

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, does_table_exist_in_db,
                               convert_cocoa_core_data_ts_to_utc, convert_ts_human_to_utc, logfunc)


def _convert_createtime(createtime):
    """createtime is numeric Mac absolute time in some schema versions and a
    'YYYY-MM-DD HH:MM:SS' text value (assumed UTC) in others."""
    if createtime is None or createtime == '':
        return ''
    if isinstance(createtime, (int, float)):
        return convert_cocoa_core_data_ts_to_utc(createtime)
    try:
        return convert_ts_human_to_utc(str(createtime))
    except ValueError:
        logfunc(f'Unrecognized createtime value in AP.db: {createtime}')
        return ''


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
            data_list.append((_convert_createtime(row[2]), row[0], row[1]))

    return data_headers, data_list, context.get_relative_path(source_path)
