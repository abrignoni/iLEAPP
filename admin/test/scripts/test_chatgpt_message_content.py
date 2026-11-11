"""ChatGPT - Conversations shows text stored outside parts, the node's created_at, and JSON.

code and system_error messages keep their text in a text key and model_editable_context
messages in model_set_context, so a module reading only parts showed those rows blank. Every
node on the tested images also carries created_at in Cocoa seconds, present where the
message has no create_time.
Parts that are objects and the metadata are written as JSON, the form the file stores.
"""
import io
import json
import unittest
from datetime import datetime, timezone

from scripts.artifacts import chatgpt as module


def run(nodes):
    """Run the artifact over one constructed conversation-v3 file held in memory."""
    storage = []
    for index, entry in enumerate(nodes):
        storage += [f'm{index}', entry]
    data = {'id': 'c1', 'title': 't', 'tree': {'storage': storage}}
    path = '/x/Containers/Data/Application/A/Library/Application Support/conversations-v3-a/c1.json'

    class Context:
        @staticmethod
        def get_files_found():
            return [path]

        @staticmethod
        def get_relative_path(value):
            return value

    real_open = open

    def fake_open(file, *args, **kwargs):
        if file == path:
            return io.StringIO(json.dumps(data))
        return real_open(file, *args, **kwargs)

    module.open = fake_open
    try:
        headers, rows, _ = module.chatgptConversations.__wrapped__(Context)
    finally:
        del module.open
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(names, row)) for row in rows]


def node(body, **extra):
    message = {'author': {'role': 'assistant'}, 'content': body, 'metadata': {}}
    message.update(extra.pop('message', {}))
    return dict({'content': message}, **extra)


class ChatGPTMessageContentTest(unittest.TestCase):

    def test_text_outside_parts_is_shown(self):
        rows = run([
            node({'content_type': 'code', 'language': 'python', 'text': 'print(1)'}),
            node({'content_type': 'system_error', 'name': 'e', 'text': 'boom'}),
            node({'content_type': 'model_editable_context', 'model_set_context': 'ctx'}),
            node({'content_type': 'text', 'parts': ['a', 'b']}),
            node({'content_type': 'unknown'}),
        ])
        self.assertEqual([r['Content'] for r in rows], ['print(1)', 'boom', 'ctx', 'a\nb', ''])

    def test_metadata_is_blank_without_the_key_and_json_when_empty(self):
        bare = {'content': {'author': {'role': 'user'}, 'content': {'content_type': 'text', 'parts': ['x']}}}
        rows = run([bare, node({'content_type': 'text', 'parts': ['y']}),
                    node({'content_type': 'text', 'parts': ['z']}, message={'metadata': None})])
        self.assertEqual([r['Metadata'] for r in rows], ['', '{}', ''])

    def test_object_parts_and_metadata_are_json(self):
        part = {'content_type': 'image_asset_pointer', 'asset_pointer': 'p', 'width': 2}
        rows = run([node({'content_type': 'multimodal_text', 'parts': [part, 'caption']},
                         message={'metadata': {'flag': True, 'none': None}})])
        first, second = rows[0]['Content'].split('\n')
        self.assertEqual(json.loads(first), part)
        self.assertEqual(second, 'caption')
        self.assertEqual(json.loads(rows[0]['Metadata']), {'flag': True, 'none': None})

    def test_node_created_at_is_cocoa_seconds_and_kept_without_create_time(self):
        rows = run([node({'content_type': 'text', 'parts': ['x']}, created_at=700000000.25),
                    node({'content_type': 'text', 'parts': ['y']},
                         message={'create_time': 1678307200.25}, created_at=700000000.25)])
        expected = datetime(2023, 3, 8, 20, 26, 40, tzinfo=timezone.utc)
        self.assertEqual(rows[0]['Creation Time'], '')
        self.assertEqual(rows[0]['Node Created At'], expected)
        self.assertEqual(rows[1]['Creation Time'], expected)
        self.assertEqual(rows[1]['Node Created At'], expected)


if __name__ == '__main__':
    unittest.main()
