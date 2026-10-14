"""Actual SEGB and protobuf fixtures retain decoded keybag field 4.4."""
import datetime
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from scripts.artifacts import biomeDKKeybag as parser

ANCHOR = 'Biome/streams/restricted/_DKEvent.Keybag.IsLocked/local'
VALUES = [0, 1, -1, 2, 987654, [0, 2, 1], 2]


def varint(value):
    """Encode independently declared signed int64 as protobuf varint."""
    value &= (1 << 64) - 1
    out = bytearray()
    while value > 127:
        out.append((value & 127) | 128)
        value >>= 7
    out.append(value)
    return bytes(out)


def wire(value):
    """Fixed start/end doubles, then nested int field 4.4, with repeats."""
    values = value if isinstance(value, list) else [value]
    nested = b''.join(b'\x20' + varint(v) for v in values)
    return b'\x11' + struct.pack('<d', 900) + b'\x19' + struct.pack('<d', 1100) + b'\x22' + varint(len(nested)) + nested


def segb_fixture(version, payloads=None):
    """Reader-format fixtures, not an independent vendor SDK writer."""
    payloads = [wire(v) for v in VALUES] if payloads is None else payloads
    observations = [(p, 1) for p in payloads] + [(payloads[0], 3)]
    if version == 1:
        body = bytearray()
        for payload, state in observations:
            body += struct.pack('<iiddIi', len(payload), state, 1000, 1001,
                                zlib.crc32(payload), 0) + payload
            body += bytes(-(56 + len(body)) % 8)
        return struct.pack('<I', 56 + len(body)) + bytes(48) + b'SEGB' + body
    body = bytearray()
    ends = []
    for payload, state in observations:
        body += struct.pack('<Ii', zlib.crc32(payload), 0) + payload
        ends.append((len(body), state))
        body += bytes(-len(body) % 4)
    trailer = b''.join(struct.pack('<iid', end, state, 1000) for end, state in ends)
    return struct.pack('<4sid16s', b'SEGB', len(ends), 1000, bytes(16)) + body + trailer


def context(root, files):
    """Real on-disk input files with evidence-relative source paths."""
    return SimpleNamespace(get_files_found=lambda: list(map(str, files)),
                           get_relative_path=lambda p: str(Path(p).relative_to(root)))


class KeybagRawValueTest(unittest.TestCase):
    def test_actual_versions_types_repeats_and_deleted_omission(self):
        epoch = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
        expected = [(epoch + datetime.timedelta(seconds=1000),
                     epoch + datetime.timedelta(seconds=900),
                     epoch + datetime.timedelta(seconds=1100), value, 'record') for value in VALUES]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for version in [1, 2]:
                with self.subTest(version=version):
                    main = root / str(version) / ANCHOR / 'record'
                    main.parent.mkdir(parents=True)
                    main.write_bytes(segb_fixture(version))
                    headers, rows, source = parser.get_biomeDKKeybag.__wrapped__(context(root, [main]))
                    self.assertEqual(len(headers), 5)
                    self.assertEqual(rows, expected)
                    self.assertEqual([type(row[3]) for row in rows], [type(v) for v in VALUES])
                    self.assertEqual(source, str(main.parent))
                    repeated = parser.get_biomeDKKeybag.__wrapped__(context(root, [main, main]))
                    self.assertEqual(repeated[1], expected + expected)
                    self.assertEqual(repeated[2], source)
                    hidden = main.with_name('.hidden')
                    hidden.write_bytes(main.read_bytes())
                    tombstone = main.parent / 'tombstone/record'
                    tombstone.parent.mkdir()
                    tombstone.write_bytes(main.read_bytes())
                    self.assertEqual(parser.get_biomeDKKeybag.__wrapped__(context(root, [hidden, tombstone]))[1:], ([], ''))

    def test_missing_and_wrong_type_keep_existing_skip(self):
        good = wire(2)
        missing = b'\x11' + struct.pack('<d', 900) + b'\x19' + struct.pack('<d', 1100) + b'\x22\x00'
        wrong = missing[:-2] + b'\x22\x03\x22\x01x'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / ANCHOR / 'record'
            path.parent.mkdir(parents=True)
            path.write_bytes(segb_fixture(1, [missing, wrong, good]))
            with patch.object(parser, 'logfunc') as log:
                rows = parser.get_biomeDKKeybag.__wrapped__(context(root, [path]))[1]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][3], 2)
            self.assertEqual(log.call_count, 2)
            self.assertTrue(all('Skipping biomeDKKeybag record' in str(call) for call in log.call_args_list))


if __name__ == '__main__':
    unittest.main()
