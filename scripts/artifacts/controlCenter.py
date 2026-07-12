__artifacts_v2__ = {
    "controlCenter": {
        "name": "Control Center Configuration",
        "description": "Parses controls/apps added to the Control Center",
        "author": "@KevinPagano3",
        "creation_date": "2024-10-18",
        "last_update_date": "2025-11-21",
        "requirements": "none",
        "category": "Control Center",
        "notes": "",
        "paths": ('*/mobile/Library/ControlCenter/ModuleConfiguration.plist',),
        "output_types": "standard",
        "artifact_icon": "adjustments",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 4 rows",
            "dexter_ios18": "iOS 18.3.2 | 6 rows",
            "felix_ios17": "iOS 17.6.1 | 7 rows",
            "fsfull002_ios17": "iOS 17.1 | 7 rows",
            "hc_ios18_7": "iOS 18.7.8 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | 8 rows",
            "iphone12_ios18": "iOS 18.7 | 5 rows",
            "iphone14plus_ios18": "iOS 18.0 | 5 rows",
            "otto_ios17": "iOS 17.5.1 | 13 rows",
            "abe_ios16": "iOS 16.5 | 12 rows",
            "felix23_ios16": "iOS 16.5 | 7 rows",
            "hickman_ios13": "iOS 13.3.1 | 5 rows",
            "hickman_ios14": "iOS 14.3 | 8 rows",
            "jess_ios15": "iOS 15.0.2 | 6 rows",
            "magnet_ios16": "iOS 16.1.1 | 7 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_plist_file_content

@artifact_processor
def controlCenter(context):
    data_list = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        pl = get_plist_file_content(file_found)
            
        for control_type, key, prefix in [
            ('Active', 'module-identifiers', 'A'),
            ('User Toggled', 'userenabled-fixed-module-identifiers', 'U'),
            ('Disabled', 'disabled-module-identifiers', 'D')
        ]:
            if key in pl and pl[key]:
                for position, module in enumerate(pl[key], 1):
                    formatted_position = f"{prefix}-{position}"
                    data_list.append((formatted_position, module, control_type, context.get_relative_path(file_found)))

    data_headers = ('Position', 'App Bundle', 'Control Type', 'Source File')
    
    return data_headers, data_list, 'see Source File for more info'


