import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_preferencesPlist(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            
            if key == ("Model"):
                data_list.append((key, val))
                logfunc(f"Model: {val}")
                logdevinfo(f"Model: {val}")
            
            if key == "System":
                localhostname = val['Network']['HostNames']['LocalHostName']
                data_list.append(('Local Host Name', localhostname ))
                logdevinfo(f"Model: {localhostname }")
                
                computername = val['System']['ComputerName']
                data_list.append(('Device/Computer Name', computername))
                logdevinfo(f"Device/Computer Name: {computername}")
                
                hostname = val['System']['HostName']
                data_list.append(('Host Name', hostname ))
                logdevinfo(f"Host Name: {hostname }")

  
    report = ArtifactHtmlReport('Device Preferences Plist')
    report.start_artifact_report(report_folder, 'Device Preferences Plist')
    report.add_script()
    data_headers = ('Key','Values' )     
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    
    tsvname = 'Device Preferences Plist'
    tsv(report_folder, data_headers, data_list, tsvname)
            



__artifacts__ = {
    "preferencesPlist": (
        "Identifiers",
        ('*preferences/SystemConfiguration/preferences.plist'),
        get_preferencesPlist)
}
