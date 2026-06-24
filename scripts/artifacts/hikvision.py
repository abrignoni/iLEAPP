"""
Developed by Evangelos D. (@theAtropos4n6)

Research for this artifact was conducted by Evangelos Dragonas, Costas Lambrinoudakis
and Michael Kotsis.

Hikvision is a well-known app used to remotely access/operate CCTV systems. The
following information can be interpreted:
- Hikvision - CCTV Channels: the available CCTV record channels.
- Hikvision - CCTV Info: information about the CCTV system.
- Hikvision - CCTV Activity: user interaction with the app. User actions are not easy
  to attribute but can indirectly indicate remote live view/play back of CCTV footage.
- Hikvision - User Created Media: media files the user created while viewing CCTV footage.
"""
__artifacts_v2__ = {
    "hikvisionChannels": {
        "name": "Hikvision - CCTV Channels",
        "description": "Available CCTV record channels from the Hikvision app",
        "author": "Evangelos D. (@theAtropos4n6)",
        "creation_date": "2023-03-27",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Hikvision",
        "notes": "",
        "paths": ('*/Documents/database.hik*',),
        "output_types": "standard",
        "artifact_icon": "video"
    },
    "hikvisionInfo": {
        "name": "Hikvision - CCTV Info",
        "description": "Information about the CCTV system from the Hikvision app",
        "author": "Evangelos D. (@theAtropos4n6)",
        "creation_date": "2023-03-27",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Hikvision",
        "notes": "",
        "paths": ('*/Documents/database.hik*',),
        "output_types": "standard",
        "artifact_icon": "info"
    },
    "hikvisionActivity": {
        "name": "Hikvision - CCTV Activity",
        "description": "User interaction with the Hikvision app (live view / play back)",
        "author": "Evangelos D. (@theAtropos4n6)",
        "creation_date": "2023-03-27",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Hikvision",
        "notes": "",
        "paths": ('*/Documents/DCLOG/YSDCLogItem.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "hikvisionMedia": {
        "name": "Hikvision - User Created Media",
        "description": "Media files the user created while viewing CCTV footage",
        "author": "Evangelos D. (@theAtropos4n6)",
        "creation_date": "2023-03-27",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Hikvision",
        "notes": "Media are stored under Documents/YYYY/MM/DD within the app container.",
        "paths": ('*/Documents/*/*/*/*.jpg', '*/Documents/*/*/*/*.mov', '*/Documents/*/*/*/*.mp4'),
        "output_types": "standard",
        "artifact_icon": "film"
    }
}

import os
import re
import sqlite3

from scripts.ilapfuncs import artifact_processor, check_in_media, get_sqlite_db_records, logfunc


def _find(context, filename):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.basename(file_found) == filename:
            return file_found
    return ''


@artifact_processor
def hikvisionChannels(context):
    data_headers = ('Device ID', 'Channel No.', 'Channel Name', 'Status')
    data_list = []
    source_path = _find(context, 'database.hik')
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        nDeviceID,
        nChannelNo,
        chChannelName,
        CASE nEnable WHEN '0' THEN 'Disabled' WHEN '1' THEN 'Enabled' END
    FROM ChannelInfo
    '''
    try:
        rows = get_sqlite_db_records(source_path, query)
    except sqlite3.Error as ex:
        logfunc(f'Error reading Hikvision channels: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for row in rows:
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def hikvisionInfo(context):
    data_headers = ('ID', 'Name/IP', 'Serial Number', 'Port', 'Channels', 'DDNS Address', 'DDNS Port')
    data_list = []
    source_path = _find(context, 'database.hik')
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        nDeviceID,
        chDeviceName,
        chDeviceSerialNo,
        nDevicePort,
        nChannelNum,
        chDDNSAddr,
        nDDNSPort
    FROM DeviceInfo
    '''
    try:
        rows = get_sqlite_db_records(source_path, query)
    except sqlite3.Error as ex:
        logfunc(f'Error reading Hikvision info: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for row in rows:
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def hikvisionActivity(context):
    data_headers = (('Timestamp', 'datetime'), 'Record Type', 'Activity')
    data_list = []
    source_path = _find(context, 'YSDCLogItem.sqlite')
    if not source_path:
        return data_headers, data_list, ''

    query = '''
    SELECT
        datetime(time/1000, 'unixepoch'),
        systemName,
        data
    FROM YSDCLogItem
    '''
    try:
        rows = get_sqlite_db_records(source_path, query)
    except sqlite3.Error as ex:
        logfunc(f'Error reading Hikvision activity: {ex}')
        return data_headers, data_list, context.get_relative_path(source_path)

    for row in rows:
        data_list.append(tuple(row))

    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def hikvisionMedia(context):
    data_headers = ('File Path', 'File Name', ('File Content', 'media'))
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
        if not file_name.endswith(('.jpg', '.mov', '.mp4')):
            continue

        # Ensure the media file belongs to the app: Documents/YYYY/MM/DD/<file>
        parts = re.split(r'[\\/]', file_found)
        if len(parts) <= 5:
            continue
        if (parts[-5] != 'Documents'
                or not (parts[-4].isdigit() and len(parts[-4]) == 4)
                or not (parts[-3].isdigit() and len(parts[-3]) == 2)
                or not (parts[-2].isdigit() and len(parts[-2]) == 2)):
            continue

        media_ref = check_in_media(file_found, file_name)
        rel_path = context.get_relative_path(file_found)
        data_list.append((rel_path, file_name, media_ref))
        sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
