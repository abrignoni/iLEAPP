__artifacts_v2__ = {
    "ATXDatastore": {
        "name": "iOS ATXDatastore",
        "description": "Parses ATXDataStore and matches actions with Frequent locations, when available.",
        "author": "@magpol",
        "version": "0.0.3",
        "date": "2023-11-21",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": ('**DuetExpertCenter/_ATXDataStore.db*', '**routined/Local.sqlite*'),
        "output_types": "all"
    }
}

from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone, artifact_processor

@artifact_processor(__artifacts_v2__["ATXDatastore"])
def get_atxDatastore(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    source_path = ''

    atxdb = ''
    localdb = ''
   
    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('_ATXDataStore.db'):
           atxdb = str(file_found)
           source_path = atxdb
        elif file_name.endswith('Local.sqlite'):
           localdb = str(file_found)
    
    if not atxdb or not localdb:
        logfunc('ATXDataStore or Local.sqlite not found')
        return data_headers, data_list, source_path

    db = open_sqlite_db_readonly(atxdb)
    cursor = db.cursor()

    cursor.execute(f'''attach database "{localdb}" as Local ''')
    cursor.execute('''
    SELECT 
        alog.id AS Id,
        alog.bundleId AS bundleId,
        alogAction.actionType AS ptype,
        Local.ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLATITUDE AS latitude, 
        Local.ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLONGITUDE AS longitude,
        DateTime(alog.date + 978307200, 'UNIXEPOCH') AS date,
        DateTime(alog.appSessionStartDate + 978307200, 'UNIXEPOCH') AS appSessionStartDate,
        DateTime(alog.appSessionEndDate + 978307200, 'UNIXEPOCH') AS appSessionEndDate,
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

    if len(all_rows) > 0:
        for row in all_rows:
            timestamp = convert_ts_human_to_utc(row[5])
            timestamp = convert_utc_human_to_timezone(timestamp, timezone_offset)
            
            startdate = convert_ts_human_to_utc(row[6])
            startdate = convert_utc_human_to_timezone(startdate, timezone_offset)
            
            enddate = convert_ts_human_to_utc(row[7])
            enddate = convert_utc_human_to_timezone(enddate, timezone_offset)
            
            data_list.append((timestamp, row[2], row[3], row[4], startdate, enddate, row[8], row[9], row[0]))
    else:
        logfunc('No items in ATXDataStore')

    db.close()

    data_headers = (('Timestamp', 'datetime'), 'Type', 'Latitude', 'Longitude', 'AppSessionStartDate', 'AppSessionEndDate', 'Location', 'Previous Location', 'ID')
    return data_headers, data_list, source_path

