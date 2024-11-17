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
        "paths": ('*LastBuildInfo.plist',),
        "output_types": ["html", "tsv", "lava"]
    },
}

import plistlib
import scripts.artifacts.artGlobals 

from scripts.ilapfuncs import artifact_processor, logfunc, device_info

@artifact_processor
def lastBuild(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    source_path = str(files_found[0])
    
    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
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
