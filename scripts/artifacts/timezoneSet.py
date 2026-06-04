__artifacts_v2__ = {
    "timezoneSet": {
        "name": "Timezone Set",
        "description": "Is the timezone set on the device?",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-10-04",
        "last_update_date": "2024-11-28",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/db/timed/Library/Preferences/com.apple.preferences.datetime.plist',),
        "output_types": "standard",
        "artifact_icon": "clock"
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
def timezoneSet(context):
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
