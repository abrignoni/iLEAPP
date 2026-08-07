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
        self.assertEqual(data_list[0][7], 'system:Arpeggio')

    def test_song_alarm_reports_the_media_item(self):
        """A song alarm has no MTSoundToneID and used to raise KeyError."""
        data_list = self._run({'MTSoundType': 3,
                               'MTSoundMediaItemID': 5999271,
                               'MTSoundVibrationID': 'SOS'})
        self.assertEqual(len(data_list), 1)
        self.assertEqual(data_list[0][7], 'media item: 5999271')


if __name__ == '__main__':
    unittest.main()
