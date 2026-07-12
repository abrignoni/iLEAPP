__artifacts_v2__ = {
    "imeiImsi": {
        "name": "IMEI - IMSI",
        "description": "Extracts Cellular information",
        "author": "@AlexisBrignoni - @stark4n6",
        "version": "0.3",
        "creation_date": "2023-10-03",
        "last_update_date": "2025-02-04",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/wireless/Library/Preferences/com.apple.commcenter.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "hash",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 20 rows",
            "dexter_ios18": "iOS 18.3.2 | 23 rows",
            "felix_ios17": "iOS 17.6.1 | 23 rows",
            "fsfull002_ios17": "iOS 17.1 | 21 rows",
            "hc_ios18_7": "iOS 18.7.8 | 18 rows",
            "iphone11_ios17": "iOS 17.3 | 21 rows",
            "iphone12_ios18": "iOS 18.7 | 18 rows",
            "iphone14plus_ios18": "iOS 18.0 | 22 rows",
            "otto_ios17": "iOS 17.5.1 | 21 rows",
            "abe_ios16": "iOS 16.5 | 20 rows",
            "felix23_ios16": "iOS 16.5 | 21 rows",
            "hickman_ios13": "iOS 13.3.1 | 22 rows",
            "hickman_ios14": "iOS 14.3 | 23 rows",
            "jess_ios15": "iOS 15.0.2 | 22 rows",
            "magnet_ios16": "iOS 16.1.1 | 21 rows",
        }
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def imeiImsi(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    data_list = []
    source_path = str(files_found[0])
    
    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == 'PersonalWallet':
                val = (list(val.values())[0])
                lastgoodimsi = val['CarrierEntitlements'].get('lastGoodImsi','')
                data_list.append(('Last Good IMSI', lastgoodimsi))
                device_info("Cellular", "Last Good IMSI", lastgoodimsi, source_path)
                
                selfregitrationupdateimsi = val['CarrierEntitlements'].get('kEntitlementsSelfRegistrationUpdateImsi','')
                data_list.append(('Self Registration Update IMSI', selfregitrationupdateimsi))
                device_info("Cellular", "Self Registration Update IMSI", selfregitrationupdateimsi, source_path)
                
                selfregistrationupdateimei = val['CarrierEntitlements'].get('kEntitlementsSelfRegistrationUpdateImei','')
                data_list.append(('Self Registration Update IMEI', selfregistrationupdateimei))
                device_info("Cellular", "Self Registration Update IMEI", selfregistrationupdateimei, source_path)
                
            elif key == 'LastKnownICCI':
                lastknownicci = val
                data_list.append(('Last Known ICCI', lastknownicci))
                device_info("Cellular", "Last Known ICCI", lastknownicci, source_path)
                
            elif key == 'PhoneNumber':
                data_list.append(('Phone Number', val))
                device_info("Cellular", "Phone Number", val, source_path)
                
            else:
                data_list.append((key, val ))
    
    data_headers = ('Property', 'Property Value')
    return data_headers, data_list, source_path
