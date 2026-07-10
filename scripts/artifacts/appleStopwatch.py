__artifacts_v2__ = {
    "stopwatch": {
        "name": "Stopwatch",
        "description": "Extraction of stopwatch set",
        "author": "Mohammad Natiq Khan",
        "creation_date": "2024-12-22",
        "last_update_date": "2025-10-09",
        "requirements": "none",
        "category": "Clock",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.mobiletimerd.plist',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 2 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 2 rows",
        }
    }
}

import datetime
from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content

@artifact_processor
def stopwatch(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "com.apple.mobiletimerd.plist")
    data_list = []

    pl = get_plist_file_content(source_path)
    if not pl or not isinstance(pl, dict):
        return (), [], ''
    
    if 'MTStopwatches' in pl:
        if 'MTStopwatches' in pl['MTStopwatches']:
            for stop_watch in pl['MTStopwatches']['MTStopwatches']:
                stop_watches_dict = stop_watch['$MTStopwatch']
                stop_watch_time = stop_watches_dict.get('MTStopwatchCurrentInterval', 0)
                stop_watch_state = stop_watches_dict.get('MTStopwatchState', '')
                stop_watch_lapses = stop_watches_dict.get('MTStopwatchLaps', [])
                stop_watch_lapses.append(stop_watch_time)
                stop_watch_total_time = sum(stop_watch_lapses)
                stop_watch_lap_count = len(stop_watch_lapses)

                data_list.append((
                    stop_watch_state, 
                    str(datetime.timedelta(seconds = stop_watch_total_time)), 
                    '', 
                    ''
                    ))

                for index, val in enumerate(stop_watch_lapses[::-1]):
                    data_list.append((
                        '', 
                        '', 
                        "Lap " + str(stop_watch_lap_count - index), 
                        str(datetime.timedelta(seconds = val))
                        ))

    data_headers = (
        'Stopwatch State', 
        'Stopwatch Time', 
        'Stopwatch Lap', 
        'Stopwatch Lap Time', 
        )
    return data_headers, data_list, source_path
