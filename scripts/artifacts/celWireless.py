__artifacts_v2__ = {
    "celWireless": {
        "name": "Cellular Wireless",
        "description": "Extracts cellular wireless information from device preferences",
        "author": "@abrignoni",
        "version": "1.0",
        "date": "2024-10-22",
        "requirements": "none",
        "category": "Cellular",
        "notes": "",
        "paths": ('*wireless/Library/Preferences/com.apple.commcenter.plist', 
                  '*wireless/Library/Preferences/com.apple.commcenter.device_specific_nobackup.plist'),
        "output_types": "standard"
    }
}

import os
import plistlib

from scripts.ilapfuncs import logdevinfo, artifact_processor

@artifact_processor
def celWireless(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    for filepath in files_found:
        basename = os.path.basename(filepath)
        if basename in ["com.apple.commcenter.device_specific_nobackup.plist", "com.apple.commcenter.plist"]:
            with open(filepath, "rb") as p:
                plist = plistlib.load(p)
                for key, val in plist.items():
                    data_list.append((key, str(val), filepath))
                    if key == "ReportedPhoneNumber":
                        logdevinfo(f"<b>Reported Phone Number: </b>{val}")
                    elif key == "CDMANetworkPhoneNumberICCID":
                        logdevinfo(f"<b>CDMA Network Phone Number ICCID: </b>{val}")
                    elif key == "imei":
                        logdevinfo(f"<b>IMEI: </b>{val}")
                    elif key == "LastKnownICCID":
                        logdevinfo(f"<b>Last Known ICCID: </b>{val}")
                    elif key == "meid":
                        logdevinfo(f"<b>MEID: </b>{val}")
    
    data_headers = ('Data Key', 'Data Value', 'Source File')
    return data_headers, data_list, filepath
