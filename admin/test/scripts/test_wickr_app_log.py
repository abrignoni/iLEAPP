"""Actual plaintext log regression cases for the retained Wickr projection."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.artifacts.wickr import wickr_app_log


class TestWickrAppLog(unittest.TestCase):
    def run_logs(self, records):
        with tempfile.TemporaryDirectory() as directory:
            files = []
            for index, raw in enumerate(records):
                path = Path(directory) / f'{index}.log'
                path.write_bytes(raw)
                files.append(str(path))
            context = SimpleNamespace(get_files_found=lambda: files)
            return wickr_app_log.__wrapped__(context)[1]

    @staticmethod
    def payload(value, omit=False):
        body = {'messageId': 'same', 'convoId': 'group', 'messageType': 4001}
        if not omit:
            body['userId'] = value
        return ('2024/01/02 03:04:05:123 Payload: ' + json.dumps(body) + '\n').encode()

    def test_decoded_values_and_missing_are_distinct(self):
        values = [0, False, True, None, '', -1, 1.25, ['x', 0], {'k': False}]
        rows = self.run_logs([b''.join(self.payload(v) for v in values) +
                              self.payload(None, omit=True)])
        self.assertEqual(len(rows), 10)
        for row, expected in zip(rows, values + ['']):
            self.assertEqual(type(row[4]), type(expected))
            self.assertEqual(row[4], expected)
            self.assertEqual(row[:4], ('2024/01/02 03:04:05', 'Notification Payload',
                                      'same', 'group'))
            self.assertEqual(row[5], 4001)

    def test_repeated_lines_and_equal_time_source_order(self):
        rows = self.run_logs([self.payload('first') * 2, self.payload('second')])
        self.assertEqual([row[4] for row in rows], ['first', 'first', 'second'])
        earlier = self.payload('earlier').replace(b'2024/01', b'2023/01')
        rows = self.run_logs([self.payload('later'), earlier])
        self.assertEqual([row[4] for row in rows], ['earlier', 'later'])

    def test_utf8_replacement_download_blank_and_json_skip(self):
        raw = self.payload('invalid-byte').replace(b'invalid-byte', b'bad\xff')
        raw += b'2024/01/02 03:04:05:0 Payload: {"messageId":"bad",}\n'
        raw += (b'2024/01/02 03:04:05:9 Download Message with Type: 004001, '
                b'ConvoID: nil, MsgID: same trailing text\n')
        rows = self.run_logs([raw])
        self.assertEqual(rows[0][4], 'bad\ufffd')
        self.assertEqual(rows[1], ('2024/01/02 03:04:05', 'Download Message',
                                   'same', '', '', '004001'))

    def test_successful_empty_source_and_caught_read_error(self):
        with tempfile.TemporaryDirectory() as directory:
            empty = Path(directory) / 'empty.log'
            empty.write_text('no matching event\n')
            missing = str(Path(directory) / 'missing.log')
            files = [str(empty), missing, str(empty)]
            with patch('scripts.artifacts.wickr.logfunc') as logger:
                _, rows, source = wickr_app_log.__wrapped__(
                    SimpleNamespace(get_files_found=lambda: files))
            self.assertEqual(rows, [])
            self.assertEqual(source, '\n'.join([str(empty), str(empty)]))
            logger.assert_called_once()
            self.assertIn('Error reading Wickr log', logger.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
