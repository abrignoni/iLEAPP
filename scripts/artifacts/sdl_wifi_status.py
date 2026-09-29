__artifacts_v2__ = {
    "wifi_status": {
        "name": "Sysdiagnose - Wifi Status",
        "description": "Parses Sysdiagnose wifi connection status",
        "author": "@Hexordia",
        "creation_date": "2026-09-29",
        "last_update_date": "2026-09-29",
        "requirements": "none",
        "category": "Sysdiagnose - Network",
        "notes": (
            "Diagnostic text file generated inside an iOS sysdiagnose dump. It provides a snapshot of"
            "the device's Wi-Fi state at the exact moment the diagnostic was triggered."
            "Key information found inside include Wi-Fi MAC address (the physical hardware MAC address of the iOS device's Wi-Fi interface),"
            "BSSID (Basic Service Set Identifier) (the MAC address of the wireless access point or router the device was last connected to),"
            "SSID (Service Set Identifier) (The human-readable name of the last connected Wi-Fi network),"
            "connection state details regarding link status, current channel, and signal metrics (RSSI) if active."
        ),
        "paths": (
            '*/WiFi/wifi_status.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "wifi"
    }
}

import re
from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files

@artifact_processor
def wifi_status(context):
    data_list = []
    source_paths = set()
    
    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), 'wifi_status.txt'):
        source_name = str(context.get_relative_path(source_path))

        try:
            if hasattr(file_obj, 'buffer'):
                file_content = file_obj.buffer.read()
            else:
                file_content = file_obj.read()
                
            if not file_content:
                continue
                
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='replace')
                
            lines = file_content.splitlines()
        except Exception:
            continue

        source_paths.add(source_path)

        for line in lines:
            line = line.strip()
            if ': ' in line:
                item, value = line.split(': ', 1)
                item = item.strip()
                value = value.strip()
                
                if 'MAC Address' in item:
                    # Isolate the hardware MAC address if present
                    hw_match = re.search(r'\(hw=([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})\)', value)
                    if hw_match:
                        hw_mac = hw_match.group(1).upper()
                        data_list.append(('Hardware MAC Address', hw_mac, source_name))
                        # Strip the extracted hardware string from the original value
                        value = re.sub(r'\s*\(hw=[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}\)', '', value)
                        
                    if value not in ('<redacted>', 'None'):
                        value = value.upper()
                    data_list.append((item, value, source_name))
                    
                elif 'BSSID' in item:
                    if value not in ('<redacted>', 'None'):
                        value = value.upper()
                    data_list.append((item, value, source_name))
                    
                else:
                    data_list.append((item, value, source_name))

    data_headers = ('Category', 'Value', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))