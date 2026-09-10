""" See artifact description below """

__artifacts_v2__ = {
    "system_version_plist": {
        "name": "System Version plist",
        "description": "Parses basic data from SystemVersion.plist "
                       "which is a plist in GK Logical Plus extractions and sysdiagnose archives "
                       "that will contain the iOS version. Previously named Ph99SystemVersionPlist.py",
        "author": "Scott Koenig",
        "creation_date": "2025-06-02",
        "last_update_date": "2026-09-10",
        "requirements": "Acquisition that contains SystemVersion.plist",
        "category": "IOS Build",
        "notes": "Added parsing of SystemVersion.plist in a sysdiagnose archive by C_Peter",
        "paths": (
            "*/System/Library/CoreServices/SystemVersion.plist",
            "*/sysdiagnose_*.tar.gz"),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "git-commit",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 6 rows",
            "dexter_ios18": "iOS 18.3.2 | 6 rows",
            "felix_ios17": "iOS 17.6.1 | 6 rows",
            "fsfull002_ios17": "iOS 17.1 | 6 rows",
            "hc_ios18_7": "iOS 18.7.8 | 6 rows",
            "iphone11_ios17": "iOS 17.3 | 6 rows",
            "iphone12_ios18": "iOS 18.7 | 6 rows",
            "iphone14plus_ios18": "iOS 18.0 | 6 rows",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
            "abe_ios16": "iOS 16.5 | 6 rows",
            "felix23_ios16": "iOS 16.5 | 6 rows",
            "hickman_ios13": "iOS 13.3.1 | 6 rows",
            "hickman_ios14": "iOS 14.3 | 6 rows",
            "magnet_ios16": "iOS 16.1.1 | 6 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_plist_file_content, \
    device_info, iOS, get_sysdiagnose_files

@artifact_processor
def system_version_plist(context):
    """ See artifact description """
    data_list = []
    data_sources = []  # Changed to a list to aggregate multiple sources

    # Process ALL matching standalone files and tar archives found
    for file_obj, source_path in get_sysdiagnose_files(context.get_files_found(), "SystemVersion.plist", text_mode=False):
        source_name = context.get_relative_path(source_path)
        # Exclude Rapid Security Response (Splat) plists to prevent duplicate/conflicting version reports
        if "/Splat/" in source_path or "logs/Splat" in source_path:
            continue
        
        # Because we updated get_plist_file_content in ilapfuncs, 
        # it will natively handle the ExFileObject stream without throwing a TypeError.
        pl = get_plist_file_content(file_obj)
        
        # If the plist is valid/populated, process and append its data
        if pl:
            if source_path not in data_sources:
                data_sources.append(source_path)
                
            for key, val in pl.items():
                data_list.append((key, val, source_name))
                
                if key == "Product Build Version":
                    device_info("Device Information", "Product Build Version", val, source_name)

                if key == "ProductVersion":
                    iOS.set_version(val)
                    context.set_installed_os_version(val)
                    device_info("Device Information", "iOS Version", val, source_name)

                if key == "ProductName":
                    device_info("Device Information", "Product Name", val, source_name)

                if key == "BuildID":
                    device_info("Device Information", "Build ID", val, source_name)

                if key == "SystemImageID":
                    device_info("Device Information", "System Image ID", val, source_name)

    data_headers = ('Property', 'Property Value', 'Source File')

    # Join the sources list into a single string for the final artifact return
    data_source_str = ", ".join(data_sources)

    return data_headers, data_list, data_source_str