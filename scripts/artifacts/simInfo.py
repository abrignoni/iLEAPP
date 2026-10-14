__artifacts_v2__ = {
    "simInfoUUID": {
        "name": "SIM - UUID",
        "description": "SIM personal wallet entries from com.apple.commcenter.data.plist",
        "author": "@abrignoni", "creation_date": "2026-06-23", "last_update_date": "2026-10-09", "requirements": "none",
        "category": "SIM Info", "notes": "Timestamp is the entry's ts value, read as Unix epoch "
                                         "time and shown in UTC. The tool picks the unit "
                                         "(seconds or a finer one) from the size of the value; "
                                         "no source for the unit was located. What the time "
                                         "marks is not established. Every "
                                         "com.apple.commcenter.data.plist found is read, and "
                                         "Source Path names the file each row came from. A "
                                         "file that does not load as a plist is skipped and "
                                         "named in the run log.",
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
        "author": "@abrignoni", "creation_date": "2026-06-23", "last_update_date": "2026-10-09", "requirements": "none",
        "category": "SIM Info", "notes": "Timestamp is the entry's ts value, read as Unix epoch "
                                         "time and shown in UTC. The tool picks the unit "
                                         "(seconds or a finer one) from the size of the value; "
                                         "no source for the unit was located. What the time "
                                         "marks is not established. Every "
                                         "com.apple.commcenter.data.plist found is read, and "
                                         "Source Path names the file each row came from. A "
                                         "file that does not load as a plist is skipped and "
                                         "named in the run log.",
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

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc


def _ts(value):
    if value in ('', None):
        return ''
    try:
        return convert_unix_ts_to_utc(int(value))
    except (ValueError, TypeError):
        return value


def _plists(context):
    """(relative path, plist) for every com.apple.commcenter.data.plist that loads."""
    loaded = []
    source_paths = sorted({str(file_found) for file_found in context.get_files_found()
                           if str(file_found).endswith('com.apple.commcenter.data.plist')})
    for source_path in source_paths:
        relative_path = context.get_relative_path(source_path)
        try:
            with open(source_path, 'rb') as fp:
                pl = plistlib.load(fp)
        except (OSError, ValueError, plistlib.InvalidFileException) as error:
            logfunc(f'SIM Info: could not read {relative_path}: {type(error).__name__}')
            continue
        if isinstance(pl, dict):
            loaded.append((relative_path, pl))
    return loaded


@artifact_processor
def simInfoUUID(context):
    data_headers = (('Timestamp', 'datetime'), 'MDN', 'ESIM', 'Type', 'CB_ID', 'No_SRC', 'Label-ID',
                    'Label-ID Confirmed', 'EAP_AKA', 'CB_Ver', 'Source Path')
    data_list = []
    loaded = _plists(context)
    for relative_path, pl in loaded:
        wallet = pl.get('PersonalWallet', {})
        if not isinstance(wallet, dict):
            continue
        for sim in wallet.values():
            if not isinstance(sim, dict):
                continue
            for z in sim.values():
                if not isinstance(z, dict):
                    continue
                data_list.append((_ts(z.get('ts', '')), z.get('mdn', ''), z.get('esim', ''),
                                  z.get('type', ''), z.get('cb_id', ''), z.get('no_src', ''),
                                  z.get('label-id', ''), z.get('label-id-confirmed', ''),
                                  z.get('eap_aka', ''), z.get('cb_ver', ''), relative_path))
    return data_headers, data_list, '\n'.join(path for path, _ in loaded)


@artifact_processor
def simInfoLabelStore(context):
    data_headers = (('Timestamp', 'datetime'), 'Tag', 'SIM Label Store ID', 'Text',
                    'Source Path')
    data_list = []
    loaded = _plists(context)
    for relative_path, pl in loaded:
        store = pl.get('unique-sim-label-store', {})
        if not isinstance(store, dict):
            continue
        for store_id, y in store.items():
            if not isinstance(y, dict):
                continue
            data_list.append((_ts(y.get('ts', '')), y.get('tag', ''), store_id,
                              y.get('text', ''), relative_path))
    return data_headers, data_list, '\n'.join(path for path, _ in loaded)
