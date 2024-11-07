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
        "output_types": "standard"
    }
}

import ast
import plistlib
from datetime import datetime, timedelta
from scripts.ilapfuncs import artifact_processor, device_info, convert_plist_date_to_timezone_offset, webkit_timestampsconv

@artifact_processor
def deviceDatam(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    
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
                except:
                    val = str(val)
                    
            data_list.append((key, str(val)))
                
    data_headers = ('Property', 'Property Value')
    return data_headers, data_list, file_found

