__artifacts_v2__ = {
    "deviceDatam": {
        "name": "Device Data",
        "description": "Device identifiers and phone number information",
        "author": "",
        "version": "1.0",
        "date": "2024-10-29",
        "requirements": "none",
        "category": "Device Information",
        "notes": "",
        "paths": ('*wireless/Library/Preferences/com.apple.commcenter.device_specific_nobackup.plist',),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 35 rows",
            "dexter_ios18": "iOS 18.3.2 | 44 rows",
            "felix_ios17": "iOS 17.6.1 | 39 rows",
            "fsfull002_ios17": "iOS 17.1 | 41 rows",
            "hc_ios18_7": "iOS 18.7.8 | 32 rows",
            "iphone11_ios17": "iOS 17.3 | 43 rows",
            "iphone12_ios18": "iOS 18.7 | 40 rows",
            "iphone14plus_ios18": "iOS 18.0 | 43 rows",
            "otto_ios17": "iOS 17.5.1 | 43 rows",
            "abe_ios16": "iOS 16.5 | 35 rows",
            "felix23_ios16": "iOS 16.5 | 33 rows",
            "hickman_ios13": "iOS 13.3.1 | 32 rows",
            "hickman_ios14": "iOS 14.3 | 37 rows",
            "jess_ios15": "iOS 15.0.2 | 38 rows",
            "magnet_ios16": "iOS 16.1.1 | 36 rows",
        }
    }
}

import ast
import plistlib
from datetime import datetime, timedelta
from scripts.ilapfuncs import artifact_processor, device_info, webkit_timestampsconv

@artifact_processor
def deviceDatam(context):
    data_list = []
    file_found = str(context.get_files_found()[0])
    
    timestamp_keys = [
        'AccountCreationTimestamp',
        'kEuiccTicketPrefetchTimestamp',
        'AddOnRemotePlanListExpiryTime',
        'dataUsageBreadcrumbsSection',
        'kCKUploadDate'
    ]
    
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            if key == 'imeis':
                device_info("Device Information", "IMEIs", val, file_found)
            elif key == 'ReportedPhoneNumber':
                device_info("Device Information", "Reported Phone Number", val, file_found)
            
            # Convert timestamps to human readable format
            if key in timestamp_keys:
                try:
                    if key == 'dataUsageBreadcrumbsSection':
                        # Handle the dictionary string with timestamps
                        data_dict = ast.literal_eval(str(val))
                        timestamps = data_dict.get('launchTimestamps', [])
                        converted_times = [f"{datetime.fromtimestamp(ts)} (original: {ts})" for ts in timestamps]
                        val = str({'launchTimestamps': converted_times})
                    elif key == 'kCKUploadDate':
                        # Convert days since Unix epoch
                        epoch = datetime(1970, 1, 1)
                        converted_time = epoch + timedelta(days=int(val))
                        val = f"{converted_time.date()} (original: {val})"
                    else:
                        # Convert from Apple epoch timestamp
                        converted_time = webkit_timestampsconv(float(val))
                        val = f"{converted_time} (original: {val})"
                except Exception:  # pylint: disable=broad-exception-caught
                    val = str(val)
                    
            data_list.append((key, str(val)))
                
    data_headers = ('Property', 'Property Value')
    return data_headers, data_list, file_found

