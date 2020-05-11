import os
import plistlib
import sqlite3
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
            
