__artifacts_v2__ = {
    "get_sysShutdown": {
        "name": "Sysdiagnose - Shutdown Log",
        "description": "Parses the shutdown.log file from Sysdiagnose logs, based off work by Kaspersky Lab https://github.com/KasperskyLab/iShutdown",
        "author": "@KevinPagano3",
        "version": "0.1",
        "date": "2024-02-13",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "",
        "paths": ('*/shutdown.log'),
        "output_types": "none", #["html","tsv","timeline","lava"]
        "function": "get_sysShutdown"
    }
}

from datetime import datetime
import os
import re

from scripts.artifact_report import ArtifactHtmlReport
from scripts.lavafuncs import lava_process_artifact, lava_insert_sqlite_data
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, convert_ts_int_to_utc, convert_utc_human_to_timezone

def get_sysShutdown(files_found, report_folder, seeker, wrap_text, time_offset):
    
    data_list_shutdown_log = []
    data_list_shutdown_reboot = []
    category = "Sysdiagnose"
    module_name = "get_sysShutdown"
    
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
                    reboot_time = convert_utc_human_to_timezone(convert_ts_int_to_utc(timestamp),time_offset)
                    data_list_shutdown_reboot.append((reboot_time,reboots,file_found))
                    reboots += 1
                    
                    for pid, path in entries:
                        data_list_shutdown_log.append((reboot_time,entry_num,pid,path,file_found))
                        
                        entry_num += 1
                    entries = []
           
    # Shutdown Log Processes Report    
    if len(data_list_shutdown_log) > 0:
        report1 = ArtifactHtmlReport('Sysdiagnose - Shutdown Log Processes')
        report1.start_artifact_report(report_folder, 'Sysdiagnose - Shutdown Log Processes')
        report1.add_script()
        data_headers1 = ('Timestamp','Entry Number','PID','Path','Source File')
        data_headers1_lava = (('Timestamp','datetime'),'Entry Number','PID','Path','Source File')

        report1.write_artifact_data_table(data_headers1, data_list_shutdown_log, file_found)
        report1.end_artifact_report()
        
        tsv(report_folder, data_headers1, data_list_shutdown_log, 'Sysdiagnose - Shutdown Log Processes')
        
        timeline(report_folder, 'Sysdiagnose - Shutdown Log Processes', data_list_shutdown_log, data_headers1)
        
        #data_headers1[0] = (data_headers1[0], 'datetime')
        
        table_name1, object_columns1, column_map1 = lava_process_artifact(category, module_name, 'Sysdiagnose - Shutdown Log Processes', data_headers1_lava, len(data_list_shutdown_log))
        lava_insert_sqlite_data(table_name1, data_list_shutdown_log, object_columns1, data_headers1_lava, column_map1)
        
    else:
        logfunc('No Sysdiagnose - Shutdown Log Processes data available')
        
    # Shutdown Log Report    
    if len(data_list_shutdown_reboot) > 0:
        report = ArtifactHtmlReport('Sysdiagnose - Shutdown Log Reboots')
        report.start_artifact_report(report_folder, 'Sysdiagnose - Shutdown Log Reboots')
        report.add_script()
        data_headers2 = ('Timestamp','Reboot Number','Source File')
        data_headers2_lava = (('Timestamp','datetime'),'Reboot Number','Source File')

        report.write_artifact_data_table(data_headers2, data_list_shutdown_reboot, file_found)
        report.end_artifact_report()
        
        tsv(report_folder, data_headers2, data_list_shutdown_reboot, 'Sysdiagnose - Shutdown Log Reboots')
        
        timeline(report_folder, 'Sysdiagnose - Shutdown Log Reboots', data_list_shutdown_reboot, data_headers2)
        
        #data_headers2[0] = (data_headers2[0], 'datetime')
        
        table_name2, object_columns2, column_map2 = lava_process_artifact(category, module_name, 'Sysdiagnose - Shutdown Log Reboots', data_headers2_lava, len(data_list_shutdown_reboot))
        lava_insert_sqlite_data(table_name2, data_list_shutdown_reboot, object_columns2, data_headers2_lava, column_map2)
        
    else:
        logfunc('No Sysdiagnose - Shutdown Log Reboots data available')
        