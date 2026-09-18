__artifacts_v2__ = {
    "pref_devinfo": {
        "name": "Sysdiagnose - Device Info",
        "description": "Parses device information preferences from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": "",
        "paths": (
            '*/Networking/preferences.plist',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
    "pref_netserv": {
        "name": "Sysdiagnose - Network Services",
        "description": "Parses network services preferences from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": "",
        "paths": (
            '*/Networking/preferences.plist',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor, device_info, get_sysdiagnose_files

@artifact_processor
def pref_devinfo(context):
    data_list_dev = []
    source_paths = set()
    
    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), "preferences.plist"):
        source_name = str(context.get_relative_path(source_path))
        
        try:
            # Attempt to read the raw binary buffer directly to avoid text-mode corruption
            if hasattr(file_obj, 'buffer'):
                plist_bytes = file_obj.buffer.read()
            else:
                plist_bytes = file_obj.read()
                
            if not plist_bytes:
                continue
                
            # Convert to bytes if the helper returned a string
            if isinstance(plist_bytes, str):
                plist_bytes = plist_bytes.encode('latin-1')
                
            pl = plistlib.loads(plist_bytes)
        except Exception:
            continue
            
        source_paths.add(source_path)
        
        system_dict = pl.get('System', {})
        system = system_dict.get('System', {}) if isinstance(system_dict, dict) else {}
        
        model = pl.get('Model', '')
        version = pl.get('__VERSION__', '')
        computerName = system.get('ComputerName', '') if isinstance(system, dict) else ''
        hostName = system.get('HostName', '') if isinstance(system, dict) else ''

        if computerName:
            device_info("Device Information", "Device Name", computerName, source_name)
        if hostName:
            device_info("Device Information", "Host Name", hostName, source_name)
        if model:
            device_info("Device Information", "Hardware Model", model, source_name)
        
        data_list_dev.append((computerName, hostName, model, version, source_name))

    data_headers = ('Device Name', 'Host Name', 'Motherboard Model', 'Version', 'Source File')
    return data_headers, data_list_dev, '\n'.join(sorted(source_paths))
        
@artifact_processor
def pref_netserv(context):
    data_list_netservices = []
    source_paths = set()

    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), "preferences.plist"):
        source_name = str(context.get_relative_path(source_path))
        
        try:
            # Attempt to read the raw binary buffer directly to avoid text-mode corruption
            if hasattr(file_obj, 'buffer'):
                plist_bytes = file_obj.buffer.read()
            else:
                plist_bytes = file_obj.read()
                
            if not plist_bytes:
                continue
                
            # Convert to bytes if the helper returned a string
            if isinstance(plist_bytes, str):
                plist_bytes = plist_bytes.encode('latin-1')
                
            pl = plistlib.loads(plist_bytes)
        except Exception:
            continue
            
        source_paths.add(source_path)
        
        netServices = pl.get('NetworkServices', {})

        if isinstance(netServices, dict):
            for key, value in netServices.items():
                if isinstance(value, dict) and 'Interface' in value:
                    udn = value['Interface'].get('UserDefinedName', '')
                    service_type = value['Interface'].get('Type', '')
                    service_hardware = value['Interface'].get('Hardware', '')
                    service_devname = value['Interface'].get('DeviceName', '')
                    netService = key
                    
                    data_list_netservices.append((netService, udn, service_type, service_hardware, service_devname, source_name))
                
    # Sort after collecting all valid entries
    data_list_netservices = sorted(data_list_netservices, key=lambda x: x[4])
    
    data_headers = ('Network Service GUID', 'Interface Name', 'Interface Type', 'Interface Hardware', 'Interface Device Name', 'Source File')
    return data_headers, data_list_netservices, '\n'.join(sorted(source_paths))