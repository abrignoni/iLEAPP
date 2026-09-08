""" See description below"""

__artifacts_v2__ = {
    "get_sysdiag_account_devices": {
        "name": "Sysdiagnose - Account Devices",
        "description": "Parses the otctl_status.txt file from Sysdiagnose logs, \
            to get informations about peers in the account's Octagon trust circle (iCloud Keychain syncing).",
        "author": "@C_Peter",
        "creation_date": "2025-05-22",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "OCTL refers to the Octagon Account (iCloud Keychain). Reference: Apple Security open source (OctagonTrust; otctl man page: 'diagnostic information for iCloud Keychain syncing'), https://github.com/apple-oss-distributions/Security",
        "paths": (
            '*/otctl_status.txt',
            '*/sysdiagnose_*.tar.gz'),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "hickman_ios14": "iOS 14.3 | 5 rows",
        }
    }
}

import json
from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files

@artifact_processor
def get_sysdiag_account_devices(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []
    

    for file_obj, source_path in get_sysdiagnose_files(files_found, "otctl_status.txt"):
        source_name = context.get_relative_path(source_path)
        try:
            f = json.load(file_obj)
        except json.JSONDecodeError:
            continue

        sources.append(source_path)
        opush = f.get("lastOctagonPush", '')

        for elem in f.get("contextDump", {}).get("peers", []):
            try:
                model = elem["permanentInfo"]["model_id"]
                m_name = context.lookup_metadata('apple_device_id_to_model', model)
                os_bnum = elem["stableInfo"]["os_version"]
                os_build = os_bnum.split('(')[1].split(')')[0]
                os_ver = context.get_apple_os_version(os_build, model)
                serial = elem["stableInfo"]["serial_number"]
            except (KeyError, IndexError):
                continue

            if not any(serial in subliste for subliste in data_list):
                data_list.append((opush, model, m_name, os_bnum, os_ver, serial,source_name))

    source_list = "; ".join(sources)
    data_headers = ("lastOctagonPush", "Model", "Product", "OS Build", "OS Version", "Serial Number","Source Path")

    return data_headers, data_list, source_list