__artifacts_v2__ = {
    "mobileBackup": {
        "name": "Mobile Backup",
        "description": "Backup/restore info from com.apple.MobileBackup.plist (backup version, "
                       "iOS version at recovery, recovery date, and whether restored from iCloud)",
        "author": "@AlexisBrignoni",
        "version": "1.0",
        "date": "2026-06-23",
        "requirements": "none",
        "category": "Mobile Backup",
        "notes": "",
        "paths": ('*/Preferences/com.apple.MobileBackup.plist',),
        "output_types": "standard",
        "artifact_icon": "save"
    }
}

import plistlib

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def mobileBackup(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    data_headers = ('Key', 'Value')
    data_list = []

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('com.apple.MobileBackup.plist'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    with open(source_path, 'rb') as fp:
        pl = plistlib.load(fp)

    state = pl.get('BackupStateInfo', {})
    if isinstance(state, dict):
        for key in ('isCloud', 'date'):
            if key in state:
                data_list.append((key, state[key]))

    restore = pl.get('RestoreInfo', {})
    if isinstance(restore, dict):
        for key in ('BackupBuildVersion', 'DeviceBuildVersion', 'WasCloudRestore', 'RestoreDate'):
            if key in restore:
                data_list.append((key, restore[key]))

    return data_headers, data_list, source_path
