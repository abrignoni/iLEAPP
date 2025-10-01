__artifacts_v2__ = {
    "timer": {
        "name": "Timers",
        "description": "Extraction of timers set",
        "author": "Mohammad Natiq Khan",
        "creation_date": "2024-12-22",
        "last_update_date": "2024-12-22",
        "requirements": "none",
        "category": "Clock",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.mobiletimerd.plist',),
        "output_types": "standard",
        "artifact_icon": "clock"
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content

@artifact_processor
def timer(context):
    files_found = context.get_files_found()
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
                timer_lastModified = timers_dict.get('MTTimerLastModifiedDate', '')
                timer_fireTime = timers_dict['MTTimerFireTime'].get('$MTTimerDate', '')
                timer_firstDate = ''
                
                if not timer_fireTime == '':
                    timer_firstDate = timer_fireTime.get('MTTimerTimeDate', '')

                data_list.append((
                    timer_firstDate, 
                    timer_lastModified, 
                    timer_title, 
                    timer_state, 
                    str(datetime.timedelta(seconds = timer_duration)), 
                    timers_dict['MTTimerSound']['$MTSound']['MTSoundToneID'] 
                    ))

    data_headers = (
            ('First Date', 'datetime'), 
            ('Last Modified', 'datetime'), 
            'Timer Title', 
            'Timer State', 
            'Timer Time', 
            'Timer Sound'
            )

    return data_headers, data_list, source_path
