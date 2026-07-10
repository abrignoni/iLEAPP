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
        "artifact_icon": "map-pin",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 5 rows",
            "dexter_ios18": "iOS 18.3.2 | 5 rows",
            "felix_ios17": "iOS 17.6.1 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 6 rows",
            "hc_ios18_7": "iOS 18.7.8 | 6 rows",
            "iphone11_ios17": "iOS 17.3 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 5 rows",
            "iphone14plus_ios18": "iOS 18.0 | 5 rows",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
        }
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
