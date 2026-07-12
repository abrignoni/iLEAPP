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
        'output_types': 'all',
        'artifact_icon': 'map-pin',
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | 10383 rows',
            'felix_ios17': 'iOS 17.6.1 | 11536 rows',
            'fsfull002_ios17': 'iOS 17.1 | 6537 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 47295 rows',
            'iphone11_ios17': 'iOS 17.3 | 84972 rows',
            'iphone12_ios18': 'iOS 18.7 | 5952 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 2614 rows',
            'otto_ios17': 'iOS 17.5.1 | 72911 rows',
            'abe_ios16': 'iOS 16.5 | 103391 rows',
            'felix23_ios16': 'iOS 16.5 | 7813 rows',
            'hickman_ios13': 'iOS 13.3.1 | 89662 rows',
            'hickman_ios14': 'iOS 14.3 | 33411 rows',
            'jess_ios15': 'iOS 15.0.2 | 4084 rows',
            'magnet_ios16': 'iOS 16.1.1 | 14563 rows',
        }
    }
}
from datetime import datetime, timezone
from scripts.ilapfuncs import (artifact_processor, get_file_path, get_sqlite_db_records, logfunc)

@artifact_processor
def CacheSQLite_Locations(context):

    data_list = []

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'Cache.sqlite')

    query = '''
    SELECT
        ZTIMESTAMP AS Timestamp,
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
            unix_timestamp = record[0] + 978307200
            timestampr = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)

            data_list.append((timestampr, record[1], record[2], record[3], record[4], record[5]))

    except Exception as e:  # pylint: disable=broad-exception-caught
        logfunc(f'Error processing Cache.sqlite locations: {e}')

    data_headers = (
        ('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Horizontal Accuracy (Meters)', 'Speed (Meters/Sec)', 'Speed (Miles/Hour)')

    return data_headers, data_list, source_path