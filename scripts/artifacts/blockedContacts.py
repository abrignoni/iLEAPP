__artifacts_v2__ = {
    "blockedContacts": {
        "name": "Blocked Contacts",
        "description": "",
        "author": "@JohannPLW",
        "version": "0.1",
        "date": "2023-12-08",
        "requirements": "none",
        "category": "Contacts",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.cmfsyncagent.plist',),
        "function": "get_blocked_contacts"
    }
}


import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_blocked_contacts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        StoreArrayKey = pl.get('__kCMFBlockListStoreTopLevelKey', {}).get('__kCMFBlockListStoreArrayKey')
        if len(StoreArrayKey) > 0:
            for item in StoreArrayKey:
                type_key = item.get('__kCMFItemTypeKey', '')
                country_code = phone_number = email = ''
                if type_key == 0:
                    country_code = item.get('__kCMFItemPhoneNumberCountryCodeKey', '')
                    phone_number = item.get('__kCMFItemPhoneNumberUnformattedKey', '')
                elif type_key == 1:
                    email = item.get('__kCMFItemEmailUnformattedKey', '')
                data_list.append((country_code, phone_number, email))

            report = ArtifactHtmlReport('Blocked Contacts')
            report.start_artifact_report(report_folder, 'Blocked Contacts')
            report.add_script()
            data_headers = ('Country Code', 'Phone Number', 'Email')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
        else:
            logfunc('No Blocked contact found')

