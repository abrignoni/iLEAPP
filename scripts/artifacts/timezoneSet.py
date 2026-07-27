""" timezoneSet """
__artifacts_v2__ = {
    "timezone_set": {
        "name": "Timezone Set",
        "description": "Is the timezone set on the device?",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-10-04",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/db/timed/Library/Preferences/com.apple.preferences.datetime.plist',),
        "output_types": ["html","lava","tsv"],
        "artifact_icon": "clock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
        }
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    device_info,
    get_file_path,
    get_plist_file_content,
    logfunc
)


@artifact_processor
def timezone_set(context):
    """ see artifact description """
    files_found = context.get_files_found()
    data_list = []

    source_path = get_file_path(files_found, 'com.apple.preferences.datetime.plist')

    if not source_path:
        logfunc('com.apple.preferences.datetime.plist not found')
        return (), [], ''

    pl = get_plist_file_content(source_path)

    if pl:
        val = pl.get('timezoneset')
        if val is not None:
            device_info("Settings", "Timezone Set", str(val), source_path)
            data_list.append(('Timezone Set', str(val)))

    data_headers = ('Key', 'Value')
    return data_headers, data_list, source_path
