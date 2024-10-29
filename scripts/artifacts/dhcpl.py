__artifacts_v2__ = {
    "dhcpLeases": {
        "name": "DHCP Received List",
        "description": "DHCP client lease information",
        "author": "",
        "version": "1.0",
        "date": "2024-10-29",
        "requirements": "none",
        "category": "DHCP",
        "notes": "",
        "paths": ('*/db/dhcpclient/leases/en*',),
        "output_types": "standard"
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor, convert_plist_date_to_timezone_offset

def format_mac_address(mac_bytes):
    if isinstance(mac_bytes, bytes):
        return ':'.join(f'{b:02x}' for b in mac_bytes)
    return mac_bytes

@artifact_processor
def dhcpLeases(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    
    for file_found in files_found:
        with open(file_found, "rb") as fp:
            pl = plistlib.load(fp)
            for key, val in pl.items():
                if key in ["IPAddress", "LeaseLength", "LeaseStartDate", 
                        "RouterHardwareAddress", "RouterIPAddress", "SSID"]:
                    if key == "LeaseStartDate":
                        val = convert_plist_date_to_timezone_offset(val, timezone_offset)
                        val = val.strftime('%Y-%m-%d %H:%M:%S')
                    elif key == "RouterHardwareAddress":
                        val = format_mac_address(val)
                    data_list.append((key, val, file_found))

    data_headers = ('Property Name', 'Property Value', 'Source File')
    
    return data_headers, data_list, ''
