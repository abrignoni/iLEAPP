__artifacts_v2__ = {
    "locServicesConfigClients": {
        "name": "LSC - clients.plist",
        "description": "Location Services configuration for the Routine bundle from clients.plist",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": ('*/Library/Caches/locationd/clients.plist',),
        "output_types": "standard",
        "artifact_icon": "map-pin"
    },
    "locServicesConfigLocationd": {
        "name": "LSC - com.apple.locationd.plist",
        "description": "Location Services configuration key/values from com.apple.locationd.plist",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": ('*/Library/Preferences/com.apple.locationd.plist',),
        "output_types": "standard",
        "artifact_icon": "map-pin"
    },
    "locServicesConfigRoutined": {
        "name": "LSC - com.apple.routined.plist",
        "description": "Location Services configuration key/values from com.apple.routined.plist",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": ('*/Library/Preferences/com.apple.routined.plist',),
        "output_types": "standard",
        "artifact_icon": "map-pin"
    }
}

import json
import plistlib
from datetime import datetime

from scripts.ilapfuncs import artifact_processor, convert_cocoa_core_data_ts_to_utc, logfunc


def _lava_safe(value):
    """Make a raw plist value safe for LAVA's generic-column json serialization."""
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')   # plist <date> is UTC
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str)
    return value


def _load_plist(context, filename):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith(filename):
            try:
                with open(file_found, 'rb') as f:
                    return plistlib.load(f), context.get_relative_path(file_found)
            except (plistlib.InvalidFileException, ValueError, OSError) as ex:
                logfunc(f'Failed to read {file_found}: {ex}')
                return None, context.get_relative_path(file_found)
    return None, ''


def _cocoa_utc_str(value):
    """Convert a Cocoa (seconds-since-2001) timestamp to a UTC string; pass empties through."""
    if value in ('', None):
        return ''
    dt = convert_cocoa_core_data_ts_to_utc(value)
    return dt.strftime('%Y-%m-%d %H:%M:%S') if hasattr(dt, 'strftime') else str(dt)


@artifact_processor
def locServicesConfigClients(context):
    data_headers = ('Value', 'Key')
    data_list = []
    plist, source_path = _load_plist(context, 'clients.plist')
    if not plist:
        return data_headers, data_list, source_path

    routine_key = 'com.apple.locationd.bundle-/System/Library/LocationBundles/Routine.bundle'
    value = plist.get(routine_key)
    if isinstance(value, dict):
        data_list.append((_cocoa_utc_str(value.get('FenceTimeStarted', '')), 'FenceTimeStarted'))
        data_list.append((_cocoa_utc_str(value.get('ConsumptionPeriodBegin', '')), 'ConsumptionPeriodBegin'))
        data_list.append((_cocoa_utc_str(value.get('ReceivingLocationInformationTimeStopped', '')),
                          'ReceivingLocationInformationTimeStopped'))
        data_list.append((value.get('Authorization', ''), 'Authorization'))
        data_list.append((_cocoa_utc_str(value.get('LocationTimeStopped', '')), 'LocationTimeStopped'))

    return data_headers, data_list, source_path


@artifact_processor
def locServicesConfigLocationd(context):
    data_headers = ('Value', 'Key')
    data_list = []
    plist, source_path = _load_plist(context, 'com.apple.locationd.plist')
    if not plist:
        return data_headers, data_list, source_path

    for key, value in plist.items():
        data_list.append((_lava_safe(value), key))

    return data_headers, data_list, source_path


@artifact_processor
def locServicesConfigRoutined(context):
    data_headers = ('Value', 'Key')
    data_list = []
    plist, source_path = _load_plist(context, 'com.apple.routined.plist')
    if not plist:
        return data_headers, data_list, source_path

    for key, value in plist.items():
        if key != 'CloudKitAccountInfoCache':
            data_list.append((_lava_safe(value), key))

    return data_headers, data_list, source_path
