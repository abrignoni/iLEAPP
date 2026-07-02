""" atxDatastore """
__artifacts_v2__ = {
    "atx_datastore": {
        "name": "iOS ATXDatastore",
        "description": (
            "Parses ATXDataStore and matches actions with Frequent "
            "locations, when available."),
        "author": "@magpol",
        "creation_date": "2023-10-11",
        "last_update_date": "2025-10-22",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": (
            '*DuetExpertCenter/_ATXDataStore.db*', 
            '*routined/Local.sqlite*'
        ),
        "output_types": "all",
        "artifact_icon": "map-pin"
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    attach_sqlite_db_readonly,
    convert_cocoa_core_data_ts_to_utc,
    get_sqlite_db_records,
    logfunc,
)


@artifact_processor
def atx_datastore(context):
    """ see artifact description """
    data_list = []
    data_headers = (
        ('Timestamp', 'datetime'),
        ('AppSessionStartDate', 'datetime'),
        ('AppSessionEndDate', 'datetime'),
        'Type',
        'Latitude',
        'Longitude',
        'Location',
        'Previous Location',
        'ID'
    )

    atxdb = ''
    localdb = ''

    for file_found in context.get_files_found():
        file_name = str(file_found)
        if file_name.endswith('_ATXDataStore.db'):
            atxdb = str(file_found)
        elif file_name.endswith('Local.sqlite'):
            localdb = str(file_found)

    source_path = (
        f"ATX Database: {context.get_relative_path(atxdb)}\n"
        f"Local Database: {context.get_relative_path(localdb)}"
    )

    if not atxdb or not localdb:
        missing_dbs = []
        if not atxdb:
            missing_dbs.append('ATXDataStore')
        if not localdb:
            missing_dbs.append('Local')

        logfunc(f"Required database(s) not found: {', '.join(missing_dbs)}")
        return data_headers, data_list, source_path

    query = '''
    SELECT
        alog.id AS Id,
        alog.bundleId AS bundleId,
        alogAction.actionType AS ptype,
        Local.ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLATITUDE AS latitude,
        Local.ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLONGITUDE AS longitude,
        alog.date AS date,
        alog.appSessionStartDate AS appSessionStartDate,
        alog.appSessionEndDate AS appSessionEndDate,
        hex(alog.location) AS location,
        hex(alog.prevLocation) AS prevLocation,
        alog.motionType AS potionType,
        alog.geohash AS geohash,
        alog.coarseGeohash AS coarseGeohash
    FROM alog
    INNER JOIN alogAction ON alogAction.id = alog.actionType
    LEFT JOIN Local.ZRTLEARNEDLOCATIONOFINTERESTMO
        ON Local.ZRTLEARNEDLOCATIONOFINTERESTMO.ZIDENTIFIER = alog.location
    '''

    attach_query = attach_sqlite_db_readonly(localdb, 'Local')
    all_rows = get_sqlite_db_records(atxdb, query, attach_query)

    for row in all_rows:
        timestamp = convert_cocoa_core_data_ts_to_utc(row[5]) if row[5] is not None else ''
        startdate = convert_cocoa_core_data_ts_to_utc(row[6]) if row[6] is not None else ''
        enddate = convert_cocoa_core_data_ts_to_utc(row[7]) if row[7] is not None else ''
        data_list.append(
            (timestamp, startdate, enddate, row[2], row[3], row[4], row[8], row[9], row[0])
        )

    return data_headers, data_list, source_path
