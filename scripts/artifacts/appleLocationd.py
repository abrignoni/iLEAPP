__artifacts_v2__ = {
    "appleLocationd": {
        "name": "Location Services",
        "description": "Extracts location services settings",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-10-03",
        "last_update_date": "2025-10-08",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.locationd.plist', ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "navigation",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 5 rows",
            "dexter_ios18": "iOS 18.3.2 | 11 rows",
            "felix_ios17": "iOS 17.6.1 | 10 rows",
            "fsfull002_ios17": "iOS 17.1 | 11 rows",
            "hc_ios18_7": "iOS 18.7.8 | 10 rows",
            "iphone11_ios17": "iOS 17.3 | 12 rows",
            "iphone12_ios18": "iOS 18.7 | 10 rows",
            "iphone14plus_ios18": "iOS 18.0 | 9 rows",
            "otto_ios17": "iOS 17.5.1 | 12 rows",
            "abe_ios16": "iOS 16.5 | 11 rows",
            "felix23_ios16": "iOS 16.5 | 10 rows",
            "hickman_ios13": "iOS 13.3.1 | 7 rows",
            "hickman_ios14": "iOS 14.3 | 6 rows",
            "jess_ios15": "iOS 15.0.2 | 8 rows",
            "magnet_ios16": "iOS 16.1.1 | 10 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, device_info, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def appleLocationd(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "com.apple.locationd.plist")
    data_list = []

    pl = get_plist_file_content(source_path)
    
    # Check if plist is valid before processing
    if not pl or not isinstance(pl, dict):
        return (), [], ''
    
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
