__artifacts_v2__ = {
    "timer": {
        "name": "Timers",
        "description": "Extraction of timers set",
        "author": "Mohammad Natiq Khan",
        "creation_date": "2024-12-22",
        "last_update_date": "2024-12-22",
        "requirements": "none",
        "category": "Alarms",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.mobiletimerd.plist',),
        "output_types": "standard",
        "artifact_icon": "clock"
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, convert_plist_date_to_utc

@artifact_processor
def timer(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "com.apple.mobiletimerd.plist")
    data_list = []

    pl = get_plist_file_content(source_path)
    if 'MTTimers' in pl:
        if 'MTTimers' in pl['MTTimers']:
            for timers in pl['MTTimers']['MTTimers']:
                timers_dict = timers['$MTTimer']
                timer_title = timers_dict.get('MTTimerTitle', '')
                timer_time = timers_dict.get('MTTimerDuration', '')
                timer_state = timers_dict.get('MTTimerState', '')
                timer_duration = timers_dict.get('MTTimerDuration', '')

                data_list.append((
                    timer_title, 
                    timer_state, 
                    str(datetime.timedelta(seconds = timer_duration)), 
                    timers_dict.get('MTTimerTimeDate',''), 
                    timers_dict.get('MTTimerLastTriggerDate',''), 
                    timers_dict['MTTimerSound']['$MTSound']['MTSoundToneID'] 
                    ))

    data_headers = (
            'Timer Title', 
            'Timer State', 
            'Timer Time', 
            'First Date', 
            'Last Triggered', 
            'Timer Sound'
            )

    return data_headers, data_list, source_path
