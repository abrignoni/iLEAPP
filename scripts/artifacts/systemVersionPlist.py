""" See artifact description below """

__artifacts_v2__ = {
    "system_version_plist": {
        "name": "System Version plist",
        "description": "Parses basic data from */System/Library/CoreServices/SystemVersion.plist "
                       "which is a plist in GK Logical Plus extractions and sysdiagnose archives "
                       "that will contain the iOS version. Previously named Ph99SystemVersionPlist.py",
        "author": "Scott Koenig",
        "creation_date": "2025-06-02",
        "last_update_date": "2025-10-14",
        "requirements": "Acquisition that contains SystemVersion.plist",
        "category": "IOS Build",
        "notes": "Added parsing of SystemVersion.plist in a sysdiagnose archive by C_Peter",
        "paths": (
            "*/System/Library/CoreServices/SystemVersion.plist",
            "*/sysdiagnose_*.tar.gz"),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "git-commit"
    }
}

import tarfile
from scripts.ilapfuncs import artifact_processor, get_plist_file_content, logfunc, \
    device_info, iOS


@artifact_processor
def system_version_plist(context):
    """ See artifact description """
    data_list = []
    data_source = ""
    pl = None

    plist_file = context.get_source_file_path("SystemVersion.plist")
    sysdiagnose_archive = context.get_source_file_path("sysdiagnose_*.tar.gz")

    if plist_file:
        data_source = system_version_plist
        pl = get_plist_file_content(data_source)
    elif 'sysdiagnose_' in sysdiagnose_archive and "IN_PROGRESS_" not in sysdiagnose_archive:
        tar = tarfile.open(sysdiagnose_archive)
        root = tar.getmembers()[0].name.split('/')[0]
        try:
            data_source = tar.extractfile(f"{root}/logs/SystemVersion/SystemVersion.plist")
            pl = get_plist_file_content(data_source)
        except KeyError:
            pl = None

    if pl is not None:
        for key, val in pl.items():
            data_list.append((key, val))
            if key == "Product Build Version":
                device_info("Device Information", "Product Build Version", val, data_source)

            if key == "ProductVersion":
                iOS.set_version(val)
                context.set_installed_os_version(val)
                logfunc(f"iOS Version: {val}")
                device_info("Device Information", "iOS Version", val, data_source)

            if key == "ProductName":
                device_info("Device Information", "Product Name", val, data_source)

            if key == "BuildID":
                device_info("Device Information", "Build ID", val, data_source)

            if key == "SystemImageID":
                device_info("Device Information", "System Image ID", val, data_source)

    data_headers = ('Property', 'Property Value')

    return data_headers, data_list, data_source
