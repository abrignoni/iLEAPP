__artifacts_v2__ = {
    "get_backupSettings": {
        "name": "Backup Settings",
        "description": "Extracts Backup settings from the device",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2024-05-09",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.mobile.ldbackup.plist',),
        "output_types": "all"
    }
}

import plistlib
from datetime import datetime
from scripts.ilapfuncs import artifact_processor, logfunc, logdevinfo, timestampsconv

@artifact_processor
def get_backupSettings(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])
    
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        if len(pl) > 0:
            for key, val in pl.items():
                if key == 'LastiTunesBackupDate':
                    lastime = timestampsconv(val)
                    data_list.append(('Last iTunes Backup Date', lastime))
                    logdevinfo(f"<b>Last iTunes Backup Date: </b>{lastime}")
                elif key == 'LastiTunesBackupTZ':
                    data_list.append((key, val))
                    logdevinfo(f"<b>Last iTunes Backup TZ: </b>{val}")
                elif key == 'LastCloudBackupDate':
                    lastcloudtime = timestampsconv(val)
                    data_list.append(('Last Cloud iTunes Backup Date', lastcloudtime))
                    logdevinfo(f"<b>Last Cloud iTunes Backup Date: </b>{lastcloudtime}")
                elif key == 'LastCloudBackupTZ':
                    data_list.append((key, val))
                    logdevinfo(f"<b>Last Cloud iTunes Backup TZ: </b>{val}")
                elif key == 'CloudBackupEnabled':
                    data_list.append((key,val))
                    logdevinfo(f"<b>Cloud Backup Enabled: </b>{val}")
                else:
                    data_list.append((key, val ))
        else:
            logfunc('No iPhone Backup Settings available')
                
        data_headers = ('Key', 'Data')
        return data_headers, data_list, source_path
            
