from datetime import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_findMy(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            
            if key == 'addTime':
                addtime = datetime.utcfromtimestamp(val)
                data_list.append(('Find My iPhone Add Time', addtime))
                logdevinfo(f"Find My iPhone: Enabled")
                logdevinfo(f"Find My iPhone Add Time: {addtime}")
                
            else:
                data_list.append((key, val ))
                
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Find My iPhone Settings')
        report.start_artifact_report(report_folder, 'Find My iPhone Settings')
        report.add_script()
        data_headers = ('Key','Values' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Find My iPhone Settings'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Find My iPhone Settings available')
            

__artifacts__ = {
    "findMy": (
        "Identifiers",
        ('*/mobile/Library/Preferences/com.apple.icloud.findmydeviced.FMIPAccounts.plist'),
        get_findMy)
}
