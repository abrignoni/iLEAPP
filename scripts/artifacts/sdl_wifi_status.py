__artifacts_v2__ = {
    "wifi_status": {
        "name": "Sysdiagnose - Wifi Status",
        "description": "Parses SysDiagnose wifi status",
        "author": "@Hexordia",
        "creation_date": "2026-09-29",
        "last_update_date": "2026-09-30",
        "requirements": "none",
        "category": "Sysdiagnose - Network",
        "notes": (
            "Diagnostic text file generated inside an iOS sysdiagnose dump. It provides a snapshot of "
            "the device's Wi-Fi state when the Sysdiagnose was triggered. "
            "Key information found inside includes Wi-Fi MAC address (and sometimes the hardware MAC address), "
            "BSSID (Basic Service Set Identifier) (the MAC address of the wireless access point or router the device was connected to when the file was written), "
            "SSID (Service Set Identifier) (of the access point or router), "
            "connection state details regarding link status, current channel, and signal metrics (RSSI) if active. "
            "SSID and BSSID are not always present: on the tested sysdiagnoses they held values on iOS 13, 14 and 16, "
            "read None on iOS 17.3 and <redacted> on iOS 26. "
            "Sysdiagnose Timestamp is read from the sysdiagnose folder name, which records the device's UTC offset, "
            "and is converted to UTC. On the six tested sysdiagnoses still in their original tar archives, "
            "the archive records wifi_status.txt as written 24 to 41 seconds after that time. "
            "magnet_ios16 carries only an unfinished (IN_PROGRESS) sysdiagnose, which is not read."
        ),
        "paths": (
            '*/WiFi/wifi_status.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "wifi",
        "sample_data": {
            "ai16_ios26_sysdiag": "iOS 26.5.2 | 31 rows",
            "hc_ios26_sysdiag": "iOS 26 | 31 rows",
            "rodeo_ios17_sysdiag": "iOS 17.3 | 29 rows",
            "felix23_ios16": "iOS 16.5 | 60 rows",
            "hickman_ios13": "iOS 13.3.1 | 28 rows",
            "hickman_ios14": "iOS 14.3 | 28 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

import re
import tarfile
import zlib
from datetime import datetime, timezone
from scripts.ilapfuncs import artifact_processor, get_sysdiagnose_files, logfunc

def _extract_sysdiag_ts(path):
    # Extracts the timestamp embedded in the sysdiagnose internal folder name and converts it to UTC.
    match = re.search(r'sysdiagnose_(\d{4}\.\d{2}\.\d{2}_\d{2}-\d{2}-\d{2}[^\_/\\]*)', path)
    if match:
        raw_ts = match.group(1)
        # Attempt to parse with and without the timezone offset
        for fmt in ("%Y.%m.%d_%H-%M-%S%z", "%Y.%m.%d_%H-%M-%S"):
            try:
                dt = datetime.strptime(raw_ts, fmt)
                if dt.tzinfo:
                    dt = dt.astimezone(timezone.utc)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
        
        # Fallback if standard parsing fails but we still extracted something
        parts = raw_ts.split('_')
        if len(parts) >= 2:
            date_part = parts[0].replace('.', '-')
            time_part = parts[1][:8].replace('-', ':')
            return f"{date_part} {time_part} (Raw)"
    return ''

@artifact_processor
def wifi_status(context):
    data_list = []
    source_paths = set()
    
    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), 'wifi_status.txt'):           
        source_name = str(context.get_relative_path(source_path))
        # Pass the full source path to target the internal folder structure
        sysdiag_ts = _extract_sysdiag_ts(source_path)

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
        except (OSError, EOFError, tarfile.TarError, zlib.error) as e:
            logfunc(f"Wifi Status: error reading {source_path}: {e}")
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
                        hw_mac = hw_match.group(1)
                        data_list.append((sysdiag_ts, 'Hardware MAC Address', hw_mac, source_name))
                        # Strip the extracted hardware string from the original value
                        value = re.sub(r'\s*\(hw=[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}\)', '', value)
                        
                    data_list.append((sysdiag_ts, item, value, source_name))
                    
                else:
                    data_list.append((sysdiag_ts, item, value, source_name))

    data_headers = (('Sysdiagnose Timestamp', 'datetime'), 'Category', 'Value', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))