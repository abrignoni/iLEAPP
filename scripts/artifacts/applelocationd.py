import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_applelocationd(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            
            if key == 'LocationServicesEnabledIn8.0':
                data_list.append(('Location Services Enabled', val))
                logdevinfo(f"Location Services Enabled: {val}")
            
            elif key == 'LastSystemVersion':
                data_list.append(('Last System Version', val))
                logdevinfo(f"Last System Version: {val}")
                
            else:
                data_list.append((key, val ))
                
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Settings - com.apple.locationd.plist')
        report.start_artifact_report(report_folder, 'Settings - com.apple.locationd.plist')
        report.add_script()
        data_headers = ('Key','Values' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Settings - com.apple.locationd.plist'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Settings - com.apple.locationd.plist')
            



__artifacts__ = {
    "applelocationd": (
        "Identifiers",
        ('*/mobile/Library/Preferences/com.apple.locationd.plist'),
        get_applelocationd)
}
