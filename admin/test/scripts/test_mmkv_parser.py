"""Pin the on-disk contract the MMKV reader depends on.

An MMKV file is [u32 actual_size][data region]. The data region opens with a varint holding
the size of the items that follow, then the entries laid end to end, then zero padding to the
page size. actual_size covers the varint and the entries. A real store writes that varint as
a fixed 4-byte placeholder on the append path (ff ff ff 07, reserved by Tencent as
ItemSizeHolder) and as a compact 1-to-3 byte varint on a full rewrite, so a reader that
assumes a fixed width starts the first key at the wrong offset and reads zero entries. Both
widths are exercised below.

MMKV is append-only between rewrites, so the same key appears more than once and the last
entry is the live one. A reader that collapses to a dict without honouring that order reports
a stale value as current, which looks exactly like a correct answer. It also writes a removal
as a zero-length value rather than deleting the entry, so a naive reader turns a removed key
into an empty string.

The other trap is varint width. Lengths in these files are small, so a reader that caps the
varint walk at the five bytes a 32-bit value needs will pass every test written against string
keys and then silently mis-read a millisecond epoch, which needs six.

The encryption tell lives in the sibling .crc meta file: a non-zero AES vector at bytes 12 to
28 means the data region is ciphertext, and a reader that walks it anyway returns garbage keys.

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

# The append-mode placeholder MMKV reserves for the items-size field: a 4-byte varint for
# 0x00ffffff. Written out here as a literal, not derived from the reader, so the test cannot
# inherit the reader's own idea of the layout.
_APPEND_HOLDER = b'\xff\xff\xff\x07'


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


def _store(*entries, holder=None):
    """A real MMKV file: [u32 actual_size][items-size varint][entries][zero padding].

    actual_size covers the varint and the entries. `holder` overrides the items-size varint so
    a test can use the 4-byte append placeholder; by default it is the compact varint a full
    rewrite would write.
    """
    data = b''.join(entries)
    items = holder if holder is not None else _varint(len(data))
    region = items + data
    return struct.pack('<I', len(region)) + region + b'\x00' * 64


class MMKVParserTest(unittest.TestCase):

    def _write(self, payload, crc=None):
        handle = tempfile.NamedTemporaryFile(suffix='.mmkv', delete=False)
        handle.write(payload)
        handle.close()
        self.addCleanup(lambda: pathlib.Path(handle.name).unlink(missing_ok=True))
        if crc is not None:
            meta = handle.name + '.crc'
            pathlib.Path(meta).write_bytes(crc)
            self.addCleanup(lambda: pathlib.Path(meta).unlink(missing_ok=True))
        return handle.name

    def test_reads_strings_and_scalars(self):
        path = self._write(_store(
            _entry('channel', _string_value('googleplay')),
            _entry('version', _varint(33)),
        ))
        self.assertEqual(read_dict(path), {'channel': 'googleplay', 'version': 33})

    def test_first_key_follows_the_items_size_varint_at_every_width(self):
        """The items-size varint is 1 to 4 bytes on disk; the first key follows it, not a
        fixed offset. A store whose varint is shorter than four bytes read as empty before."""
        entries = (_entry('alpha', _string_value('one')), _entry('beta', _string_value('two')))
        for holder in (_APPEND_HOLDER,        # 4-byte append placeholder
                       _varint(2 ** 20),       # 3-byte
                       _varint(2 ** 12),       # 2-byte
                       _varint(3)):            # 1-byte
            path = self._write(_store(*entries, holder=holder))
            self.assertEqual(read_dict(path), {'alpha': 'one', 'beta': 'two'},
                             msg=f'holder width {len(holder)}')

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
        region = _varint(len(live)) + live
        payload = struct.pack('<I', len(region)) + region + stale
        self.assertEqual(read_dict(self._write(payload)), {'live': 'yes'})

    def test_truncated_walk_keeps_what_was_read(self):
        good = _entry('first', _string_value('kept'))
        region = _varint(len(good)) + good + b'\x7f\x7f\x7f\x7f'
        payload = struct.pack('<I', len(region)) + region
        self.assertEqual(read_dict(self._write(payload)), {'first': 'kept'})

    def test_short_file_and_oversized_size_field_raise(self):
        with self.assertRaises(MMKVError):
            read_entries(self._write(b'\x00\x01'))
        with self.assertRaises(MMKVError):
            read_entries(self._write(struct.pack('<I', 4096) + b'\x01'))

    def test_empty_store_reads_as_no_entries(self):
        self.assertEqual(read_entries(self._write(struct.pack('<I', 0))), [])

    def test_encrypted_store_is_refused_rather_than_returning_garbage(self):
        """A non-zero AES vector in the .crc meta file means the region is ciphertext."""
        payload = _store(_entry('a', _string_value('b')))
        meta = bytearray(32)
        meta[12:28] = bytes(range(1, 17))               # crc, version, sequence, then a vector
        with self.assertRaises(MMKVError):
            read_entries(self._write(payload, crc=bytes(meta)))

    def test_zero_vector_meta_is_not_treated_as_encryption(self):
        payload = _store(_entry('a', _string_value('b')))
        self.assertEqual(read_dict(self._write(payload, crc=bytes(32))), {'a': 'b'})


if __name__ == '__main__':
    unittest.main()
