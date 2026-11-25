__artifacts_v2__ = {
    "calculatorHistory": {
        "name": "Calculator - History",
        "description": "Calculations kept in the history of Apple's Calculator app: the time, the "
                       "mode, the input and the result of each record.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Device Activity",
        "notes": "One row per row of ZHISTORYRECORD in default.store, the Core Data store in the "
                 "Calculator app's data container. A default.store is read only when the "
                 "container's metadata plist names com.apple.calculator and the store has a "
                 "ZHISTORYRECORD table with a ZRESULTVALUE column, so a container without its "
                 "metadata plist is not read. No Apple documentation of this store was found, so "
                 "the column names are the only labels used here. Values other than Timestamp are "
                 "reported as stored, with NULL shown as empty; ZID is not shown. Timestamp is "
                 "ZTIMESTAMP read as Core Data seconds since 2001 and shown in UTC to the second; "
                 "on every row of the tested images it is within 0.02 seconds of the persistent "
                 "history transaction that inserted the row. Input holds the expression as text. "
                 "On the tested images operands of 1,000 or more carry grouping commas (2 rows), "
                 "and on 1 row the first operand is in the same integer and exponent form as "
                 "Result and matches the Result of the row before it. On the tested images Result "
                 "is text shaped as an integer, the letter E and a negative exponent (the shape "
                 "1234E-2, which read as a power of ten is 12.34); on all 4 rows, read that way, "
                 "it equals the sum the Input spells out, with the Input operand on 1 row read the "
                 "same way. Mode held basic on every row, the unit ID columns were empty on every "
                 "row, and Is Currency, Is RPN and Assume Degrees held 0, 0 and 1 on every row. No "
                 "tested image holds a record made in another mode, so what these columns hold "
                 "there is not established. The persistent history tables of the store record only "
                 "inserts on the tested images, and the primary key counter equals the row count "
                 "on both, so these stores show no deleted record; what clearing the history "
                 "leaves behind was not tested. hill_iphone15pro_ios26 holds 3 rows and "
                 "wilkerson_iphone16_ios26 holds 1. On both, the database file without its "
                 "write-ahead log holds none of them: the rows come from the -wal, which SQLite "
                 "reads when it is beside the database. iphone11_ios17 (iOS 17.3) has a Calculator "
                 "container with no default.store.",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/Application Support/default.store*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "hash",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 3 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 0 rows, no default.store in the Calculator container",
        },
    }
}


import os
import plistlib

from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc,
                               does_column_exist_in_db, get_sqlite_db_records, is_sqlite_sidecar,
                               logfunc)

_BUNDLE_ID = 'com.apple.calculator'


def _owner(store):
    '''The container's bundle ID from its metadata plist, or '' when it cannot be read.'''
    container = store.split(os.sep + 'Library' + os.sep + 'Application Support')[0]
    metadata = os.path.join(container, '.com.apple.mobile_container_manager.metadata.plist')
    if not os.path.isfile(metadata):
        return ''
    try:
        with open(metadata, 'rb') as handle:
            value = plistlib.load(handle).get('MCMMetadataIdentifier', '')
    except (plistlib.InvalidFileException, ValueError, OSError) as error:
        logfunc(f'Calculator: could not read {metadata}: {error}')
        return ''
    return value if isinstance(value, str) else ''


def _utc(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return ''
    return convert_cocoa_core_data_ts_to_utc(value)


def _text(value):
    return '' if value is None else value


@artifact_processor
def calculatorHistory(context):
    data_list, sources = [], []
    for found in sorted(str(path) for path in context.get_files_found()):
        if os.path.basename(found) != 'default.store' or is_sqlite_sidecar(found):
            continue
        if _owner(found) != _BUNDLE_ID:
            continue
        if not does_column_exist_in_db(found, 'ZHISTORYRECORD', 'ZRESULTVALUE'):
            continue
        sources.append(found)
        for row in get_sqlite_db_records(found, '''
                SELECT ZTIMESTAMP, ZMODE, ZINPUTVALUE, ZRESULTVALUE, ZINPUTUNITID, ZRESULTUNITID,
                       ZISCURRENCY, ZISRPN, ZASSUMEDEGREES
                FROM ZHISTORYRECORD
                ORDER BY ZTIMESTAMP, Z_PK'''):
            data_list.append((_utc(row[0]),) + tuple(_text(value) for value in row[1:]))
    data_headers = (('Timestamp', 'datetime'), 'Mode', 'Input', 'Result (as stored)',
                    'Input Unit ID', 'Result Unit ID', 'Is Currency (as stored)',
                    'Is RPN (as stored)', 'Assume Degrees (as stored)')
    return data_headers, data_list, '\n'.join(sources)
