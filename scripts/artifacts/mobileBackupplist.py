__artifacts_v2__ = {
    "mobilebackupplist": {
        "name": "Mobile Backup Plist Settings com-apple-MobileBackup-plist",
        "description": "Parses basic data from */mobile/Library/Preferences/com.apple.MobileBackup.plist which"
                       " contains some important data related to a device Backup, device restore from iCloud Backup,"
                       " and or Quick Start Data Transfer.",
        "author": "Other Unknown contributors and Scott Koenig",
        "version": "2.0",
        "date": "2024-06-11",
        "requirements": "Acquisition that contains com.apple.MobileBackup.plist",
        "category": "Mobile Backup Plist",
        "notes": "",
        "paths": ('*/Library/Preferences/com.apple.MobileBackup.plist',),
        "output_types": "standard",
        "artifact_icon": "save"
    }
}

import plistlib

from scripts.ilapfuncs import artifact_processor

_SECTIONS = {
    'BackupStateInfo': ('isCloud', 'date', 'errors'),
    'RestoreInfo': ('BackupBuildVersion', 'DeviceBuildVersion', 'WasCloudRestore', 'RestoreDate'),
    'DeviceTransferInfo': ('BytesTransferred', 'RestoreDuration', 'FileTransferDuration',
                           'PreFlightDuration', 'SourceDeviceProtocolVersion', 'BuildVersion',
                           'FileTransferStartDate', 'ConnectionType', 'RestoreStartDate',
                           'SourceDeviceBuildVersion', 'FilesTransferred', 'PreFlightStartDate',
                           'SourceDeviceUDID'),
    'FSEventState': ('eventId', 'eventDatabaseUUID', 'dateCreated'),
}


@artifact_processor
def mobilebackupplist(context):
    data_headers = ('Key', 'Values')
    data_list = []

    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('com.apple.MobileBackup.plist'):
            source_path = file_found
            break
    if not source_path:
        return data_headers, data_list, ''

    with open(source_path, 'rb') as fp:
        pl = plistlib.load(fp)

    for section, keys in _SECTIONS.items():
        block = pl.get(section)
        if isinstance(block, dict):
            for key in keys:
                if key in block:
                    data_list.append((key, block[key]))

    return data_headers, data_list, source_path
