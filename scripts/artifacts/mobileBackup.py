import plistlib

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_mobileBackup(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])

    with open(file_found, 'rb') as fp:
        pl = plistlib.load(fp)

        if 'BackupStateInfo' in pl.keys():
            for key, val in pl['BackupStateInfo'].items():
                if key == 'isCloud':
                    data_list.append((key, val))
                if key == 'date':
                    data_list.append((key, val))

        if 'RestoreInfo' in pl.keys():
            for key, val in pl['RestoreInfo'].items():
                if key == 'BackupBuildVersion':
                    data_list.append((key, val))
                if key == 'DeviceBuildVersion':
                    data_list.append((key, val))
                if key == 'WasCloudRestore':
                    data_list.append((key, val))
                if key == 'RestoreDate':
                    data_list.append((key, val))

    data_headers = ('Key', 'Value')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_mobileBackup": {
        "name": "Mobile Backup",
        "description": "",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Mobile Backup",
        "notes": "",
        "paths": ('*/Preferences/com.apple.MobileBackup.plist',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
