__artifacts_v2__ = {
    "wifiIdentifiers": {
        "name": "WIFI Identifiers",
        "description": "Extracts Wi-Fi MAC addresses",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-09-30",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/preferences/SystemConfiguration/NetworkInterfaces.plist',),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 3 rows",
            "dexter_ios18": "iOS 18.3.2 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | 3 rows",
            "fsfull002_ios17": "iOS 17.1 | 3 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "iphone12_ios18": "iOS 18.7 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
        }
    }
}

import struct
from scripts.ilapfuncs import (
    artifact_processor,
    device_info,
    get_plist_file_content,
    get_file_path,
    logfunc
    )


def pad_mac_adr(adr):
    return ':'.join([i.zfill(2) for i in adr.split(':')]).upper()


@artifact_processor
def wifiIdentifiers(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = get_file_path(files_found, 'NetworkInterfaces.plist')
    if not source_path:
        logfunc('NetworkInterfaces.plist not found')
        return (), [], ''
    pl = get_plist_file_content(source_path)

    if pl:
        for key, value in pl.items():
            if key == 'Interfaces':
                for y in value:
                    hexstring = "N/A"
                    sc_info = y.get('SCNetworkInterfaceInfo', {})
                    userdefinedname = sc_info.get('UserDefinedName', 'N/A')
                    bsdname = y.get('BSD Name', 'N/A')
                    hexstring_raw = y.get('IOMACAddress')
                    if hexstring_raw:
                        try:
                            mac_octets = struct.unpack("BBBBBB", hexstring_raw)
                            hexstring = pad_mac_adr(":".join(f"{octet:x}" for octet in mac_octets))
                            device_info(
                                "Network",
                                "MAC Addresses",
                                f"{userdefinedname}: {hexstring}",
                                source_path
                            )
                        except (struct.error, TypeError) as ex:
                            logfunc(f"Error processing Wi-Fi MAC address: {ex}")

                    data_list.append((
                        hexstring,
                        userdefinedname,
                        bsdname
                    ))

    data_headers = (
        'MAC Address',
        'User Defined Name',
        'BSD Name'
        )
    return data_headers, data_list, source_path
