__artifacts_v2__ = {
    "get_confaccts": {
        "name": "Account Configuration",
        "description": "Extracts account configuration information from the device",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2022-08-09",
        "requirements": "none",
        "category": "Accounts",
        "notes": "",
        "paths": ('*/com.apple.accounts.exists.plist',),
        "output_types": ["html", "tsv", "lava"]
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor, logfunc

@artifact_processor
def get_confaccts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    source_path = str(files_found[0])
    
    if not source_path:
        logfunc('com.apple.accounts.exists.plist not found')
        return data_headers, data_list, source_path

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        if len(pl) > 0:
            for key, val in pl.items():
                data_list.append((key, val))
        else:
            logfunc("No account configuration found")
    
    data_headers = ('Key', 'Data')
    return data_headers, data_list, source_path
