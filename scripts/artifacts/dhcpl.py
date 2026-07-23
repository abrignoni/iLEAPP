__artifacts_v2__ = {
    "dhcpLeases": {
        "name": "DHCP Received List",
        "description": "DHCP client lease information",
        "author": "",
        "creation_date": "2024-10-29",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "DHCP",
        "notes": "LeaseStartDate is stored as UTC.",
        "paths": ('*/db/dhcpclient/leases/en*',),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 6 rows",
            "hc_ios18_7": "iOS 18.7.8 | 6 rows",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
            "abe_ios16": "iOS 16.5 | 6 rows",
            "felix23_ios16": "iOS 16.5 | 6 rows",
            "hickman_ios13": "iOS 13.3.1 | 6 rows",
            "hickman_ios14": "iOS 14.3 | 6 rows",
            "magnet_ios16": "iOS 16.1.1 | 6 rows",
        }
    }
}

import plistlib

from scripts.ilapfuncs import artifact_processor, logfunc

_WANTED = ("IPAddress", "LeaseLength", "LeaseStartDate", "RouterHardwareAddress",
           "RouterIPAddress", "SSID")


def format_mac_address(mac_bytes):
    if isinstance(mac_bytes, bytes):
        return ':'.join(f'{b:02x}' for b in mac_bytes)
    return mac_bytes


@artifact_processor
def dhcpLeases(context):
    data_headers = ('Property Name', 'Property Value', 'Source File')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        rel = context.get_relative_path(file_found)
        try:
            with open(file_found, "rb") as fp:
                pl = plistlib.load(fp)
        except (plistlib.InvalidFileException, ValueError, OSError) as ex:
            logfunc(f'Failed to read DHCP lease {file_found}: {ex}')
            continue

        for key, val in pl.items():
            if key not in _WANTED:
                continue
            if key == "LeaseStartDate" and hasattr(val, 'strftime'):
                # plist <date> values are UTC; format as-is (no examiner-local shift)
                val = val.strftime('%Y-%m-%d %H:%M:%S')
            elif key == "RouterHardwareAddress":
                val = format_mac_address(val)
            data_list.append((key, val, rel))
        sources.append(rel)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
