__artifacts_v2__ = {
    "simInfoUUID": {
        "name": "SIM - UUID",
        "description": "SIM personal wallet entries from com.apple.commcenter.data.plist",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "SIM Info", "notes": "Timestamps are Unix epoch seconds (UTC).",
        "paths": ('*/com.apple.commcenter.data.plist',),
        "output_types": "standard", "artifact_icon": "credit-card",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 4 rows",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
        }
    },
    "simInfoLabelStore": {
        "name": "SIM - Unique Label Store",
        "description": "SIM unique label store from com.apple.commcenter.data.plist",
        "author": "", "creation_date": "2026-06-23", "last_update_date": "2026-06-24", "requirements": "none",
        "category": "SIM Info", "notes": "Timestamps are Unix epoch seconds (UTC).",
        "paths": ('*/com.apple.commcenter.data.plist',),
        "output_types": "standard", "artifact_icon": "tag",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "hickman_ios14": "iOS 14.3 | 1 row",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
        }
    }
}

import plistlib

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc


def _ts(value):
    if value in ('', None):
        return ''
    try:
        return convert_unix_ts_to_utc(int(value))
    except (ValueError, TypeError):
        return value


def _find(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('com.apple.commcenter.data.plist'):
            return file_found
    return ''


@artifact_processor
def simInfoUUID(context):
    data_headers = (('Timestamp', 'datetime'), 'MDN', 'ESIM', 'Type', 'CB_ID', 'No_SRC', 'Label-ID',
                    'Label-ID Confirmed', 'EAP_AKA', 'CB_Ver')
    data_list = []
    source_path = _find(context)
    if not source_path:
        return data_headers, data_list, ''
    with open(source_path, 'rb') as fp:
        pl = plistlib.load(fp)
    for sim in pl.get('PersonalWallet', {}).values():
        if not isinstance(sim, dict):
            continue
        for z in sim.values():
            if not isinstance(z, dict):
                continue
            data_list.append((_ts(z.get('ts', '')), z.get('mdn', ''), z.get('esim', ''),
                              z.get('type', ''), z.get('cb_id', ''), z.get('no_src', ''),
                              z.get('label-id', ''), z.get('label-id-confirmed', ''),
                              z.get('eap_aka', ''), z.get('cb_ver', '')))
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def simInfoLabelStore(context):
    data_headers = (('Timestamp', 'datetime'), 'Tag', 'SIM Label Store ID', 'Text')
    data_list = []
    source_path = _find(context)
    if not source_path:
        return data_headers, data_list, ''
    with open(source_path, 'rb') as fp:
        pl = plistlib.load(fp)
    for store_id, y in pl.get('unique-sim-label-store', {}).items():
        if not isinstance(y, dict):
            continue
        data_list.append((_ts(y.get('ts', '')), y.get('tag', ''), store_id, y.get('text', '')))
    return data_headers, data_list, context.get_relative_path(source_path)
