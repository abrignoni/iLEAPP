__artifacts_v2__ = {
    "teamsSegmentLocations": {
        "name": "Microsoft Teams - Locations",
        "description": "Location segments logged by Microsoft Teams (DriveIQ)",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Microsoft Teams",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/DriveIQ/segments/current/*.*',),
        "output_types": ["html", "tsv", "timeline", "lava", "kml"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | Microsoft Teams 2.3.1 | 53 rows",
        }
    },
    "teamsSegmentMotion": {
        "name": "Microsoft Teams - Motion",
        "description": "Motion/activity segments logged by Microsoft Teams (DriveIQ)",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Microsoft Teams",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/DriveIQ/segments/current/*.*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | Microsoft Teams 2.3.1 | 9 rows",
        }
    },
    "teamsSegmentTimezone": {
        "name": "Microsoft Teams - Timezone",
        "description": "Timezone check segments logged by Microsoft Teams (DriveIQ)",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Microsoft Teams",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/DriveIQ/segments/current/*.*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | Microsoft Teams 2.3.1 | 2 rows",
        }
    },
    "teamsSegmentPower": {
        "name": "Microsoft Teams - Power Log",
        "description": "Power/battery segments logged by Microsoft Teams (DriveIQ)",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Microsoft Teams",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/DriveIQ/segments/current/*.*',),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | Microsoft Teams 2.3.1 | 36 rows",
        }
    },
    "teamsSegmentStateChange": {
        "name": "Microsoft Teams - State Change",
        "description": "State change segments logged by Microsoft Teams (DriveIQ)",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Microsoft Teams",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Library/DriveIQ/segments/current/*.*',),
        "output_types": "standard",
        "artifact_icon": "repeat",
        "sample_data": {
            "hickman_ios14": "iOS 14.3 | Microsoft Teams 2.3.1 | 8 rows",
        }
    }
}

import json

from scripts.ilapfuncs import artifact_processor, convert_ts_human_to_utc, logfunc


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
    for file_found in context.get_files_found():
        file_found = str(file_found)
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
