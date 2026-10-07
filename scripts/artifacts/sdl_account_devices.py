""" See description below"""

__artifacts_v2__ = {
    "sdl_account_devices": {
        "name": "Sysdiagnose - Account Devices",
        "description": "Parses otctl_status.txt from sysdiagnose logs for the peers listed under contextDump/peers, one row per serial number: model, OS build and serial as stored, with the file's lastOctagonPush value.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2025-05-22",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": (
            "otctl_status.txt is named for otctl, a command line tool whose man page describes it "
            "as a 'Command line interface do provide diagnostic information for iCloud Keychain "
            "syncing'. A peer lacking model_id, os_version or serial_number, or whose serial "
            "number was already reported, including from another sysdiagnose, is not listed. "
            "Serials are compared only with previously admitted raw serial values using native "
            "equality, not with other report cells. Original parser contribution: @C_Peter. "
            "lastOctagonPush is a value of the file and repeats on every row from it. Product and "
            "OS Version are looked up from the tool's tables. Reference: Apple Security open "
            "source, otctl man page, "
            "https://github.com/apple-oss-distributions/Security/blob/5366a77746f485a8846aeabf7e8b64d3a25cebfd/keychain/otctl/otctl.1#L6"
        ),
        "paths": (
            '*/otctl_status.txt',
            '*/sysdiagnose_*.tar.gz'),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "hickman_ios13": "iOS 13.3.1 | 2 rows",
            "hickman_ios14": "iOS 14.3 | 5 rows",
            "ai16_ios26_sysdiag": "iOS 26.5.2 sysdiagnose | 14 rows",
            "hc_ios26_sysdiag": "iOS 26 sysdiagnose | 1 row",
            "rodeo_ios17_sysdiag": "iOS 17.3 sysdiagnose | 5 rows",
        }
    }
}

import json
from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files

@artifact_processor
def sdl_account_devices(context):
    files_found = context.get_files_found()
    data_list = []
    admitted_serials = []
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

            if serial not in admitted_serials:
                data_list.append((opush, model, m_name, os_bnum, os_ver, serial,source_name))
                admitted_serials.append(serial)

    data_headers = ("lastOctagonPush", "Model", "Product", "OS Build", "OS Version", "Serial Number","Source Path")
    return data_headers, data_list, '\n'.join(sorted(sources))
