__artifacts_v2__ = {
    "celWireless": {
        "name": "Cellular Wireless",
        "description": "Extracts cellular wireless information from device preferences",
        "author": "@abrignoni",
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

from scripts.ilapfuncs import device_info, artifact_processor, get_plist_content
from scripts.context import Context

@artifact_processor
def celWireless(context:Context):
    data_list = []
    for filepath in context.files_found():
        basename = os.path.basename(filepath)
        if basename in ["com.apple.commcenter.device_specific_nobackup.plist", "com.apple.commcenter.plist"]:
            with open(filepath, "rb") as p:
                plist = get_plist_content(p)
                for key, val in plist.items():
                    data_list.append((key, str(val), filepath))
                    if key == "ReportedPhoneNumber":
                        device_info("Cellular", "Reported Phone Number", val, filepath)
                    elif key == "CDMANetworkPhoneNumberICCID":
                        device_info("Cellular", "CDMA Network Phone Number ICCID", val, filepath)
                    elif key == "imei":
                        device_info("Cellular", "IMEI", val, filepath)
                    elif key == "LastKnownICCID":
                        device_info("Cellular", "Last Known ICCID", val, filepath)
                    elif key == "meid":
                        device_info("Cellular", "MEID", val, filepath)
    
    data_headers = ('Data Key', 'Data Value', 'Source File')
    return data_headers, data_list, filepath
