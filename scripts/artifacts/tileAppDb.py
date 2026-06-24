__artifacts_v2__ = {
    "tileAppDb": {
        "name": "Tile App DB Info & Geolocation",
        "description": "Tile device information and last-known geolocation from the Tile network database",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Locations",
        "notes": "Timestamps are Cocoa/Mac absolute time (seconds since 2001-01-01 UTC), converted to UTC.",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-TileNetworkDB.sqlite*',),
        "output_types": "all",
        "artifact_icon": "map-pin"
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


@artifact_processor
def tileAppDb(context):
    data_headers = (
        ('Timestamp', 'datetime'), 'Tile Name', ('Activation Timestamp', 'datetime'),
        ('Registration Timestamp', 'datetime'), 'Altitude', 'Latitude', 'Longitude', 'Tile ID',
        'Tile Type', 'Status', 'Is Lost?', ('Last Community Connection', 'datetime'))
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('tile-TileNetworkDB.sqlite'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    query = '''
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
    INNER JOIN ZTILENTITY_TILESTATE ON ZTILENTITY_NODE.ZTILE_STATE = ZTILENTITY_TILESTATE.Z_PK
    '''
    for row in get_sqlite_db_records(source_path, query):
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)
