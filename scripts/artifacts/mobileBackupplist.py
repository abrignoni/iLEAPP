__artifacts_v2__ = {
    "mobilebackupplist": {
        "name": "Mobile Backup Plist Settings com-apple-MobileBackup-plist",
        "description": "Parses basic data from */mobile/Library/Preferences/com.apple.MobileBackup.plist which"
                       " contains some important data related to a device Backup, device restore from iCloud Backup,"
                       " and or Quick Start Data Transfer.",
        "author": "Other Unknown contributors and Scott Koenig",
        "creation_date": "2024-06-11",
        "last_update_date": "2026-06-24",
        "requirements": "Acquisition that contains com.apple.MobileBackup.plist",
        "category": "Mobile Backup Plist",
        "notes": "",
        "paths": ('*/Library/Preferences/com.apple.MobileBackup.plist',
                  '*/Preferences/com.apple.MobileBackup.plist'),
        "output_types": "standard",
        "artifact_icon": "device-floppy"
    }
}

import json
import plistlib
from datetime import datetime

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
    data_headers = ('Key', 'Value')
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
                    value = block[key]
                    if isinstance(value, datetime):
                        # plist <date> values are UTC; store as a UTC string (the generic
                        # 'Value' column is not datetime-typed, so a datetime would not
                        # be JSON-serializable for LAVA).
                        value = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(value, bytes):
                        value = value.hex()
                    elif isinstance(value, (dict, list)):
                        # default=str handles nested datetimes/bytes that LAVA's json.dumps cannot.
                        value = json.dumps(value, default=str)
                    data_list.append((key, value))

    return data_headers, data_list, context.get_relative_path(source_path)
