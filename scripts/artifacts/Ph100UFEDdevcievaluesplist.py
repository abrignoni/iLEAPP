__artifacts_v2__ = {
    'Ph100UFEDdevicevaluesPlist': {
        'name': 'Ph100-UFED-device-values-Plist',
        'description': 'Parses basic data from */device_values.plist which is a part of a UFED Advance Logical'
                       ' acquisitions with non-encrypted backups. The parsing of this file will allow for iLEAPP'
                       ' to parse some basic information such as */PhotoData/Photos.sqlite.'
                       ' Based on research and published blogs written by Scott Koenig https://theforensicscooter.com/',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains device_values.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': ('*/device_values.plist',),
        "output_types": ["standard", "tsv", "none"]
    }
}
import os
import plistlib
import biplist
import nska_deserialize as nd
from scripts.builds_ids import OS_build
import scripts.artifacts.artGlobals
from scripts.ilapfuncs import artifact_processor, logfunc, device_info, get_file_path

@artifact_processor
def Ph100UFEDdevicevaluesPlist(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            data_list.append((key, str(val)))

            if key == "ProductVersion":
                scripts.artifacts.artGlobals.versionf = str(val)
                logfunc(f"iOS version: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Product Version", str(val), source_path)

            if key == "BuildVersion":
                logfunc(f"Build Version: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Build Version", str(val), source_path)

            if key == "ProductType":
                logfunc(f"Product Type: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Product Type", str(val), source_path)

            if key == "HardwareModel":
                logfunc(f"Hardware Model: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Hardware Model", str(val), source_path)

            if key == "InternationalMobileEquipmentIdentity":
                logfunc(f"IMEI: {val}")
                device_info("devicevaluesplist-ufedadvlog", "IMEI", str(val), source_path)

            if key == "SerialNumber":
                logfunc(f"Serial Number: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Serial Number", str(val), source_path)

            if key == "DeviceName":
                logfunc(f"Device Name: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Device Name", str(val), source_path)

            if key == "PasswordProtected":
                logfunc(f"Password Protected: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Password Protected", str(val), source_path)

            if key == "TimeZone":
                logfunc(f"TimeZone: {val}")
                device_info("devicevaluesplist-ufedadvlog", "TimeZone", str(val), source_path)

            else:
                data_list.append((key, str(val)))

    data_headers = ('Property','Property Value')
    return data_headers, data_list, source_path
