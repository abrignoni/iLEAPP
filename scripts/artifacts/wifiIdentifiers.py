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
        "artifact_icon": "wifi"
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
                    try:
                        hexstring_raw = y.get('IOMACAddress')
                        if hexstring_raw:
                            hexstring = pad_mac_adr("%x:%x:%x:%x:%x:%x" % struct.unpack("BBBBBB", hexstring_raw))
                        else:
                            hexstring = "N/A"

                        # Usamos .get() para evitar errores si la clave no existe
                        sc_info = y.get('SCNetworkInterfaceInfo', {})
                        userdefinedname = sc_info.get('UserDefinedName', 'N/A')
                        bsdname = y.get('BSD Name', 'N/A')

                        data_list.append((
                            hexstring,
                            userdefinedname,
                            bsdname
                        ))
                        if userdefinedname != 'N/A':
                            device_info("Network", userdefinedname, hexstring, source_path)
                    except Exception as e:
                        logfunc(f"Error processing interface: {e}")

    data_headers = (
        'MAC Address',
        'User Defined Name',
        'BSD Name'
        )
    return data_headers, data_list, source_path
