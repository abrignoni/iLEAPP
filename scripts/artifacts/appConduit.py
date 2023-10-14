import datetime
import glob
import os
import sys
import stat
import pathlib
import string
import json
import re
import textwrap

from html import escape

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, convert_time_obj_to_utc, convert_time_obj_to_utc 

def get_appConduit(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    device_type_and_info = []

    info = ''
    reg_filter = (r'(([A-Za-z]+[\s]+([a-zA-Z]+[\s]+[0-9]+)[\s]+([0-9]+\:[0-9]+\:[0-9]+)[\s]+([0-9]{4}))([\s]+[\[\d\]]+[\s]+[\<a-z\>]+[\s]+[\(\w\)]+)[\s\-]+(((.*)(device+\:([\w]+\-[\w]+\-[\w]+\-[\w]+\-[\w]+))(.*)$)))')        
    date_filter = re.compile(reg_filter)
    
    source_files = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.startswith('\\\\?\\'):
            file_name = pathlib.Path(file_found[4:]).name
            source_files.append(file_found[4:])
        else:
            file_name = pathlib.Path(file_found).name
            source_files.append(file_found)

        file = open(file_found, "r", encoding="utf8")
        linecount = 0

        for line in file:
            linecount = linecount + 1
            line_match = re.match(date_filter, line)
            

            if line_match:
                date_time = line_match.group(3, 5, 4)
                conv_time = ' '.join(date_time)
                dtime_obj = datetime.datetime.strptime(conv_time, '%b %d %Y %H:%M:%S')
                dtime_obj = convert_time_obj_to_utc(dtime_obj)
                dtime_obj = convert_utc_human_to_timezone(dtime_obj, timezone_offset)
                
                values  = line_match.group(9)
                device_id = line_match.group(11)

                if 'devicesAreNowConnected' in values:
                    device_type_and_info.append((device_id,line_match.group(12).split(" ")[4],line_match.group(12).split(" ")[5]))
                    info = 'Connected'
                    data_list.append((dtime_obj,info,device_id,file_name))
                if 'devicesAreNoLongerConnected' in values:
                    info = 'Disconnected'
                    data_list.append((dtime_obj,info,device_id,file_name))
                # if 'Resuming because' in values:
                #     info = 'Resumed'
                #     data_list.append((dtime_obj,info,device_id,device_type_tmp,file_name))
                # if 'Suspending because' in values:
                #     info = 'Suspended'
                #     data_list.append((dtime_obj,info,device_id,device_type_tmp,file_name))
                # if 'Starting reunion sync because device ' in values:
                #     info = 'Reachable again after reunion sync'
                #     data_list.append((dtime_obj,info,device_id,device_type_tmp,file_name))

    device_type_and_info = list(set(device_type_and_info))

    data_headers_device_info = ('Device ID', 'Device type and version', 'Device extra information')
    data_headers = ('Time', 'Device interaction', 'Device ID', 'Log File Name')   

    report = ArtifactHtmlReport('App Conduit')
    report.start_artifact_report(report_folder, 'App Conduit', 'The AppConduit log file stores information about interactions between iPhone and other iOS devices, i.e. Apple Watch')
    
    report.add_script()
    source_files_found = ', '.join(source_files)
    
    report.write_artifact_data_table(data_headers_device_info, device_type_and_info, source_files_found, cols_repeated_at_bottom=False)
    report.write_artifact_data_table(data_headers, data_list, file_found, True, False)
    report.end_artifact_report()

    tsvname = 'App Conduit'
    tsv(report_folder, data_headers, data_list, tsvname)        
    
__artifacts__ = {
    "appconduit": (
        "App Conduit",
        ('**/AppConduit.log.*'),
        get_appConduit)
}