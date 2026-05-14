__artifacts_v2__ = {
    "droneFlightLog": {
        "name": "Drone - .LOG files",
        "description": "Parse log data from DJI Drone LOG files (*.LOG) and Extracts Events.",
        "author": "@NoviAdintya, @HudanStudiawan, @BaskoroAdiPratomo",
        "version": "1.1",
        "date": "2025-03-16",
        "requirements": "DJI drone log files (*.log) from device storage.",
        "category": "Drone Logs",
        "notes": "Processes log timestamps, log levels, sources, and messages.",
        "paths": ("**/*.log",),
        "output_types": "all",
        "artifact_icon": "slack"
    }
}

import re
import os
import datetime
from scripts.ilapfuncs import artifact_processor, logfunc

@artifact_processor
def droneFlightLog(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    data_list = []
    source_paths = set()
    sorted_files = sorted(files_found, key=os.path.getmtime)
    logfunc(f'Found {len(sorted_files)} log files.')
    for file_found in sorted_files:
        if file_found.lower().endswith('.log'):
            logfunc(f'Processing: {file_found}')
            log_entries = parse_dji_log(file_found)
            if log_entries:
                data_list.extend(log_entries)
            source_paths.add(file_found)
    if not data_list:
        logfunc('No valid log data found in any file.')
        return None
    data_headers = (('Timestamp', 'datetime'), 'Log Level', 'Source', 'Message')
    return data_headers, data_list, ', '.join(source_paths)

def parse_dji_log(file_path):
    log_entries = []
    try:
        file_date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).date()
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*\[(.)\]\s*\[(.*?)\]\s*(.+)', line)
                if match:
                    time_part, log_level, log_source, message = match.groups()
                    timestamp = f"{file_date} {time_part}"
                    message = re.sub(r':\[\w+\.\w+\.\w+\]\s*', '', message).strip()
                    log_entries.append((timestamp, log_level, log_source, message))
    except (OSError, RuntimeError) as e:
        logfunc(f"Error processing {file_path}: {str(e)}")
    return log_entries
