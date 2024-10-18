__artifacts_v2__ = {
    "controlCenter": {
        "name": "Control Center Configuration",
        "description": "Parses controls/apps added to the Control Center",
        "author": "@KevinPagano3",
        "version": "0.0.2",
        "date": "2024-10-18",
        "requirements": "none",
        "category": "Control Center",
        "notes": "",
        "paths": ('*/mobile/Library/ControlCenter/ModuleConfiguration.plist',),
        "output_types": "standard"
    }
}


import plistlib
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 
from scripts.ilapfuncs import artifact_processor

@artifact_processor
def controlCenter(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, 'rb') as f:
            pl = plistlib.load(f)
            
            for control_type, key, prefix in [
                ('Active', 'module-identifiers', 'A'),
                ('User Toggled', 'userenabled-fixed-module-identifiers', 'U'),
                ('Disabled', 'disabled-module-identifiers', 'D')
            ]:
                if key in pl and pl[key]:
                    for position, module in enumerate(pl[key], 1):
                        formatted_position = f"{prefix}-{position}"
                        data_list.append((formatted_position, module, control_type))
    
    data_headers = ('Position', 'App Bundle', 'Control Type')
    
    if not data_list:
        logfunc('No Control Center Configuration data available')
    
    return data_headers, data_list, file_found


