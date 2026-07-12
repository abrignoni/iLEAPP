__artifacts_v2__ = {
    "recentApphistory": {
        "name": "CarPlay Recent App History",
        "description": "CarPlay recent app history from com.apple.CarPlayApp.plist",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "CarPlay",
        "notes": "Timestamps are Unix epoch seconds (UTC).",
        "paths": ('*/com.apple.CarPlayApp.plist',),
        "output_types": "standard",
        "artifact_icon": "navigation",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

import plistlib

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc


@artifact_processor
def recentApphistory(context):
    data_headers = (('Timestamp', 'datetime'), 'Bundle ID')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('com.apple.CarPlayApp.plist'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    with open(source_path, 'rb') as fp:
        plist = plistlib.load(fp)
    for bundle_id, timestamp in (plist.get('CARRecentAppHistory') or {}).items():
        try:
            ts = convert_unix_ts_to_utc(int(timestamp))
        except (ValueError, TypeError):
            ts = timestamp
        data_list.append((ts, bundle_id))

    return data_headers, data_list, context.get_relative_path(source_path)
