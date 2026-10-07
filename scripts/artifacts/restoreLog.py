""" See description below """

__artifacts_v2__ = {
    'restore_log': {
        'name': 'Mobile Software Update',
        'description': 'Dictionary events in each "data = " line in restore.log that contain originalOSVersion, with the original and current OS builds as stored and their versions looked up from the tool\'s build table.',
        'author': '@AlexisBrignoni, Codex',
        'creation_date': '2021-10-18',
        'last_update_date': '2026-10-06',
        'requirements': 'none',
        'category': 'OS Updates',
        'notes': (
            'Only lines containing "data = " are read. Dictionary entries of each line\'s events '
            'array are read in stored order, including repeats, when they contain originalOSVersion. Original '
            'OS Version and Updated OS Version are looked up from the tool\'s build table and are '
            'not stored values. Updated OS Build is the stored currentOSVersion value. '
            'Rows do not establish completed updates. Unsupported JSON shapes are skipped with bounded '
            'diagnostics; JSON parsing, timestamp handling and first-file selection are unchanged. '
            'Original parser contribution: @stark4n6.'
        ),
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
from scripts.ilapfuncs import artifact_processor, get_file_path, convert_unix_ts_to_utc, logfunc


@artifact_processor
def restore_log(context):
    """ See artifact description """
    data_source = get_file_path(context.get_files_found(), "restore.log")
    data_list = []
    pattern = 'data = '
    shape_counts = {'parsed_root_not_object': 0, 'events_not_array': 0, 'event_not_object': 0}
    relative_path = json.dumps(context.get_relative_path(str(data_source)), ensure_ascii=True)[1:-1]
    if len(relative_path) > 512:
        suffix = f'...[truncated; length={len(relative_path)}]'
        relative_path = relative_path[:512 - len(suffix)] + suffix

    def skip_shape(reason, value, line_number, event_ordinal=None):
        shape_counts[reason] += 1
        if sum(shape_counts.values()) > 10:
            return
        if value is None:
            value_type = 'null'
        elif isinstance(value, bool):
            value_type = 'boolean'
        elif isinstance(value, (int, float)):
            value_type = 'number'
        elif isinstance(value, str):
            value_type = 'string'
        elif isinstance(value, list):
            value_type = 'array'
        else:
            value_type = 'object'
        location = f'line={line_number}'
        if event_ordinal is not None:
            location += f' event={event_ordinal}'
        logfunc(f'restoreLog: {relative_path} {location} skipped {reason} type={value_type}')

    with open(data_source, "r", encoding="utf-8") as f:
        data = f.readlines()
        for line_number, line in enumerate(data, 1):
            if pattern in line:
                dict_line = json.loads(line.split('data = ')[1])
                if not isinstance(dict_line, dict):
                    skip_shape('parsed_root_not_object', dict_line, line_number)
                    continue
                stored_events = dict_line.get("events", [])
                if not isinstance(stored_events, list):
                    skip_shape('events_not_array', stored_events, line_number)
                    continue
                for event_ordinal, events in enumerate(stored_events, 1):
                    if not isinstance(events, dict):
                        skip_shape('event_not_object', events, line_number, event_ordinal)
                        continue
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

    skipped = sum(shape_counts.values())
    if skipped:
        logfunc(f'restoreLog: {relative_path} shape skips: '
                f'parsed_root_not_object={shape_counts["parsed_root_not_object"]}, '
                f'events_not_array={shape_counts["events_not_array"]}, '
                f'event_not_object={shape_counts["event_not_object"]}, '
                f'suppressed_examples={max(0, skipped - 10)}')

    data_headers = (
        ('Timestamp', 'datetime'), 'Original OS Build', 'Original OS Version',
        'Updated OS Build', 'Updated OS Version', 'Event', 'Device Family',
        'Board ID', 'Device Model', 'Battery Level', 'Battery Is Charging')

    return data_headers, data_list, data_source
