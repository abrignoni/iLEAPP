__artifacts_v2__ = {
    "user_settings": {
        "name": "Sysdiagnose - User Settings",
        "description": "Parses user settings from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": "",
        "paths": ('*/Shared/UserSettings.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
    "user_autolock_settings": {
        "name": "Sysdiagnose - User Auto-Lock Settings",
        "description": "Parses user auto-lock settings from Sysdiagnose",
        "author": "@Hexordia",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Sysdiagnose - Settings & Preferences",
        "notes": "",
        "paths": ('*/Shared/UserSettings.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "lock"
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def user_settings(context):
    data_list = []    
    source_paths = set()
    for file_found in context.get_files_found():
        source_name = str(context.get_relative_path(file_found))
        source_paths.add(file_found)
        with open(file_found, 'rb') as f:
            pl = plistlib.load(f)
            
            # General Settings
            restrictedBool = pl.get('restrictedBool')
            for key, value in restrictedBool.items():
                setting_value = str(value.get('value'))
                data_list.append((key,setting_value,source_name))
                
    data_headers = ('Setting','Value','Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))
                
@artifact_processor                
def user_autolock_settings(context):
    data_list_lockout = []
    source_paths = set()
    for file_found in context.get_files_found():
        source_name = str(context.get_relative_path(file_found))
        source_paths.add(file_found)
        with open(file_found, 'rb') as f:
            pl = plistlib.load(f)

            # Auto-Lock and Password Re-Entry
            restrictedValue = pl.get('restrictedValue')
            for key, value in restrictedValue.items():
                # Auto-Lock parsing
                if 'maxInactivity' in key:
                    auto_lock = value.get('value')
                    if auto_lock == 30:
                        auto_lock = '30 Seconds'
                    elif auto_lock == 60:
                        auto_lock = '1 Minute'
                    elif auto_lock == 120:
                        auto_lock = '2 Minutes'
                    elif auto_lock == 180:
                        auto_lock = '3 Minutes'
                    elif auto_lock == 240:
                        auto_lock = '4 Minutes'
                    elif auto_lock == 300:
                        auto_lock = '5 Minutes'
                    elif auto_lock == 2147483647:
                        auto_lock = 'Never'                
                    else:
                        continue
                    
                    data_list_lockout.append(('Auto-Lock',auto_lock,source_name))
                    device_info("Settings & Preferences", "Auto-Lock", auto_lock, source_name)
                    
                    auto_lock_min = value.get('rangeMinimum','')
                    #data_list_lockout.append(('Auto-Lock Minimum (Seconds)',auto_lock_min))
                
                # Password Re-Entry parsing
                elif 'maxGracePeriod' in key:
                    min_grace = value.get('rangeMinimum')
                    #data_list_lockout.append(('Require Password Re-Entry (Min Seconds)',min_grace))
                    
                    max_grace = value.get('rangeMaximum')
                    #data_list_lockout.append(('Require Password Re-Entry (Max Seconds)',max_grace))
                    
                    grace_val = value.get('value')
                    if grace_val == 0:
                        grace_val = 'Immediately'
                    elif grace_val == 60:
                        grace_val = 'After 1 Minute'
                    elif grace_val == 300:
                        grace_val = 'After 5 Minutes'
                    elif grace_val == 900:
                        grace_val = 'After 15 Minutes'
                    elif grace_val == 3600:
                        grace_val = 'After 1 Hour'
                    elif grace_val == 14400:
                        grace_val = 'After 4 Hour'            
                    else:
                        continue
                    data_list_lockout.append(('Require Password Re-Entry',grace_val,source_name))
                    device_info("Settings & Preferences", "Require Password Re-Entry", grace_val, source_name)
                    
    data_headers = ('Setting','Value','Source File')
    return data_headers, data_list_lockout, '\n'.join(sorted(source_paths))