__artifacts_v2__ = {
    "transparency_devices": {
        "name": "Sysdiagnose - Transparency Log",
        "description": "Parses Transparency log devices from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": (
            '*/[Tt]ransparency.log',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "download-cloud"
    },
    "transparency_cloud": {
        "name": "Sysdiagnose - Transparency Log Cloud Records",
        "description": "Parses Transparency log cloud records from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": (
            '*/[Tt]ransparency.log',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "timeline", "tsv", "lava"],
        "artifact_icon": "box"
    }
}

import json
import re
from datetime import datetime, timezone
from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

regex_pattern = re.compile(r"[Tt]ransparency\.log")

def _parse_to_utc(ts_str):
    """Converts offset date strings (e.g. 2023-05-20 18:36:50.961 -0400) to UTC formatted strings."""
    if not ts_str:
        return ""
    ts_str = ts_str.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f %z", "%Y-%m-%d %H:%M:%S %z"):
        try:
            dt = datetime.strptime(ts_str, fmt)
            dt_utc = dt.astimezone(timezone.utc)
            if dt.microsecond:
                return dt_utc.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            return dt_utc.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    return ts_str

@artifact_processor
def transparency_devices(context):
    data_list_devices = []
    source_paths = set()
    
    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), regex_pattern):
        if 'PaxHeader' in source_path:
            continue
        else:
            source_name = context.get_relative_path(source_path)
            source_paths.add(source_path)
            try:
                f = json.load(file_obj)
            except json.JSONDecodeError:
                continue
            
            if 'stateMachine' in f:
                # Devices
                if not (f['stateMachine'].get('devices') is None):
                    stateMachine = f['stateMachine']['devices']
                    
                    for x in stateMachine.values():
                        name = x.get('name','')
                        dev_model = context.lookup_metadata('apple_device_id_to_model', x.get('model',''))
                        if dev_model == '':
                            dev_model = x.get('model','')
                        
                        build = x.get('build','')
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

    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), regex_pattern):
        if 'PaxHeader' in source_path:
            continue
        else:
            source_name = context.get_relative_path(source_path)
            source_paths.add(source_path)
            try:
                f = json.load(file_obj)
            except json.JSONDecodeError:
                continue
                
            if 'stateMachine' in f:                    
                # Cloud Records        
                if not (f['stateMachine'].get('cloudRecords') is None):
                    cloudRecords = f['stateMachine'].get('cloudRecords')
                    if 'optIn' in cloudRecords:
                        for name, values in cloudRecords['optIn'].items():
                            item_name = name
                            timestamp = ''
                            state = ''
                            osVersion = ''
                            serial = ''
                            for x,y in values.items():
                                if x == 'timestampReadable':
                                    timestamp = _parse_to_utc(y)
                                    #timestamp = str(y).split(' +')[0]
                                    
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