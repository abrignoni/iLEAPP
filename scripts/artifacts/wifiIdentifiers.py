__artifacts_v2__ = {
    "wifiIdentifiers": {
        "name": "WIFI Identifiers",
        "description": "Extracts Wi-Fi MAC addresses",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2023-09-30",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/preferences/SystemConfiguration/NetworkInterfaces.plist',),
        "output_types": ["html", "tsv", "lava"]
    }
}
        

import plistlib
import struct

from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def wifiIdentifiers(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, value in pl.items():
            if key == 'Interfaces':
                for y in value:
                    hexstring = (y['IOMACAddress'])
                    hexstring = "%x:%x:%x:%x:%x:%x" % struct.unpack("BBBBBB",hexstring)
                    userdefinedname = y['SCNetworkInterfaceInfo']['UserDefinedName']
                    bsdname = y['BSD Name']
                    
                    data_list.append((hexstring, userdefinedname, bsdname))
                    device_info("Network", "MAC Addresses", f"- {userdefinedname}: {hexstring}", source_path)
                    
    data_headers = ('MAC Address', 'User Defined Name', 'BSD Name')
    return data_headers, data_list, source_path
