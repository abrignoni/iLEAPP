__artifacts_v2__ = {
    'systemVersionPlist': {
        'name': 'System Version plist',
        'description': 'Parses basic data from */System/Library/CoreServices/SystemVersion.plist'
                       ' which is a plist in GK Logical Plus extractions that will contain the iOS version.'
                       ' Previously named Ph99SystemVersionPlist.py',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-03',
        'requirements': 'Acquisition that contains SystemVersion.plist',
        'category': 'IOS Build',
        'notes': '',
        'paths': ('*/System/Library/CoreServices/SystemVersion.plist',),
        "output_types": ["standard", "tsv", "none"]
    }
}

import plistlib
import scripts.artifacts.artGlobals
from scripts.ilapfuncs import artifact_processor, logfunc, device_info

@artifact_processor
def systemVersionPlist(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    source_path = str(files_found[0])
    
    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            data_list.append((key, val))
            if key == "ProductBuildVersion":
                device_info("Device Information", "ProductBuildVersion", val, source_path)

            if key == "ProductVersion":
                scripts.artifacts.artGlobals.versionf = val
                logfunc(f"iOS version: {val}")
                device_info("Device Information", "iOS version", val, source_path)

            if key == "ProductName":
                device_info("Device Information", "Product Name", val, source_path)

    data_headers = ('Property','Property Value')
    return data_headers, data_list, source_path
