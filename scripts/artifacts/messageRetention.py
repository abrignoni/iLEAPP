from datetime import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_messageRetention(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            
            if key == 'KeepMessageForDays':
                data_list.append(('Keep Message for Days', val))
                logdevinfo(f"Keep Message for Days: {val}")
            
        if len(data_list) == 0:
            data_list.append(('Keep Message for Days', 'Forever'))
            logdevinfo(f"Keep Message for Days: Forever")
            
    if len(data_list) > 0:
        report = ArtifactHtmlReport('iOS Message Retention')
        report.start_artifact_report(report_folder, 'iOS Message Retention')
        report.add_script()
        data_headers = ('Key','Values' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'iOS Message Retention'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No iOS Message Retention data')
            

__artifacts__ = {
    "messageRetention": (
        "Identifiers",
        ('*/mobile/Library/Preferences/com.apple.MobileSMS.plist'),
        get_messageRetention)
}
