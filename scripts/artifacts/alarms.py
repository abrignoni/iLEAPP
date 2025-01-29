__artifacts_v2__ = {
    "alarms": {
        "name": "Alarms",
        "description": "Extraction of alarms set",
        "author": "Anna-Mariya Mateyna",
        "creation_date": "2021-01-17",
        "last_update_date": "2024-12-17",
        "requirements": "none",
        "category": "Alarms",
        "notes": "",
        "paths": ('*/mobile/Library/Preferences/com.apple.mobiletimerd.plist',),
        "output_types": "standard",
        "artifact_icon": "clock"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, convert_plist_date_to_utc

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
def alarms(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "com.apple.mobiletimerd.plist")
    data_list = []

    pl = get_plist_file_content(source_path)
    if 'MTAlarms' in pl:
        if 'MTAlarms' in pl['MTAlarms']:
            for alarms in pl['MTAlarms']['MTAlarms']:
                alarms_dict = alarms['$MTAlarm']

                alarm_title = alarms_dict.get('MTAlarmTitle', 'Alarm')
                fire_date = alarms_dict.get('MTAlarmFireDate', '')
                fire_date = convert_plist_date_to_utc(fire_date)
                dismiss_date = alarms_dict.get('MTAlarmDismissDate', '')
                dismiss_date = convert_plist_date_to_utc(dismiss_date)
                last_modified_date = alarms_dict.get('MTAlarmLastModifiedDate', '')
                last_modified_date = convert_plist_date_to_utc(last_modified_date)
                repeat_schedule = decode_repeat_schedule(alarms_dict['MTAlarmRepeatSchedule'])

                data_list.append(
                    (fire_date, 
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
