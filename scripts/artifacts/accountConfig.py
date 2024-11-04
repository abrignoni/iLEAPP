__artifacts_v2__ = {
    "accountConfig": {
        "name": "Account Configuration",
        "description": "Extracts account configuration information",
        "author": "@AlexisBrignoni",
        "version": "0.1.3",
        "date": "2020-04-30",
        "requirements": "none",
        "category": "Accounts",
        "notes": "",
        "paths": ('*/com.apple.accounts.exists.plist',),
        "output_types": ["html", "tsv", "lava"]
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor

@artifact_processor
def accountConfig(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    source_path = str(files_found[0])
    
    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            data_list.append((key, val))
    
    data_headers = ('Account ID', 'Data Value')
    return data_headers, data_list, source_path
