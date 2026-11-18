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
                 "as seconds since 2001-01-01 UTC with its fraction kept; no Apple source for that "
                 "epoch was found. Read this way, rows span 4 days on hill_iphone15pro_ios26, 7 on "
                 "wilkerson_iphone16_ios26 and 9 on iphone11_ios17, and the last row falls 17 to "
                 "27 minutes before the modified time of the database's -wal file on those images. "
                 "What a row covers is not documented: the gap to the next row ranged from under a "
                 "second to 13 hours on hill_iphone15pro_ios26, to 24 hours on iphone11_ios17 and "
                 "to 1.9 days (one gap) on wilkerson_iphone16_ios26. Timestamp (as stored) is the "
                 "timestamp column. It held values from about 27 to about 418,000 on the three "
                 "tested images, between 812 and 815 million smaller than startTime on the two iOS "
                 "26 images and between 742 and 744 million smaller on iphone11_ios17, and what "
                 "clock it counts is not established. Every Type value on the three tested images "
                 "has one bit set (1, 4, 16, 64, 128, 256 and 4096 seen); no Apple-published names "
                 "for these values were found, so none are applied. Is Moving and Is Vehicular "
                 "held 0 or 1 on every row of the three tested images and are reported as stored, "
                 "as are Confidence, Vehicle Type, Vehicular Flags, Vehicle Exit State, Mounted, "
                 "Mounted Confidence and Turn. Confidence held 2 on all 1,524 rows of "
                 "hill_iphone15pro_ios26. Vehicle Exit State and Turn held 0 on every row of all "
                 "three tested images. Vehicle Type is empty on every row of iphone11_ios17, whose "
                 "iOS 17.3 table has no vehicleType column; a column the table lacks is read as "
                 "empty rather than costing the query its rows. The same database holds "
                 "StepCountHistory and ElevationHistory on all three tested images and "
                 "PednetHistory on the two iOS 26 images. They are not read here. On the two iOS "
                 "26 images the step samples that Health - Steps reads from healthdb_secure.sqlite "
                 "start about six and a half months before the first StepCountHistory row and end "
                 "within 11 seconds of the last one; the StepCountHistory count did not decrease "
                 "from one row to the next on any of the three images, over 2, 4 and 9 days. The "
                 "two stores were not compared value by value. StrideCalHistory, "
                 "ExerciseMinuteHistory, MobilityWalkingBoutHistory, MaxMetsProcessingHistory, "
                 "MotionAlarm and ActiveConfig were empty on all three tested images."),
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
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import artifact_processor, does_table_exist_in_db, get_sqlite_db_records, \
    is_sqlite_sidecar

_EPOCH_2001 = datetime(2001, 1, 1, tzinfo=timezone.utc)

_COLUMNS = ('startTime', 'timestamp', 'type', 'confidence', 'isMoving', 'isVehicular', 'vehicleType',
            'vehicularFlagsData', 'vehicleExitState', 'mounted', 'mountedConfidence', 'turn', 'id')


def _start(value):
    '''startTime, seconds since 2001, as UTC with its fraction kept; a missing or non-positive
    value stays blank.'''
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return ''
    try:
        return _EPOCH_2001 + timedelta(seconds=value)
    except OverflowError:
        return ''


@artifact_processor
def locationdMotionStateHistory(context):
    data_headers = (
        ('Start Time', 'datetime'), 'Timestamp (as stored)', 'Type (as stored)',
        'Confidence (as stored)',
        'Is Moving (as stored)', 'Is Vehicular (as stored)', 'Vehicle Type (as stored)',
        'Vehicular Flags (as stored)', 'Vehicle Exit State (as stored)', 'Mounted (as stored)',
        'Mounted Confidence (as stored)', 'Turn (as stored)', 'Row ID')
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
