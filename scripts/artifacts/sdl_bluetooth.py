__artifacts_v2__ = {
    "bluetooth_status": {
        "name": "Sysdiagnose - Bluetooth Status",
        "description": "Parses Bluetooth status from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": (
            '*/WiFi/bluetooth_status.txt',
            '*/logs/Bluetooth/CoreCapture/bluetooth_status.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bluetooth"
    },
    "bluetooth_devices": {
        "name": "Sysdiagnose - Bluetooth Devices",
        "description": "Parses Bluetooth devices from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": (
            '*/WiFi/bluetooth_status.txt',
            '*/logs/Bluetooth/CoreCapture/bluetooth_status.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bluetooth"
    }
}

from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files

@artifact_processor
def bluetooth_status(context):
    data_list_bluetooth_status = []
    source_paths = set()

    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), "bluetooth_status.txt", text_mode=True, encoding='utf-8'):
        source_name = str(context.get_relative_path(source_path))
        if "/CoreCapture/" in source_path: # Skips duplicate files from "logs/Bluetooth/CoreCapture/"
            continue
        # Bluetooth Status
        if source_path.endswith('bluetooth_status.txt'):
            source_paths.add(source_path)
            
            lines = file_obj.readlines()[2:8]

            for line in lines:
                line = line.strip()
                if ': ' in line:
                    item, value = line.split(': ', 1)
                    item = item.strip()
                    value = value.strip()
                    
                    if 'MAC Address' in item and value != 'None':
                        value = str(value).upper()
                    
                    data_list_bluetooth_status.append((item, value, source_name))

    data_headers = ('Category', 'Value', 'Source File')
    return data_headers, data_list_bluetooth_status, '\n'.join(sorted(source_paths))


@artifact_processor
def bluetooth_devices(context):
    def read_device_chunks(file, start_line=9):
        """Yields blocks of lines grouped by blank-line separation."""
        # Skip the initial header lines
        for _ in range(start_line):
            try:
                next(file)
            except StopIteration:
                return
        
        chunk = []
        for line in file:
            stripped = line.strip()
            if stripped:
                chunk.append(stripped)
            elif chunk:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

    def process_chunks(file_path, source_name):
        """Extracts device names and key-value pairs safely from variable chunks."""
        for chunk in read_device_chunks(file_path, start_line=9):
            if not chunk:
                continue
            
            # The first line is the device name
            device_name = chunk[0]
            
            # Parse subsequent lines into a key-value dictionary
            device_props = {}
            for line in chunk[1:]:
                if ':' in line:
                    key, val = line.split(':', 1)
                    device_props[key.strip()] = val.strip()
            
            # Extract fields with safe defaults if not present
            address_val = str(device_props.get('Address', '')).upper()
            paired_val = device_props.get('Paired', '')
            cloud_paired_val = device_props.get('CloudPaired', '')
            connected_val = device_props.get('Connected', '')
            type_val = device_props.get('Type', '')
            le_val = device_props.get('LE', '')
            
            data_list_bt_device.append((
                device_name,
                address_val,
                paired_val,
                cloud_paired_val,
                connected_val,
                type_val,
                le_val,
                source_name
            ))
    
    data_list_bt_device = []
    source_paths = set()   
    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), "bluetooth_status.txt", text_mode=True, encoding='utf-8'):
        source_name = str(context.get_relative_path(source_path))
        if "/CoreCapture/" in source_path: # Skips duplicate files from "logs/Bluetooth/CoreCapture/"
            continue
            
        if source_path.endswith('bluetooth_status.txt'):
            source_paths.add(source_path)
            process_chunks(file_obj, source_name)
    
    data_headers = (
        'Device Name',
        'Address',
        'Paired',
        'Cloud Paired',
        'Connected',
        'Type',
        'Low Energy',
        'Source File'
    )
    return data_headers, data_list_bt_device, '\n'.join(sorted(source_paths))