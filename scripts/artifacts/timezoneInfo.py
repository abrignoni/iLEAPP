from datetime import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def timestampsconv(webkittime):
    unix_timestamp = webkittime + 978307200
    finaltime = datetime.utcfromtimestamp(unix_timestamp)
    return(finaltime)

def get_timezoneInfo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            
            if key == 'lastBootstrapTimeZone':
                data_list.append(('lastBootstrapTimeZone', val))
                logdevinfo(f"Last Bootstrap Timezone: {val}")
                
            elif key == 'lastBootstrapDate':
                times = timestampsconv(val)
                data_list.append(('lastBootstrapDate', times))
                logdevinfo(f"Last Bootstrap Date: {times}")
                
            else:
                data_list.append((key, val ))
                
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Timezone Information')
        report.start_artifact_report(report_folder, 'Timezone Information')
        report.add_script()
        data_headers = ('Key','Values' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Timezone Information'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Timezone Information in com.apple.AppStore.plist')
            



__artifacts__ = {
    "timezoneInfo": (
        "Identifiers",
        ('*/mobile/Library/Preferences/com.apple.AppStore.plist'),
        get_timezoneInfo)
}
