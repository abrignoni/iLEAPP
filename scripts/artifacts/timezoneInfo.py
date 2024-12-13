__artifacts_v2__ = {
    "timezoneInfo": {
        "name": "Timezone Information",
        "description": "Timezone Information",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2023-10-03",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.AppStore.plist',),
        "output_types": ["html", "tsv", "lava"]
    }
}


import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, device_info, webkit_timestampsconv

@artifact_processor
def timezoneInfo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])
    
    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == 'lastBootstrapTimeZone':
                data_list.append(('lastBootstrapTimeZone', val))
                device_info("Settings", "Last Bootstrap Timezone", val, source_path)
                
            elif key == 'lastBootstrapDate':
                times = webkit_timestampsconv(val)
                data_list.append(('lastBootstrapDate', times))
                device_info("Device Information", "Last Bootstrap Date", times, source_path)
                
            else:
                data_list.append((key, val ))
                
    data_headers = ('Property','Property Value' )     
    return data_headers, data_list, source_path
