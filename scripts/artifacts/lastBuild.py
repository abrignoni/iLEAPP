import datetime
import os
import plistlib
import scripts.artifacts.artGlobals 

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_lastBuild(files_found, report_folder, seeker):
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
            

def get_iTunesBackupInfo(files_found, report_folder, seeker):
    versionnum = 0
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if isinstance(val, str) or isinstance(val, int) or isinstance(val, datetime.datetime):
                data_list.append((key, val))
                if key in ('Build Version', 'Device Name', 'ICCID', 'IMEI', 'Last Backup Date', 
                            'MEID', 'Phone Number', 'Product Name', 'Product Type',
                            'Product Version', 'Serial Number'):
                    logdevinfo(f"{key}: {val}")

                if key == ('Product Version'):
                    scripts.artifacts.artGlobals.versionf = val
                    logfunc(f"iOS version: {val}")

            elif key == "Installed Applications":
                data_list.append((key, ', '.join(val)))
  
    report = ArtifactHtmlReport('iTunes Backup')
    report.start_artifact_report(report_folder, 'iTunes Backup Information')
    report.add_script()
    data_headers = ('Key','Values')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    
    tsvname = 'iTunes Backup'
    tsv(report_folder, data_headers, data_list, tsvname)
