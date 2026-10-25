"""sms.db deep-field artifacts (reactions, edits, unsends, replies, recently deleted, payloads).

SYNTHETIC input only: the databases come from synthetic_sms_deep.py.
"""
import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts import sms_deep
from scripts.artifacts import smsAppPayloads, smsEdits, smsRecentlyDeleted, smsReactions, smsReplies

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('synthetic_sms_deep', HERE / 'synthetic_sms_deep.py')
SYNTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNTH)


def _context(path):
    return SimpleNamespace(get_files_found=lambda: [str(path)],
                           get_relative_path=lambda value: Path(value).name)


def _run(function, path):
    headers, rows, _source = function.__wrapped__(_context(path))
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return names, [dict(zip(names, row)) for row in rows]


class SyntheticMessagesTest(unittest.TestCase):
    variant = 'ios26'

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / 'private' / 'var' / 'mobile' / 'Library' / 'SMS' / 'sms.db'
        self.path.parent.mkdir(parents=True)
        self.expected = SYNTH.build(str(self.path), self.variant)

    def tearDown(self):
        self.folder.cleanup()

    def count(self, sql):
        db = sqlite3.connect(self.path)
        try:
            return db.execute(sql).fetchone()[0]
        finally:
            db.close()


class Ios26Test(SyntheticMessagesTest):
    def test_typedstream_round_trip(self):
        for text in ('a', 'Synthetic text', 'x' * 130, 'accent é and emoji \U0001F600'):
            self.assertEqual(sms_deep.typedstream_text(SYNTH.typedstream_bytes(text)), text)
        for bad in (None, b'', b'garbage', SYNTH.typedstream_bytes('abc')[:20]):
            self.assertIsNone(sms_deep.typedstream_text(bad))

    def test_associated_guid_forms(self):
        self.assertEqual(sms_deep.split_associated_guid('p:3/ABC'), (3, 'ABC'))
        self.assertEqual(sms_deep.split_associated_guid('bp:ABC'), (None, 'ABC'))
        self.assertEqual(sms_deep.split_associated_guid('ABC'), (None, 'ABC'))
        self.assertEqual(sms_deep.split_associated_guid(None), (None, ''))

    def test_reactions(self):
        _names, rows = _run(smsReactions.smsReactions, self.path)
        self.assertEqual(len(rows), self.expected['reactions'])
        self.assertEqual(len(rows), self.count(
            'SELECT count(*) FROM message WHERE associated_message_type = 1000 '
            'OR associated_message_type BETWEEN 2000 AND 3007'))
        by_type = {row['Stored Type']: row for row in rows}
        self.assertEqual(by_type[2000]['Reaction'], 'Loved')
        self.assertEqual(by_type[2000]['Action'], 'Added')
        self.assertEqual(by_type[2000]['Target Message Text'], 'Synthetic plain message one')
        self.assertEqual(by_type[2000]['Target Found'], 'Yes')
        self.assertEqual(by_type[2000]['Target Part'], 0)
        self.assertEqual(by_type[3001]['Action'], 'Removed')
        self.assertEqual(by_type[3001]['Reaction'], 'Liked')
        self.assertEqual(by_type[3001]['Target Message Text'], 'Synthetic body-only message')
        self.assertEqual(by_type[3001]['Target Sender'], 'Me')
        self.assertEqual(by_type[2006]['Emoji'], '\U0001F44D')
        self.assertEqual(by_type[2006]['Target Sender'], SYNTH.BOB)
        self.assertEqual(by_type[1000]['Reaction'], 'Sticker')
        self.assertEqual(by_type[1000]['Sticker File'], 'sticker.png')
        self.assertEqual(by_type[2003]['Target Found'], 'No')
        self.assertEqual(by_type[2003]['Target Message Text'], '')
        self.assertEqual(by_type[2003]['Target Part'], '')
        self.assertNotIn(2, by_type)
        self.assertEqual(str(by_type[2000]['Reaction Timestamp'])[:19], '2026-03-01 12:02:10')

    def test_edit_history(self):
        _names, rows = _run(smsEdits.smsEditHistory, self.path)
        self.assertEqual(len(rows), self.expected['edit_history_rows'])
        first = [row for row in rows if row['Version Text'] in ('First draft', 'Second draft', 'Final text')]
        self.assertEqual([row['Version Text'] for row in first], ['First draft', 'Second draft', 'Final text'])
        self.assertEqual([row['Version'] for row in first], [1, 2, 3])
        self.assertEqual([row['Current Version'] for row in first], ['', '', 'Yes'])
        self.assertTrue(all(row['Versions in Part'] == 3 and row['Edit Count'] == 2 for row in first))
        self.assertEqual(str(first[0]['Version Timestamp'])[:19], '2026-03-01 12:03:20')
        self.assertEqual(str(first[2]['Last Edited Timestamp'])[:19], '2026-03-01 12:04:50')
        self.assertEqual(first[0]['Original Text Length'], 11)
        broken = [row for row in rows if row['Version Text'] in ('', 'Repaired')]
        self.assertEqual([row['Version Text'] for row in broken], ['', 'Repaired'])
        self.assertEqual(self.count('SELECT count(*) FROM message WHERE date_edited > 0'), 5)

    def test_unsent_parts(self):
        _names, rows = _run(smsEdits.smsUnsentMessages, self.path)
        self.assertEqual(len(rows), self.expected['unsent_rows'])
        whole, partial = rows
        self.assertEqual(whole['Unsent Part'], 0)
        self.assertEqual(whole['Original Text Length'], 18)
        self.assertEqual(whole['Remaining Text'], '')
        self.assertEqual(whole['Parts Remaining (as stored)'], 0)
        self.assertEqual(str(whole['Unsent Timestamp'])[:19], '2026-03-01 12:05:30')
        self.assertEqual(partial['Unsent Part'], 1)
        self.assertEqual(partial['Original Text Length'], 9)
        self.assertEqual(partial['Remaining Text'], 'Kept')
        self.assertEqual(partial['Retracted Timestamp'], '')

    def test_replies(self):
        _names, rows = _run(smsReplies.smsReplies, self.path)
        self.assertEqual(len(rows), self.expected['replies'])
        found, orphan = rows
        self.assertEqual(found['Originator Found'], 'Yes')
        self.assertEqual(found['Originator Text'], 'Synthetic plain message one')
        self.assertEqual(found['Originator Sender'], SYNTH.ALICE)
        self.assertEqual(found['Originator Part (as stored)'], '0:0:27')
        self.assertEqual(orphan['Originator Found'], 'No')
        self.assertEqual(orphan['Originator Text'], '')

    def test_recently_deleted(self):
        _names, rows = _run(smsRecentlyDeleted.smsRecentlyDeleted, self.path)
        self.assertEqual(len(rows), self.expected['recently_deleted'])
        row = rows[0]
        self.assertEqual(row['Text'], 'Synthetic deleted message')
        self.assertEqual(row['Still Linked to Chat'], 'No')
        self.assertEqual(row['Chat Contact ID'], SYNTH.ALICE)
        self.assertEqual(str(row['Deleted Timestamp'])[:19], '2026-03-01 12:15:00')
        self.assertEqual(self.count('SELECT count(*) FROM chat_recoverable_message_join'), 1)

    def test_recently_deleted_parts(self):
        _names, rows = _run(smsRecentlyDeleted.smsRecentlyDeletedParts, self.path)
        self.assertEqual(len(rows), self.expected['recently_deleted_parts'])
        self.assertEqual([row['Part Index'] for row in rows], [1, 2])
        self.assertEqual(rows[0]['Part Text'], 'Synthetic deleted part')
        self.assertEqual(rows[1]['Part Text'], '')
        self.assertTrue(all(row['Still Linked to Chat'] == 'Yes' for row in rows))
        self.assertTrue(all(row['Remaining Message Text'] == 'Remaining part' for row in rows))

    def test_link_previews(self):
        _names, rows = _run(smsAppPayloads.smsLinkPreviews, self.path)
        self.assertEqual(len(rows), self.expected['link_previews'])
        new, old = rows
        self.assertEqual(new['URL'], 'https://example.com/page')
        self.assertEqual(new['Original URL'], 'https://example.com/original')
        self.assertEqual(new['Title'], 'Synthetic title')
        self.assertEqual(new['Site Name'], 'Example')
        self.assertEqual(new['Placeholder (as stored)'], 'False')
        self.assertEqual(old['URL'], 'https://example.org/')
        self.assertEqual(old['Title'], 'Old format')

    def test_app_messages(self):
        _names, rows = _run(smsAppPayloads.smsAppMessages, self.path)
        self.assertEqual(len(rows), self.expected['app_messages'])
        app, undecoded = rows
        self.assertEqual(app['App Name'], 'ExampleApp')
        self.assertEqual(app['Caption'], 'Synthetic caption')
        self.assertEqual(app['Image Title'], 'Synthetic image title')
        self.assertEqual(app['URL'], 'data:example?x=1')
        self.assertEqual(app['Payload Format'], 'Keyed archive')
        self.assertEqual(undecoded['Payload Format'], 'Not decoded')
        self.assertEqual(undecoded['App Bundle'], 'com.example.handwriting')
        self.assertEqual(undecoded['Caption'], '')


class Ios16Test(SyntheticMessagesTest):
    """A database without the newer columns and tables returns rows where it can and never raises."""
    variant = 'ios16'

    def test_missing_columns_and_tables(self):
        for function in (smsEdits.smsEditHistory, smsEdits.smsUnsentMessages, smsReplies.smsReplies,
                         smsRecentlyDeleted.smsRecentlyDeleted, smsRecentlyDeleted.smsRecentlyDeletedParts):
            _names, rows = _run(function, self.path)
            self.assertEqual(rows, [], function.__name__)
        _names, rows = _run(smsReactions.smsReactions, self.path)
        self.assertEqual(len(rows), self.expected['reactions'])
        self.assertEqual(rows[2]['Emoji'], '')
        _names, rows = _run(smsAppPayloads.smsLinkPreviews, self.path)
        self.assertEqual(len(rows), self.expected['link_previews'])


class DamagedInputTest(unittest.TestCase):
    def test_not_a_database_and_empty_database(self):
        with tempfile.TemporaryDirectory() as folder:
            bad = Path(folder) / 'sms.db'
            bad.write_bytes(b'this is not a sqlite database' * 10)
            empty = Path(folder) / 'empty' / 'sms.db'
            empty.parent.mkdir()
            sqlite3.connect(empty).close()
            for function in (smsReactions.smsReactions, smsEdits.smsEditHistory, smsEdits.smsUnsentMessages,
                             smsReplies.smsReplies, smsRecentlyDeleted.smsRecentlyDeleted,
                             smsRecentlyDeleted.smsRecentlyDeletedParts, smsAppPayloads.smsLinkPreviews,
                             smsAppPayloads.smsAppMessages):
                for path in (bad, empty):
                    _names, rows = _run(function, path)
                    self.assertEqual(rows, [], f'{function.__name__} {path.name}')


if __name__ == '__main__':
    unittest.main()
