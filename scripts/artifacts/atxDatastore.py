__artifacts_v2__ = {
    "atxDatastore": {
        "name": "iOS ATXDatastore",
        "description": "Parses ATXDataStore and matches actions with Frequent locations, when available.",
        "author": "@magpol",
        "creation_date": "2023-10-11",
        "last_update_date": "2025-10-22",
        "requirements": "none",
        "category": "Locations",
        "notes": "",
        "paths": ('*DuetExpertCenter/_ATXDataStore.db*', '*routined/Local.sqlite*'),
        "output_types": "all"
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, attach_sqlite_db_readonly, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def atxDatastore(context):
    data_list = []
    data_headers = ()

    atxdb = ''
    localdb = ''
   
    for file_found in context.get_files_found():
        file_name = str(file_found)
        if file_name.endswith('_ATXDataStore.db'):
            atxdb = str(file_found)
        elif file_name.endswith('Local.sqlite'):
            localdb = str(file_found)
    
    db = open_sqlite_db_readonly(atxdb)
    cursor = db.cursor()

    attach_query = attach_sqlite_db_readonly(localdb, 'Local')
    cursor.execute(attach_query)

    cursor.execute('''
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
    ''')

    all_rows = cursor.fetchall()

    for row in all_rows:
        timestamp = convert_cocoa_core_data_ts_to_utc(row[5]) if row[5] is not None else ''
        startdate = convert_cocoa_core_data_ts_to_utc(row[6]) if row[6] is not None else ''
        enddate = convert_cocoa_core_data_ts_to_utc(row[7]) if row[7] is not None else ''
        data_list.append(
            (timestamp, startdate, enddate, row[2], row[3], row[4],row[8], row[9], row[0])
            )

    db.close()

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
    
    source_path = f"ATX Database: {atxdb}\nLocal Database: {localdb}"
    return data_headers, data_list, source_path 
