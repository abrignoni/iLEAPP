# pylint: disable=W0611,W0613
__artifacts_v2__ = {
    'Ph082ComAppleMediaAnalysisDPlist': {
        'name': 'Ph082-Com-Apple-MediaAnalysisD-Plist',
        'description': 'Parses basic data from */mobile/Library/Preferences/com.apple.mediaanalysisd.plist which'
                       ' contains some important data related to Apple Photos Libraries storage locations and'
                       ' Media Analysis Completion. Additional information and explanation of some keys-fields'
                       ' might be found with research and published blogs written by Scott Koenig'
                       ' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/',
        'author': 'Scott Koenig',
        'version': '5.0',
        'date': '2025-01-05',
        'requirements': 'Acquisition that contains com.apple.mediaanalysisd.plist',
        'category': 'Photos.sqlite-Y-Settings-Plist-MediaAnalysis-PhotoLib-List',
        'notes': '',
        'paths': ('*/mobile/Library/Preferences/com.apple.mediaanalysisd.plist',),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "book",
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 1 row',
            'dexter_ios18': 'iOS 18.3.2 | 17 rows',
            'felix_ios17': 'iOS 17.6.1 | 9 rows',
            'fsfull002_ios17': 'iOS 17.1 | 9 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 19 rows',
            'iphone11_ios17': 'iOS 17.3 | 9 rows',
            'iphone12_ios18': 'iOS 18.7 | 17 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 15 rows',
            'otto_ios17': 'iOS 17.5.1 | 9 rows',
            'abe_ios16': 'iOS 16.5 | 7 rows',
            'felix23_ios16': 'iOS 16.5 | 7 rows',
            'jess_ios15': 'iOS 15.0.2 | 2 rows',
            'magnet_ios16': 'iOS 16.1.1 | 8 rows',
        }
    }
}

import datetime
import os
import plistlib
import nska_deserialize as nd
from scripts.ilapfuncs import artifact_processor, logfunc, device_info, get_file_path

@artifact_processor
def Ph082ComAppleMediaAnalysisDPlist(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    source_path = str(files_found[0])

    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            data_list.append((key, str(val)))

    data_headers = ('Property','Property Value')
    return data_headers, data_list, source_path
