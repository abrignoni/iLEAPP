__artifacts_v2__ = {
    "get_bluetoothPairedReg": {
        "name": "Bluetooth Paired",
        "description": "",
        "author": "@JohnHyla",
        "creation_date": "2024-10-21",
        "last_update_date": "2025-11-03",
        "requirements": "none",
        "category": "Bluetooth",
        "notes": "",
        "paths": ('*/com.apple.MobileBluetooth.devices.plist'),
        "output_types": "standard"
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_plist_file_content

@artifact_processor
def get_bluetoothPairedReg(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        
        plist = get_plist_file_content(file_found)
        if plist and isinstance(plist, dict):
            for x in plist.items():
                macaddress = x[0]
                if 'LastSeenTime' in x[1]:
                    lastseen = convert_unix_ts_to_utc(x[1]['LastSeenTime'])
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

                data_list.append((lastseen, macaddress, usernkey, nameu, deviceid, defname, file_found))

        data_headers = (('Last Seen Time', 'datetime'), 'MAC Address', 'Name Key', 'Name', 'Device Product ID', 'Default Name', 'Source File')     

        return data_headers, data_list, 'see Source File for more info'
