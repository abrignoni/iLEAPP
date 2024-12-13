__artifacts_v2__ = {
    "preferencesPlist": {
        "name": "Preferences PList",
        "description": "Extract Device information",
        "author": "@AlexisBrignoni",
        "version": "0.2",
        "date": "2023-09-30",
        "requirements": "none",
        "category": "Identifiers",
        "notes": "",
        "paths": ('*preferences/SystemConfiguration/preferences.plist', ),
        "output_types": ["html", "tsv", "lava"]
    }
}


import plistlib
from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def preferencesPlist(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    source_path = str(files_found[0])
    with open(source_path, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == ("Model"):
                data_list.append((key, val))
                device_info("Device Information", "Model", val, source_path)
            
            if key == "System":
                localhostname = val['Network']['HostNames']['LocalHostName']
                data_list.append(('Local Host Name', localhostname ))
                device_info("Device Information", "Local Host Name", localhostname, source_path)
                
                computername = val['System']['ComputerName']
                data_list.append(('Device/Computer Name', computername))
                device_info("Device Information", "Device/Computer Name", computername, source_path)
                
                hostname = val['System']['HostName']
                data_list.append(('Host Name', hostname ))
                device_info("Device Information", "Host Name", hostname, source_path)

    data_headers = ('Property','Property Value' )
    return data_headers, data_list, source_path
