__artifacts_v2__ = {
    "backupSettings": {
        "name": "Backup Settings",
        "description": "Extracts Backup settings",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-10-04",
        "last_update_date": "2024-12-20",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.mobile.ldbackup.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "save"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, device_info, convert_cocoa_core_data_ts_to_utc

@artifact_processor
def backupSettings(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
