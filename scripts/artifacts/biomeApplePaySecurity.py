__artifacts_v2__ = {
    "biomeDbAppOpenings": {
        "name": "Biome DB - App Openings",
        "description": "Per-launch application records (bundle ID, event time, launch type) pre-aggregated by Apple "
                       "in the ApplePay.Security.Features Biome database.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go. "
                 "Table availability varies by iOS version; missing tables are skipped with a log message.",
        "paths": ('*/Biome/databases/ApplePay.Security.Features/ApplePay.Security.Features.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "package",
    },
    "biomeDbAppOpeningsHourly": {
        "name": "Biome DB - App Openings (Hourly)",
        "description": "Hourly per-application launch counts pre-aggregated by Apple in the "
                       "ApplePay.Security.Features Biome database.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go. "
                 "Timestamps are normalized by Apple to the start of the hour.",
        "paths": ('*/Biome/databases/ApplePay.Security.Features/ApplePay.Security.Features.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "clock",
    },
    "biomeDbCablePlugEvents": {
        "name": "Biome DB - Cable Plug Events",
        "description": "Cable connection/disconnection events pre-aggregated by Apple in the "
                       "ApplePay.Security.Features Biome database.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go.",
        "paths": ('*/Biome/databases/ApplePay.Security.Features/ApplePay.Security.Features.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "activity",
    },
    "biomeDbBacklightEvents": {
        "name": "Biome DB - Backlight Events",
        "description": "Screen backlight level change events pre-aggregated by Apple in the "
                       "ApplePay.Security.Features Biome database.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go.",
        "paths": ('*/Biome/databases/ApplePay.Security.Features/ApplePay.Security.Features.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
    },
    "biomeDbButtonClicks": {
        "name": "Biome DB - Button Clicks (Daily)",
        "description": "Per-day hardware button click counts pre-aggregated by Apple in the "
                       "ApplePay.Security.Features Biome database.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go. "
                 "Timestamps are normalized by Apple to the start of the day.",
        "paths": ('*/Biome/databases/ApplePay.Security.Features/ApplePay.Security.Features.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
    "biomeDbMinBattery": {
        "name": "Biome DB - Minimum Battery (Daily)",
        "description": "Per-day minimum battery percentage pre-aggregated by Apple in the "
                       "ApplePay.Security.Features Biome database.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go. "
                 "Timestamps are normalized by Apple to the start of the day.",
        "paths": ('*/Biome/databases/ApplePay.Security.Features/ApplePay.Security.Features.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "activity",
    },
    "biomeDbCarPlay": {
        "name": "Biome DB - CarPlay Activity (Daily)",
        "description": "Per-day CarPlay activity counts pre-aggregated by Apple in the "
                       "ApplePay.Security.Features Biome database.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Based on research by North Loop Consulting: https://northloopconsulting.com/blog/f/ready-sets-go. "
                 "Timestamps are normalized by Apple to the start of the day.",
        "paths": ('*/Biome/databases/ApplePay.Security.Features/ApplePay.Security.Features.sqlite3*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    },
}

from scripts.ilapfuncs import (artifact_processor, get_sqlite_db_records, does_table_exist_in_db,
                               convert_unix_ts_to_utc, logfunc)

DB_BASENAME = 'ApplePay.Security.Features.sqlite3'


def _find_db(context):
    """Returns the main ApplePay.Security.Features.sqlite3 path, skipping the
    -fullRebuild variant and journal files."""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith(DB_BASENAME) and not file_found.endswith('-fullRebuild.sqlite3'):
            return file_found
    return ''


def _table_rows(context, table, query):
    """Runs the query when the source db and table exist; returns (rows, path)."""
    source_path = _find_db(context)
    if not source_path:
        return [], ''
    if not does_table_exist_in_db(source_path, table):
        # Table availability varies by iOS version
        logfunc(f'No {table} table in {source_path} (not populated on this iOS version)')
        return [], source_path
    return get_sqlite_db_records(source_path, query), source_path


@artifact_processor
def biomeDbAppOpenings(context):
    data_headers = (('Event Timestamp', 'datetime'), 'Bundle ID', 'Starting', 'Launch Type')
    data_list = []
    rows, source_path = _table_rows(context, 'AppOpeningsRawMatView', '''
        SELECT eventTimestamp, bundleID, starting, launchType
        FROM AppOpeningsRawMatView''')
    for row in rows:
        data_list.append((convert_unix_ts_to_utc(row[0]), row[1], row[2], row[3]))
    return data_headers, data_list, source_path


@artifact_processor
def biomeDbAppOpeningsHourly(context):
    data_headers = (('Hour (UTC)', 'datetime'), 'Bundle ID', 'Launch Type', 'App Open Count')
    data_list = []
    rows, source_path = _table_rows(context, 'AppOpeningsMatView', '''
        SELECT date_hour, bundleID, launchType, appOpenAcount
        FROM AppOpeningsMatView''')
    for row in rows:
        data_list.append((convert_unix_ts_to_utc(row[0]), row[1], row[2], row[3]))
    return data_headers, data_list, source_path


@artifact_processor
def biomeDbCablePlugEvents(context):
    data_headers = (('Event Timestamp', 'datetime'), 'Starting')
    data_list = []
    rows, source_path = _table_rows(context, 'PluginRawMatView', '''
        SELECT eventTimestamp, starting FROM PluginRawMatView''')
    for row in rows:
        data_list.append((convert_unix_ts_to_utc(row[0]), row[1]))
    return data_headers, data_list, source_path


@artifact_processor
def biomeDbBacklightEvents(context):
    data_headers = (('Event Timestamp', 'datetime'), 'Backlight Level')
    data_list = []
    rows, source_path = _table_rows(context, 'BacklightRawMatView', '''
        SELECT eventTimestamp, backlightLevel FROM BacklightRawMatView''')
    for row in rows:
        data_list.append((convert_unix_ts_to_utc(row[0]), row[1]))
    return data_headers, data_list, source_path


@artifact_processor
def biomeDbButtonClicks(context):
    data_headers = (('Date (UTC)', 'datetime'), 'Button Click Count', 'Reason')
    data_list = []
    rows, source_path = _table_rows(context, 'ButtonClickMatView', '''
        SELECT date, buttonClickCount, reason FROM ButtonClickMatView''')
    for row in rows:
        data_list.append((convert_unix_ts_to_utc(row[0]), row[1], row[2]))
    return data_headers, data_list, source_path


@artifact_processor
def biomeDbMinBattery(context):
    data_headers = (('Date (UTC)', 'datetime'), 'Minimum Battery Percentage')
    data_list = []
    rows, source_path = _table_rows(context, 'MinBatteryMatView', '''
        SELECT date, minBatteryPerc FROM MinBatteryMatView''')
    for row in rows:
        data_list.append((convert_unix_ts_to_utc(row[0]), row[1]))
    return data_headers, data_list, source_path


@artifact_processor
def biomeDbCarPlay(context):
    data_headers = (('Date (UTC)', 'datetime'), 'CarPlay Activity Count')
    data_list = []
    rows, source_path = _table_rows(context, 'CarPlayMatView', '''
        SELECT date, carPlayActivityCount FROM CarPlayMatView''')
    for row in rows:
        data_list.append((convert_unix_ts_to_utc(row[0]), row[1]))
    return data_headers, data_list, source_path
