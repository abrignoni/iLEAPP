"""A conversation view's data values must reach the LAVA manifest as the artifact wrote them.

`lava_process_artifact` turns the keys of a conversation data view that name a column into
that column's SQL name, so `timeColumn: 'Sent'` is stored as `sent`. It used to do that to
every value that matched a header, including the two keys LAVA reads as data rather than as
a column: `directionSentValue` and `sentMessageStaticLabel`.

An artifact whose direction value is 'Sent' beside a 'Sent' time column therefore reached the
manifest with `directionSentValue: 'sent'`. LAVA classifies a message as sent by comparing the
direction column against that value, no row matched, and every message in the conversation view
was shown as received. Nothing errored, and the row counts were right.
"""
import datetime
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

# 'Sent' is both the time column and the direction value, and 'Me' is both a column and the
# static label, which is the collision the writer has to get right.
HEADERS = [('Sent', 'datetime'), 'Direction', 'Author', 'Me', 'Body', 'Thread', 'Media']

SENT_AT = datetime.datetime(2026, 9, 19, 12, 0, tzinfo=datetime.timezone.utc)


class TestConversationViewValues(unittest.TestCase):
    """Column keys are sanitized; data values are written as they were given."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        Context.set_artifact_info({'name': 'Conversation Values', 'description': 'test artifact'})
        # Only the basename is read, so this path never has to exist. Keeping it synthetic
        # lets the same test file be shared across the LEAPP tools unchanged.
        Context.set_module_file_path(
            str(REPO_ROOT / 'scripts' / 'artifacts' / 'conversation_values.py'))

    def tearDown(self):
        if lavafuncs.lava_db is not None:
            lavafuncs.lava_db.close()
            lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _process(self, data_views):
        table_name, object_columns, column_map = lavafuncs.lava_process_artifact(
            'Testing', 'conversation_values_module', 'Conversation Values', HEADERS,
            record_count=2, func_name='conversation_values', data_views=data_views)
        artifact = lavafuncs.lava_data['artifacts']['Testing'][0]
        return artifact['data_views']['conversation'], table_name, object_columns, column_map

    def test_data_values_survive_matching_a_column_name(self):
        view, _, _, _ = self._process({'conversation': {
            'conversationDiscriminatorColumn': 'Thread',
            'textColumn': 'Body',
            'directionColumn': 'Direction',
            'directionSentValue': 'Sent',
            'timeColumn': 'Sent',
            'senderColumn': 'Author',
            'sentMessageStaticLabel': 'Me',
        }})

        self.assertEqual(view['directionSentValue'], 'Sent')
        self.assertEqual(view['sentMessageStaticLabel'], 'Me')
        # The same text used as a column name is still sanitized.
        self.assertEqual(view['timeColumn'], 'sent')

    def test_the_stored_sent_value_matches_the_rows(self):
        """The check LAVA makes: direction column against the manifest's sent value."""
        view, table_name, object_columns, column_map = self._process({'conversation': {
            'conversationDiscriminatorColumn': 'Thread',
            'textColumn': 'Body',
            'directionColumn': 'Direction',
            'directionSentValue': 'Sent',
            'timeColumn': 'Sent',
            'senderColumn': 'Author',
        }})
        rows = [
            (SENT_AT, 'Sent', 'me', 'me', 'first', 'thread-1', ''),
            (SENT_AT, 'Received', 'them', 'me', 'second', 'thread-1', ''),
        ]
        lavafuncs.lava_insert_sqlite_data(table_name, rows, object_columns, HEADERS, column_map)

        cursor = lavafuncs.lava_db.cursor()
        matched = cursor.execute(
            f'SELECT COUNT(*) FROM "{table_name}" WHERE "{view["directionColumn"]}" = ?',
            (view['directionSentValue'],)).fetchone()[0]
        self.assertEqual(matched, 1, 'no row matches the sent value the manifest carries')

    def test_column_keys_are_still_sanitized(self):
        view, _, _, _ = self._process({'conversation': {
            'conversationDiscriminatorColumn': 'Thread',
            'conversationLabelColumn': 'Thread',
            'textColumn': 'Body',
            'directionColumn': 'Direction',
            'directionSentValue': 'Outgoing',
            'timeColumn': 'Sent',
            'senderColumn': 'Author',
            'mediaColumn': 'Media',
            'sentMessageLabelColumn': 'Me',
        }})

        self.assertEqual(view, {
            'conversationDiscriminatorColumn': 'thread',
            'conversationLabelColumn': 'thread',
            'textColumn': 'body',
            'directionColumn': 'direction',
            'directionSentValue': 'Outgoing',
            'timeColumn': 'sent',
            'senderColumn': 'author',
            'mediaColumn': 'media',
            'sentMessageLabelColumn': 'me',
        })

    def test_a_value_that_names_no_column_is_untouched(self):
        view, _, _, _ = self._process({'conversation': {
            'conversationDiscriminatorColumn': 'Thread',
            'textColumn': 'Body',
            'directionColumn': 'Direction',
            'directionSentValue': 'Outgoing',
            'timeColumn': 'Sent',
            'senderColumn': 'Author',
        }})

        self.assertEqual(view['directionSentValue'], 'Outgoing')

    def test_legacy_chat_view_keys_are_renamed_and_the_value_kept(self):
        """The deprecated 'chat' view is upgraded to 'conversation' on the way through."""
        view, _, _, _ = self._process({'chat': {
            'threadDiscriminatorColumn': 'Thread',
            'threadLabelColumn': 'Thread',
            'textColumn': 'Body',
            'directionColumn': 'Direction',
            'directionSentValue': 'Sent',
            'timeColumn': 'Sent',
            'senderColumn': 'Author',
        }})

        self.assertEqual(view['conversationDiscriminatorColumn'], 'thread')
        self.assertEqual(view['conversationLabelColumn'], 'thread')
        self.assertEqual(view['directionSentValue'], 'Sent')


if __name__ == '__main__':
    unittest.main()
