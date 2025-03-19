__artifacts_v2__ = {
    "get_bluetoothPairedReg": {
        "name": "Bluetooth Paired",
        "description": "",
        "author": "@JohnHyla",
        "version": "0.0.2",
        "date": "2024-10-21",
        "requirements": "none",
        "category": "Bluetooth",
        "notes": "",
        "paths": ('**/com.apple.MobileBluetooth.devices.plist'),
        "output_types": "standard"
    }
}


import plistlib
import datetime

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_str


@artifact_processor
def get_bluetoothPairedReg(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        with open(file_found, 'rb') as f:
            plist = plistlib.load(f)
        if len(plist) > 0:
            for x in plist.items():
                macaddress = x[0]
                if 'LastSeenTime' in x[1]:
                    lastseen = convert_unix_ts_to_str(x[1]['LastSeenTime'])
                else:
                    lastseen = ''
                if 'UserNameKey' in x[1]:
                    usernkey = x[1]['UserNameKey']
                else:
                    usernkey = ''

                if 'Name' in x[1]:
                    nameu = x[1]['Name']
                else:
                    nameu = ''
                if 'DeviceIdProduct' in x[1]:
                    deviceid = x[1]['DeviceIdProduct']
                else:
                    deviceid = ''
                if 'DefaultName' in x[1]:
                    defname = x[1]['DefaultName']
                else:
                    defname = ''

                data_list.append((lastseen, macaddress, usernkey, nameu, deviceid, defname))

        data_headers = ('Last Seen Time', 'MAC Address', 'Name Key', 'Name', 'Device Product ID', 'Default Name' )     

        return data_headers, data_list, file_found
