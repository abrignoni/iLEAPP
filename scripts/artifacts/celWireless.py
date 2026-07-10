__artifacts_v2__ = {
    "celWireless": {
        "name": "Cellular Wireless",
        "description": "Extracts cellular wireless information from device preferences",
        "author": "@abrignoni",
        "creation_date": "2024-10-22",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Cellular",
        "notes": "",
        "paths": ('*wireless/Library/Preferences/com.apple.commcenter.plist', 
                  '*wireless/Library/Preferences/com.apple.commcenter.device_specific_nobackup.plist'),
        "output_types": "standard",
        "artifact_icon": "antenna",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 53 rows",
            "dexter_ios18": "iOS 18.3.2 | 65 rows",
            "felix_ios17": "iOS 17.6.1 | 60 rows",
            "fsfull002_ios17": "iOS 17.1 | 120 rows",
            "hc_ios18_7": "iOS 18.7.8 | 48 rows",
            "iphone11_ios17": "iOS 17.3 | 62 rows",
            "iphone12_ios18": "iOS 18.7 | 56 rows",
            "iphone14plus_ios18": "iOS 18.0 | 63 rows",
            "otto_ios17": "iOS 17.5.1 | 62 rows",
        }
    }
}

import os
from scripts.ilapfuncs import device_info, artifact_processor, get_plist_file_content

@artifact_processor
def celWireless(context):
    data_list = []
    for filepath in context.get_files_found():
        basename = os.path.basename(filepath)
        if basename in ["com.apple.commcenter.device_specific_nobackup.plist", "com.apple.commcenter.plist"]:
            plist = get_plist_file_content(filepath)
            for key, val in plist.items():
                data_list.append((key, str(val), context.get_relative_path(filepath)))
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
    
    return data_headers, data_list, 'see Source File for more info'
