""" See description below """

__artifacts_v2__ = {
    'restore_log': {
        'name': 'Mobile Software Update',
        'description': 'Extracts events related to operating system updates from the restore.log file.',
        'author': '@stark4n6',
        'creation_date': '2021-10-18',
        'last_update_date': '2025-10-06',
        'requirements': 'none',
        'category': 'OS Updates',
        'notes': '',
        'paths': ('*/mobile/MobileSoftwareUpdate/restore.log',),
        'output_types': 'standard',
        'artifact_icon': 'refresh',
        'sample_data': {
            'ctf2020_ios12': 'iOS 12.4 | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | 0 rows',
            'felix_ios17': 'iOS 17.6.1 | 0 rows',
            'fsfull002_ios17': 'iOS 17.1 | 0 rows',
            'hc_ios18_7': 'iOS 18.7.8 | 0 rows',
            'iphone11_ios17': 'iOS 17.3 | 1 row',
            'iphone12_ios18': 'iOS 18.7 | 0 rows',
            'iphone14plus_ios18': 'iOS 18.0 | 0 rows',
            'otto_ios17': 'iOS 17.5.1 | 1 row',
            'abe_ios16': 'iOS 16.5 | 1 row',
            'felix23_ios16': 'iOS 16.5 | 1 row',
            'hickman_ios13': 'iOS 13.3.1 | 0 rows',
            'hickman_ios14': 'iOS 14.3 | 2 rows',
            'jess_ios15': 'iOS 15.0.2 | 0 rows',
            'magnet_ios16': 'iOS 16.1.1 | 0 rows',
        }
    }
}

import json
from scripts.ilapfuncs import artifact_processor, get_file_path, convert_unix_ts_to_utc


@artifact_processor
def restore_log(context):
    """ See artifact description """
    data_source = get_file_path(context.get_files_found(), "restore.log")
    data_list = []
    pattern = 'data = '

    with open(data_source, "r", encoding="utf-8") as f:
        data = f.readlines()
        for line in data:
            if pattern in line:
                dict_line = json.loads(line.split('data = ')[1])
                events = dict_line.get("events", [{}])[0]
                if "originalOSVersion" in events:
                    event_time = convert_unix_ts_to_utc(events.get("eventTime", ""))
                    device_family = events.get("deviceClass", "")
                    original_os_build = events.get("originalOSVersion", "")
                    original_os_name = context.get_apple_os_version(original_os_build, device_family)
                    current_os_build = events.get("currentOSVersion", "")
                    current_os_name = context.get_apple_os_version(current_os_build, device_family)
                    event = events.get("event", "")
                    board_id = events.get("deviceModel", "")
                    device_model = context.lookup_metadata('apple_board_id_to_model', board_id)
                    battery_level = events.get("batteryLevel", "")
                    battery_is_charging = events.get("batteryIsCharging", "")

                    data_list.append(
                        (event_time, original_os_build, original_os_name, current_os_build,
                         current_os_name, event, device_family, board_id, device_model,
                         battery_level, battery_is_charging))

    data_headers = (
        ('Timestamp', 'datetime'), 'Original OS Build', 'Original OS Version',
        'Updated OS Build', 'Updated OS Version', 'Event', 'Device Family',
        'Board ID', 'Device Model', 'Battery Level', 'Battery Is Charging')

    return data_headers, data_list, data_source
