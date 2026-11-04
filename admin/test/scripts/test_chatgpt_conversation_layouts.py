"""ChatGPT conversations are read from every folder layout the app has used.

The 2023 app kept its conversation files in a plain Library/Application Support/conversations/
folder, which the conversations-* pattern did not match, so those conversations were not
reported. Any app could have a folder of that name, so it is read only from the container a
ChatGPT preference file identifies. conversations-v3 files keep the message tree as a list
alternating the message id and its node, which the message artifact skipped.

These tests write constructed conversation files to a temporary folder and run the two
artifacts over them the way the runner hands them over.
"""
import json
import os
import shutil
import tempfile
import unittest

from scripts.artifacts import chatgpt as module

NODE = {'content': {'author': {'role': 'user'}, 'create_time': 1700000000,
                    'content': {'content_type': 'text', 'parts': ['hello']}}}


class Context:
    def __init__(self, data, files):
        self.data = data
        self.files = files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return path[len(self.data):] if path.startswith(self.data) else path


class ChatGPTConversationLayoutsTest(unittest.TestCase):

    def setUp(self):
        self.data = tempfile.mkdtemp() + '/'
        self.addCleanup(shutil.rmtree, self.data)
        apps = self.data + 'root/private/var/mobile/Containers/Data/Application/'
        self.chatgpt = apps + '1A2B3C4D-0000-4000-8000-000000000001'
        self.other = apps + '9F8E7D6C-0000-4000-8000-000000000002'
        self.marker = self.write(self.chatgpt + '/Library/Preferences/com.openai.chat.plist', b'')
        dict_tree = {'id': 'c1', 'title': 't', 'tree': {'storage': {'m1': NODE}}}
        self.legacy = self.write(
            self.chatgpt + '/Library/Application Support/conversations/c1.json', dict_tree)
        self.other_legacy = self.write(
            self.other + '/Library/Application Support/conversations/c1.json', dict_tree)
        self.v3 = self.write(
            self.chatgpt + '/Library/Application Support/conversations-v3-abc/c2.json',
            {'id': 'c2', 'tree': {'storage': ['m1', NODE, 'm2', dict(NODE, id='m2')]}})

    def write(self, path, content):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as fh:
            fh.write(content if isinstance(content, bytes) else json.dumps(content).encode())
        return path

    def rows(self, artifact, files):
        return artifact.__wrapped__(Context(self.data, files))[1]

    def test_legacy_folder_is_read_from_the_marked_container(self):
        files = [self.marker, self.legacy]
        self.assertEqual([r[3] for r in self.rows(module.chatgptConversationsMetadata, files)], ['c1'])
        self.assertEqual([(r[1], r[6]) for r in self.rows(module.chatgptConversations, files)],
                         [('m1', 'text')])

    def test_legacy_folder_without_a_marker_is_not_read(self):
        for artifact in (module.chatgptConversationsMetadata, module.chatgptConversations):
            self.assertEqual(self.rows(artifact, [self.other_legacy]), [])

    def test_a_marker_in_another_container_does_not_admit_the_folder(self):
        for artifact in (module.chatgptConversationsMetadata, module.chatgptConversations):
            self.assertEqual(self.rows(artifact, [self.marker, self.other_legacy]), [])

    def test_v3_list_tree_yields_one_row_per_node(self):
        rows = self.rows(module.chatgptConversations, [self.v3])
        self.assertEqual([(r[1], r[3]) for r in rows], [('m1', 'c2'), ('m2', 'c2')])

    def test_a_file_matched_by_two_patterns_is_read_once(self):
        rows = self.rows(module.chatgptConversationsMetadata, [self.v3, self.v3])
        self.assertEqual(len(rows), 1)


if __name__ == '__main__':
    unittest.main()
