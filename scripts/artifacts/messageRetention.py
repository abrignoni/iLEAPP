# pylint: disable=E0601,W0611,W0613
__artifacts_v2__ = {
    "messageRetention": {
        "name": "iOS Message Retention",
        "description": "Extract how long messages are kept on the device",
        "author": "@AlexisBrignoni",
        "version": "0.4",
        "date": "2023-10-04",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.MobileSMS.plist', '*/mobile/Library/Preferences/com.apple.mobileSMS.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message-circle",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1 row",
            "dexter_ios18": "iOS 18.3.2 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "iphone12_ios18": "iOS 18.7 | 3 rows",
            "iphone14plus_ios18": "iOS 18.0 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 1 row",
            "abe_ios16": "iOS 16.5 | 1 row",
            "felix23_ios16": "iOS 16.5 | 1 row",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 1 row",
        }
    }
}

from datetime import datetime
import os
from scripts.ilapfuncs import artifact_processor, get_plist_file_content, device_info

@artifact_processor
def messageRetention(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path_one = seeker.search('*/mobile/Library/Preferences/com.apple.MobileSMS.plist', return_on_first_hit=True, force=True)
    data_list = []

    if source_path_one:
        pl = get_plist_file_content(source_path_one)

        indicator = 0
        
        for key, val in pl.items():
            if key == 'KeepMessageForDays':
                if val == 0:
                    keep_val = 'Forever'
                elif val == 365:
                    keep_val = '1 Year'
                elif val == 30:
                    keep_val = '30 Days'
                
                data_list.append(('com.apple.MobileSMS.plist - Keep Messages for Days (iOS <=16)', keep_val, source_path_one))
                device_info('Messages Settings', 'com.apple.MobileSMS.plist - Keep Messages for Days (iOS <=16)', keep_val, source_path_one)
                indicator = 1
                
            if key == 'SSKeepMessages':
                if val == 0:
                    keep_val = 'Forever'
                elif val == 365:
                    keep_val = '1 Year'
                elif val == 30:
                    keep_val = '30 Days'
                
                data_list.append(('com.apple.MobileSMS.plist - Keep Messages for Days (iOS 17+)', keep_val, source_path_one))
                device_info('Messages Settings', 'com.apple.MobileSMS.plist - Keep Messages for Days (iOS 17+)', keep_val, source_path_one)
                indicator = 1
                            
        if indicator == 0:
            data_list.append(('com.apple.MobileSMS.plist - Keep Messages for Days','No value', source_path_one))
            device_info('Messages Settings', 'com.apple.MobileSMS.plist - Keep Messages for Days','No value', source_path_one)
            
    source_path_two = seeker.search('*/mobile/Library/Preferences/com.apple.mobileSMS.plist', return_on_first_hit=True, force=True)
    if source_path_two:
        pl = get_plist_file_content(source_path_two)

        indicator = 0
        
        for key, val in pl.items():
            if key == 'KeepMessageForDays':
                if val == 0:
                    keep_val = 'Forever'
                elif val == 365:
                    keep_val = '1 Year'
                elif val == 30:
                    keep_val = '30 Days'                            
                
                data_list.append(('com.apple.mobileSMS.plist - Keep Messages for Days (iOS <=16)', keep_val, source_path_two))
                device_info('Messages Settings', 'com.apple.mobileSMS.plist - Keep Messages for Days (iOS <=16)', keep_val, source_path_two)
                indicator = 1
                
            if key == 'SSKeepMessages':
                if val == 0:
                    keep_val = 'Forever'
                elif val == 365:
                    keep_val = '1 Year'
                elif val == 30:
                    keep_val = '30 Days'
                    
                data_list.append(('com.apple.mobileSMS.plist - Keep Messages for Days (iOS 17+)', keep_val, source_path_two))
                device_info('Messages Settings', 'com.apple.mobileSMS.plist - Keep Messages for Days (iOS 17+)', keep_val, source_path_two)
                indicator = 1
                
        if indicator == 0:
            data_list.append(('com.apple.mobileSMS.plist - Keep Messages for Days', 'No value', source_path_two))
            device_info('Messages Settings', 'com.apple.mobileSMS.plist - Keep Messages for Days', 'No value', source_path_two)
        
    data_headers = ('Setting', 'Data Value', 'Path')
    return data_headers, data_list, 'File path in the report below'
