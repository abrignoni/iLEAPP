__artifacts_v2__ = {
    "remotectl_dump": {
        "name": "Sysdiagnose - Dump State",
        "description": "Parses dump state details from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": ('*/remotectl_dumpstate.txt',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    }
}

from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def remotectl_dump(context):
    data_list = []
    source_paths = set()

    for file_found in context.get_files_found():
        if 'PaxHeader' in file_found:
            continue
        else:
            source_name = str(context.get_relative_path(file_found))
            source_paths.add(file_found)
            with open(file_found, encoding = 'utf-8', mode = 'r') as f:
                lines = f.readlines()[1:]
                
                for line in lines:
                    if 'UUID: ' in line:
                        entry = line.strip().split('UUID: ')
                        UUID = entry[1]
                        data_list.append(('UUID',UUID,source_name))

                        device_info("Device Information", "UUID", UUID, source_name)
                    
                    elif 'Product Type: ' in line:
                        entry = line.strip().split('Product Type: ')
                        prod_type = context.lookup_metadata('apple_device_id_to_model',entry[1])
                        data_list.append(('Product Type',prod_type,source_name))

                        device_info("Device Information", "Product Type", prod_type, source_name)
                        
                    elif 'OS Build: ' in line:
                        entry = line.strip().split('OS Build: ')
                        os_build = entry[1]
                        data_list.append(('OS Build',os_build,source_name))
                        
                    elif 'SerialNumber => ' in line:
                        entry = line.strip().split('SerialNumber => ')
                        serial = entry[1]
                        data_list.append(('Serial Number',serial,source_name))
                        
                        device_info("Device Information", "Device Serial Number", serial, source_name)
                        
                    elif 'ModelNumber => ' in line:
                        entry = line.strip().split('ModelNumber => ')
                        model_num = entry[1]
                        data_list.append(('Model Number',model_num,source_name))
                        
                    elif 'RegionCode => ' in line:
                        entry = line.strip().split('RegionCode => ')
                        prod_region = context.lookup_metadata('apple_device_region_code_to_region',entry[1])
                        data_list.append(('Product Region',prod_region,source_name))

                        device_info("Device Information", "Product Region", prod_region, source_name)
                        
                    elif 'HWModel => ' in line:
                        entry = line.strip().split('HWModel => ')
                        hwmodel = entry[1]
                        data_list.append(('Hardware Model',hwmodel,source_name))
                    
                    elif 'CPUArchitecture => ' in line:
                        entry = line.strip().split('CPUArchitecture => ')
                        cpu_arch = entry[1]
                        data_list.append(('CPU Architecture',cpu_arch,source_name))
                        
                    elif 'UniqueDeviceID => ' in line:
                        entry = line.strip().split('UniqueDeviceID => ')
                        unique_dev = entry[1]
                        data_list.append(('Unique Device ID',unique_dev,source_name))
                        
                    elif 'UniqueChipID => ' in line:
                        entry = line.strip().split('UniqueChipID => ')
                        unique_chip = entry[1]
                        data_list.append(('Unique Chip ID',unique_chip,source_name))

    data_headers = ('Property','Value','Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))