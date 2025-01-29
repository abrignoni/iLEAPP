__artifacts_v2__ = {
    "lastBuild": {
        "name": "iOS Information",
        "description": "Extract iOS information from the LastBuildInfo.plist file",
        "author": "@AlexisBrignoni - @ydkhatri",
        "version": "0.5.4",
        "date": "2020-04-30",
        "requirements": "none",
        "category": "IOS Build",
        "notes": "",
        "paths": ('*/installd/Library/MobileInstallation/LastBuildInfo.plist',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "git-commit"
    }
}

import scripts.artifacts.artGlobals 

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, logfunc, device_info

@artifact_processor
def lastBuild(files_found, report_folder, seeker, wrap_text, time_offset):
    source_path = get_file_path(files_found, "LastBuildInfo.plist")
    data_list = []
    
    pl = get_plist_file_content(source_path)
    for key, val in pl.items():
        data_list.append((key, val))
        if key == ("ProductVersion"):
            scripts.artifacts.artGlobals.versionf = val
            logfunc(f"iOS version: {val}")
            device_info("Device Information", "iOS version", val, source_path)
        
        if key == "ProductBuildVersion":
            device_info("Device Information", "ProductBuildVersion", val, source_path)
        
        if key == ("ProductName"):
            logfunc(f"Product: {val}")
            device_info("Device Information", "Product Name", val, source_path)

    data_headers = ('Property','Property Value' )     
    return data_headers, data_list, source_path
