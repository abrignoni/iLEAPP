__artifacts_v2__ = {
    "blockedContacts": {
        "name": "Blocked contacts",
        "description": "Extract blocked contacts",
        "author": "@JohannPLW",
        "creation_date": "2023-12-08",
        "last_update_date": "2024-12-20",
        "requirements": "none",
        "category": "Contacts",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.cmfsyncagent.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user-x"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content

@artifact_processor
def blockedContacts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "com.apple.cmfsyncagent.plist")
    data_list = []

    pl = get_plist_file_content(source_path)
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
