"""Pin the on-disk contract the SNSS reader depends on.

A Chromium tab restore file is "SNSS", an int32 version, then records of a uint16 size followed
by that many bytes whose first byte is the command id. Command 1 carries a base::Pickle holding
a tab id and a SerializedNavigationEntry; command 4 is a fixed 16 byte struct, not a pickle, and
a reader that treats it as one reads nonsense.

The trap this file exists for is alignment. A base::Pickle advances every field to a four byte
boundary, so a three byte string is followed by one pad byte. A reader that skips exactly the
string length works on any string whose length happens to be a multiple of four and silently
walks off the rails on every other one, which looks like a corrupt file rather than a bug.

The expected bytes below are written out as literals rather than produced by the reader, so the
test cannot inherit the reader's own idea of the layout.

Buffers are built by hand rather than taken from an extraction, so this test carries no sample
data.
"""
import pathlib
import struct
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.snss_parser import (  # pylint: disable=wrong-import-position
    SNSSError,
    decode_navigation_entry,
    decode_selected_navigation,
    read_commands,
    read_navigation_entries,
    read_selected_navigations,
)


def _pad(payload):
    return payload + b'\x00' * ((4 - len(payload) % 4) % 4)


def _p_int(value):
    return struct.pack('<i', value)


def _p_int64(value):
    return struct.pack('<q', value)


def _p_string(text):
    raw = text.encode('utf-8')
    return _p_int(len(raw)) + _pad(raw)


def _p_string16(text):
    raw = text.encode('utf-16-le')
    return _p_int(len(raw) // 2) + _pad(raw)


def _pickle(body):
    return struct.pack('<I', len(body)) + body


def _navigation(tab_id=7, index=2, url='https://example.test/a', title='Example',
                page_state=b'ps', transition=8, type_mask=0, referrer='https://ref.test/',
                original='https://orig.test/', overriding_ua=0, timestamp=13300000000000000,
                http=200, referrer_policy=1, extended=(), tail=True):
    body = _p_int(tab_id) + _p_int(index) + _p_string(url) + _p_string16(title)
    body += _p_int(len(page_state)) + _pad(page_state)
    body += _p_int(transition) + _p_int(type_mask) + _p_string(referrer) + _p_int(0)
    body += _p_string(original) + _p_int(overriding_ua) + _p_int64(timestamp)
    body += _p_string16('') + _p_int(http) + _p_int(referrer_policy)
    body += _p_int(len(extended))
    for key, value in extended:
        body += _p_string(key) + _p_string(value)
    if tail:
        body += _p_int64(0) + _p_int64(0) + _p_int64(0) + _p_int(0)
    return _pickle(body)


def _file(*commands, version=3, magic=b'SNSS'):
    out = magic + struct.pack('<i', version)
    for command_id, payload in commands:
        body = bytes([command_id]) + payload
        out += struct.pack('<H', len(body)) + body
    return out


class SNSSParserTest(unittest.TestCase):

    def _write(self, payload):
        handle = tempfile.NamedTemporaryFile(suffix='.snss', delete=False)
        handle.write(payload)
        handle.close()
        self.addCleanup(lambda: pathlib.Path(handle.name).unlink(missing_ok=True))
        return handle.name

    def test_header_and_command_framing(self):
        path = self._write(_file((1, _navigation()), (4, struct.pack('<iiq', 7, 2, 13300000000000001))))
        ids = [command_id for command_id, _ in read_commands(path)]
        self.assertEqual(ids, [1, 4])

    def test_rejects_a_file_that_is_not_snss(self):
        with self.assertRaises(SNSSError):
            list(read_commands(self._write(b'NOPE' + struct.pack('<i', 3))))
        with self.assertRaises(SNSSError):
            list(read_commands(self._write(_file(version=9))))

    def test_navigation_entry_decodes_and_consumes_the_pickle_exactly(self):
        entry = decode_navigation_entry(_navigation())
        self.assertEqual(entry['tab_id'], 7)
        self.assertEqual(entry['index'], 2)
        self.assertEqual(entry['url'], 'https://example.test/a')
        self.assertEqual(entry['title'], 'Example')
        self.assertEqual(entry['transition_type'], 8)
        self.assertEqual(entry['referrer_url'], 'https://ref.test/')
        self.assertEqual(entry['original_request_url'], 'https://orig.test/')
        self.assertEqual(entry['timestamp'], 13300000000000000)
        self.assertEqual(entry['http_status_code'], 200)
        self.assertEqual(entry['unread'], 0)

    def test_string_lengths_that_are_not_a_multiple_of_four_still_align(self):
        """A three byte string is followed by one pad byte; a reader that skips only the length
        reads the next field from the wrong offset."""
        for url in ('https://a.test/1', 'https://a.test/12', 'https://a.test/123',
                    'https://a.test/1234'):
            entry = decode_navigation_entry(_navigation(url=url, title='t' * (len(url) % 4)))
            self.assertEqual(entry['url'], url, msg=f'url length {len(url)}')
            self.assertEqual(entry['http_status_code'], 200, msg=f'url length {len(url)}')
            self.assertEqual(entry['unread'], 0, msg=f'url length {len(url)}')

    def test_extended_info_pairs_are_read(self):
        entry = decode_navigation_entry(_navigation(extended=(('k1', 'v1'), ('k2', 'v2'))))
        self.assertEqual(entry['extended_info'], {'k1': 'v1', 'k2': 'v2'})
        self.assertEqual(entry['unread'], 0)

    def test_a_payload_that_stops_after_the_type_mask_keeps_what_was_read(self):
        """Chromium treats every field after the type mask as optional, so a short record is not
        an error and the fields before it still count."""
        body = _p_int(9) + _p_int(0) + _p_string('https://short.test/') + _p_string16('Short')
        body += _p_int(0) + _p_int(8)
        entry = decode_navigation_entry(_pickle(body))
        self.assertEqual(entry['url'], 'https://short.test/')
        self.assertEqual(entry['title'], 'Short')
        self.assertEqual(entry['transition_type'], 8)
        self.assertIsNone(entry['http_status_code'])

    def test_selected_navigation_is_a_struct_not_a_pickle(self):
        record = decode_selected_navigation(struct.pack('<iiq', 1068719225, 6, 13411502943000000))
        self.assertEqual(record, {'tab_id': 1068719225, 'index': 6,
                                  'timestamp': 13411502943000000})
        with self.assertRaises(SNSSError):
            decode_selected_navigation(b'\x00' * 8)

    def test_reader_helpers_select_the_right_commands(self):
        path = self._write(_file(
            (1, _navigation(tab_id=7, index=0, url='https://one.test/')),
            (11, b'\x00\x00\x00\x00'),
            (1, _navigation(tab_id=7, index=1, url='https://two.test/')),
            (4, struct.pack('<iiq', 7, 1, 13300000000000002)),
        ))
        self.assertEqual([e['url'] for e in read_navigation_entries(path)],
                         ['https://one.test/', 'https://two.test/'])
        self.assertEqual([r['index'] for r in read_selected_navigations(path)], [1])

    def test_a_truncated_trailing_command_is_dropped_rather_than_guessed(self):
        good = _file((1, _navigation(url='https://kept.test/')))
        path = self._write(good + struct.pack('<H', 400) + b'\x01\x02\x03')
        self.assertEqual([e['url'] for e in read_navigation_entries(path)], ['https://kept.test/'])


if __name__ == '__main__':
    unittest.main()
