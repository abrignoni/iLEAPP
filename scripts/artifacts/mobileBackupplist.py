# Author:  Multiple Contributors
# Version: 2.0
#
#   Description:
#   Parses basic data from */mobile/Library/Preferences/com.apple.MobileBackup.plist which contains some important data
#   related to a device Backup, device restore from iCloud Backup, and or Quick Start Data Transfer.

import plistlib

from scripts.ilapfuncs import artifact_processor


@artifact_processor
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
                if key in ('BytesTransferred', 'RestoreDuration', 'FileTransferDuration',
                          'PreFlightDuration', 'SourceDeviceProtocolVersion', 'BuildVersion',
                          'FileTransferStartDate', 'ConnectionType', 'RestoreStartDate',
                          'SourceDeviceBuildVersion', 'FilesTransferred', 'PreFlightStartDate',
                          'SourceDeviceUDID'):
                    data_list.append((key, val))

        if 'FSEventState' in pl.keys():
            for key, val in pl['FSEventState'].items():
                if key in ('eventId', 'eventDatabaseUUID', 'dateCreated'):
                    data_list.append((key, val))

    data_headers = ('Key', 'Values')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    'get_mobilebackupplist': {
        'name': 'Mobile Backup Plist Settings',
        'description': 'Parses basic data from */mobile/Library/Preferences/com.apple.MobileBackup.plist which'
                       ' contains some important data related to a device Backup, device restore from iCloud Backup,'
                       ' and or Quick Start Data Transfer.',
        'author': 'Other Unknown contributors and Scott Koenig',
        'version': '2.0',
        'date': '2024-06-11',
        'requirements': 'Acquisition that contains com.apple.MobileBackup.plist',
        'category': 'Mobile Backup Plist',
        'notes': '',
        'paths': ('*/Library/Preferences/com.apple.MobileBackup.plist',),
        'output_types': 'all',
        'artifact_icon': 'alert-triangle'
    }
}
