__artifacts_v2__ = {
    "appGrouplisting": {
        "name": "Bundle ID by AppGroup & PluginKit IDs",
        "description": "List can included once installed but not present apps. Each file is named .com.apple.mobile_container_manager.metadata.plist",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-09-22",
        "last_update_date": "2024-12-20",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": (
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist', 
            '*/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package"
    }
}

import pathlib
from scripts.ilapfuncs import artifact_processor, get_plist_file_content

@artifact_processor
def appGrouplisting(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = 'Path column in the report'
    data_list = []       
    
    for file_found in files_found:
        plist = get_plist_file_content(file_found)
        bundleid = plist['MCMMetadataIdentifier']
        
        p = pathlib.Path(file_found)
        appgroupid = p.parent.name
        fileloc = str(p.parents[1])
        typedir = str(p.parents[1].name)
        
        data_list.append((bundleid, typedir, appgroupid, fileloc))
                
    data_headers = ('Bundle ID', 'Type', 'Directory GUID', 'Path')
    return data_headers, data_list, source_path
    