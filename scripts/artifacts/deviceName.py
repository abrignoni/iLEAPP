__artifacts_v2__ = {
    "deviceName": {
        "name": "Device Name",
        "description": "Extracts the device name from data_ark.plist",
        "author": "@AlexisBrignoni",
        "version": "1.0",
        "date": "2024-10-29",
        "requirements": "none",
        "category": "Identifiers",
        "paths": ('*/root/Library/Lockdown/data_ark.plist',),
        "output_types": "none"
    }
}

import plistlib
from scripts.ilapfuncs import device_info, artifact_processor

@artifact_processor
def deviceName(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == '-DeviceName':
                device_info("Device Information", "Device Name", val, file_found)
                break
    
    # Return empty data since this artifact only collects device info
    return (), [], ''
