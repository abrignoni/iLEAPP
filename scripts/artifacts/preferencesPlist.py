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
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 4 rows",
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "felix_ios17": "iOS 17.6.1 | 4 rows",
            "fsfull002_ios17": "iOS 17.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | 4 rows",
            "iphone12_ios18": "iOS 18.7 | 4 rows",
            "iphone14plus_ios18": "iOS 18.0 | 4 rows",
            "otto_ios17": "iOS 17.5.1 | 4 rows",
            "abe_ios16": "iOS 16.5 | 4 rows",
            "felix23_ios16": "iOS 16.5 | 4 rows",
            "hickman_ios13": "iOS 13.3.1 | 4 rows",
            "hickman_ios14": "iOS 14.3 | 4 rows",
            "jess_ios15": "iOS 15.0.2 | 4 rows",
            "magnet_ios16": "iOS 16.1.1 | 4 rows",
        }
    }
}


import plistlib
from scripts.ilapfuncs import artifact_processor, device_info

@artifact_processor
def preferencesPlist(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
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
