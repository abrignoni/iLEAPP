__artifacts_v2__ = {
    "timezoneInfo": {
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
        "artifact_icon": "globe"
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    device_info,
    get_file_path,
    get_plist_file_content,
    convert_cocoa_core_data_ts_to_utc,
    logfunc
)


@artifact_processor
def timezoneInfo(context):
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
                device_info("Settings", "Last Bootstrap Timezone", val, source_path)

            elif key == 'lastBootstrapDate':
                times = convert_cocoa_core_data_ts_to_utc(val)
                data_list.append(('Last Bootstrap Date', times))
                device_info("Device Information", "Last Bootstrap Date", str(times), source_path)
            else:
                data_list.append((key, str(val)))

    data_headers = ('Property', 'Property Value')
    return data_headers, data_list, source_path
