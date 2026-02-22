from scripts.ilapfuncs import (artifact_processor, open_sqlite_db_readonly,
                              convert_ts_human_to_utc, convert_utc_human_to_timezone)


@artifact_processor
def get_tileAppDb(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('tile-TileNetworkDB.sqlite'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(ZTIMESTAMP,'unixepoch','31 years'),
    ZNAME,
    datetime(ZACTIVATION_TIMESTAMP,'unixepoch','31 years'),
    datetime(ZREGISTRATION_TIMESTAMP,'unixepoch','31 years'),
    ZALTITUDE,
    ZLATITUDE,
    ZLONGITUDE,
    ZID,
    ZNODE_TYPE,
    ZSTATUS,
    ZIS_LOST,
    datetime(ZLAST_LOST_TILE_COMMUNITY_CONNECTION,'unixepoch','31 years')
    FROM ZTILENTITY_NODE INNER JOIN ZTILENTITY_TILESTATE ON ZTILENTITY_NODE.ZTILE_STATE = ZTILENTITY_TILESTATE.Z_PK
    ''')

    all_rows = cursor.fetchall()
    data_list = []
    for row in all_rows:
        timestamp = row[0]
        if timestamp is not None:
            timestamp = convert_ts_human_to_utc(timestamp)
            timestamp = convert_utc_human_to_timezone(timestamp, timezone_offset)

        acttimestamp = row[2]
        if acttimestamp is not None:
            acttimestamp = convert_ts_human_to_utc(acttimestamp)
            acttimestamp = convert_utc_human_to_timezone(acttimestamp, timezone_offset)

        regtimestamp = row[3]
        if regtimestamp is not None:
            regtimestamp = convert_ts_human_to_utc(regtimestamp)
            regtimestamp = convert_utc_human_to_timezone(regtimestamp, timezone_offset)

        data_list.append((timestamp, row[1], acttimestamp, regtimestamp, row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]))

    db.close()

    data_headers = ('Timestamp', 'Tile Name', 'Activation Timestamp', 'Registration Timestamp',
                    'Altitude', 'Latitude', 'Longitude', 'Tile ID', 'Tile Type', 'Status',
                    'Is Lost?', 'Last Community Connection')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_tileAppDb": {
        "name": "Tile App DB Info",
        "description": "",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*/mobile/Containers/Shared/AppGroup/*/com.thetileapp.tile-TileNetworkDB.sqlite*',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
