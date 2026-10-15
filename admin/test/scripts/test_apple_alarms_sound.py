"""An alarm whose sound is a song must not kill the alarms artifact.

com.apple.mobiletimerd.plist stores the alarm sound under
MTAlarmSound/$MTSound, but the key inside it depends on what the user picked:
a built-in tone has MTSoundToneID, while a song from the media library has
MTSoundMediaItemID and no MTSoundToneID at all. The artifact indexed
MTSoundToneID directly, so a single song alarm raised KeyError and the whole
artifact returned no rows.
"""
import pathlib
import plistlib
import sys
import tempfile
import unittest
from datetime import datetime, timezone

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts.appleAlarms import alarms  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position


def _alarm(sound):
    return {
        'MTAlarmTitle': 'Alarm',
        'MTAlarmHour': 5,
        'MTAlarmMinute': 35,
        'MTAlarmEnabled': True,
        'MTAlarmRepeatSchedule': 0,
        'MTAlarmIsSleep': False,
        'MTAlarmBedtimeDoNotDisturb': False,
        'MTAlarmSound': {'$MTSound': sound},
    }


class TestAppleAlarmsSound(unittest.TestCase):

    def _run(self, sound):
        plist = {'MTAlarms': {'MTAlarms': [{'$MTAlarm': _alarm(sound)}],
                              'MTSleepAlarms': []}}
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'com.apple.mobiletimerd.plist'
            path.write_bytes(plistlib.dumps(plist))
            Context.clear()
            Context.set_files_found([str(path)])
            _, data_list, _ = alarms.__wrapped__(Context)
        return data_list

    def test_tone_alarm_reports_the_tone_id(self):
        data_list = self._run({'MTSoundType': 2,
                               'MTSoundToneID': 'system:Arpeggio',
                               'MTSoundVibrationID': 'SOS'})
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0][12], 'system:Arpeggio')

    def test_song_alarm_reports_the_media_item(self):
        """A song alarm has no MTSoundToneID and used to raise KeyError."""
        data_list = self._run({'MTSoundType': 3,
                               'MTSoundMediaItemID': 5999271,
                               'MTSoundVibrationID': 'SOS'})
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0][12], 'media item: 5999271')

    def _run_plist(self, plist):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'com.apple.mobiletimerd.plist'
            path.write_bytes(plistlib.dumps(plist))
            Context.clear()
            Context.set_files_found([str(path)])
            _, data_list, _ = alarms.__wrapped__(Context)
        return data_list

    def test_sleep_alarms_list_is_reported(self):
        """In the registered images from iOS 14.3 on, sleep alarms sit in the MTSleepAlarms
        list, with no title, no MTAlarmBedtimeFireDate and a sound with no tone or media item."""
        sleep = {'MTAlarmHour': 6, 'MTAlarmMinute': 5,
                 'MTAlarmBedtimeHour': 22, 'MTAlarmBedtimeMinute': 30,
                 'MTAlarmEnabled': True, 'MTAlarmRepeatSchedule': 31,
                 'MTAlarmIsSleep': True, 'MTAlarmBedtimeDoNotDisturb': True,
                 'MTAlarmSound': {'$MTSound': {'MTSoundType': 4, 'MTSoundVolume': 0.5}}}
        data_list = self._run_plist({'MTAlarms': {
            'MTAlarms': [{'$MTAlarm': _alarm({'MTSoundToneID': 'system:Arpeggio'})}],
            'MTSleepAlarms': [{'$MTAlarm': sleep}]}})
        self.assertEqual(len(data_list), 2)
        regular, sleep_row = data_list
        self.assertEqual(regular[15], '')
        self.assertEqual(sleep_row[8], '06:05')
        self.assertEqual(sleep_row[9], '')
        self.assertEqual(sleep_row[11], 'Monday, Tuesday, Wednesday, Thursday, Friday')
        self.assertEqual(sleep_row[12], '')
        self.assertIs(sleep_row[13], True)
        self.assertEqual(sleep_row[15], '22:30')

    def test_plist_without_sleep_list_still_reports_alarms(self):
        """The registered iOS 12.4 and 13.3.1 images store no MTSleepAlarms key."""
        data_list = self._run_plist({'MTAlarms': {
            'MTAlarms': [{'$MTAlarm': _alarm({'MTSoundToneID': 'system:Arpeggio'})}]}})
        self.assertEqual(len(data_list), 1)

    def test_missing_optional_keys_do_not_drop_the_alarm(self):
        """An alarm without schedule, state or time keys still yields its row."""
        data_list = self._run_plist({'MTAlarms': {'MTAlarms': [{'$MTAlarm': {}}]}})
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0][8], '')
        self.assertEqual(data_list[0][11], '')

    def test_missing_dates_are_none_not_empty_strings(self):
        """The first eight columns are datetime columns. A missing date must reach LAVA as
        NULL, not as an empty string in an INTEGER column."""
        data_list = self._run_plist({'MTAlarms': {'MTAlarms': [{'$MTAlarm': {}}]}})
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0][:8], (None,) * 8)

    def test_dates_lead_the_row(self):
        """Every timestamp sits directly after Fire Date."""
        fire = datetime(2026, 1, 2, 6, 5, tzinfo=timezone.utc)
        dismiss = datetime(2026, 1, 2, 6, 6, tzinfo=timezone.utc)
        modified = datetime(2026, 1, 1, 22, 0, tzinfo=timezone.utc)
        alarm = _alarm({'MTSoundToneID': 'system:Arpeggio'})
        alarm.update({'MTAlarmFireDate': fire.replace(tzinfo=None),
                      'MTAlarmDismissDate': dismiss.replace(tzinfo=None),
                      'MTAlarmLastModifiedDate': modified.replace(tzinfo=None)})
        data_list = self._run_plist({'MTAlarms': {'MTAlarms': [{'$MTAlarm': alarm}]}})
        self.assertEqual(data_list[0][:9], (fire, dismiss, modified,
                                            None, None, None, None, None, '05:35'))

    def test_mobiletimer_date_keys_fill_their_columns(self):
        """MobileTimer's MTDictionarySerializer writes these five keys once the matching
        setter (setKeepOffUntilDate:, setSnoozeFireDate:, setBedtimeFiredDate:,
        setBedtimeSnoozeFireDate:, setBedtimeDismissedDate:) has set a date."""
        keys = ('MTAlarmKeepOffUntilDate', 'MTAlarmSnoozeFireDate', 'MTAlarmBedtimeFireDate',
                'MTAlarmBedtimeSnoozeFireDate', 'MTAlarmBedtimeDismissDate')
        dates = [datetime(2026, 1, 3, 7, minute, tzinfo=timezone.utc) for minute in range(5)]
        sleep = {'MTAlarmHour': 6, 'MTAlarmMinute': 5, 'MTAlarmIsSleep': True}
        sleep.update({key: date.replace(tzinfo=None) for key, date in zip(keys, dates)})
        data_list = self._run_plist({'MTAlarms': {'MTAlarms': [],
                                                  'MTSleepAlarms': [{'$MTAlarm': sleep}]}})
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0][:3], (None, None, None))
        self.assertEqual(data_list[0][3:8], tuple(dates))
        self.assertEqual(data_list[0][8], '06:05')

    def test_row_width_matches_headers(self):
        """Every row is as wide as the header tuple, so no column shifts."""
        plist = {'MTAlarms': {'MTAlarms': [{'$MTAlarm': {}}]}}
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'com.apple.mobiletimerd.plist'
            path.write_bytes(plistlib.dumps(plist))
            Context.clear()
            Context.set_files_found([str(path)])
            headers, data_list, _ = alarms.__wrapped__(Context)
        self.assertEqual(len(data_list[0]), len(headers))


if __name__ == '__main__':
    unittest.main()
