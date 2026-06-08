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
        "output_types": "standard"
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
                    data_list.append((formatted_position, module, control_type, file_found))

    data_headers = ('Position', 'App Bundle', 'Control Type', 'Source File')
    
    return data_headers, data_list, 'see Source File for more info'


