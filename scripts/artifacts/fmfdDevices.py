__artifacts_v2__ = {
    "fmfd_notbackedup_devices": {
        "name": "Find My - Devices",
        "author": "@ghmihkel",
        "version": "1.0",
        "date": "2026-03-31",
        "requirements": "none",
        "category": "Find My",
        "notes": "Located in the NotBackedUp preferences area. Contains devices visible in the Find My Friends network.",
        "paths": ('*/Library/Preferences/com.apple.icloud.fmfd.notbackedup.plist',),
        "output_types": "all",
        "artifact_icon": "map-pin"
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor, logfunc


def _resolve(uid_or_val, objects):
    if isinstance(uid_or_val, plistlib.UID):
        return objects[uid_or_val.data]
    return uid_or_val


def _parse_fmfd_plist(raw_bytes):
    """
    The outer plist has a single key 'kFMFDStoredDataKey' whose value is
    a binary blob that is itself a NSKeyedArchiver plist. This function
    decodes the inner archive and returns a list of device tuples.
    """
    inner = plistlib.loads(raw_bytes)
    objects = inner.get('$objects', [])

    # Object[1] is the root NSDictionary
    root = objects[1]
    keys = [_resolve(k, objects) for k in root['NS.keys']]
    vals = root['NS.objects']
    key_to_val = dict(zip(keys, vals))

    devices_container_uid = key_to_val.get('kFMFDDevicesListKey')
    if devices_container_uid is None:
        return []

    devices_container = _resolve(devices_container_uid, objects)
    device_uids = devices_container.get('NS.objects', [])

    devices = []
    for du in device_uids:
        d = _resolve(du, objects)
        if not isinstance(d, dict):
            continue

        device_name   = _resolve(d.get('deviceName',   ''), objects)
        device_id     = _resolve(d.get('deviceId',     ''), objects)
        ids_device_id = _resolve(d.get('idsDeviceId',  ''), objects)
        is_active     = d.get('isActiveDevice',    '')
        is_this       = d.get('isThisDevice',      '')
        is_companion  = d.get('isCompanionDevice', '')
        is_auto_me    = d.get('isAutoMeCapable',   '')

        devices.append((
            device_name,
            ids_device_id,
            is_active,
            is_this,
            is_companion,
            is_auto_me,
            device_id,

        ))

    return devices


@artifact_processor
def fmfd_notbackedup_devices(context):
    files_found = context.get_files_found()
    data_headers = (
        'Device Name',
        'Device ID',
        'Active?',
        'This Device?',
        'Companion Device?',
        'Auto Me Capable?',
        'Device FMF ID',
    )
    data_list = []
    source_file = ''

    for file_found in files_found:
        source_file = str(file_found)
        try:
            with open(source_file, 'rb') as f:
                outer = plistlib.load(f)

            raw = outer.get('kFMFDStoredDataKey')
            if not raw:
                logfunc(f'fmfd: kFMFDStoredDataKey not found in {source_file}')
                continue

            devices = _parse_fmfd_plist(raw)
            data_list.extend(devices)

        except Exception as e:
            logfunc(f'fmfd: Error parsing {source_file}: {e}')

    return data_headers, data_list, source_file
