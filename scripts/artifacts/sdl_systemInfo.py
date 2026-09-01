__artifacts_v2__ = {
    "systemInfo": {
        "name": "Sysdiagnose - System OS Info",
        "description": "Parses system OS info from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": "",
        "paths": ('*/SystemVersion/SystemVersion.plist','*/OS/SystemVersion.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    }
}

import os
import plistlib
 
from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def systemInfo(context):
    data_list = []
    source_paths = set()
    prod_version = ''
    build_version = ''

    for file_found in context.get_files_found():
        source_name = str(context.get_relative_path(file_found))
        source_paths.add(file_found)
    
        with open(file_found, 'rb') as f:
            pl = plistlib.load(f)
            
            prod_name = pl['ProductName']
            prod_version = pl['ProductVersion']
            build_id = pl['BuildID']
            build_version = pl['ProductBuildVersion']
            sys_img_id = pl['SystemImageID']
             
            data_list.append((prod_name,prod_version,build_id,build_version,sys_img_id,source_name))
            
    device_info('Device Information', 'OS Version', prod_version, source_name)
    device_info('Device Information', 'OS Build Version', build_version, source_name)
    
    data_headers = ('Product Name','Product Version','Build ID','Product Build Version','System Image ID','Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))