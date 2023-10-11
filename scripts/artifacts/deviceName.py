import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_deviceName(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            
            if key == '-DeviceName':
                devicenamed = val
                logdevinfo(f"Device Name: {val}")
                
__artifacts__ = {
    "deviceName": (
        "Identifiers",
        ('*/root/Library/Lockdown/data_ark.plist'),
        get_deviceName)
}
