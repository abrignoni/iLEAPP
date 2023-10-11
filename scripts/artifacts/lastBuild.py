import datetime
import os
import plistlib
import scripts.artifacts.artGlobals 

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_lastBuild(files_found, report_folder, seeker, wrap_text, time_offset):
    versionnum = 0
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            data_list.append((key, val))
            if key == ("ProductVersion"):
                #ilapfuncs.globalvars()
                scripts.artifacts.artGlobals.versionf = val
                logfunc(f"iOS version: {val}")
                logdevinfo(f"iOS version: {val}")
            
            if key == "ProductBuildVersion":
                logdevinfo(f"ProductBuildVersion: {val}")
            
            if key == ("ProductName"):
                logfunc(f"Product: {val}")
                logdevinfo(f"Product: {val}")

  
    report = ArtifactHtmlReport('iOS Build')
    report.start_artifact_report(report_folder, 'Build Information')
    report.add_script()
    data_headers = ('Key','Values' )     
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    
    tsvname = 'Last Build'
    tsv(report_folder, data_headers, data_list, tsvname)
            

def get_iTunesBackupInfo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    versionnum = 0
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if isinstance(val, str) or isinstance(val, int) or isinstance(val, datetime.datetime):
                data_list.append((key, val))
                if key == ('Product Version'):
                    scripts.artifacts.artGlobals.versionf = val
                    logfunc(f"iOS version: {val}")

            elif key == "Installed Applications":
                data_list.append((key, ', '.join(val)))

    keys = [data[0] for data in data_list]
    device_info = ('Product Name', 'Product Type', 'Device Name', 'Product Version', 'Build Version', 
                   'Serial Number', 'MEID', 'IMEI', 'IMEI 2', 'ICCID', 'Phone Number', 
                   'Unique Identifier', 'Last Backup Date')
    for info in device_info:
        if info in keys:
            index = keys.index(info)
            info_key = data_list[index][0]
            value_key = data_list[index][1]
            logdevinfo(f"{info_key}: {value_key}")

    report = ArtifactHtmlReport('iTunes Backup')
    report.start_artifact_report(report_folder, 'iTunes Backup Information')
    report.add_script()
    data_headers = ('Key','Values')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    
    tsvname = 'iTunes Backup'
    tsv(report_folder, data_headers, data_list, tsvname)

__artifacts__ = {
    "lastbuild": (
        "IOS Build",
        ('*LastBuildInfo.plist'),
        get_lastBuild),
    "iTunesBackupInfo": (
        "IOS Build (iTunes Backup)",
        ('*LastBuildInfo.plist'),
        get_iTunesBackupInfo)
}
