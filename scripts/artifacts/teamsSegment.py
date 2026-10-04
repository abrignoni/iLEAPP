__artifacts_v2__ = {
    "teamsSegmentLocations": {
        "name": "Microsoft Teams - Locations",
        "description": "Location records from the JSON-lines files under "
                       "Library/DriveIQ/segments/current in the Microsoft Teams app container",
        "author": "@abrignoni",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Microsoft Teams",
        "notes": "Rows come only from an app container whose "
                 ".com.apple.mobile_container_manager.metadata.plist records MCMMetadataIdentifier "
                 "com.microsoft.skype.teams. A DriveIQ folder in a container that records another "
                 "identifier, or whose metadata plist is absent or unreadable, is skipped and named "
                 "in the run log. On hickman_ios14, the one registered image found to hold such a "
                 "folder, its container records com.microsoft.skype.teams, so the skip is "
                 "unexercised on the registered images. What DriveIQ is was not established; the "
                 "name is the folder's. Timestamp is the record's sourceTimestamp value read as UTC",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/DriveIQ/segments/current/*.*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | Microsoft Teams 2.3.1 | 53 rows",
        }
    },
    "teamsSegmentMotion": {
        "name": "Microsoft Teams - Motion",
        "description": "Motion records from the JSON-lines files under Library/DriveIQ/segments/current in the "
                       "Microsoft Teams app container",
        "author": "@abrignoni",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Microsoft Teams",
        "notes": "Rows come only from an app container whose "
                 ".com.apple.mobile_container_manager.metadata.plist records MCMMetadataIdentifier "
                 "com.microsoft.skype.teams. A DriveIQ folder in a container that records another "
                 "identifier, or whose metadata plist is absent or unreadable, is skipped and named "
                 "in the run log. On hickman_ios14, the one registered image found to hold such a "
                 "folder, its container records com.microsoft.skype.teams, so the skip is "
                 "unexercised on the registered images. What DriveIQ is was not established; the "
                 "name is the folder's. Timestamp is the record's first element read as UTC",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/DriveIQ/segments/current/*.*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | Microsoft Teams 2.3.1 | 9 rows",
        }
    },
    "teamsSegmentTimezone": {
        "name": "Microsoft Teams - Timezone",
        "description": "timeCheck records from the JSON-lines files under Library/DriveIQ/segments/current in "
                       "the Microsoft Teams app container",
        "author": "@abrignoni",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Microsoft Teams",
        "notes": "Rows come only from an app container whose "
                 ".com.apple.mobile_container_manager.metadata.plist records MCMMetadataIdentifier "
                 "com.microsoft.skype.teams. A DriveIQ folder in a container that records another "
                 "identifier, or whose metadata plist is absent or unreadable, is skipped and named "
                 "in the run log. On hickman_ios14, the one registered image found to hold such a "
                 "folder, its container records com.microsoft.skype.teams, so the skip is "
                 "unexercised on the registered images. What DriveIQ is was not established; the "
                 "name is the folder's. Timestamp is the record's first element read as UTC",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/DriveIQ/segments/current/*.*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | Microsoft Teams 2.3.1 | 2 rows",
        }
    },
    "teamsSegmentPower": {
        "name": "Microsoft Teams - Power Log",
        "description": "Power records from the JSON-lines files under Library/DriveIQ/segments/current in the "
                       "Microsoft Teams app container",
        "author": "@abrignoni",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Microsoft Teams",
        "notes": "Rows come only from an app container whose "
                 ".com.apple.mobile_container_manager.metadata.plist records MCMMetadataIdentifier "
                 "com.microsoft.skype.teams. A DriveIQ folder in a container that records another "
                 "identifier, or whose metadata plist is absent or unreadable, is skipped and named "
                 "in the run log. On hickman_ios14, the one registered image found to hold such a "
                 "folder, its container records com.microsoft.skype.teams, so the skip is "
                 "unexercised on the registered images. What DriveIQ is was not established; the "
                 "name is the folder's. Timestamp is the record's first element read as UTC",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/DriveIQ/segments/current/*.*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | Microsoft Teams 2.3.1 | 36 rows",
        }
    },
    "teamsSegmentStateChange": {
        "name": "Microsoft Teams - State Change",
        "description": "stateChange records from the JSON-lines files under Library/DriveIQ/segments/current in "
                       "the Microsoft Teams app container",
        "author": "@abrignoni",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Microsoft Teams",
        "notes": "Rows come only from an app container whose "
                 ".com.apple.mobile_container_manager.metadata.plist records MCMMetadataIdentifier "
                 "com.microsoft.skype.teams. A DriveIQ folder in a container that records another "
                 "identifier, or whose metadata plist is absent or unreadable, is skipped and named "
                 "in the run log. On hickman_ios14, the one registered image found to hold such a "
                 "folder, its container records com.microsoft.skype.teams, so the skip is "
                 "unexercised on the registered images. What DriveIQ is was not established; the "
                 "name is the folder's. Timestamp is the record's first element read as UTC",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/DriveIQ/segments/current/*.*',
                  '*/mobile/Containers/Data/Application/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "repeat",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | Microsoft Teams 2.3.1 | 8 rows",
        }
    }
}

import json
import os
import plistlib

from scripts.ilapfuncs import artifact_processor, convert_ts_human_to_utc, logfunc

_METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'
_TEAMS_ID = 'com.microsoft.skype.teams'


def _container_ids(files_found):
    """{container directory: MCMMetadataIdentifier} from each container's own metadata plist."""
    containers = {}
    for found in files_found:
        path = str(found)
        if os.path.basename(path) != _METADATA_NAME or os.path.isdir(path):
            continue
        try:
            with open(path, 'rb') as handle:
                plist = plistlib.load(handle)
        except (plistlib.InvalidFileException, OSError, ValueError) as error:
            logfunc(f'Microsoft Teams DriveIQ: could not read a container metadata plist: {error}')
            continue
        if isinstance(plist, dict):
            containers[os.path.dirname(path).replace('\\', '/')] = plist.get('MCMMetadataIdentifier')
    return containers


def _seg_ts(value):
    """Normalize a DriveIQ ISO segment timestamp to aware UTC; pass empties/unparseable through."""
    if not value:
        return ''
    cleaned = str(value).replace('T', ' ').replace('Z', '').strip()
    try:
        return convert_ts_human_to_utc(cleaned)
    except (ValueError, TypeError):
        return value


def _iter_records(context):
    """Read all DriveIQ segment files and return (parsed JSON records, joined source paths)."""
    records = []
    sources = []
    containers = _container_ids(context.get_files_found())
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.basename(file_found) == _METADATA_NAME or os.path.isdir(file_found):
            continue
        # <container>/Library/DriveIQ/segments/current/<file>
        container = file_found.replace('\\', '/').rsplit('/Library/DriveIQ/', 1)[0]
        if containers.get(container) != _TEAMS_ID:
            logfunc(f'Microsoft Teams DriveIQ: skipped {context.get_relative_path(file_found)}; '
                    f'its container records identifier {containers.get(container)!r}, '
                    f'not {_TEAMS_ID}')
            continue
        try:
            with open(file_found, encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except OSError as ex:
            logfunc(f'Failed to read {file_found}: {ex}')
            continue
        sources.append(context.get_relative_path(file_found))
    return records, ', '.join(dict.fromkeys(sources))


@artifact_processor
def teamsSegmentLocations(context):
    data_headers = (('Timestamp', 'datetime'), 'Longitude', 'Latitude', 'Speed', 'Altitude',
                    'Vertical Accuracy', 'Horizontal Accuracy')
    data_list = []
    records, source_path = _iter_records(context)
    for serial in records:
        if len(serial) > 2 and serial[1] == 'location':
            payload = serial[2]
            data_list.append((
                _seg_ts(payload.get('sourceTimestamp', '')),
                payload.get('longitude', ''),
                payload.get('latitude', ''),
                payload.get('speed', ''),
                payload.get('altitude', ''),
                payload.get('verticalAccuracy', ''),
                payload.get('horizontalAccuracy', '')))
    return data_headers, data_list, source_path


@artifact_processor
def teamsSegmentMotion(context):
    data_headers = (('Timestamp', 'datetime'), 'Activity')
    data_list = []
    records, source_path = _iter_records(context)
    for serial in records:
        if len(serial) > 2 and serial[1] == 'motion':
            data_list.append((_seg_ts(serial[0]), serial[2].get('activityName', '')))
    return data_headers, data_list, source_path


@artifact_processor
def teamsSegmentTimezone(context):
    data_headers = (('Timestamp', 'datetime'), 'Timezone', 'Timezone Offset', 'Timezone reason')
    data_list = []
    records, source_path = _iter_records(context)
    for serial in records:
        if len(serial) > 2 and serial[1] == 'timeCheck':
            payload = serial[2]
            data_list.append((_seg_ts(serial[0]), payload.get('timezone', ''),
                              payload.get('offset', ''), payload.get('reason', '')))
    return data_headers, data_list, source_path


@artifact_processor
def teamsSegmentPower(context):
    data_headers = (('Timestamp', 'datetime'), 'Is plugged in?', 'Battery Level')
    data_list = []
    records, source_path = _iter_records(context)
    for serial in records:
        if len(serial) > 2 and serial[1] == 'power':
            payload = serial[2]
            data_list.append((_seg_ts(serial[0]), payload.get('isPluggedIn', ''),
                              payload.get('batteryLevel', '')))
    return data_headers, data_list, source_path


@artifact_processor
def teamsSegmentStateChange(context):
    data_headers = (('Timestamp', 'datetime'), 'Change')
    data_list = []
    records, source_path = _iter_records(context)
    for serial in records:
        if len(serial) > 2 and serial[1] == 'stateChange':
            agg = ' '.join(f'{a}: {b}' for a, b in serial[2].items())
            data_list.append((_seg_ts(serial[0]), agg))
    return data_headers, data_list, source_path
