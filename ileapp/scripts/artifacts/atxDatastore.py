__artifacts_v2__ = {
    "atxDatastore": {
        "name": "iOS ATXDatastore",
        "description": "Parses ATXDataStore and matches actions with Frequent locations, when available.",
        "author": "@magpol",
        "version": "0.1.4",
        "date": "2023-10-11",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": ('*DuetExpertCenter/_ATXDataStore.db*', '*routined/Local.sqlite*'),
        "output_types": "all"
    }
}

from ileapp.scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, attach_sqlite_db_readonly, convert_ts_human_to_timezone_offset 

@artifact_processor
def atxDatastore(files_found, report_folder, seeker, wrap_text, timezone_offset):
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

    for row in all_rows:
        timestamp = convert_ts_human_to_timezone_offset(row[5], timezone_offset)
        
        startdate = convert_ts_human_to_timezone_offset(row[6], timezone_offset)
        
        enddate = convert_ts_human_to_timezone_offset(row[7], timezone_offset)
        
        data_list.append(
            (timestamp, row[2], row[3], row[4], startdate, enddate, row[8], row[9], row[0])
            )

    db.close()

    data_headers = (
        ('Timestamp', 'datetime'), 
        'Type', 
        'Latitude', 
        'Longitude', 
        'AppSessionStartDate', 
        'AppSessionEndDate', 
        'Location', 
        'Previous Location', 
        'ID'
        )
    return data_headers, data_list, source_path
