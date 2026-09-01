import os
import re
from datetime import datetime, timezone
from scripts.ilapfuncs import artifact_processor, logfunc

__artifacts_v2__ = {
    "spindump_process": {
        "name": "Sysdiagnose - Spin Dump Processes",
        "description": "Parses process metadata, PID, state, and resource consumption from Apple spindump logs",
        "author": "@stark4n6 & Gemini",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": ('*/spindump-nosymbols.txt'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "activity",
    }
}


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
def spindump_process(context):
    data_list = []
    source_paths = set()
    # Regex patterns for header metadata and process blocks
    header_start_time_pattern = re.compile(r"^Date/Time:\s+(.+)$")
    header_end_time_pattern = re.compile(r"^End time:\s+(.+)$")
    header_os_pattern = re.compile(r"^OS Version:\s+(.+)$")
    header_hw_pattern = re.compile(r"^Hardware model:\s+(.+)$")

    process_header_pattern = re.compile(
        r"^Process:\s+(?P<process_name>.+?)\s+\[(?P<pid>\d+)\](?:\s*\((?P<state>.+?)\))?\s*$"
    )
    key_val_pattern = re.compile(r"^(?P<key>[A-Za-z0-9\s]+?):\s+(?P<val>.*)$")
    
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            continue

        source_name = str(context.get_relative_path(file_found))
        source_paths.add(file_found)
        global_start_time = ""
        global_end_time = ""
        os_version = ""
        hw_model = ""

        try:
            with open(
                file_found, "r", encoding="utf-8", errors="replace"
            ) as f_in:
                lines = f_in.readlines()
        except Exception as e:
            logfunc(f"[!] Could not read {file_found}: {e}")
            continue

        in_process_block = False
        current_proc = {}

        for line in lines:
            line_str = line.strip()

            # Global report context (Lines 1-2 & hardware metadata)
            if not global_start_time and header_start_time_pattern.match(line_str):
                global_start_time = header_start_time_pattern.match(
                    line_str
                ).group(1)
                continue
            if not global_end_time and header_end_time_pattern.match(line_str):
                global_end_time = header_end_time_pattern.match(
                    line_str
                ).group(1)
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
                # Flush previous entry if one was being tracked
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

        # Handle final trailing process block at end of file
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
    """Formats timestamps to UTC and safely extracts dictionary values into standard row ordering."""
    # Use process-specific start/end times if logged (e.g. backupd), otherwise fall back to report times
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