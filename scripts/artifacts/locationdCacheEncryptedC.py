__artifacts_v2__ = {
    'locationdMotionStateHistory': {
        'name': 'Locationd Cache - Motion State History',
        'description': "Rows of locationd's MotionStateHistory table, with the motion type, "
                       'confidence and the moving and vehicular flags each row stores',
        'author': '@AlexisBrignoni, Claude',
        'creation_date': '2026-11-17',
        'last_update_date': '2026-11-17',
        'requirements': 'none',
        'category': 'Locations',
        'notes': ("One row per row of the MotionStateHistory table in locationd's "
                 "cache_encryptedC.db; the table and column names are the only labels used here, "
                 "and no Apple documentation of this table was found. Start Time is startTime read "
                 "as seconds since 2001 and shown in UTC; it places rows over the last 4 days on "
                 "hill_iphone15pro_ios26, 7 days on wilkerson_iphone16_ios26 and 9 days on "
                 "iphone11_ios17, each ending near the extraction, so the table holds recent "
                 "history only. What a row covers is not documented: the gap to the next row "
                 "ranged from under a second to more than a day. Timestamp (as stored) is the "
                 "timestamp column, which is not a date: it is between 812 and 815 million seconds "
                 "smaller than startTime on every row of the two iOS 26 images and about 743 "
                 "million smaller on iphone11_ios17, and what clock it counts is not established. Type is stored as a single bit value (1, 4, 16, 64, 128, 256 "
                 "and 4096 seen); Apple publishes no names for these values, so none are applied. "
                 "Is Moving and Is Vehicular held 0 or 1 on every row and are reported as stored, "
                 "as are Confidence, Vehicle Type, Vehicular Flags, Vehicle Exit State, Mounted, "
                 "Mounted Confidence and Turn. Confidence held 2 on all 1,524 rows of "
                 "hill_iphone15pro_ios26. Vehicle Exit State and Turn held 0 on every row of all "
                 "three tested images. Vehicle Type is empty on every row of iphone11_ios17, whose "
                 "iOS 17.3 table has no vehicleType column; a column the table lacks is read as "
                 "empty rather than costing the query its rows. The same database holds "
                 "StepCountHistory, PednetHistory and ElevationHistory, which are not read here: "
                 "the Health - Steps artifact reports step samples from healthdb_secure.sqlite "
                 "that, on both iOS 26 images, start about six months earlier and end at the same "
                 "time, while the StepCountHistory count never decreases from one row to the next "
                 "over its 2 to 4 days. "
                 "StrideCalHistory, ExerciseMinuteHistory, MobilityWalkingBoutHistory, "
                 "MaxMetsProcessingHistory, MotionAlarm and ActiveConfig were empty on both iOS 26 "
                 "images."),
        'paths': ('*/root/Library/Caches/locationd/cache_encryptedC.db*',),
        'output_types': 'standard',
        'artifact_icon': 'activity',
        'sample_data': {
            'hill_iphone15pro_ios26': 'iOS 26.3.1 | 1524 rows',
            'wilkerson_iphone16_ios26': 'iOS 26.5.2 | 1116 rows',
            'iphone11_ios17': 'iOS 17.3 | 3417 rows; no vehicleType column',
        },
    },
}

import os

from scripts.ilapfuncs import artifact_processor, convert_cocoa_core_data_ts_to_utc, \
    does_table_exist_in_db, get_sqlite_db_records, is_sqlite_sidecar

_COLUMNS = ('startTime', 'type', 'confidence', 'isMoving', 'isVehicular', 'vehicleType',
            'vehicularFlagsData', 'vehicleExitState', 'mounted', 'mountedConfidence', 'turn',
            'timestamp', 'id')


def _start(value):
    '''startTime, seconds since 2001, as UTC; a missing or non-positive value stays blank.'''
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return ''
    return convert_cocoa_core_data_ts_to_utc(value)


@artifact_processor
def locationdMotionStateHistory(context):
    data_headers = (
        ('Start Time', 'datetime'), 'Type (as stored)', 'Confidence (as stored)',
        'Is Moving (as stored)', 'Is Vehicular (as stored)', 'Vehicle Type (as stored)',
        'Vehicular Flags (as stored)', 'Vehicle Exit State (as stored)', 'Mounted (as stored)',
        'Mounted Confidence (as stored)', 'Turn (as stored)', 'Timestamp (as stored)', 'Row ID')
    data_list, sources = [], []
    for found in sorted(dict.fromkeys(str(path) for path in context.get_files_found())):
        if os.path.basename(found) != 'cache_encryptedC.db' or is_sqlite_sidecar(found):
            continue
        sources.append(found)
        if not does_table_exist_in_db(found, 'MotionStateHistory'):
            continue
        available = {record['name'] for record in
                     get_sqlite_db_records(found, 'PRAGMA table_info(MotionStateHistory)')}
        selected = ', '.join(name if name in available else f'NULL AS {name}' for name in _COLUMNS)
        query = f'SELECT {selected} FROM MotionStateHistory ORDER BY startTime, id'
        for record in get_sqlite_db_records(found, query):
            data_list.append((_start(record['startTime']),) + tuple(
                record[name] for name in _COLUMNS[1:]))
    return data_headers, data_list, '\n'.join(sources)
