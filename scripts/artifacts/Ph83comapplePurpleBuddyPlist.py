__artifacts_v2__ = {
    'Ph83ComApplePurpleBuddyPlist': {
        'name': 'Ph83-Com-Apple-PurpleBuddy-Plist',
        'description': 'Parses basic data from com.apple.purplebuddy.plist which contains some important data'
                       ' related to device restore.',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains com.apple.purplebuddy.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': ('*/Library/Preferences/com.apple.purplebuddy.plist',),
        "output_types": ["standard", "tsv", "none"]
    }
}

import datetime
import os
import plistlib
import nska_deserialize as nd
import scripts.artifacts.artGlobals
from scripts.builds_ids import OS_build
from scripts.ilapfuncs import artifact_processor, logfunc, device_info, get_file_path

@artifact_processor
def Ph83ComApplePurpleBuddyPlist(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    source_path = str(files_found[0])

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():

            if key == 'SetupState':
                logfunc(f"SetupState: {val}")
                device_info("com.apple.purplebuddy.plist", "SetupState", str(val), source_path)

            else:
                data_list.append((key, str(val)))

    data_headers = ('Property','Property Value')
    return data_headers, data_list, source_path
