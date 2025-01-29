__artifacts_v2__ = {
    "blockedContacts": {
        "name": "Blocked contacts",
        "description": "Extract blocked contacts",
        "author": "@JohannPLW",
        "version": "0.1",
        "date": "2023-12-08",
        "requirements": "none",
        "category": "Contacts",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.cmfsyncagent.plist'),
        "output_types": ["html", "tsv", "lava"]
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor 

@artifact_processor
def blockedContacts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        StoreArrayKey = pl.get('__kCMFBlockListStoreTopLevelKey', {}).get('__kCMFBlockListStoreArrayKey', {})
        for item in StoreArrayKey:
            type_key = item.get('__kCMFItemTypeKey', '')
            phone_number = email = country_code = ''
            if type_key == 0:
                phone_number = item.get('__kCMFItemPhoneNumberUnformattedKey', '')
                country_code = item.get('__kCMFItemPhoneNumberCountryCodeKey', '')
            elif type_key == 1:
                email = item.get('__kCMFItemEmailUnformattedKey', '')
            data_list.append((phone_number, country_code, email))

    data_headers = (('Phone Number', 'phonenumber'), 'Country Code', 'Email')     
    return data_headers, data_list, source_path
