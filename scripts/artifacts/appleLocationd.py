__artifacts_v2__ = {
    "appleLocationd": {
        "name": "Location Services",
        "description": "Extracts location services settings",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-10-03",
        "last_update_date": "2024-12-20",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.locationd.plist', ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "navigation"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, device_info, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def appleLocationd(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "com.apple.locationd.plist")
    data_list = []

    pl = get_plist_file_content(source_path)
    for key, val in pl.items():
        if key == 'LocationServicesEnabledIn8.0':
            data_list.append(('Location Services Enabled', val))
            device_info("Settings", "Location Services Enabled", val, source_path)
        
        elif key == 'LastSystemVersion':
            data_list.append(('Last System Version', val))
            device_info("Settings", "Last System Version", val, source_path)
            
        elif key == 'steadinessClassificationNextClassificationTime' or key == 'VO2MaxCloudKitLastForcedFetch' \
            or key == 'kP6MWDNextEstimateTime' or key == 'VO2MaxCloudKitManagerNextActivityTime':
            val = convert_cocoa_core_data_ts_to_utc(val)
            data_list.append((key, val))
        else:
            data_list.append((key, val))
                
    data_headers = ('Property', 'Property Value')     
    return data_headers, data_list, source_path
