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
        "artifact_icon": "power",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 10 rows",
            "dexter_ios18": "iOS 18.3.2 | 253 rows",
            "fsfull002_ios17": "iOS 17.1 | 539 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1064 rows",
            "iphone12_ios18": "iOS 18.7 | 79 rows",
            "iphone14plus_ios18": "iOS 18.0 | 64 rows",
            "otto_ios17": "iOS 17.5.1 | 188 rows",
            "abe_ios16": "iOS 16.5 | 644 rows",
            "felix23_ios16": "iOS 16.5 | 501 rows",
            "hickman_ios13": "iOS 13.3.1 | 537 rows",
            "hickman_ios14": "iOS 14.3 | 217 rows",
            "jess_ios15": "iOS 15.0.2 | 448 rows",
        }
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
        "artifact_icon": "refresh",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 9 rows",
            "fsfull002_ios17": "iOS 17.1 | 30 rows",
            "hc_ios18_7": "iOS 18.7.8 | 57 rows",
            "iphone12_ios18": "iOS 18.7 | 5 rows",
            "iphone14plus_ios18": "iOS 18.0 | 5 rows",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
            "abe_ios16": "iOS 16.5 | 18 rows",
            "felix23_ios16": "iOS 16.5 | 35 rows",
            "hickman_ios13": "iOS 13.3.1 | 3 rows",
            "hickman_ios14": "iOS 14.3 | 7 rows",
            "jess_ios15": "iOS 15.0.2 | 12 rows",
        }
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
