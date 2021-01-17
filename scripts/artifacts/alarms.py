import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline


def get_alarms(files_found, report_folder, seeker):
    data_list = []

    for file_found in files_found:
        with open(file_found, "rb") as plist_file:
            pl = plistlib.load(plist_file)

            for alarms in pl['MTAlarms']['MTAlarms']:
                alarms_dict = alarms['$MTAlarm']

                alarm_title = check_if_key_exists('MTAlarmTitle', alarms_dict, 'Alarm')
                fire_date = check_if_key_exists('MTAlarmFireDate', alarms_dict)
                dismiss_date = check_if_key_exists('MTAlarmDismissDate', alarms_dict)

                data_list.append((alarm_title, alarms_dict['MTAlarmEnabled'], fire_date, dismiss_date,
                                  alarms_dict['MTAlarmLastModifiedDate'],
                                  alarms_dict['MTAlarmRepeatSchedule'], alarms_dict['MTAlarmSound']['$MTSound']['MTSoundToneID'],
                                  alarms_dict['MTAlarmIsSleep'], alarms_dict['MTAlarmBedtimeDoNotDisturb'], ''))

            for sleep_alarms in pl['MTAlarms']['MTSleepAlarm']:
                sleep_alarm_dict = pl['MTAlarms']['MTSleepAlarm'][sleep_alarms]

                alarm_title = check_if_key_exists('MTAlarmTitle', sleep_alarm_dict, 'Bedtime')

                data_list.append((alarm_title, sleep_alarm_dict['MTAlarmEnabled'], sleep_alarm_dict['MTAlarmFireDate'],
                                  sleep_alarm_dict['MTAlarmDismissDate'], sleep_alarm_dict['MTAlarmLastModifiedDate'],
                                  sleep_alarm_dict['MTAlarmRepeatSchedule'], sleep_alarm_dict['MTAlarmSound']['$MTSound']['MTSoundToneID'],
                                  sleep_alarm_dict['MTAlarmIsSleep'], sleep_alarm_dict['MTAlarmBedtimeDoNotDisturb'],
                                  sleep_alarm_dict['MTAlarmBedtimeFireDate']))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Alarms')
        report.start_artifact_report(report_folder, 'Alarms')
        report.add_script()
        data_headers = ('Alarm Title', 'Alarm Enabled', 'Fire Date', 'Dismiss Date', 'Last Modified', 'Repeat Schedule', 'Alarm Sound', 'Is Sleep Alarm', 'Bedtime Not Disturbed', 'Bedtime Fire Date')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Alarms'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Alarms'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Alarms found')


def check_if_key_exists(dict_key, alarms_dict, replace_value=''):
    if dict_key in alarms_dict:
        return alarms_dict[dict_key]
    else:
        if not replace_value:
            return ''
        return replace_value
