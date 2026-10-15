__artifacts_v2__ = {
    "alarms": {
        "name": "Alarms",
        "description": "Alarms in com.apple.mobiletimerd.plist, disabled and sleep alarms included",
        "author": "Anna-Mariya Mateyna",
        "creation_date": "2021-01-17",
        "last_update_date": "2026-10-15",
        "requirements": "none",
        "category": "Clock",
        "notes": "Rows come from the MTAlarms list and, for sleep alarms, the MTSleepAlarms list. "
                 "Alarm Title is blank when no MTAlarmTitle is stored; no sleep alarm in the "
                 "checked images stored one. Alarm Time and Bedtime are HH:MM text built from "
                 "MTAlarmHour and MTAlarmMinute, and from MTAlarmBedtimeHour and "
                 "MTAlarmBedtimeMinute. The stored values are integers; the module zero-pads them "
                 "and joins them with a colon, and attaches no date or time zone. Some sleep alarm"
                 " items also carry MTAlarmDay, MTAlarmMonth and MTAlarmYear keys, which this "
                 "module does not read. Keep Off Until, Snooze Fire Date, Bedtime Fire Date, "
                 "Bedtime Snooze Fire Date and Bedtime Dismiss Date are read from "
                 "MTAlarmKeepOffUntilDate, MTAlarmSnoozeFireDate, MTAlarmBedtimeFireDate, "
                 "MTAlarmBedtimeSnoozeFireDate and MTAlarmBedtimeDismissDate. These key names come "
                 "from Apple's MobileTimer framework on macOS 27.0.1, whose alarm serializer wrote "
                 "each key once the matching date was set on an alarm. The column names follow the "
                 "key names; what sets each date on a device was not tested. Keep Off Until is "
                 "filled on rows from MTSleepAlarms in abe_ios16, otto_ios17, iphone11_ios17 and "
                 "hickman_ios14, and is empty on every row in the other images listed in "
                 "sample_data. Snooze Fire Date, "
                 "Bedtime Fire Date, Bedtime Snooze Fire Date and Bedtime Dismiss Date are empty in "
                 "every image listed in sample_data. Bedtime "
                 "is filled only for rows from MTSleepAlarms, and "
                 "its meaning is taken from the key names, not compared with the device's display."
                 " Sleep alarm sounds in the checked images held a sound type and volume but no "
                 "tone or media item ID, so Alarm Sound is blank for them. The Repeat Schedule "
                 "labels (1 Monday, 2 Tuesday, 4 Wednesday, 8 Thursday, 16 Friday, 32 Saturday, 64"
                 " Sunday, 127 Every Day, 0 Never) are assigned by this module; no vendor "
                 "documentation for them was found. The comparison they were derived from is not "
                 "recorded here.",
        "paths": ('*/mobile/Library/Preferences/com.apple.mobiletimerd.plist',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 6 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 5 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 5 rows",
            "abe_ios16": "iOS 16.5 | 3 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 1 row",
            "hickman_ios14": "iOS 14.3 | 2 rows",
            "jess_ios15": "iOS 15.0.2 | 1 row",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_plist_file_content, convert_plist_date_to_utc, logfunc

from datetime import datetime as _dt

def _safe_plist_date(value):
    """Convert plist <date> objects to UTC; pass anything else, None included, through unchanged."""
    return convert_plist_date_to_utc(value) if isinstance(value, _dt) else value


def decode_alarm_sound(alarm_dict):
    """Describe the alarm sound.

    A tone carries MTSoundToneID, a song from the media library carries
    MTSoundMediaItemID instead, so neither key is guaranteed to be present.
    """
    sound = alarm_dict.get('MTAlarmSound', {}).get('$MTSound', {})
    if 'MTSoundToneID' in sound:
        return sound['MTSoundToneID']
    if 'MTSoundMediaItemID' in sound:
        return f"media item: {sound['MTSoundMediaItemID']}"
    return ''


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


def _hour_minute(hour, minute):
    """Format a stored hour and minute as HH:MM, or '' when either is missing."""
    if hour is None or minute is None:
        return ''
    return str(hour).zfill(2) + ':' + str(minute).zfill(2)


def _alarm_row(alarm, is_sleep_list):
    alarms_dict = alarm.get('$MTAlarm', {}) if isinstance(alarm, dict) else {}

    repeat_value = alarms_dict.get('MTAlarmRepeatSchedule')
    repeat_schedule = ', '.join(decode_repeat_schedule(repeat_value)) \
        if isinstance(repeat_value, int) else ''

    # Sleep alarms carry their bedtime in MTAlarmBedtimeHour/Minute. Regular alarms
    # carry those keys too, so the column is only filled for the sleep list.
    bedtime = _hour_minute(alarms_dict.get('MTAlarmBedtimeHour'),
                           alarms_dict.get('MTAlarmBedtimeMinute')) if is_sleep_list else ''

    return (_safe_plist_date(alarms_dict.get('MTAlarmFireDate')),
            _safe_plist_date(alarms_dict.get('MTAlarmDismissDate')),
            _safe_plist_date(alarms_dict.get('MTAlarmLastModifiedDate')),
            _safe_plist_date(alarms_dict.get('MTAlarmKeepOffUntilDate')),
            _safe_plist_date(alarms_dict.get('MTAlarmSnoozeFireDate')),
            _safe_plist_date(alarms_dict.get('MTAlarmBedtimeFireDate')),
            _safe_plist_date(alarms_dict.get('MTAlarmBedtimeSnoozeFireDate')),
            _safe_plist_date(alarms_dict.get('MTAlarmBedtimeDismissDate')),
            _hour_minute(alarms_dict.get('MTAlarmHour'), alarms_dict.get('MTAlarmMinute')),
            alarms_dict.get('MTAlarmTitle', ''),
            alarms_dict.get('MTAlarmEnabled', ''),
            repeat_schedule,
            decode_alarm_sound(alarms_dict),
            alarms_dict.get('MTAlarmIsSleep', ''),
            alarms_dict.get('MTAlarmBedtimeDoNotDisturb', ''),
            bedtime)


@artifact_processor
def alarms(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "com.apple.mobiletimerd.plist")
    data_list = []

    pl = get_plist_file_content(source_path)

    # Check if plist is valid before processing
    if not pl or not isinstance(pl, dict):
        return (), [], source_path

    alarms_root = pl.get('MTAlarms', {})
    if isinstance(alarms_root, dict):
        for list_key, is_sleep_list in (('MTAlarms', False), ('MTSleepAlarms', True)):
            alarm_list = alarms_root.get(list_key, [])
            if not isinstance(alarm_list, list):
                logfunc(f'Alarms: {list_key} is a {type(alarm_list).__name__}, not a list; skipped')
                continue
            for alarm in alarm_list:
                data_list.append(_alarm_row(alarm, is_sleep_list))

    data_headers = (
        ('Fire Date', 'datetime'),
        ('Dismiss Date', 'datetime'),
        ('Last Modified', 'datetime'),
        ('Keep Off Until', 'datetime'),
        ('Snooze Fire Date', 'datetime'),
        ('Bedtime Fire Date', 'datetime'),
        ('Bedtime Snooze Fire Date', 'datetime'),
        ('Bedtime Dismiss Date', 'datetime'),
        'Alarm Time',
        'Alarm Title',
        'Alarm Enabled',
        'Repeat Schedule',
        'Alarm Sound',
        'Is Sleep Alarm',
        'Bedtime Do Not Disturb',
        'Bedtime'
        )
    return data_headers, data_list, source_path
