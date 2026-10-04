__artifacts_v2__ = {
'Ph087UFEDdevcievaluesplist': {
'name': 'Ph087-UFED-device-values-Plist',
'description': 'A file named device_values.plist found anywhere in the input is read. The module'
' author associates this file with Cellebrite UFED Advanced Logical acquisitions; no'
' source for that is cited and no tested image is recorded for this artifact. Lists'
' each key and value as stored. When no iOS version has been set earlier in the run,'
' ProductVersion becomes the iOS version for the rest of the run, which decides which'
' version-specific queries other artifacts use. ProductVersion, BuildVersion,'
' ProductType, HardwareModel, InternationalMobileEquipmentIdentity, SerialNumber,'
' DeviceName, PasswordProtected and TimeZone are also copied to Device Info. The linked'
' post by the module author mentions a Cellebrite UFED Advanced Logical acquisition and'
' does not name this file:'
' https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/',
'author': 'Scott Koenig',
'creation_date': '2026-05-28',
'last_update_date': '2026-07-31',
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

from scripts.ilapfuncs import artifact_processor, get_plist_file_content, logfunc, \
device_info, iOS


@artifact_processor
def Ph087UFEDdevcievaluesplist(context):
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

            elif key == "BuildVersion":
                logfunc(f"Build Version: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Build Version", str(val), data_source)

            elif key == "ProductType":
                logfunc(f"Product Type: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Product Type", str(val), data_source)

            elif key == "HardwareModel":
                logfunc(f"Hardware Model: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Hardware Model", str(val), data_source)

            elif key == "InternationalMobileEquipmentIdentity":
                logfunc(f"IMEI: {val}")
                device_info("devicevaluesplist-ufedadvlog", "IMEI", str(val), data_source)

            elif key == "SerialNumber":
                logfunc(f"Serial Number: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Serial Number", str(val), data_source)

            elif key == "DeviceName":
                logfunc(f"Device Name: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Device Name", str(val), data_source)

            elif key == "PasswordProtected":
                logfunc(f"Password Protected: {val}")
                device_info("devicevaluesplist-ufedadvlog", "Password Protected", str(val), data_source)

            elif key == "TimeZone":
                logfunc(f"TimeZone: {val}")
                device_info("devicevaluesplist-ufedadvlog", "TimeZone", str(val), data_source)

    data_headers = ("Property", "Property Value")

    return data_headers, data_list, data_source
