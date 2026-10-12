"""ChatGPT tmp media is reported only from a container a ChatGPT preference file identifies.

The paths of chatgptMediaUploads and chatgptVoicePrompts match the tmp directory of every
app container, since container names are UUIDs. Without a marker the artifacts reported
every match, and issue #1732 showed Voice Memos recordings from a device without ChatGPT
listed as ChatGPT voice prompts.

The marker is a preference file named for ChatGPT's bundle id, at its place inside the
container. A conversations-* folder is not one, because any app can have a folder of that
name, and neither is a staged path that only mentions com.openai.chat somewhere.

These tests run the two artifacts over constructed file lists the way the runner hands them
over, with media check-in replaced so no report folder is needed.
"""
import unittest
from unittest.mock import patch

from scripts.artifacts import chatgpt as module

DATA = '/cases/com.openai.chat review/tmp/data/'
APPS = DATA + 'root/private/var/mobile/Containers/Data/Application/'
CHATGPT = APPS + '1A2B3C4D-0000-4000-8000-000000000001'
OTHER = APPS + '9F8E7D6C-0000-4000-8000-000000000002'
MARKERS = (CHATGPT + '/Library/Preferences/com.openai.chat.plist',
           CHATGPT + '/Library/Preferences/com.openai.chat.StatsigService.plist')
OTHER_CONVERSATIONS = OTHER + '/Library/Application Support/conversations-abc/1.json'
OTHER_PLIST = OTHER + '/Library/Preferences/com.openai.chat.example.plist'
CHATGPT_AUDIO = CHATGPT + '/tmp/recordings/prompt.m4a'
OTHER_AUDIO = OTHER + '/tmp/recordings/memo.m4a'
CHATGPT_IMAGE = CHATGPT + '/tmp/photo-1.png'
OTHER_IMAGE = OTHER + '/tmp/uploads/picture.png'
NOT_TMP_AUDIO = CHATGPT + '/Documents/tmp/recordings/kept.m4a'


class Context:
    def __init__(self, files):
        self.files = files

    def get_files_found(self):
        return self.files

    @staticmethod
    def get_relative_path(path):
        return path[len(DATA):] if path.startswith(DATA) else path


def rows(artifact, files):
    _, data_list, source = artifact.__wrapped__(Context(files))
    return [row[2] for row in data_list], source


def relative(path):
    return path[len(DATA):]


class ChatGPTTmpMediaRequiresMarkerTest(unittest.TestCase):

    def setUp(self):
        checkin = patch.object(module, 'check_in_media', side_effect=lambda path, name: path)
        checkin.start()
        self.addCleanup(checkin.stop)

    def test_no_marker_reports_nothing(self):
        for artifact in (module.chatgptVoicePrompts, module.chatgptMediaUploads):
            self.assertEqual(rows(artifact, [OTHER_AUDIO, OTHER_IMAGE]), ([], ''))

    def test_either_preference_file_limits_rows_to_its_container(self):
        for marker in MARKERS:
            files = [OTHER_AUDIO, CHATGPT_AUDIO, marker, OTHER_IMAGE, CHATGPT_IMAGE]
            self.assertEqual(rows(module.chatgptVoicePrompts, files),
                             ([relative(CHATGPT_AUDIO)], CHATGPT + '/tmp/recordings'))
            self.assertEqual(rows(module.chatgptMediaUploads, files),
                             ([relative(CHATGPT_IMAGE)], CHATGPT + '/tmp'))

    def test_another_apps_conversations_folder_is_not_a_marker(self):
        files = [OTHER_CONVERSATIONS, OTHER_PLIST, OTHER_AUDIO, OTHER_IMAGE]
        for artifact in (module.chatgptVoicePrompts, module.chatgptMediaUploads):
            self.assertEqual(rows(artifact, files), ([], ''))

    def test_a_file_matched_by_two_patterns_is_one_row(self):
        files = [MARKERS[0], CHATGPT_AUDIO, CHATGPT_AUDIO]
        self.assertEqual(rows(module.chatgptVoicePrompts, files)[0], [relative(CHATGPT_AUDIO)])

    def test_tmp_means_the_containers_own_tmp_folder(self):
        files = [MARKERS[0], NOT_TMP_AUDIO]
        self.assertEqual(rows(module.chatgptVoicePrompts, files), ([], ''))


if __name__ == '__main__':
    unittest.main()
