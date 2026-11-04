"""Pin the vendored LevelDB reader's handling of a damaged .log file.

ccl_chromium_reader a321210 and 6e5dbe5 resume at the next 32 KiB block after a block
that cannot be read, where the earlier reader stopped. The log here is built in the
LevelDB log format (7-byte record header: crc32c, length, type; 32 KiB blocks), with
a zero-filled block between whole records, and with a record cut off by one.
"""
import pathlib
import struct
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.vendor.ccl import ccl_leveldb  # pylint: disable=wrong-import-position

BLOCK = 32768


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


def _batch(sequence, key, value):
    return (struct.pack('<QI', sequence, 1) + b'\x01' + _varint(len(key)) + key
            + _varint(len(value)) + value)


def _block(payload):
    record = struct.pack('<IHB', 0, len(payload), 1) + payload  # FULL record; the reader does not check the CRC
    return record + bytes(BLOCK - len(record))


class LogDamageTest(unittest.TestCase):
    def _read(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            (pathlib.Path(tmp) / '000003.log').write_bytes(data)
            with ccl_leveldb.RawLevelDb(tmp) as db:
                records = [(r.user_key, r.seq) for r in db.iterate_records_raw()]
                damage = [item for reader in db._files for item in reader.damage]  # pylint: disable=protected-access
        return records, damage

    def test_reading_resumes_after_a_zero_filled_block(self):
        # As in leveldb, zero-filled space between whole records is skipped, not reported.
        records, damage = self._read(_block(_batch(1, b'before', b'1')) + bytes(BLOCK)
                                     + _block(_batch(2, b'after', b'2')))
        self.assertEqual(records, [(b'before', 1), (b'after', 2)])
        self.assertEqual(damage, [])

    def test_a_record_cut_by_zero_filled_space_is_reported(self):
        first = _batch(1, b'before', b'1')
        head = struct.pack('<IHB', 0, len(first), 1) + first
        # A FIRST fragment (type 2) fills the rest of block 0; its continuation in block 1 is zeros.
        room = BLOCK - len(head) - 7
        cut = struct.pack('<IHB', 0, room, 2) + bytes(room)
        records, damage = self._read(head + cut + bytes(BLOCK) + _block(_batch(3, b'after', b'3')))
        self.assertEqual(records, [(b'before', 1), (b'after', 3)])
        self.assertEqual(len(damage), 1)
        self.assertLess(damage[0].offset, BLOCK)


if __name__ == '__main__':
    unittest.main()
