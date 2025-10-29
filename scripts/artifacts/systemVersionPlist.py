__artifacts_v2__ = {
    'systemVersionPlist': {
        'name': 'System Version plist',
        'description': 'Parses basic data from */System/Library/CoreServices/SystemVersion.plist'
                       ' which is a plist in GK Logical Plus extractions and sysdiagnose archives' 
                       ' that will contain the iOS version. Previously named Ph99SystemVersionPlist.py',
        'author': 'Scott Koenig',
        'version': '5.1',
        'date': '2025-06-02',
        'requirements': 'Acquisition that contains SystemVersion.plist',
        'category': 'IOS Build',
        'notes': 'Added parsing of SystemVersion.plist in a sysdiagnose archive by C_Peter',
        'paths': ('*/System/Library/CoreServices/SystemVersion.plist','**/sysdiagnose_*.tar.gz'),
        "output_types": ["standard", "tsv", "none"]
    }
}

import plistlib
import tarfile
from scripts.ilapfuncs import artifact_processor, logfunc, device_info, iOS

@artifact_processor
def systemVersionPlist(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    for filename in files_found:
        if "SystemVersion.plist" in filename:
            source_path = str(filename)
            with open(source_path, "rb") as fp:
                pl = plistlib.load(fp)
            break
        elif 'sysdiagnose_' in filename and not "IN_PROGRESS_" in filename:
            source_path = str(filename)
            tar = tarfile.open(filename)
            root = tar.getmembers()[0].name.split('/')[0]
            try:
                tarf = tar.extractfile(f"{root}/logs/SystemVersion/SystemVersion.plist")
                pl = plistlib.load(tarf)
            except:
                pl = None
    
    if pl != None:
        # Known & fallback key names across iOS generations
        version_keys = [
            "ProductVersion", "_ProductVersion", "ReleaseVersion", "OSVersion"
        ]
        build_keys = [
            "Product Build Version", "BuildVersion", "_BuildVersion", "Build"
        ]
        
        # Extract version and build with fallback logic
        os_version = None
        build_version = None
        
        for key in version_keys:
            if key in pl and pl[key]:
                os_version = pl[key]
                break
                
        for key in build_keys:
            if key in pl and pl[key]:
                build_version = pl[key]
                break
        
        # Process all keys for data list
        for key, val in pl.items():
            data_list.append((key, val))
            
            # Handle build version with fallback
            if key in build_keys and val:
                device_info("Device Information", "Product Build Version", val, source_path)

            # Handle iOS version with fallback
            if key in version_keys and val:
                iOS.set_version(val)
                logfunc(f"iOS Version: {val}")
                device_info("Device Information", "iOS Version", val, source_path)

            if key == "ProductName":
                device_info("Device Information", "Product Name", val, source_path)
                
            if key == "BuildID":
                device_info("Device Information", "Build ID", val, source_path)
                
            if key == "SystemImageID":
                device_info("Device Information", "System Image ID", val, source_path)

    data_headers = ('Property','Property Value')
    return data_headers, data_list, source_path
