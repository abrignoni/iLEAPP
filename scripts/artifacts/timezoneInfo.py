""" timezoneInfo """
__artifacts_v2__ = {
    "timezone_info": {
        "name": "Timezone Information",
        "description": "Timezone Information extracted from AppStore plist.",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-10-02",
        "last_update_date": "2024-11-28",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.AppStore.plist',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 16 rows",
            "dexter_ios18": "iOS 18.3.2 | 13 rows",
            "felix_ios17": "iOS 17.6.1 | 17 rows",
            "hc_ios18_7": "iOS 18.7.8 | 14 rows",
            "iphone11_ios17": "iOS 17.3 | 13 rows",
            "iphone12_ios18": "iOS 18.7 | 14 rows",
            "iphone14plus_ios18": "iOS 18.0 | 14 rows",
            "otto_ios17": "iOS 17.5.1 | 19 rows",
            "abe_ios16": "iOS 16.5 | 17 rows",
            "felix23_ios16": "iOS 16.5 | 17 rows",
            "hickman_ios13": "iOS 13.3.1 | 11 rows",
            "hickman_ios14": "iOS 14.3 | 13 rows",
            "jess_ios15": "iOS 15.0.2 | 14 rows",
            "magnet_ios16": "iOS 16.1.1 | 14 rows",
        }
    }
}

from datetime import datetime

from scripts.ilapfuncs import (
    artifact_processor,
    device_info,
    get_file_path,
    get_plist_file_content,
    convert_cocoa_core_data_ts_to_utc,
    logfunc
)


@artifact_processor
def timezone_info(context):
    """ see artifact description """
    files_found = context.get_files_found()
    data_list = []

    source_path = get_file_path(files_found, 'com.apple.AppStore.plist')

    if not source_path:
        logfunc('com.apple.AppStore.plist not found')
        return (), [], ''

    pl = get_plist_file_content(source_path)

    if pl:
        for key, val in pl.items():
            if key == 'lastBootstrapTimeZone':
                data_list.append(('Last Bootstrap Timezone', val))
                device_info("Settings", "Last Bootstrap Timezone", str(val), source_path)

            elif key == 'lastBootstrapDate':
                if isinstance(val, datetime):
                    times = val
                else:
                    times = convert_cocoa_core_data_ts_to_utc(val)
                data_list.append(('Last Bootstrap Date', times))
                device_info("Device Information", "Last Bootstrap Date", str(times), source_path)
            else:
                data_list.append((key, str(val)))

    data_headers = ('Property', 'Property Value')
    return data_headers, data_list, source_path
