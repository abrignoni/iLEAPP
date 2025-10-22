""" See artifact description below """

__artifacts_v2__ = {
    "ph_100_ufed_device_values_plist": {
        "name": "Ph100-UFED-device-values-Plist",
        "description": "Parses basic data from */device_values.plist which is a "
                       "part of a UFED Advance Logical acquisitions with "
                       "non-encrypted backups. The parsing of this file will "
                       "allow for iLEAPP to parse some basic information such "
                       "as */PhotoData/Photos.sqlite. "
                       "Based on research and published blogs written by "
                       "Scott Koenig https://theforensicscooter.com/",
        "author": "Scott Koenig",
        "creation_date": "2025-01-05",
        "last_update_date": "2025-10-14",
        "requirements": "Acquisition that contains device_values.plist",
        "category": "Photos-Z-Settings",
        "notes": "",
        "paths": ("*/device_values.plist",),
        "output_types": ["standard", "tsv", "none"],
        "artifact_icon": "settings"
    }
}

from scripts.ilapfuncs import artifact_processor, get_plist_file_content, logfunc, \
    device_info, iOS


@artifact_processor
def ph_100_ufed_device_values_plist(context):
    """ See artifact description """
    data_source = context.get_source_file_path('device_values.plist')
    data_list = []

    with open(data_source, "rb") as pl:
        pl = get_plist_file_content(data_source)
        for key, val in pl.items():
            data_list.append((key, str(val)))

            if key == "ProductVersion":
                iOS.set_version(val)
                context.set_installed_os_version(val)
                logfunc(f"iOS version: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Product Version", str(val), data_source)

            if key == "BuildVersion":
                logfunc(f"Build Version: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Build Version", str(val), data_source)

            if key == "ProductType":
                logfunc(f"Product Type: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Product Type", str(val), data_source)

            if key == "HardwareModel":
                logfunc(f"Hardware Model: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Hardware Model", str(val), data_source)

            if key == "InternationalMobileEquipmentIdentity":
                logfunc(f"IMEI: {val}")
                device_info("devicevaluesplist-ufedadvlog", "IMEI", str(val), data_source)

            if key == "SerialNumber":
                logfunc(f"Serial Number: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Serial Number", str(val), data_source)

            if key == "DeviceName":
                logfunc(f"Device Name: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Device Name", str(val), data_source)

            if key == "PasswordProtected":
                logfunc(f"Password Protected: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Password Protected", str(val), data_source)

            if key == "TimeZone":
                logfunc(f"TimeZone: {val}")
                device_info("devicevaluesplist-ufedadvlog", "TimeZone", str(val), data_source)

            else:
                data_list.append((key, str(val)))

    data_headers = ("Property", "Property Value")

    return data_headers, data_list, data_source
