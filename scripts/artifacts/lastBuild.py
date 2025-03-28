__artifacts_v2__ = {
    "lastBuild": {
        "name": "iOS Information",
        "description": "Extract iOS information from the LastBuildInfo.plist file",
        "author": "@AlexisBrignoni - @ydkhatri - @stark4n6",
        "creation_date": "2020-04-30",
        "last_update_date": "2025-03-28",
        "requirements": "none",
        "category": "IOS Build",
        "notes": "",
        "paths": (
            '*/installd/Library/MobileInstallation/LastBuildInfo.plist', 
            '*/logs/SystemVersion/SystemVersion.plist'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "git-commit"
    }
}

from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_plist_file_content, logfunc, device_info, iOS

@artifact_processor
def lastBuild(files_found, report_folder, seeker, wrap_text, time_offset):
    last_build_path = get_file_path(files_found, "LastBuildInfo.plist")
    system_version_path = get_file_path(files_found, "SystemVersion.plist")
    source_path = last_build_path if last_build_path else system_version_path

    data_list = []

    pl = get_plist_file_content(source_path)
    for key, val in pl.items():
        data_list.append((key, val))
        if key == ("ProductVersion"):
            iOS.set_version(val)
            logfunc(f"iOS version: {val}")
            device_info("Device Information", "iOS version", val, source_path)
        
        if key == "ProductBuildVersion":
            device_info("Device Information", "ProductBuildVersion", val, source_path)
        
        if key == ("ProductName"):
            logfunc(f"Product: {val}")
            device_info("Device Information", "Product Name", val, source_path)

    data_headers = ('Property', 'Property Value')
    return data_headers, data_list, source_path
