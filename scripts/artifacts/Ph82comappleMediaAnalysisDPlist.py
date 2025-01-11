__artifacts_v2__ = {
    'Ph82ComAppleMediaAnalysisDPlist': {
        'name': 'Ph82-Com-Apple-MediaAnalysisD-Plist',
        'description': 'Parses basic data from */mobile/Library/Preferences/com.apple.mediaanalysisd.plist which'
                       ' contains some important data related to Apple Photos Libraries storage locations and'
                       ' Media Analysis Completion. Additional information and explanation of some keys-fields'
                       ' might be found with research and published blogs written by'
                       ' Scott Koenig https://theforensicscooter.com/',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains com.apple.mediaanalysisd.plist',
        'category': 'Photos-Z-Settings',
        'notes': '',
        'paths': ('*/mobile/Library/Preferences/com.apple.mediaanalysisd.plist',),
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
def Ph82ComAppleMediaAnalysisDPlist(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    source_path = str(files_found[0])

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            data_list.append((key, str(val)))

    data_headers = ('Property','Property Value')
    return data_headers, data_list, source_path
