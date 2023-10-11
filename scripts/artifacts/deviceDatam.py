import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_deviceDatam(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            
            if key == 'imeis':
                imeis = val
                #print(imeis[0])
                data_list.append(('IMEIs', imeis ))
                logdevinfo(f"IMEIs: {imeis}")
            
            elif key == 'ReportedPhoneNumber':
                reportedphonenum = val
                data_list.append(('Reported Phone Number', val ))
                logdevinfo(f"Reported Phone Number: {val}")
                
            else:
                data_list.append((key, val ))
                
    report = ArtifactHtmlReport('Device Data')
    report.start_artifact_report(report_folder, 'Device Data')
    report.add_script()
    data_headers = ('Key','Values' )     
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    
    tsvname = 'Device Data'
    tsv(report_folder, data_headers, data_list, tsvname)
            



__artifacts__ = {
    "devicedata": (
        "Identifiers",
        ('*wireless/Library/Preferences/com.apple.commcenter.device_specific_nobackup.plist'),
        get_deviceDatam)
}
