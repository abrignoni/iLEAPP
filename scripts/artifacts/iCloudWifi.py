__artifacts_v2__ = {
    "iCloudWifi": {
        "name": "iCloud Wifi Networks",
        "description": "Wi-Fi networks synced via iCloud (com.apple.wifid.plist)",
        "author": "@ydkhatri",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "Wifi Connections",
        "notes": "The synced-data plist lives at Library/SyncedPreferences/com.apple.wifid.plist "
                 "and, in the only local test image carrying it (iOS 12.4), holds an empty values "
                 "dictionary. The earlier glob matched any com.apple.wifid.plist and so reported "
                 "the unrelated /System/Library/LaunchDaemons daemon configuration as the found "
                 "file on most images; the narrower path stops that. "
                 "Reference: cheeky4n6monkey (based on research by M. Epifani, H. Mahalik), "
                 "'iOS_sysdiagnose_forensic_scripts', "
                 "https://github.com/cheeky4n6monkey/iOS_sysdiagnose_forensic_scripts",
        "paths": ('*/SyncedPreferences/com.apple.wifid.plist',),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows (plist present, values dictionary empty)",
            "iphone11_ios17": "iOS 17.3 | 0 rows (file not present)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (file not present)",
            "hc_ios26": "iOS 26.5.2 | 0 rows (file not present)",
        }
    }
}

import plistlib
from datetime import datetime

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def iCloudWifi(context):
    data_headers = ('BSSID', 'SSID', 'Added By', 'Enabled', ('Added At', 'datetime'))
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('com.apple.wifid.plist'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    with open(source_path, 'rb') as fp:
        pl = plistlib.load(fp)

    for val in pl.get('values', {}).values():
        if not isinstance(val, dict):
            continue
        info = val.get('value')
        if not isinstance(info, dict):
            continue
        added_at = info.get('added_at')
        if added_at:
            try:
                added_at = datetime.strptime(str(added_at), '%b  %d %Y %H:%M:%S')
            except ValueError:
                added_at = str(added_at)
        else:
            added_at = ''
        data_list.append((str(info.get('BSSID', 'Not Available')),
                          str(info.get('SSID_STR', 'Not Available')),
                          str(info.get('added_by', 'Not Available')),
                          str(info.get('enabled', 'Not Available')),
                          added_at))

    return data_headers, data_list, context.get_relative_path(source_path)
