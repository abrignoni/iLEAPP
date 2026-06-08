# Author:  Multiple Contributors
# Version: 2.0
#
#   Description:
#   Parses basic data from */mobile/Library/Preferences/com.apple.MobileBackup.plist which contains some important data
#   related to a device Backup, device restore from iCloud Backup, and or Quick Start Data Transfer.

__artifacts_v2__ = {
    'Mobile_Backup_plist': {
        'name': 'Mobile Backup Plist Settings com-apple-MobileBackup-plist',
        'description': 'Parses basic data from */mobile/Library/Preferences/com.apple.MobileBackup.plist which'
                       ' contains some important data related to a device Backup, device restore from iCloud Backup,'
                       ' and or Quick Start Data Transfer.',
        'author': 'Other Unknown contributors and Scott Koenig',
        'version': '2.0',
        'date': '2024-06-11',
        'requirements': 'Acquisition that contains com.apple.MobileBackup.plist',
        'category': 'Mobile Backup Plist',
        'notes': '',
        'paths': '*/Library/Preferences/com.apple.MobileBackup.plist',
        'function': 'get_mobilebackupplist'
    }
}

import os
import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_mobilebackupplist(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
                if key == 'errors':
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

        if 'DeviceTransferInfo' in pl.keys():
            for key, val in pl['DeviceTransferInfo'].items():
                if key == 'BytesTransferred':
                    data_list.append((key, val))
                if key == 'RestoreDuration':
                    data_list.append((key, val))
                if key == 'FileTransferDuration':
                    data_list.append((key, val))
                if key == 'PreFlightDuration':
                    data_list.append((key, val))
                if key == 'SourceDeviceProtocolVersion':
                    data_list.append((key, val))
                if key == 'BuildVersion':
                    data_list.append((key, val))
                if key == 'FileTransferStartDate':
                    data_list.append((key, val))
                if key == 'ConnectionType':
                    data_list.append((key, val))
                if key == 'RestoreStartDate':
                    data_list.append((key, val))
                if key == 'SourceDeviceBuildVersion':
                    data_list.append((key, val))
                if key == 'FilesTransferred':
                    data_list.append((key, val))
                if key == 'PreFlightStartDate':
                    data_list.append((key, val))
                if key == 'SourceDeviceUDID':
                    data_list.append((key, val))

        if 'FSEventState' in pl.keys():
            for key, val in pl['FSEventState'].items():
                if key == 'eventId':
                    data_list.append((key, val))
                if key == 'eventDatabaseUUID':
                    data_list.append((key, val))
                if key == 'dateCreated':
                    data_list.append((key, val))

    description = ('Parses basic data from */mobile/Library/Preferences/com.apple.MobileBackup.plist which contains'
                   ' some important data related to a device Backup, device restore from iCloud Backup, and'
                   ' or Quick Start Data Transfer.')
    report = ArtifactHtmlReport('Mobile Backup Plist')
    report.start_artifact_report(report_folder, 'Mobile_Backup_plist', description)
    report.add_script()
    data_headers = ('Key', 'Values')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    
    tsvname = 'Mobile_Backup_plist'
    tsv(report_folder, data_headers, data_list, tsvname)
