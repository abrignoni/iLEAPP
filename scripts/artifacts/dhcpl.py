import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_dhcpl(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    data_list = []
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == "IPAddress":
                data_list.append((key,val))
            if key == "LeaseLength":
                data_list.append((key,val))
            if key == "LeaseStartDate":
                data_list.append((key,val))
            if key == "RouterHardwareAddress":
                data_list.append((key,val))
            if key == "RouterIPAddress":
                data_list.append((key,val))
            if key == "SSID":
                data_list.append((key,val))
    
    if len(data_list) > 0:
        report = ArtifactHtmlReport('DHCP Received List')
        report.start_artifact_report(report_folder, 'Received List')
        report.add_script()
        data_headers = ('Key', 'Value')   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'DHCP Received List'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No data available')
    return

__artifacts__ = {
    "dhcpl": (
        "DHCP",
        ('*/db/dhcpclient/leases/en*'),
        get_dhcpl)
}