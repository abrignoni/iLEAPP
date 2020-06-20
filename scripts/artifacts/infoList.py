import os
import plistlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_infoList(files_found, report_folder, seeker):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            data_list.append((key, val))
            
            if key == "-Build Version":
                logdevinfo(f"Build Version: {val}")
            if key == "-Device Name":
                logdevinfo(f"Device name: {val}")
            if key == "-GUID":
                logdevinfo(f"GUID: {val}")
            if key == "-IMEI":
                logdevinfo(f"IMEI: {val}")
            if key == "-Installed Applications":
                logdevinfo(f"Installed Applications: {val}")
            if key == "-Last Backup Date":
                logdevinfo(f"Last Backup Date: {val}")
            if key == "-MEID":
                logdevinfo(f"MEID: {val}")
            if key == "-Product Name":
                logdevinfo(f"Product Name: {val}")
            if key == "-Product Type":
                logdevinfo(f"Product Type: {val}")
            if key == "-Product Version":
                logdevinfo(f"Product Version: {val}")
            if key == "-Serial Number":
                logdevinfo(f"Serial Number: {val}")
            if key == "-Unique Identifier":
                logdevinfo(f"Unique Identifier: {val}")
            if key == "-Applications":
                logdevinfo(f"Applications:")
            if key == "-iTunes Files":
                logdevinfo(f"iTunes Files:")
            if key == "-iTunes Settings":
                logdevinfo(f"iTunes Settings:")
  
    report = ArtifactHtmlReport('Info List')
    report.start_artifact_report(report_folder, 'Info List')
    report.add_script()
    data_headers = ('Key','Values' )     
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    
    tsvname = 'infoList'
    tsv(report_folder, data_headers, data_list, tsvname)
            
