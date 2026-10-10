"""ChatGPT tmp media is reported only from a container a ChatGPT marker file identifies.

The paths of chatgptMediaUploads and chatgptVoicePrompts match the tmp directory of every
app container, since container names are UUIDs. Without a marker the artifacts reported
every match, and issue #1732 showed Voice Memos recordings from a device without ChatGPT
listed as ChatGPT voice prompts.

These tests run the two artifacts over constructed file lists the way the runner hands them
over, with media check-in replaced so no report folder is needed.
"""
import unittest
from unittest.mock import patch

from scripts.artifacts import chatgpt as module

APPS = 'root/private/var/mobile/Containers/Data/Application/'
CHATGPT = APPS + '1A2B3C4D-0000-4000-8000-000000000001'
OTHER = APPS + '9F8E7D6C-0000-4000-8000-000000000002'
MARKER = CHATGPT + '/Library/Application Support/conversations-abc/1.json'
CHATGPT_AUDIO = CHATGPT + '/tmp/recordings/prompt.m4a'
OTHER_AUDIO = OTHER + '/tmp/recordings/memo.m4a'
CHATGPT_IMAGE = CHATGPT + '/tmp/photo-1.png'
OTHER_IMAGE = OTHER + '/tmp/uploads/picture.png'


class Context:
    def __init__(self, files):
        self.files = files

    def get_files_found(self):
        return self.files

    @staticmethod
    def get_relative_path(path):
        return path


class ChatGPTTmpMediaRequiresMarkerTest(unittest.TestCase):

    def setUp(self):
        checkin = patch.object(module, 'check_in_media', side_effect=lambda path, name: path)
        checkin.start()
        self.addCleanup(checkin.stop)

    def test_no_marker_reports_nothing(self):
        for artifact in (module.chatgptVoicePrompts, module.chatgptMediaUploads):
            _, rows, source = artifact.__wrapped__(Context([OTHER_AUDIO, OTHER_IMAGE]))
            self.assertEqual(rows, [])
            self.assertEqual(source, '')

    def test_a_marker_limits_rows_to_its_container(self):
        files = [OTHER_AUDIO, CHATGPT_AUDIO, MARKER, OTHER_IMAGE, CHATGPT_IMAGE]

        _, audio, audio_source = module.chatgptVoicePrompts.__wrapped__(Context(files))
        _, images, image_source = module.chatgptMediaUploads.__wrapped__(Context(files))

        self.assertEqual([row[2] for row in audio], [CHATGPT_AUDIO])
        self.assertEqual(audio_source, CHATGPT + '/tmp/recordings')
        self.assertEqual([row[2] for row in images], [CHATGPT_IMAGE])
        self.assertEqual(image_source, CHATGPT + '/tmp')


if __name__ == '__main__':
    unittest.main()
