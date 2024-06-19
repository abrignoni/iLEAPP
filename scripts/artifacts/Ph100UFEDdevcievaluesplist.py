# Author:  Scott Koenig https://theforensicscooter.com/
# Version: 1.0
#
#   Description:
#   Parses basic data from */device_values.plist which is a part of a UFED Advance Logical acquisitions
#   with non-encrypted backups. The parsing of this file will allow for iLEAPP to parse some basic information
#   such as */PhotoData/Photos.sqlite.
#   Based on research and published blogs written by Scott Koenig https://theforensicscooter.com/

import os
import plistlib
import biplist
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 


def get_ph100ufeddevicevaluesplist(files_found, report_folder, seeker, wrap_text, timezone_offset):
    versionnum = 0
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            data_list.append((key, val))
            if key == "ProductVersion":
                scripts.artifacts.artGlobals.versionf = val
                logfunc(f"iOS version: {val}")
                logdevinfo(f"<b>iOS version: </b>{val}")

            if key == "BuildVersion":
                logdevinfo(f"<b>BuildVersion: </b>{val}")

            if key == "ProductType":
                logfunc(f"ProductType: {val}")
                logdevinfo(f"<b>ProductType: </b>{val}")

            if key == "HardwareModel":
                logdevinfo(f"<b>HardwareModel: </b>{val}")

            if key == "InternationalMobileEquipmentIdentity":
                logdevinfo(f"<b>InternationalMobileEquipmentIdentity: </b>{val}")

            if key == "SerialNumber":
                logdevinfo(f"<b>SerialNumber: </b>{val}")

            if key == "DeviceName":
                logdevinfo(f"<b>DeviceName: </b>{val}")

            if key == "PasswordProtected":
                logdevinfo(f"<b>PasswordProtected: </b>{val}")

            if key == "TimeZone":
                logdevinfo(f"<b>TimeZone: </b>{val}")

    description = ('Parses basic data from */device_values.plist which is a part of a UFED Advance Logical'
                   ' acquisitions with non-encrypted backups. The parsing of this file will allow for iLEAPP'
                   ' to parse some basic information such as */PhotoData/Photos.sqlite.'
                   ' Based on research and published blogs written by Scott Koenig https://theforensicscooter.com/')
    report = ArtifactHtmlReport('Photos-Z-Settings')
    report.start_artifact_report(report_folder, 'Ph100-UFED-device-values-Plist', description)
    report.add_script()
    data_headers = ('Key', 'Values')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()

    tsvname = 'Ph100-UFED-device-values-Plist'
    tsv(report_folder, data_headers, data_list, tsvname)


__artifacts_v2__ = {
    'Ph100-UFED-device-values-Plist': {
        'name': 'UFED Adv Log Acquisition Ph100 UFED Device Values Plist',
        'description': 'Parses basic data from */device_values.plist which is a part of a UFED Advance Logical'
                       ' acquisitions with non-encrypted backups. The parsing of this file will allow for iLEAPP'
                       ' to parse some basic information such as */PhotoData/Photos.sqlite.'
                       ' Based on research and published blogs written by Scott Koenig https://theforensicscooter.com/',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.0',
        'date': '2024-06-10',
        'requirements': 'Acquisition that contains device_values.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': '*/device_values.plist',
        'function': 'get_ph100ufeddevicevaluesplist'
    }
}
