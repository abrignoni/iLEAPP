""" See description below """

__artifacts_v2__ = {
    "last_build": {
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
        "artifact_icon": "git-commit",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 9 rows",
            "dexter_ios18": "iOS 18.3.2 | 10 rows",
            "felix_ios17": "iOS 17.6.1 | 10 rows",
            "fsfull002_ios17": "iOS 17.1 | 10 rows",
            "hc_ios18_7": "iOS 18.7.8 | 10 rows",
            "iphone11_ios17": "iOS 17.3 | 10 rows",
            "iphone12_ios18": "iOS 18.7 | 10 rows",
            "iphone14plus_ios18": "iOS 18.0 | 10 rows",
            "otto_ios17": "iOS 17.5.1 | 10 rows",
            "abe_ios16": "iOS 16.5 | 10 rows",
            "felix23_ios16": "iOS 16.5 | 10 rows",
            "hickman_ios13": "iOS 13.3.1 | 9 rows",
            "hickman_ios14": "iOS 14.3 | 9 rows",
            "jess_ios15": "iOS 15.0.2 | 9 rows",
            "magnet_ios16": "iOS 16.1.1 | 10 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_plist_file_content, logfunc, \
    device_info, iOS


@artifact_processor
def last_build(context):
    """ See artifact description """
    last_build_path = context.get_source_file_path("LastBuildInfo.plist")
    system_version_path = context.get_source_file_path("SystemVersion.plist")
    data_source = last_build_path if last_build_path else system_version_path

    data_list = []

    pl = get_plist_file_content(data_source)
    for key, val in pl.items():
        data_list.append((key, val))
        if key == ("ProductVersion"):
            iOS.set_version(val)
            context.set_installed_os_version(val)
            logfunc(f"iOS version: {val}")
            device_info("Device Information", "iOS version", val, data_source)

        if key == "ProductBuildVersion":
            device_info("Device Information", "ProductBuildVersion", val, data_source)

        if key == ("ProductName"):
            logfunc(f"Product: {val}")
            device_info("Device Information", "Product Name", val, data_source)

    data_headers = ('Property', 'Property Value')
    return data_headers, data_list, data_source
