"""Actual JSON cache occurrences retain their existing cells and branch origin."""
import copy
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

MODULE = Path(__file__).resolve().parents[3] / 'scripts/artifacts/kleinanzeigen.de.py'
SPEC = importlib.util.spec_from_file_location('kleinanzeigen_cache_origins', MODULE)
PARSER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PARSER)


def cache_fixture():
    """Writer-declared two equal old tuples plus repeated and distinct rows."""
    preview = {
        'conversationId': 'conv', 'ad': {'displayTitle': 'Item', 'identifier': 'ad'},
        'counterParty': {'name': 'Other', 'identifier': 'other'},
        'clientData': {'role': 'Seller', 'sellerName': 'Local', 'userIdSeller': 'local',
                       'textShortTrimmed': 'text 雪 <>& " + :\nnext', 'receivedDate': 0,
                       'boundness': 'OUTBOUND', 'adStatus': 'ACTIVE'}, 'messages': []}
    message = {'messageId': '', 'sentDate': 0, 'text': preview['clientData']['textShortTrimmed'],
               'attachments': [], 'sender': 0}
    cached = copy.deepcopy(preview)
    cached['messages'] = [message, copy.deepcopy(message)]
    incoming = copy.deepcopy(preview)
    incoming['clientData'] = {'role': 'Buyer', 'buyerName': 'Buyer', 'userIdBuyer': 42,
                              'textShortTrimmed': 'in', 'receivedDate': 1,
                              'boundness': 'UNKNOWN'}
    incoming['messages'] = [{'messageId': None, 'sentDate': 1, 'text': 'in', 'sender': 7,
                             'attachments': [{'imageURL': 'https://fixture.invalid/a?x=1&y=2'},
                                             {'imageURL': 'https://fixture.invalid/b'}]}]
    invalid_preview = copy.deepcopy(preview)
    del invalid_preview['clientData']['receivedDate']
    bad_date = copy.deepcopy(preview)
    bad_date['clientData']['receivedDate'] = 'not a date'
    row = ('2001-01-01 00:00:00', 1, 'Local', 'Item (Other)',
           preview['clientData']['textShortTrimmed'], 'conv', 'ad', 'local', 'Other',
           'other', 'none', '', 'ACTIVE')
    incoming_row = ('2001-01-01 00:00:01', 0, 'Other', 'Item (Other)', 'in', 'conv',
                    'ad', 'other', 'Buyer', 42,
                    'https://fixture.invalid/a?x=1&y=2, https://fixture.invalid/b',
                    None, 'UNKNOWN')
    return {'data': [preview, cached, invalid_preview, bad_date, incoming, copy.deepcopy(preview)]}, [
        row + ('Preview',), row + ('Cached Message',), row + ('Cached Message',),
        incoming_row + ('Cached Message',), row + ('Preview',)]


class TestCacheOrigins(unittest.TestCase):
    def test_actual_cache_retains_equal_old_rows_and_repeats(self):
        payload, expected = cache_fixture()
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / 'conversation_cache'
            path.write_text(json.dumps(payload), encoding='utf-8')
            context = SimpleNamespace(get_files_found=lambda: [path])
            headers, rows, source = PARSER.get_kleinanzeigenmessagecache.__wrapped__(context)
        self.assertEqual(rows, expected)
        self.assertEqual(len(headers), 14)
        self.assertEqual(rows[0][:13], rows[1][:13])
        self.assertNotEqual(rows[0][13], rows[1][13])
        self.assertIsNone(rows[3][11])
        self.assertEqual(source, path)

    def test_first_cache_and_empty_selection_are_unchanged(self):
        payload, expected = cache_fixture()
        with TemporaryDirectory() as temporary:
            first = Path(temporary) / 'a/conversation_cache'
            second = Path(temporary) / 'b/conversation_cache'
            for path, value in [(first, payload), (second, {'data': []})]:
                path.parent.mkdir()
                path.write_text(json.dumps(value), encoding='utf-8')
            for paths, rows_expected in [([first, second, first], expected), ([second, first], [])]:
                context = SimpleNamespace(get_files_found=lambda paths=paths: paths)
                _, rows, source = PARSER.get_kleinanzeigenmessagecache.__wrapped__(context)
                self.assertEqual(rows, rows_expected)
                self.assertEqual(source, paths[0])


if __name__ == '__main__':
    unittest.main()
