__artifacts_v2__ = {
    "sysShutdown": {
        "name": "Sysdiagnose - Shutdown Log",
        "description": "Parses the shutdown.log file from Sysdiagnose logs, based off work by Kaspersky Lab https://github.com/KasperskyLab/iShutdown",
        "author": "@KevinPagano3",
        "version": "0.1",
        "date": "2024-02-13",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": ('*/shutdown.log'),
        "function": "get_sysShutdown"
    }
}

from datetime import datetime
import os
import re

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, convert_ts_int_to_utc, convert_utc_human_to_timezone

def get_sysShutdown(files_found, report_folder, seeker, wrap_text, time_offset):
    
    data_list_shutdown_log = []
    data_list_shutdown_reboot = []
    
    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, encoding = 'utf-8', mode = 'r') as f:
            lines = f.readlines()
            
            entry_num = 1
            entries = []
            reboots = 1
            
            for line in lines:
                pid_match = re.search(r'remaining client pid: (\d+) \((.*?)\)', line)
                if pid_match:
                    pid, path = pid_match.groups()
                    entries.append((pid, path))

                sigterm_match = re.search(r'SIGTERM: \[(\d+)\]', line)
                if sigterm_match:
                    timestamp = int(sigterm_match.group(1))
                    #reboot_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    reboot_time = convert_utc_human_to_timezone(convert_ts_int_to_utc(timestamp),time_offset)
                    data_list_shutdown_reboot.append((reboot_time,reboots,file_found))
                    reboots += 1
                    
                    for pid, path in entries:
                        data_list_shutdown_log.append((reboot_time,entry_num,pid,path,file_found))
                        
                        entry_num += 1
                    entries = []
           
    # Shutdown Log Processes Report    
    if len(data_list_shutdown_log) > 0:
        report = ArtifactHtmlReport('Sysdiagnose - Shutdown Log Processes')
        report.start_artifact_report(report_folder, 'Sysdiagnose - Shutdown Log Processes')
        report.add_script()
        data_headers = ('Timestamp','Entry Number','PID','Path','Source File')

        report.write_artifact_data_table(data_headers, data_list_shutdown_log, file_found)
        report.end_artifact_report()
        
        tsvname = f'Sysdiagnose - Shutdown Log Processes'
        tsv(report_folder, data_headers, data_list_shutdown_log, tsvname)
        
        tlactivity = f'Sysdiagnose - Shutdown Log Processes'
        timeline(report_folder, tlactivity, data_list_shutdown_log, data_headers)
    else:
        logfunc('No Sysdiagnose - Shutdown Log Processes data available')
        
    # Shutdown Log Report    
    if len(data_list_shutdown_reboot) > 0:
        report = ArtifactHtmlReport('Sysdiagnose - Shutdown Log Reboots')
        report.start_artifact_report(report_folder, 'Sysdiagnose - Shutdown Log Reboots')
        report.add_script()
        data_headers = ('Timestamp','Reboot Number','Source File')

        report.write_artifact_data_table(data_headers, data_list_shutdown_reboot, file_found)
        report.end_artifact_report()
        
        tsvname = f'Sysdiagnose - Shutdown Log Reboots'
        tsv(report_folder, data_headers, data_list_shutdown_reboot, tsvname)
        
        tlactivity = f'Sysdiagnose - Shutdown Log Reboots'
        timeline(report_folder, tlactivity, data_list_shutdown_reboot, data_headers)
    else:
        logfunc('No Sysdiagnose - Shutdown Log Reboots data available')
        