__artifacts_v2__ = {
    "pref_devinfo": {
        "name": "Sysdiagnose - Device Info",
        "description": "Parses device information preferences from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": "",
        "paths": ('*/Networking/preferences.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
    "pref_netserv": {
        "name": "Sysdiagnose - Network Services",
        "description": "Parses network services preferences from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": "",
        "paths": ('*/Networking/preferences.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    }
}

import plistlib
 
from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def pref_devinfo(context):
    data_list_dev = []
    source_paths = set()
    
    for file_found in context.get_files_found():
        source_name = str(context.get_relative_path(file_found))
        source_paths.add(file_found)
        with open(file_found, 'rb') as f:
            pl = plistlib.load(f)
            system = pl['System'].get('System')
            
            model = pl.get('Model','')
            version = pl.get('__VERSION__','')
            computerName = system.get('ComputerName','')
            hostName = system.get('HostName','')

            device_info("Device Information", "Device Name", computerName, source_name)
            
            device_info("Device Information", "Host Name", hostName, source_name)
            
            device_info("Device Information", "Hardware Model", model, source_name)
            
            data_list_dev.append((computerName,hostName,model,version,source_name))

    data_headers = ('Device Name','Host Name','Motherboard Model','Version','Source File')
    return data_headers, data_list_dev, '\n'.join(sorted(source_paths))
        
@artifact_processor
def pref_netserv(context):
    data_list_netservices = []
    source_paths = set()

    for file_found in context.get_files_found():
        source_name = str(context.get_relative_path(file_found))
        source_paths.add(file_found)
        with open(file_found, 'rb') as f:
            pl = plistlib.load(f)
            netServices = pl.get('NetworkServices')
    
            for key, value in netServices.items():
                udn = value['Interface'].get('UserDefinedName','')
                service_type = value['Interface'].get('Type','')
                service_hardware = value['Interface'].get('Hardware','')
                service_devname = value['Interface'].get('DeviceName','')
                netService = key
                
                data_list_netservices.append((netService,udn,service_type,service_hardware,service_devname,source_name))
                data_list_netservices = sorted(data_list_netservices, key=lambda x: x[4])
    
    data_headers = ('Network Service GUID','Interface Name','Interface Type','Interface Hardware','Interface Device Name','Source File')
    return data_headers, data_list_netservices, '\n'.join(sorted(source_paths))