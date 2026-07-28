__artifacts_v2__ = {
    "appGrouplisting": {
        "name": "Bundle ID by AppGroup & PluginKit IDs",
        "description": "List can included once installed but not present apps. Each file is named .com.apple.mobile_container_manager.metadata.plist",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-09-22",
        "last_update_date": "2025-10-08",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": (
            '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist', 
            '*/Containers/Data/PluginKitPlugin/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 439 rows",
            "dexter_ios18": "iOS 18.3.2 | 1111 rows",
            "felix_ios17": "iOS 17.6.1 | 829 rows",
            "fsfull002_ios17": "iOS 17.1 | 780 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1085 rows",
            "iphone11_ios17": "iOS 17.3 | 950 rows",
            "iphone12_ios18": "iOS 18.7 | 1066 rows",
            "iphone14plus_ios18": "iOS 18.0 | 901 rows",
            "otto_ios17": "iOS 17.5.1 | 892 rows",
            "abe_ios16": "iOS 16.5 | 827 rows",
            "felix23_ios16": "iOS 16.5 | 674 rows",
            "hickman_ios13": "iOS 13.3.1 | 458 rows",
            "hickman_ios14": "iOS 14.3 | 521 rows",
            "jess_ios15": "iOS 15.0.2 | 490 rows",
            "magnet_ios16": "iOS 16.1.1 | 685 rows",
        }
    }
}

import pathlib
from scripts.ilapfuncs import artifact_processor, get_plist_file_content

@artifact_processor
def appGrouplisting(context):
    source_path = 'Path column in the report'
    data_list = []       
    
    for file_found in context.get_files_found():
        plist = get_plist_file_content(file_found)
        # Check if plist is a valid parseable object
        if not plist or not isinstance(plist, dict):
            continue
        bundleid = plist['MCMMetadataIdentifier']
        
        p = pathlib.Path(file_found)
        appgroupid = p.parent.name
        fileloc = str(p.parents[1])
        typedir = str(p.parents[1].name)
        
        data_list.append((bundleid, typedir, appgroupid, fileloc))
                
    data_headers = ('Bundle ID', 'Type', 'Directory GUID', 'Path')
    return data_headers, data_list, source_path
    