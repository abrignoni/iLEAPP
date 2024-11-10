__artifacts_v2__ = {
    "imeiImsi": {
        "name": "IMEI - IMSI",
        "description": "Extracts Cellular information",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2023-10-03",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/wireless/Library/Preferences/com.apple.commcenter.plist'),
        "output_types": ["html", "tsv", "lava"]
    }
}


import plistlib
from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def imeiImsi(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])
    
    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == 'PersonalWallet':
                val = (list(val.values())[0])
                lastgoodimsi = val['CarrierEntitlements']['lastGoodImsi']
                data_list.append(('Last Good IMSI', lastgoodimsi))
                device_info("Cellular", "Last Good IMSI", lastgoodimsi, source_path)
                
                selfregitrationupdateimsi = val['CarrierEntitlements']['kEntitlementsSelfRegistrationUpdateImsi']
                data_list.append(('Self Registration Update IMSI', selfregitrationupdateimsi))
                device_info("Cellular", "Self Registration Update IMSI", selfregitrationupdateimsi, source_path)
                
                selfregistrationupdateimei = val['CarrierEntitlements']['kEntitlementsSelfRegistrationUpdateImei']
                data_list.append(('Self Registration Update IMEI', selfregistrationupdateimei))
                device_info("Cellular", "Self Registration Update IMEI", selfregistrationupdateimei, source_path)
                
            elif key == 'LastKnownICCI':
                lastknownicci = val
                data_list.append(('Last Known ICCI', lastknownicci))
                device_info("Cellular", "Last Known ICCI", lastknownicci, source_path)
                
            elif key == 'PhoneNumber':
                phonenumber = val
                data_list.append(('Phone Number', val))
                device_info("Cellular", "Phone Number", val, source_path)
                
            else:
                data_list.append((key, val ))
    
    data_headers = ('Property', 'Property Value' )     
    return data_headers, data_list, source_path
