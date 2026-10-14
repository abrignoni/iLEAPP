__artifacts_v2__ = {
    "wifi_status": {
        "name": "Sysdiagnose - Wifi Status",
        "description": "Parses SysDiagnose wifi status",
        "author": '@Hexordia, @AlexisBrignoni, Codex',
        "creation_date": "2026-09-29",
        "last_update_date": '2026-10-04',
        "requirements": "none",
        "category": "Sysdiagnose - Network",
        "notes": (
            "Diagnostic text file generated inside an iOS sysdiagnose dump. It holds key and value "
            "lines about the device's Wi-Fi state. "
            "Key information found inside includes Wi-Fi MAC address (and sometimes the hardware MAC address), "
            "BSSID (Basic Service Set Identifier) (the BSSID value the file lists; what state of "
            "connection it reflects is not established here), "
            "SSID (Service Set Identifier) (of the access point or router), "
            "connection state details regarding link status, current channel, and signal metrics (RSSI) if active. "
            "SSID and BSSID are not always present: on test data they held values on some "
            "sysdiagnoses and read None or <redacted> on others. "
            "Sysdiagnose Timestamp is read from the first sysdiagnose_<date>_<time> name in the "
            "file's path. Where the name records a UTC offset it is converted to UTC; where it does "
            "not, the datetime is blank and its zone is not established. Folder Time preserves the "
            "complete timestamp text from the name, including formats the parser cannot convert. On the six tested sysdiagnoses still "
            "in their original tar archives, "
            "the archive records wifi_status.txt as written 24 to 41 seconds after that time. "
            "magnet_ios16 carries only an unfinished (IN_PROGRESS) sysdiagnose folder, which "
            "produced no rows."
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
    # Only a recorded UTC offset establishes an instant; preserve the full name value.
    match = re.search(r'sysdiagnose_(\d{4}\.\d{2}\.\d{2}_\d{2}-\d{2}-\d{2}[^\_/\\]*)', path)
    if not match:
        return '', ''
    raw_ts = match.group(1)
    try:
        parsed = datetime.strptime(raw_ts, "%Y.%m.%d_%H-%M-%S%z")
        return parsed.astimezone(timezone.utc), raw_ts
    except ValueError:
        return '', raw_ts

@artifact_processor
def wifi_status(context):
    data_list = []
    source_paths = set()
    
    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), 'wifi_status.txt'):           
        source_name = str(context.get_relative_path(source_path))
        # Pass the full source path to target the internal folder structure
        sysdiag_ts, raw_ts = _extract_sysdiag_ts(source_path)

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
                        data_list.append((sysdiag_ts, raw_ts, 'Hardware MAC Address', hw_mac, source_name))
                        # Strip the extracted hardware string from the original value
                        value = re.sub(r'\s*\(hw=[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}\)', '', value)
                        
                    data_list.append((sysdiag_ts, raw_ts, item, value, source_name))
                    
                else:
                    data_list.append((sysdiag_ts, raw_ts, item, value, source_name))

    data_headers = (('Sysdiagnose Timestamp', 'datetime'), 'Folder Time (as stored)', 'Category', 'Value', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))