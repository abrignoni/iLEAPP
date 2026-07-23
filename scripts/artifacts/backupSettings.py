__artifacts_v2__ = {
    "backupSettings": {
        "name": "Backup Settings",
        "description": "Extracts Backup settings",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-10-04",
        "last_update_date": "2025-10-29",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.mobile.ldbackup.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-floppy",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 8 rows",
            "dexter_ios18": "iOS 18.3.2 | 5 rows",
            "felix_ios17": "iOS 17.6.1 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 8 rows",
            "iphone12_ios18": "iOS 18.7 | 5 rows",
            "iphone14plus_ios18": "iOS 18.0 | 4 rows",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
            "abe_ios16": "iOS 16.5 | 6 rows",
            "felix23_ios16": "iOS 16.5 | 6 rows",
            "hickman_ios13": "iOS 13.3.1 | 7 rows",
            "hickman_ios14": "iOS 14.3 | 8 rows",
            "jess_ios15": "iOS 15.0.2 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 7 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, device_info, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def backupSettings(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "com.apple.mobile.ldbackup.plist")
    data_list = []
    
    pl = get_plist_file_content(source_path)
    for key, val in pl.items():
        if key == 'LastiTunesBackupDate':
            lastime = convert_cocoa_core_data_ts_to_utc(val)
            data_list.append(('Last iTunes Backup Date', lastime))
            device_info("Backup Settings", "Last iTunes Backup Date", lastime, source_path)
        elif key == 'LastiTunesBackupTZ':
            data_list.append((key, val))
            device_info("Backup Settings", "Last iTunes Backup TZ", val, source_path)
        elif key == 'LastCloudBackupDate':
            lastcloudtime = convert_cocoa_core_data_ts_to_utc(val)
            data_list.append(('Last Cloud iTunes Backup Date', lastcloudtime))
            device_info("Backup Settings", "Last Cloud iTunes Backup Date", lastcloudtime, source_path)
        elif key == 'LastCloudBackupTZ':
            data_list.append((key, val))
            device_info("Backup Settings", "Last Cloud iTunes Backup TZ", val, source_path)
        elif key == 'CloudBackupEnabled':
            data_list.append((key,val))
            device_info("Backup Settings", "Cloud Backup Enabled", val, source_path)
        else:
            data_list.append((key, val ))
                
    data_headers = ('Property', 'Property Value')
    return data_headers, data_list, source_path            
