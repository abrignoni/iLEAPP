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
        "artifact_icon": "map-pin",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 5 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 5 rows",
            "felix23_ios16": "iOS 16.5 | 5 rows",
            "hickman_ios13": "iOS 13.3.1 | 5 rows",
            "hickman_ios14": "iOS 14.3 | 5 rows",
            "jess_ios15": "iOS 15.0.2 | 5 rows",
            "magnet_ios16": "iOS 16.1.1 | 5 rows",
        }
    },
    "locServicesConfigLocationd": {
        "name": "LSC - com.apple.locationd.plist",
        "description": "Location Services configuration key/values from com.apple.locationd.plist",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": ('*/Library/Preferences/com.apple.locationd.plist',),
        "output_types": ["html","lava","tsv"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 5 rows",
            "dexter_ios18": "iOS 18.3.2 | 11 rows",
            "felix_ios17": "iOS 17.6.1 | 10 rows",
            "fsfull002_ios17": "iOS 17.1 | 11 rows",
            "hc_ios18_7": "iOS 18.7.8 | 10 rows",
            "iphone11_ios17": "iOS 17.3 | 12 rows",
            "iphone12_ios18": "iOS 18.7 | 3 rows",
            "iphone14plus_ios18": "iOS 18.0 | 9 rows",
            "otto_ios17": "iOS 17.5.1 | 12 rows",
            "abe_ios16": "iOS 16.5 | 11 rows",
            "felix23_ios16": "iOS 16.5 | 10 rows",
            "hickman_ios13": "iOS 13.3.1 | 7 rows",
            "hickman_ios14": "iOS 14.3 | 6 rows",
            "jess_ios15": "iOS 15.0.2 | 8 rows",
            "magnet_ios16": "iOS 16.1.1 | 10 rows",
        }
    },
    "locServicesConfigRoutined": {
        "name": "LSC - com.apple.routined.plist",
        "description": "Location Services configuration key/values from com.apple.routined.plist",
        "author": "",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-07-21",
        "requirements": "none",
        "category": "Location",
        "notes": "",
        "paths": ('*/Library/Preferences/com.apple.routined.plist',),
        "output_types": ["html","lava","tsv"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 17 rows",
            "dexter_ios18": "iOS 18.3.2 | 108 rows",
            "felix_ios17": "iOS 17.6.1 | 97 rows",
            "fsfull002_ios17": "iOS 17.1 | 94 rows",
            "hc_ios18_7": "iOS 18.7.8 | 55 rows",
            "iphone11_ios17": "iOS 17.3 | 107 rows",
            "iphone12_ios18": "iOS 18.7 | 52 rows",
            "iphone14plus_ios18": "iOS 18.0 | 99 rows",
            "otto_ios17": "iOS 17.5.1 | 117 rows",
            "abe_ios16": "iOS 16.5 | 86 rows",
            "felix23_ios16": "iOS 16.5 | 78 rows",
            "hickman_ios13": "iOS 13.3.1 | 24 rows",
            "hickman_ios14": "iOS 14.3 | 29 rows",
            "jess_ios15": "iOS 15.0.2 | 27 rows",
            "magnet_ios16": "iOS 16.1.1 | 67 rows",
        }
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
