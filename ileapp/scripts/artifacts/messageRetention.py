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
        "artifact_icon": "message-circle"
    }
}

from datetime import datetime
import os
from ileapp.scripts.ilapfuncs import artifact_processor, get_plist_file_content, device_info

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
