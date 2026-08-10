__artifacts_v2__ = {
    "tileAppDb": {
        "name": "Tile App DB Info & Geolocation",
        "description": "Tile device information and most recent stored coordinates (via the TILESTATE join) from the Tile network database",
        "author": "@abrignoni",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-08-09",
        "requirements": "none",
        "category": "Locations",
        "notes": "Timestamps are Cocoa/Mac absolute time (seconds since 2001-01-01 UTC), converted to UTC.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-TileNetworkDB.sqlite*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | group.thetileapp.Tile.Documents | 0 rows",
            "abe_ios16": "iOS 16.5 | group.thetileapp.Tile.Documents | 0 rows",
        }
    }
}

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records,
                               null_absent_columns, does_table_exist_in_db)


@artifact_processor
def tileAppDb(context):
    data_headers = (
        ('Timestamp', 'datetime'), 'Tile Name', ('Activation Timestamp', 'datetime'),
        ('Registration Timestamp', 'datetime'), 'Altitude', 'Latitude', 'Longitude', 'Tile ID',
        'Tile Type', 'Status', 'Is Lost?', ('Last Lost-Tile Community Connection', 'datetime'))
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('tile-TileNetworkDB.sqlite'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    # Older app schemas have no ZTILENTITY_TILESTATE table; there the lost
    # state lives on ZTILENTITY_NODE itself and the location/timestamp columns
    # this query takes from the state table do not exist anywhere (verified on
    # the abe_ios16 and otto_ios17 images). null_absent_columns nulls those, so
    # the column list stays identical across both generations.
    state_join = (
        'INNER JOIN ZTILENTITY_TILESTATE ON ZTILENTITY_NODE.ZTILE_STATE = ZTILENTITY_TILESTATE.Z_PK'
        if does_table_exist_in_db(source_path, 'ZTILENTITY_TILESTATE')
        else ''
    )

    query = f'''
    SELECT
        datetime(ZTIMESTAMP + 978307200, 'unixepoch'),
        ZNAME,
        datetime(ZACTIVATION_TIMESTAMP + 978307200, 'unixepoch'),
        datetime(ZREGISTRATION_TIMESTAMP + 978307200, 'unixepoch'),
        ZALTITUDE,
        ZLATITUDE,
        ZLONGITUDE,
        ZID,
        ZNODE_TYPE,
        ZSTATUS,
        ZIS_LOST,
        datetime(ZLAST_LOST_TILE_COMMUNITY_CONNECTION + 978307200, 'unixepoch')
    FROM ZTILENTITY_NODE
    {state_join}
    '''
    for row in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)
