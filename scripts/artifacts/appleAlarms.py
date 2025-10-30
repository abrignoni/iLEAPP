__artifacts_v2__ = {
    "alarms": {
        "name": "Alarms",
        "description": "Extraction of alarms set",
        "author": "Anna-Mariya Mateyna",
        "creation_date": "2021-01-17",
        "last_update_date": "2025-10-08",
        "requirements": "none",
        "category": "Clock",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.mobiletimerd.plist',),
        "output_types": "standard",
        "artifact_icon": "clock"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, convert_plist_date_to_utc, logfunc

def decode_repeat_schedule(repeat_schedule_value):
    days_list = {
        64: 'Sunday', 
        32: 'Saturday', 
        16: 'Friday', 
        8: 'Thursday', 
        4: 'Wednesday', 
        2: 'Tuesday', 
        1: 'Monday'
        }
    schedule = []

    if repeat_schedule_value == 127:
        schedule.append('Every Day')
        return schedule
    elif repeat_schedule_value == 0:
        schedule.append('Never')
        return schedule

    for day in days_list:
        if repeat_schedule_value > 0 and repeat_schedule_value >= day:
            repeat_schedule_value -= day
            schedule.append(days_list[day])
    return reversed(schedule)


@artifact_processor
def alarms(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "com.apple.mobiletimerd.plist")
    data_list = []

    pl = get_plist_file_content(source_path)
    
    # Check if plist is valid before processing
    if not pl or not isinstance(pl, dict):
        return (), [], ''
        
    if 'MTAlarms' in pl:
        if 'MTAlarms' in pl['MTAlarms']:
            for alarms in pl['MTAlarms']['MTAlarms']:
                alarms_dict = alarms['$MTAlarm']

                alarm_title = alarms_dict.get('MTAlarmTitle', 'Alarm')
                alarm_hour = alarms_dict.get('MTAlarmHour', '')
                alarm_min = alarms_dict.get('MTAlarmMinute', '')
                fire_date = alarms_dict.get('MTAlarmFireDate', '')
                fire_date = convert_plist_date_to_utc(fire_date)
                dismiss_date = alarms_dict.get('MTAlarmDismissDate', '')
                dismiss_date = convert_plist_date_to_utc(dismiss_date)
                last_modified_date = alarms_dict.get('MTAlarmLastModifiedDate', '')
                last_modified_date = convert_plist_date_to_utc(last_modified_date)
                repeat_schedule = decode_repeat_schedule(alarms_dict['MTAlarmRepeatSchedule'])

                alarm_time = str(alarm_hour).zfill(2) + ':' + str(alarm_min).zfill(2)

                data_list.append(
                    (fire_date,
                    alarm_time,
                    alarm_title, 
                    alarms_dict['MTAlarmEnabled'], 
                    dismiss_date,
                    last_modified_date, 
                    ', '.join(repeat_schedule),
                    alarms_dict['MTAlarmSound']['$MTSound']['MTSoundToneID'],
                    alarms_dict['MTAlarmIsSleep'], 
                    alarms_dict['MTAlarmBedtimeDoNotDisturb'],
                    '')
                    )

        if 'MTSleepAlarm' in pl['MTAlarms']:
            for sleep_alarms in pl['MTAlarms']['MTSleepAlarm']:
                logfunc(sleep_alarms)
                sleep_alarm_dict = pl['MTAlarms']['MTSleepAlarm'][sleep_alarms]

                alarm_title = sleep_alarm_dict.get('MTAlarmTitle', 'Bedtime')
                fire_date = sleep_alarm_dict.get('MTAlarmFireDate', '')
                fire_date = convert_plist_date_to_utc(fire_date)
                dismiss_date = sleep_alarm_dict.get('MTAlarmDismissDate', '')
                dismiss_date = convert_plist_date_to_utc(dismiss_date)
                last_modified_date = sleep_alarm_dict.get('MTAlarmLastModifiedDate', '')
                last_modified_date = convert_plist_date_to_utc(last_modified_date)
                repeat_schedule = decode_repeat_schedule(sleep_alarm_dict['MTAlarmRepeatSchedule'])

                data_list.append(
                    (fire_date, 
                    None, # alarm time 
                    alarm_title, 
                    sleep_alarm_dict['MTAlarmEnabled'], 
                    dismiss_date, 
                    last_modified_date, 
                    ', '.join(repeat_schedule), 
                    sleep_alarm_dict['MTAlarmSound']['$MTSound']['MTSoundToneID'], 
                    sleep_alarm_dict['MTAlarmIsSleep'], 
                    sleep_alarm_dict['MTAlarmBedtimeDoNotDisturb'], 
                    sleep_alarm_dict['MTAlarmBedtimeFireDate'])
                    )

    data_headers = (
        ('Fire Date', 'datetime'), 
        ('Alarm Time', 'datetime'),
        'Alarm Title', 
        'Alarm Enabled', 
        ('Dismiss Date', 'datetime'), 
        ('Last Modified', 'datetime'), 
        'Repeat Schedule', 
        'Alarm Sound', 
        'Is Sleep Alarm', 
        'Bedtime Not Disturbed', 
        'Bedtime Fire Date'
        )
    return data_headers, data_list, source_path
