"""Pin the on-disk contract the MMKV reader depends on.

MMKV is append-only between rewrites, so the same key appears more than once and the last
entry is the live one. A reader that collapses to a dict without honouring that order
reports a stale value as current, which looks exactly like a correct answer. It also writes
a removal as a zero-length value rather than deleting the entry, so a naive reader turns a
removed key into an empty string.

The other trap is varint width. Lengths in these files are small, so a reader that caps the
varint walk at the five bytes a 32-bit value needs will pass every test written against
string keys and then silently mis-read a millisecond epoch, which needs six. That is what
happened here, and it surfaced as a timestamp column holding raw bytes.

Buffers are built by hand rather than taken from an extraction, so this test carries no
sample data.
"""
import pathlib
import struct
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.mmkv_parser import (  # pylint: disable=wrong-import-position
    MMKVError,
    decode_value,
    read_dict,
    read_entries,
)


def _varint(value):
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _string_value(text):
    encoded = text.encode('utf-8')
    return _varint(len(encoded)) + encoded


def _entry(key, container):
    encoded_key = key.encode('utf-8')
    return _varint(len(encoded_key)) + encoded_key + _varint(len(container)) + container


def _store(*entries):
    """An MMKV file is [u32 size][u32 crc][data][zero padding to the page size]."""
    data = b''.join(entries)
    return struct.pack('<II', len(data), 0) + data + b'\x00' * 64


class MMKVParserTest(unittest.TestCase):

    def _write(self, payload):
        handle = tempfile.NamedTemporaryFile(suffix='.mmkv', delete=False)
        handle.write(payload)
        handle.close()
        self.addCleanup(lambda: pathlib.Path(handle.name).unlink(missing_ok=True))
        return handle.name

    def test_reads_strings_and_scalars(self):
        path = self._write(_store(
            _entry('channel', _string_value('googleplay')),
            _entry('version', _varint(33)),
        ))
        self.assertEqual(read_dict(path), {'channel': 'googleplay', 'version': 33})

    def test_scalar_wider_than_32_bits_is_not_truncated(self):
        """A millisecond epoch needs six varint bytes; a five-byte cap returns raw bytes."""
        milliseconds = 1785482702086
        path = self._write(_store(_entry('ts', _varint(milliseconds))))
        self.assertEqual(read_dict(path), {'ts': milliseconds})

    def test_last_entry_for_a_key_wins_and_earlier_ones_remain_visible(self):
        path = self._write(_store(
            _entry('checked', _string_value('')),
            _entry('checked', _string_value('8.11.4')),
        ))
        self.assertEqual(
            read_entries(path),
            [('checked', _string_value('')), ('checked', _string_value('8.11.4'))])
        self.assertEqual(read_dict(path), {'checked': '8.11.4'})

    def test_zero_length_value_removes_the_key_rather_than_emptying_it(self):
        path = self._write(_store(
            _entry('token', _string_value('abc')),
            _entry('token', b''),
        ))
        self.assertEqual(len(read_entries(path)), 2)
        self.assertNotIn('token', read_dict(path))
        self.assertIsNone(decode_value(b''))

    def test_empty_string_is_kept_and_is_not_a_removal(self):
        path = self._write(_store(_entry('note', _string_value(''))))
        self.assertEqual(read_dict(path), {'note': ''})

    def test_only_the_recorded_data_region_is_read(self):
        """Bytes past the recorded size are stale or uninitialised, not live entries."""
        live = _entry('live', _string_value('yes'))
        stale = _entry('stale', _string_value('no'))
        payload = struct.pack('<II', len(live), 0) + live + stale
        self.assertEqual(read_dict(self._write(payload)), {'live': 'yes'})

    def test_truncated_walk_keeps_what_was_read(self):
        good = _entry('first', _string_value('kept'))
        payload = struct.pack('<II', len(good) + 4, 0) + good + b'\x7f\x7f\x7f\x7f'
        self.assertEqual(read_dict(self._write(payload)), {'first': 'kept'})

    def test_short_file_and_oversized_size_field_raise(self):
        with self.assertRaises(MMKVError):
            read_entries(self._write(b'\x00\x01'))
        with self.assertRaises(MMKVError):
            read_entries(self._write(struct.pack('<II', 4096, 0) + b'\x01'))

    def test_empty_store_reads_as_no_entries(self):
        self.assertEqual(read_entries(self._write(struct.pack('<II', 0, 0))), [])


if __name__ == '__main__':
    unittest.main()
