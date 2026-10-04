__artifacts_v2__ = {
    "iCloudWifi": {
        "name": "iCloud Wifi Networks",
        "description": "Wi-Fi network entries in Library/SyncedPreferences/com.apple.wifid.plist",
        "author": "@ydkhatri, @AlexisBrignoni, Codex",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Wifi Connections",
        "notes": "The plist read is Library/SyncedPreferences/com.apple.wifid.plist; "
                 "on the tested images it is present only on the iOS 12.4, 13.3.1 and 14.3 "
                 "images, holding an empty values dictionary on the first and two and three "
                 "networks on the other two, and the file was not present on the tested iOS "
                 "17.3, 18.7.8 and 26.5.2 images. The "
                 "earlier glob matched any com.apple.wifid.plist and so reported the unrelated "
                 "/System/Library/LaunchDaemons daemon configuration as the found file on most "
                 "images; the narrower path stops that. Every matching plist is read. "
                 "Added At is a text date with no zone recorded; it is reported as stored text and "
                 "its zone is not established. Added By and Enabled are reported as stored. "
                 "Whether these entries were synced through iCloud is not established by the "
                 "file. The values, SSID_STR and added_at keys read here are the ones "
                 "cheeky4n6monkey's sysdiagnose-wifi-icloud.py reads from the sysdiagnose file "
                 "WiFi/ICLOUD_com.apple.wifid.plist. Reference: cheeky4n6monkey (based on "
                 "research by M. Epifani, H. Mahalik), 'iOS_sysdiagnose_forensic_scripts', "
                 "https://github.com/cheeky4n6monkey/iOS_sysdiagnose_forensic_scripts/blob/f8ca96d4a3a6cdb57f920d8200812487d25003ec/sysdiagnose-wifi-icloud.py#L4",
        "paths": ('*/SyncedPreferences/com.apple.wifid.plist',),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows (plist present, values dictionary empty)",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "hickman_ios14": "iOS 14.3 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows (file not present)",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (file not present)",
            "hc_ios26": "iOS 26.5.2 | 0 rows (file not present)",
        }
    }
}

import plistlib

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def iCloudWifi(context):
    data_headers = ('added_at (as stored, no zone)', 'BSSID', 'SSID', 'Added By', 'Enabled')
    data_list = []

    sources = []
    for file_found in context.get_files_found():
        source_path = str(file_found)
        if not source_path.endswith('com.apple.wifid.plist'):
            continue
        with open(source_path, 'rb') as fp:
            pl = plistlib.load(fp)
        sources.append(context.get_relative_path(source_path))

        for val in pl.get('values', {}).values():
            if not isinstance(val, dict):
                continue
            info = val.get('value')
            if not isinstance(info, dict):
                continue
            added_at = str(info.get('added_at') or '')
            data_list.append((added_at, str(info.get('BSSID', 'Not Available')),
                              str(info.get('SSID_STR', 'Not Available')),
                              str(info.get('added_by', 'Not Available')),
                              str(info.get('enabled', 'Not Available'))))

    return data_headers, data_list, '\n'.join(sources)
