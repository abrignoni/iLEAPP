# pylint: disable=W0611,W0613
__artifacts_v2__ = {
    'Ph083ComApplePurpleBuddyPlist': {
        'name': 'Ph083-Com-Apple-PurpleBuddy-Plist',
        'description': 'Parses basic data from com.apple.purplebuddy.plist which contains some important data'
                       ' related to device restore.'
                       ' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains com.apple.purplebuddy.plist',
        'category': 'Photos.sqlite-Y-Settings-Plist-PurpleBuddy',
        'notes': '',
        'paths': ('*/Library/Preferences/com.apple.purplebuddy.plist',),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "settings",
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 33 rows',
            'dexter_ios18': 'iOS 18.3.2 | 37 rows',
            'felix_ios17': 'iOS 17.6.1 | 34 rows',
            'fsfull002_ios17': 'iOS 17.1 | 39 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 35 rows',
            'iphone11_ios17': 'iOS 17.3 | 33 rows',
            'iphone12_ios18': 'iOS 18.7 | 35 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 34 rows',
            'otto_ios17': 'iOS 17.5.1 | 35 rows',
            'abe_ios16': 'iOS 16.5 | 36 rows',
            'felix23_ios16': 'iOS 16.5 | 29 rows',
            'hickman_ios13': 'iOS 13.3.1 | 34 rows',
            'hickman_ios14': 'iOS 14.3 | 33 rows',
            'jess_ios15': 'iOS 15.0.2 | 36 rows',
            'magnet_ios16': 'iOS 16.1.1 | 34 rows',
        }
    }
}

import datetime
import os
import plistlib
import nska_deserialize as nd
from scripts.ilapfuncs import artifact_processor, logfunc, device_info, get_file_path

@artifact_processor
def Ph083ComApplePurpleBuddyPlist(files_found, report_folder, seeker, wrap_text, time_offset):
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
