__artifacts_v2__ = {
    "geodpdplacecache": {
        "name": "Geolocation - PD Place Cache",
        "description": "Cached place lookups from the geod PDPlaceCache.db",
        "author": "@flamusdiu",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Location",
        "notes": "lastaccesstime and expiretime are read as Mac absolute time (Cocoa, seconds "
                 "since 2001-01-01 UTC); the basis for that epoch is not given here. PD Place is "
                 "the set of printable ASCII strings of four characters or more found in the "
                 "stored pdplace value, sorted with repeats removed; it is not a decode of the "
                 "record and the order is not the stored order. A lookup row with no matching "
                 "pdplaces row is not reported. Only the first PDPlaceCache.db matched is read. A "
                 "row is a place lookup the system cached and does not establish that the device "
                 "was at that place.",
        "paths": ('**/PDPlaceCache.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 5 rows",
            "felix_ios17": "iOS 17.6.1 | 3 rows",
            "fsfull002_ios17": "iOS 17.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | 19 rows",
            "iphone12_ios18": "iOS 18.7 | 36 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 11 rows",
            "abe_ios16": "iOS 16.5 | 5 rows",
            "felix23_ios16": "iOS 16.5 | 6 rows",
            "hickman_ios13": "iOS 13.3.1 | 11 rows",
            "hickman_ios14": "iOS 14.3 | 21 rows",
            "jess_ios15": "iOS 15.0.2 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 3 rows",
        }
    }
}

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, does_table_exist_in_db,
                               convert_cocoa_core_data_ts_to_utc, strings)


@artifact_processor
def geodpdplacecache(context):
    data_headers = (('Last Access Time', 'datetime'), 'Request Key', 'PD Place Hash',
                    ('Expire Time', 'datetime'), 'PD Place')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('.db'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    if does_table_exist_in_db(source_path, 'pdplacelookup'):
        query = '''SELECT requestkey, pdplacelookup.pdplacehash, lastaccesstime, expiretime, pdplace
            FROM pdplacelookup
            INNER JOIN pdplaces ON pdplacelookup.pdplacehash = pdplaces.pdplacehash'''
        for row in get_sqlite_db_records(source_path, query):
            pd_place = '\n'.join(sorted(set(strings(row[4]))))
            data_list.append((convert_cocoa_core_data_ts_to_utc(row[2]), row[0], row[1],
                              convert_cocoa_core_data_ts_to_utc(row[3]), pd_place))

    return data_headers, data_list, context.get_relative_path(source_path)
