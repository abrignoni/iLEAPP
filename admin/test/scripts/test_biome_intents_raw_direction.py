"""Retain decoded plist direction values through actual protobuf and SEGB readers."""
from pathlib import Path
import datetime
import plistlib
import struct
import tempfile
from types import SimpleNamespace
import unittest
import zlib

from scripts.artifacts import biomeIntents


def varint(value):
    """Encode a positive protobuf length or tag."""
    out = bytearray()
    while value > 127:
        out.append((value & 127) | 128)
        value >>= 7
    return bytes(out) + bytes([value])


def field(number, value):
    """Encode one length-delimited protobuf field."""
    return varint(number * 8 + 2) + varint(len(value)) + value


def wire(flag, fmt, missing=False):
    """Use actual plist bytes in the actual outer/inner protobuf envelope."""
    value = {
        'intent': {'backingStore': {'bytes': b'\x0a\x01x'}},
        'dateInterval': {
            'NS.startDate': datetime.datetime(2024, 1, 2, 3, 4, 5),
            'NS.endDate': datetime.datetime(2024, 1, 2, 3, 5, 5),
            'NS.duration': 60.0,
        },
        '_donatedBySiri': False,
        'groupIdentifier': 'fixture-group',
    }
    if not missing:
        value['direction'] = flag
    payload = plistlib.dumps(value, fmt=fmt, sort_keys=False)
    return (field(2, b'fixture.unknown') + field(4, b'FixtureClass') + b'\x28\x07' +
            field(8, payload))


def stream(version, entries):
    """Declare SEGB offsets and states independently of the production reader."""
    offsets = []
    body = bytearray()
    if version == 1:
        for state, data in entries:
            offsets.append(56 + len(body) + 32)
            body += struct.pack('<iiddIi', len(data), state, 1000, 1001,
                                zlib.crc32(data), 0) + data
            body += bytes(-(56 + len(body)) % 8)
        return struct.pack('<I', 56 + len(body)) + bytes(48) + b'SEGB' + body, offsets
    trailer = []
    for state, data in entries:
        offsets.append(32 + len(body))
        body += struct.pack('<Ii', zlib.crc32(data), 0) + data
        trailer.append((len(body), state))
        body += bytes(-len(body) % 4)
    header = struct.pack('<4sid16s', b'SEGB', len(entries), 1000, bytes(16))
    tail = b''.join(struct.pack('<iid', end, state, 1000) for end, state in trailer)
    return header + body + tail, offsets


class RawDirectionTest(unittest.TestCase):
    """Native field types must survive the former equality-based enum mapping."""

    def test_actual_plists_and_both_segb_versions(self):
        values = [0, 1, 2, -1, 5, False, True, 0.0, 1.0, 2.0, 1.5, '', '0',
                  'unknown', '雪', b'\x00\xff', [0, True, 'x'], {'a': 0, 'b': False}]
        for version in [1, 2]:
            for fmt in [getattr(plistlib, 'FMT_XML'), getattr(plistlib, 'FMT_BINARY')]:
                entries = [(1, wire(v, fmt)) for v in values]
                entries += [(1, wire(None, fmt, missing=True)), (3, wire(2, fmt))]
                entries.append(entries[0])
                content, offsets = stream(version, entries)
                with tempfile.TemporaryDirectory() as folder:
                    root = Path(folder)
                    path = root / 'record'
                    path.write_bytes(content)
                    ctx = SimpleNamespace(get_files_found=lambda value=path: [str(value)],
                                          get_relative_path=lambda p: Path(p).name)
                    headers, (rows, html), source = biomeIntents.get_biomeIntents.__wrapped__(ctx)
                    expected = values + [None, values[0]]
                    self.assertEqual(headers[7], 'direction (as stored)')
                    self.assertEqual(len(headers), 12)
                    self.assertEqual([(type(r[7]), r[7]) for r in rows],
                                     [(type(v), v) for v in expected])
                    self.assertEqual([r[7] for r in html], expected)
                    self.assertEqual([r[11] for r in rows], offsets[:-2] + offsets[-1:])
                    self.assertEqual(source, str(root))
                    stamp = datetime.datetime(2024, 1, 2, 3, 4, 5,
                                              tzinfo=datetime.timezone.utc)
                    self.assertEqual([r[:7] for r in rows],
                                     [(stamp, stamp + datetime.timedelta(seconds=60),
                                       60.0, 'False', 'fixture.unknown', 'FixtureClass', 7)]
                                     * len(rows))
                    self.assertEqual([r[8:11] for r in rows],
                                     [('fixture-group', '', 'record')] * len(rows))
                    self.assertEqual([r[9] for r in html], ['Unsupported intent.'] * len(rows))

    def test_existing_admission_and_repeated_context(self):
        content, _ = stream(1, [(1, wire(False, getattr(plistlib, 'FMT_XML')))])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paths = [root/'record', root/'.hidden', root/'tombstone'/'record']
            for path in paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            ctx = SimpleNamespace(get_files_found=lambda: [str(paths[0])] * 2 +
                                  [str(p) for p in paths[1:]] + [str(root)],
                                  get_relative_path=lambda p: str(Path(p).relative_to(root)))
            _, (rows, html), source = biomeIntents.get_biomeIntents.__wrapped__(ctx)
            self.assertEqual([r[7] for r in rows], [False, False])
            self.assertEqual([r[7] for r in html], [False, False])
            self.assertEqual(source, str(root))


if __name__ == '__main__':
    unittest.main()
