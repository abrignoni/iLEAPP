__artifacts_v2__ = {
    "sysShutdownProcesses": {
        "name": "Sysdiagnose - Shutdown Log Processes",
        "description": "Parses the processes still running at shutdown from the shutdown.log file "
                       "in Sysdiagnose logs, based off work by Kaspersky Lab "
                       "https://github.com/KasperskyLab/iShutdown",
        "author": "@KevinPagano3",
        "creation_date": "2024-02-13",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": ('*/shutdown*.log',),
        "output_types": "standard",
        "artifact_icon": "power"
    },
    "sysShutdownReboots": {
        "name": "Sysdiagnose - Shutdown Log Reboots",
        "description": "Parses reboot events from the shutdown.log file in Sysdiagnose logs, based off "
                       "work by Kaspersky Lab https://github.com/KasperskyLab/iShutdown",
        "author": "@KevinPagano3",
        "creation_date": "2024-02-13",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": ('*/shutdown*.log',),
        "output_types": "standard",
        "artifact_icon": "refresh-cw"
    }
}

import re

from scripts.ilapfuncs import artifact_processor, convert_ts_int_to_utc, logfunc


def _parse_shutdown_logs(context):
    """Parse shutdown.log(s): return (processes, reboots, joined sources). Times are UTC."""
    processes = []
    reboots = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        rel = context.get_relative_path(file_found)
        try:
            with open(file_found, encoding='utf-8', mode='r') as fh:
                lines = fh.readlines()
        except OSError as ex:
            logfunc(f'Failed to read shutdown log {file_found}: {ex}')
            continue

        entry_num = 1
        reboot_num = 1
        entries = []
        for line in lines:
            pid_match = re.search(r'remaining client pid: (\d+) \((.*?)\)', line)
            if pid_match:
                entries.append(pid_match.groups())

            sigterm_match = re.search(r'SIGTERM: \[(\d+)\]', line)
            if sigterm_match:
                reboot_time = convert_ts_int_to_utc(int(sigterm_match.group(1)))
                reboots.append((reboot_time, reboot_num, rel))
                reboot_num += 1
                for pid, path in entries:
                    processes.append((reboot_time, entry_num, pid, path, rel))
                    entry_num += 1
                entries = []
        sources.append(rel)

    return processes, reboots, ', '.join(dict.fromkeys(sources))


@artifact_processor
def sysShutdownProcesses(context):
    data_headers = (('Timestamp', 'datetime'), 'Entry Number', 'PID', 'Path', 'Source File')
    processes, _reboots, source_path = _parse_shutdown_logs(context)
    return data_headers, processes, source_path


@artifact_processor
def sysShutdownReboots(context):
    data_headers = (('Timestamp', 'datetime'), 'Reboot Number', 'Source File')
    _processes, reboots, source_path = _parse_shutdown_logs(context)
    return data_headers, reboots, source_path
