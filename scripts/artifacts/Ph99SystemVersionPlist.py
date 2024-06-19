# Author:  Scott Koenig
# Version: 1.0
#
#   Description:
#   Parses basic data from */System/Library/CoreServices/SystemVersion.plist which contains some important data
#   related to a device being analyzed to include the iOS version data.

import os
import plistlib
import scripts.artifacts.artGlobals
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 


def get_systemversionplist(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])

    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            data_list.append((key, val))
            if key == "BuildID":
                logdevinfo(f"<b>BuildID: </b>{val}")

            if key == "ProductBuildVersion":
                logdevinfo(f"<b>BuildVersion: </b>{val}")

            if key == "ProductVersion":
                scripts.artifacts.artGlobals.versionf = val
                logfunc(f"iOS version: {val}")
                logdevinfo(f"<b>iOS version: </b>{val}")

            if key == "ProductName":
                logdevinfo(f"<b>ProductName: </b>{val}")

            if key == "ReleaseType":
                logdevinfo(f"<b>ReleaseType: </b>{val}")

            if key == "SystemImageID":
                logdevinfo(f"<b>SystemImageID: </b>{val}")

    description = ('Parses basic data from device acquisition */System/Library/CoreServices/SystemVersion.plist'
                   ' which contains some important data related to a device being analyzed to include the iOS version.')
    report = ArtifactHtmlReport('Photos-Z-Settings')
    report.start_artifact_report(report_folder, 'Ph99-System-Version-Plist', description)
    report.add_script()
    data_headers = ('Key', 'Values')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    
    tsvname = 'Ph99-System-Version-Plist'
    tsv(report_folder, data_headers, data_list, tsvname)


__artifacts_v2__ = {
    'Ph99-System-Version-Plist': {
        'name': 'Ph99 System Version plist',
        'description': 'Parses basic data from device acquisition */System/Library/CoreServices/SystemVersion.plist'
                       ' which contains some important data related to a device being analyzed to include'
                       ' the iOS version.',
        'author': 'Scott Koenig',
        'version': '1.0',
        'date': '2024-06-17',
        'requirements': 'Acquisition that contains SystemVersion.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': '*/SystemVersion.plist',
        'function': 'get_systemversionplist'
    }
}
