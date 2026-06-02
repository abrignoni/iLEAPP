__artifacts_v2__ = {
    'CacheSQLite_Locations': {
        'name': 'Cache Locations',
        'description': 'Parses Cache.sqlite Routined Location Records',
        'author': 'Heather Charpentier',
        'creation_date': '2026-05-12',
        'last_update_date': '2026-05-12',
        'requirements': 'none',
        'category': 'Locations',
        'notes': 'Parses latitude, longitude, accuracy, and speeds from Cache.sqlite',
        'paths': ('*/Library/Caches/com.apple.routined/Cache.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'map-pin'
    }
}

from scripts.ilapfuncs import (artifact_processor, get_file_path, get_sqlite_db_records, logfunc)

@artifact_processor
def CacheSQLite_Locations(context):

    data_list = []

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'Cache.sqlite')

    query = '''
    SELECT
        datetime(ZTIMESTAMP + 978307200, 'unixepoch') AS Timestamp,
        ZLATITUDE,
        ZLONGITUDE,
        ZHORIZONTALACCURACY,
        ZSPEED,
        CASE
            WHEN ZSPEED = -1.0 THEN NULL
            ELSE ZSPEED * 2.23694
        END AS SpeedMPH
    FROM ZRTCLLOCATIONMO
    '''

    try:
        db_records = get_sqlite_db_records(source_path, query)

        for record in db_records:

            data_list.append((record[0], record[1], record[2], record[3], record[4], record[5]))

    except Exception as e:
        logfunc(f'Error processing Cache.sqlite locations: {e}')

    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Horizontal Accuracy (Meters)', 'Speed (Meters/Sec)', 'Speed (Miles/Hour)')

    return data_headers, data_list, source_path