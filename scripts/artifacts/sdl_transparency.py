__artifacts_v2__ = {
    "transparency_devices": {
        "name": "Sysdiagnose - Transparency Log",
        "description": "Parses Transparency log devices from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": ('*/Transparency.log'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "download-cloud"
    },
    "transparency_cloud": {
        "name": "Sysdiagnose - Transparency Log Cloud Records",
        "description": "Parses Transparency log cloud records from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": ('*/Transparency.log'),
        "output_types": ["html", "timeline", "tsv", "lava"],
        "artifact_icon": "box"
    }
}

import json
from scripts.ilapfuncs import artifact_processor, convert_utc_human_to_timezone, convert_ts_int_to_utc
#from scripts.builds_ids import OS_build, device_id

@artifact_processor
def transparency_devices(context):
    data_list_devices = []
    source_paths = set()

    for file_found in context.get_files_found():
        if 'PaxHeader' in file_found:
            continue
        else:
            source_name = str(context.get_relative_path(file_found))
            source_paths.add(file_found)
            with open(file_found, "r", encoding='utf-8') as f:
                json_file = json.loads(f.read())
                if 'stateMachine' in json_file:
                    # Devices
                    if not (json_file['stateMachine'].get('devices') is None):
                        stateMachine = json_file['stateMachine']['devices']
                        
                        for x in stateMachine.values():
                            name = x.get('name','')
                            #dev_model = device_id.get(x.get('model',''),x.get('model',''))
                            dev_model = context.lookup_metadata('apple_device_id_to_model', x.get('model',''))
                            if dev_model == '':
                                dev_model = x.get('model','')
                            
                            build = x.get('build','')
                            #os_version = OS_build.get(x.get('build',''),x.get('build',''))
                            os_version = context.get_apple_os_version(x.get('build',''),x.get('build',''))
                            
                            devID = x.get('deviceID','')
                            pushToken = x.get('pushToken','')
                            serial = x.get('serial','')
                            
                            data_list_devices.append((name,dev_model,os_version,build,serial,devID,pushToken,source_name))
    
    data_headers = ('Device Name','Device Model','OS Version','OS Build','Serial Number','Device ID','Push Token','Source File')
    return data_headers, data_list_devices, '\n'.join(sorted(source_paths))

@artifact_processor                    
def transparency_cloud(context):
    data_list_cloudrecords = []
    source_paths = set()

    for file_found in context.get_files_found():
        if 'PaxHeader' in file_found:
            continue
        else:
            source_name = str(context.get_relative_path(file_found))
            source_paths.add(file_found)
            with open(file_found, "r", encoding='utf-8') as f:
                json_file = json.loads(f.read())
                if 'stateMachine' in json_file:                    
                    # Cloud Records        
                    if not (json_file['stateMachine'].get('cloudRecords') is None):
                        cloudRecords = json_file['stateMachine'].get('cloudRecords')
                        if 'optIn' in cloudRecords:
                            for name, values in cloudRecords['optIn'].items():
                                item_name = name
                                timestamp = ''
                                state = ''
                                osVersion = ''
                                serial = ''
                                for x,y in values.items():
                                    if x == 'timestampReadable':
                                        #timestamp = convert_utc_human_to_timezone(convert_ts_int_to_utc(int(float(y))),time_offset)
                                        timestamp = str(y).split(' +')[0]
                                    if x == 'state':
                                        state = y
                                    if x == 'osVersion':
                                        if y == '-':
                                            continue
                                        else:
                                            osVersion = y
                                    if x == 'sn':
                                        if y == '-':
                                            continue
                                        else:
                                            serial = y
                                    
                                data_list_cloudrecords.append((timestamp,item_name,state,osVersion,serial,source_name))
    
    data_headers = (('Timestamp','datetime'),'Record','State','OS Version','Serial Number','Source File')
    return data_headers, data_list_cloudrecords, '\n'.join(sorted(source_paths))