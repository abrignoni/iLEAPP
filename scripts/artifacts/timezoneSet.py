__artifacts_v2__ = {
    "timezoneSet": {
        "name": "Timezone Set",
        "description": "Is the timezone set on the device?",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2023-10-04",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/db/timed/Library/Preferences/com.apple.preferences.datetime.plist',),
        "output_types": "none"
    }
}


import plistlib
from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def timezoneSet(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = str(files_found[0])
    
    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == 'timezoneset':
                device_info("Settings", "Timezone Set", val, source_path)
                break

    # Return empty data since this artifact only collects device info
    return (), [], source_path
