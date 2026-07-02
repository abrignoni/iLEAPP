__artifacts_v2__ = {
    "findMy": {
        "name": "Find My iPhone Settings",
        "description": "Find My iPhone account settings (FMIPAccounts.plist)",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.icloud.findmydeviced.FMIPAccounts.plist',),
        "output_types": "standard",
        "artifact_icon": "map-pin"
    }
}

import plistlib
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def findMy(context):
    data_headers = ('Key', 'Value')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('FMIPAccounts.plist'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    with open(source_path, 'rb') as fp:
        pl = plistlib.load(fp)

    for key, val in pl.items():
        if key == 'addTime':
            try:
                val = datetime.fromtimestamp(val, tz=timezone.utc)
                key = 'Find My iPhone Add Time'
            except (TypeError, ValueError, OSError):
                pass
        data_list.append((key, val))

    return data_headers, data_list, context.get_relative_path(source_path)
