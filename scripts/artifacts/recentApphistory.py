__artifacts_v2__ = {
    "recentApphistory": {
        "name": "CarPlay Recent App History",
        "description": "CarPlay recent app history from com.apple.CarPlayApp.plist",
        "author": "",
        "version": "2.0",
        "date": "2026-06-23",
        "requirements": "none",
        "category": "CarPlay",
        "notes": "Timestamps are Unix epoch seconds (UTC).",
        "paths": ('*/com.apple.CarPlayApp.plist',),
        "output_types": "standard",
        "artifact_icon": "navigation"
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
