import plistlib

from datetime import datetime

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_iCloudWifi(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, 'rb') as fp:
        pl = plistlib.load(fp)

        if 'values' in pl.keys():
            for key, val in pl['values'].items():

                if isinstance(val, dict):
                    for key2, val2 in val.items():
                        if key2 == 'value':
                            if isinstance(val2, dict):
                                bssid = str(val2.get('BSSID', 'Not Available'))
                                ssid = str(val2.get('SSID_STR', 'Not Available'))
                                added_by = str(val2.get('added_by', 'Not Available'))
                                enabled = str(val2.get('enabled', 'Not Available'))

                                if 'added_at' in val2:
                                    my_time2 = str(val2['added_at'])
                                    datetime_obj = datetime.strptime(my_time2, '%b  %d %Y %H:%M:%S')
                                    added_at = str(datetime_obj)
                                else:
                                    added_at = 'Not Available'
                                data_list.append((bssid, ssid, added_by, enabled, added_at))

    data_headers = ('BSSID', 'SSID', 'Added By', 'Enabled', 'Added At')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_iCloudWifi": {
        "name": "Wifi Connections",
        "description": "",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Wifi Connections",
        "notes": "",
        "paths": ('**/com.apple.wifid.plist',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
