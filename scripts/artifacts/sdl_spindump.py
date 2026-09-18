__artifacts_v2__ = {
    "spindump": {
        "name": "Sysdiagnose - Spin Dump Info",
        "description": "Parses spin dump details from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": (
            '*/spindump-nosymbols.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
    "spindump_process": {
        "name": "Sysdiagnose - Spin Dump Processes",
        "description": "Parses process metadata, PID, state, and resource consumption from Apple spindump logs",
        "author": "@stark4n6 & Gemini",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-18",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": (
            '*/spindump-nosymbols.txt',
            '*/sysdiagnose_*.tar.gz',
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "activity",
    }
}

import re
from datetime import datetime, timezone
from scripts.ilapfuncs import artifact_processor, device_info, get_sysdiagnose_files

def display_time(seconds):
    days = int(seconds / (24 * 3600))
    seconds -= days * (24 * 3600)
    hours = int(seconds / 3600)
    seconds -= hours * 3600
    minutes = int(seconds / 60)
    seconds -= minutes * 60
    return f"{days}d {hours}h {minutes}m {seconds}s"

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
def spindump(context):
    data_list = []
    source_paths = set()

    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), "spindump-nosymbols.txt"):
        if 'PaxHeader' in source_path:
            continue
        
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
                
            # Line slicing offset removed to preserve header lines
            lines = file_content.splitlines()
        except Exception:
            continue
        
        source_paths.add(source_path)
            
        for line in lines:
            if 'Time Since Boot:' in line:
                entry = line.strip().split('Time Since Boot: ')
                sec_since_boot = entry[1][:-1]
                sec_since_boot = display_time(int(sec_since_boot))
                data_list.append(('Duration Since Boot',sec_since_boot,source_name))
                device_info('System Stats','Duration Since Boot',sec_since_boot,source_name)
                
            elif 'Time Awake Since Boot:' in line:
                entry = line.strip().split('Time Awake Since Boot: ')
                sec_awake_since_boot = entry[1][:-1]
                sec_awake_since_boot = display_time(int(sec_awake_since_boot))
                data_list.append(('Duration Awake Since Boot',sec_awake_since_boot,source_name))
                device_info('System Stats','Duration Awake Since Boot',sec_awake_since_boot,source_name)
                
            elif 'Time Since Wake:' in line:
                entry = line.strip().split('Time Since Wake: ')
                if 'n/a ' in line:
                    sec_since_wake = 'N/A (Machine Hasn\'t Slept)'
                else:
                    sec_since_wake = entry[1][:-1]
                    sec_since_wake = display_time(int(sec_since_wake))
                data_list.append(('Duration Since Wake',sec_since_wake,source_name))
                device_info('System Stats','Time Since Wake',sec_since_wake,source_name)
                
            elif 'Preferred User Language: ' in line:
                entry = line.strip().split('Preferred User Language: ')
                language = entry[1]
                data_list.append(('Preferred Language',language,source_name))
                device_info('Settings & Preferences','Preferred Language',language,source_name)
                
            elif 'Country Code: ' in line:
                entry = line.strip().split('Country Code: ')
                country_code = entry[1]
                data_list.append(('Country Code',country_code,source_name))
                device_info('Device Information','Country Code',country_code,source_name)
                
            elif 'Keyboards: ' in line:
                entry = line.strip().split('Keyboards: ')
                keyboards = entry[1]
                data_list.append(('Keyboard(s)',keyboards,source_name))
                
            elif 'Free disk space: ' in line:
                entry = line.strip().split('Free disk space: ')
                disk_space = entry[1].strip().split(', ')
                fds = disk_space[0]
                data_list.append(('Disk Space',fds,source_name))
                device_info('System Stats','Disk Space',fds,source_name)

    data_headers = ('Property','Value','Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def spindump_process(context):
    data_list = []
    source_paths = set()

    header_start_time_pattern = re.compile(r"^Date/Time:\s+(.+)$")
    header_end_time_pattern = re.compile(r"^End time:\s+(.+)$")
    header_os_pattern = re.compile(r"^OS Version:\s+(.+)$")
    header_hw_pattern = re.compile(r"^Hardware model:\s+(.+)$")

    process_header_pattern = re.compile(
        r"^Process:\s+(?P<process_name>.+?)\s+\[(?P<pid>\d+)\](?:\s*\((?P<state>.+?)\))?\s*$"
    )
    key_val_pattern = re.compile(r"^(?P<key>[A-Za-z0-9\s]+?):\s+(?P<val>.*)$")
    
    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), "spindump-nosymbols.txt"):
        if 'PaxHeader' in source_path:
            continue

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
                
            # Line slicing offset removed to preserve header lines
            lines = file_content.splitlines()
        except Exception:
            continue

        source_paths.add(source_path)
        global_start_time = ""
        global_end_time = ""
        os_version = ""
        hw_model = ""

        in_process_block = False
        current_proc = {}

        for line in lines:
            line_str = line.strip()

            # Global report context
            if not global_start_time and header_start_time_pattern.match(line_str):
                global_start_time = header_start_time_pattern.match(line_str).group(1)
                continue
            if not global_end_time and header_end_time_pattern.match(line_str):
                global_end_time = header_end_time_pattern.match(line_str).group(1)
                continue
            if not os_version and header_os_pattern.match(line_str):
                os_version = header_os_pattern.match(line_str).group(1)
                continue
            if not hw_model and header_hw_pattern.match(line_str):
                hw_model = header_hw_pattern.match(line_str).group(1)
                continue

            # Start of a new process entry
            proc_match = process_header_pattern.match(line_str)
            if proc_match:
                if in_process_block and current_proc:
                    _append_process_record(
                        data_list,
                        current_proc,
                        global_start_time,
                        global_end_time,
                        os_version,
                        hw_model,
                        source_name,
                    )
                    current_proc = {}

                in_process_block = True
                current_proc["Process Name"] = proc_match.group("process_name")
                current_proc["PID"] = proc_match.group("pid")
                current_proc["State"] = (
                    proc_match.group("state")
                    if proc_match.group("state")
                    else "Active"
                )
                continue

            # Within process block: capture key-value pairs or detect block termination
            if in_process_block:
                if (
                    line_str.startswith("Thread ")
                    or line_str.startswith("Binary Images:")
                    or line_str.startswith("---")
                ):
                    in_process_block = False
                    _append_process_record(
                        data_list,
                        current_proc,
                        global_start_time,
                        global_end_time,
                        os_version,
                        hw_model,
                        source_name,
                    )
                    current_proc = {}
                    continue

                kv_match = key_val_pattern.match(line_str)
                if kv_match:
                    key = kv_match.group("key").strip()
                    val = kv_match.group("val").strip()
                    current_proc[key] = val

        # Append final process block
        if in_process_block and current_proc:
            _append_process_record(
                data_list,
                current_proc,
                global_start_time,
                global_end_time,
                os_version,
                hw_model,
                source_name,
            )

    data_headers = (
        ("Dump Start Time (UTC)", "datetime"),
        ("Dump End Time (UTC)", "datetime"),
        "Process Name",
        "PID",
        "State",
        "Identifier",
        "Version",
        "Path",
        "UUID",
        "Parent",
        "Responsible",
        "UID",
        "Architecture",
        "Footprint",
        "Time Since Fork",
        "CPU Time",
        "Sudden Term",
        "OS Version",
        "Hardware Model",
        "Source File",
    )

    return data_headers, data_list, '\n'.join(sorted(source_paths))


def _append_process_record(
    data_list,
    proc_dict,
    global_start_time,
    global_end_time,
    os_version,
    hw_model,
    filename,
):
    raw_start = proc_dict.get("Start time", global_start_time)
    raw_end = proc_dict.get("End time", global_end_time)

    utc_start = _parse_to_utc(raw_start)
    utc_end = _parse_to_utc(raw_end)

    record = [
        utc_start,
        utc_end,
        proc_dict.get("Process Name", ""),
        proc_dict.get("PID", ""),
        proc_dict.get("State", ""),
        proc_dict.get("Identifier", ""),
        proc_dict.get("Version", ""),
        proc_dict.get("Path", ""),
        proc_dict.get("UUID", ""),
        proc_dict.get("Parent", ""),
        proc_dict.get("Responsible", ""),
        proc_dict.get("UID", ""),
        proc_dict.get("Architecture", ""),
        proc_dict.get("Footprint", ""),
        proc_dict.get("Time Since Fork", ""),
        proc_dict.get("CPU Time", ""),
        proc_dict.get("Sudden Term", ""),
        os_version,
        hw_model,
        filename,
    ]
    data_list.append(record)