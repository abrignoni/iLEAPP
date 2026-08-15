__artifacts_v2__ = {
    "duckduckgo_history": {
        "name": "DuckDuckGo - Browsing History",
        "description": "Browsing history entries from the DuckDuckGo browser, with the page title, "
                       "the last visit time and the number of trackers the browser blocked on the page",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Read from the Core Data store History.sqlite. ZBROWSINGHISTORYENTRYMANAGEDOBJECT "
                 "holds one row per visited page with an aggregate visit count and blocked-tracker "
                 "count; the timestamps are Core Data (Cocoa) seconds. A store lacking the "
                 "ZCOOKIEPOPUPBLOCKED column and the tab history table has been observed in a "
                 "private sample; columns absent from a store are reported empty, not as No.",
        "paths": ('*/Library/Application Support/History.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | DuckDuckGo | 2 rows",
        },
    },
    "duckduckgo_page_visits": {
        "name": "DuckDuckGo - Page Visits",
        "description": "Individual page visits from the DuckDuckGo browser, each joined to its "
                       "history entry URL and, where present, the tab the visit belonged to",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-09",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "ZPAGEVISITMANAGEDOBJECT records one row per visit and links to a history entry and "
                 "to a tab history row, so a single page can appear several times with different "
                 "visit times. Timestamps are Core Data (Cocoa) seconds.",
        "paths": ('*/Library/Application Support/History.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | DuckDuckGo | 3 rows",
        },
    },
}

from scripts.ilapfuncs import (
    artifact_processor,
    convert_cocoa_core_data_ts_to_utc,
    get_file_path,
    get_sqlite_db_records, null_absent_columns,
    does_table_exist_in_db,
)


def _yes_no(value):
    '''Render a stored boolean, keeping absence empty.

    A NULL here usually means the store predates the column (null_absent_columns
    substituted it), so the file records nothing either way. Rendering that as
    "No" would turn absence into a negative finding.
    '''
    if value is None:
        return ''
    return 'Yes' if value else 'No'


@artifact_processor
def duckduckgo_history(context):
    source_path = get_file_path(context.get_files_found(), 'History.sqlite')
    data_list = []

    query = '''
    SELECT ZLASTVISIT, ZURL, ZTITLE, ZNUMBEROFTOTALVISITS, ZNUMBEROFTRACKERSBLOCKED,
           ZTRACKERSFOUND, ZBLOCKEDTRACKINGENTITIES, ZFAILEDTOLOAD, ZCOOKIEPOPUPBLOCKED
    FROM ZBROWSINGHISTORYENTRYMANAGEDOBJECT
    ORDER BY ZLASTVISIT
    '''
    for record in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record[0]),
            record[1],
            record[2],
            record[3],
            record[4],
            record[5],
            record[6],
            _yes_no(record[7]),
            _yes_no(record[8]),
        ))

    data_headers = (
        ('Last Visit', 'datetime'),
        'URL',
        'Title',
        'Total Visits',
        'Trackers Blocked',
        'Trackers Found',
        'Blocked Tracking Entities',
        'Failed To Load',
        'Cookie Popup Blocked',
    )
    return data_headers, data_list, source_path


@artifact_processor
def duckduckgo_page_visits(context):
    source_path = get_file_path(context.get_files_found(), 'History.sqlite')
    data_list = []

    # Some app versions have no ZTABHISTORYMANAGEDOBJECT table at all
    # (verified on the felix_ios17 image, which still holds page visits), and
    # even a LEFT JOIN against a missing table fails the whole query. Join it
    # only when the file carries it; the Tab ID column stays empty otherwise.
    if does_table_exist_in_db(source_path, 'ZTABHISTORYMANAGEDOBJECT'):
        tab_id = 't.ZTABID'
        tab_join = 'LEFT JOIN ZTABHISTORYMANAGEDOBJECT t ON v.ZTABHISTORY = t.Z_PK'
    else:
        tab_id = 'NULL'
        tab_join = ''

    query = f'''
    SELECT v.ZDATE, h.ZURL, h.ZTITLE, {tab_id} AS ZTABID
    FROM ZPAGEVISITMANAGEDOBJECT v
    LEFT JOIN ZBROWSINGHISTORYENTRYMANAGEDOBJECT h ON v.ZHISTORYENTRY = h.Z_PK
    {tab_join}
    ORDER BY v.ZDATE
    '''
    for record in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(record[0]),
            record[1],
            record[2],
            record[3],
        ))

    data_headers = (
        ('Visit Time', 'datetime'),
        'URL',
        'Title',
        'Tab ID',
    )
    return data_headers, data_list, source_path
