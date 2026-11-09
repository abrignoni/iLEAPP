"""Pin the vendored LevelDB reader's handling of a damaged data block in a table (.ldb) file.

A data block that does not decompress is skipped and logged, and reading goes on with the next block
and the next file, where the reader used to raise and the caller got nothing more from the folder. The tables here are built
in the LevelDB table format (doc/table_format.md and table/table_builder.cc: data blocks, a metaindex and an index block, each with
a 5-byte trailer of compression type and masked crc32c, then the 48-byte footer).
"""
import pathlib
import struct
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.vendor.ccl import ccl_leveldb, ccl_simplesnappy  # pylint: disable=wrong-import-position

MAGIC = 0xdb4775248b80fb57


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


def _block(entries):
    """A block with every entry at its own restart point (no shared key prefix)."""
    body, restarts = bytearray(), []
    for key, value in entries:
        restarts.append(len(body))
        body += _varint(0) + _varint(len(key)) + _varint(len(value)) + key + value
    for offset in restarts:
        body += struct.pack('<I', offset)
    return bytes(body + struct.pack('<I', len(restarts)))


def _masked_crc(data):
    crc = ccl_simplesnappy.crc32c(data)
    return ((((crc >> 15) | (crc << 17)) & 0xffffffff) + 0xa282ead8) % 0x100000000


def _internal_key(user_key, sequence):
    return user_key + struct.pack('<Q', (sequence << 8) | 1)


def _snappy_literal(data):
    """`data` as a snappy stream of one literal (lengths up to 60)."""
    assert 0 < len(data) <= 60
    return _varint(len(data)) + bytes([(len(data) - 1) << 2]) + data


def _table(blocks):
    """A table file from (contents, compression type, damage) data blocks.

    damage True zero-fills the stored block; bytes replace it.
    """
    out, index = bytearray(), []
    for entries, compression, damaged in blocks:
        contents = _block(entries)
        stored = _snappy_literal(contents) if compression == 1 else contents
        trailer = bytes([compression]) + struct.pack('<I', _masked_crc(stored + bytes([compression])))
        if isinstance(damaged, bytes):
            stored = damaged
        elif damaged:
            stored = bytes(len(stored))
        index.append((entries[-1][0], _varint(len(out)) + _varint(len(stored))))
        out += stored + trailer

    def add(contents):
        offset = len(out)
        out.extend(contents + b'\x00' + struct.pack('<I', _masked_crc(contents + b'\x00')))
        return _varint(offset) + _varint(len(contents))

    meta_handle = add(_block([]))
    index_handle = add(_block(index))
    footer = meta_handle + index_handle
    out += footer + bytes(40 - len(footer)) + struct.pack('<Q', MAGIC)
    return bytes(out)


class TableDamageTest(unittest.TestCase):
    def _read(self, files):
        with tempfile.TemporaryDirectory() as tmp:
            for name, data in files.items():
                (pathlib.Path(tmp) / name).write_bytes(data)
            with ccl_leveldb.RawLevelDb(tmp) as db:
                records = [(r.user_key, r.seq) for r in db.iterate_records_raw()]
                damage = {reader.path.name: list(reader.damage) for reader in db._files}  # pylint: disable=protected-access
        return records, damage

    def test_an_undamaged_table_reads_whole_and_reports_no_damage(self):
        table = _table([([(_internal_key(b'a', 1), b'1')], 1, False),
                        ([(_internal_key(b'b', 2), b'2')], 0, False)])
        records, damage = self._read({'000005.ldb': table})
        self.assertEqual(records, [(b'a', 1), (b'b', 2)])
        self.assertEqual(damage, {'000005.ldb': []})

    def test_a_zero_filled_compressed_block_is_skipped_and_the_next_block_read(self):
        table = _table([([(_internal_key(b'lost', 1), b'x' * 20)], 1, True),
                        ([(_internal_key(b'kept', 2), b'2')], 0, False)])
        records, damage = self._read({'000005.ldb': table})
        self.assertEqual(records, [(b'kept', 2)])
        self.assertEqual(len(damage['000005.ldb']), 1)
        item = damage['000005.ldb'][0]
        self.assertEqual(item.offset, 0)
        self.assertIn('block checksum does not match', item.reason)

    def test_a_compressed_block_ending_after_a_tag_byte_is_skipped(self):
        # A literal tag of 0xf0 says one length byte follows; with the stream ending there,
        # ccl_simplesnappy raises TypeError rather than ValueError.
        table = _table([([(_internal_key(b'lost', 1), b'x' * 20)], 1, b'\x05\xf0'),
                        ([(_internal_key(b'kept', 2), b'2')], 0, False)])
        records, damage = self._read({'000005.ldb': table})
        self.assertEqual(records, [(b'kept', 2)])
        self.assertEqual(len(damage['000005.ldb']), 1)

    def test_files_after_a_damaged_table_are_still_read(self):
        damaged = _table([([(_internal_key(b'lost', 1), b'x' * 20)], 1, True)])
        later = _table([([(_internal_key(b'later', 3), b'3')], 0, False)])
        records, damage = self._read({'000005.ldb': damaged, '000007.ldb': later})
        self.assertEqual(records, [(b'later', 3)])
        self.assertEqual(len(damage['000005.ldb']), 1)
        self.assertEqual(damage['000007.ldb'], [])


if __name__ == '__main__':
    unittest.main()
