__artifacts_v2__ = {
'Ph087UFEDdevcievaluesplist': {
'name': 'Ph087-UFED-device-values-Plist',
'description': 'A file named device_values.plist found anywhere in the input is read, and'
' each key and value is listed as stored, with the file it came from. The module author'
' associates this file with Cellebrite UFED Advanced Logical acquisitions; no source for'
' that is cited, no registered test image holds a file of this name, and the path'
' pattern is not tied to any folder, so a file of this name from another origin is'
' read the same way. When exactly one such file is found and its ProductVersion is'
' digits separated by dots, and no iOS version has been set earlier in the run,'
' ProductVersion becomes the iOS version for the rest of the run, which decides which'
' version-specific queries other artifacts use. In that case ProductVersion,'
' BuildVersion, ProductType, HardwareModel, InternationalMobileEquipmentIdentity,'
' SerialNumber, DeviceName, PasswordProtected and TimeZone are also copied to Device'
' Info. When more than one such file is found, the rows are still listed, no iOS'
' version is set and nothing is copied to Device Info, because nothing in the files'
' says which one describes the device. This behaviour was checked on constructed'
' files only. The linked post by the module author mentions a Cellebrite UFED Advanced'
' Logical acquisition and does not name this file:'
' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/',
'author': 'Scott Koenig',
'creation_date': '2026-05-28',
'last_update_date': '2026-10-04',
'version': '1.0',
'date': '2025-01-05',
'requirements': 'Acquisition that contains device_values.plist',
'category': 'Photos.sqlite',
'notes': '',
'paths': ('*/device_values.plist',),
"output_types": ["standard", "tsv", "none"],
"artifact_icon": "settings"
}
}

import os
import re

from scripts.ilapfuncs import artifact_processor, get_plist_file_content, logfunc, \
device_info, iOS

_DEVICE_INFO_LABELS = {
    "ProductVersion": "Product Version",
    "BuildVersion": "Build Version",
    "ProductType": "Product Type",
    "HardwareModel": "Hardware Model",
    "InternationalMobileEquipmentIdentity": "IMEI",
    "SerialNumber": "Serial Number",
    "DeviceName": "Device Name",
    "PasswordProtected": "Password Protected",
    "TimeZone": "TimeZone",
}
_VERSION_SHAPE = re.compile(r'\d+(?:\.\d+)*')


@artifact_processor
def Ph087UFEDdevcievaluesplist(context):
    """ See artifact description """
    data_list = []
    read_files = []

    for file_found in sorted(set(str(path) for path in context.get_files_found())):
        if os.path.isdir(file_found) or os.path.basename(file_found) != 'device_values.plist':
            continue
        pl = get_plist_file_content(file_found)
        if not isinstance(pl, dict) or not pl:
            logfunc(f"No keys read from {context.get_relative_path(file_found)}")
            continue
        read_files.append((file_found, pl))

    # Nothing in the file says which copy describes the device, so the run's iOS
    # version and Device Info are taken from it only when it is the only one found.
    describes_device = len(read_files) == 1
    if len(read_files) > 1:
        logfunc(f"{len(read_files)} device_values.plist files found: "
                "iOS version and Device Info not taken from any of them")

    for file_found, pl in read_files:
        source_file = context.get_relative_path(file_found)
        for key, val in pl.items():
            data_list.append((key, str(val), source_file))

            if not describes_device or key not in _DEVICE_INFO_LABELS:
                continue

            if key == "ProductVersion":
                if _VERSION_SHAPE.fullmatch(str(val)):
                    iOS.set_version(str(val))
                    context.set_installed_os_version(str(val))
                    logfunc(f"iOS version: {val}")
                else:
                    logfunc("ProductVersion in device_values.plist is not digits separated "
                            "by dots: not used as the iOS version")
            else:
                logfunc(f"{_DEVICE_INFO_LABELS[key]}: {val}")
            device_info("devicevaluesplist-ufedadvlog", _DEVICE_INFO_LABELS[key], str(val), file_found)

    data_headers = ("Property", "Property Value", "Source File")

    return data_headers, data_list, '\n'.join(file_found for file_found, _ in read_files)
