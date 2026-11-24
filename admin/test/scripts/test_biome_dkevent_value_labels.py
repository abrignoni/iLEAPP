"""Each _DKEvent stream artifact that labels its value does so through a real SEGB file.

Real SEGB v2 files go through the real reader and decoder for every entry point in
biomeDKEventStreams. The three labelled ones must label each mapped integer, leave an
unmapped or missing value empty with the stored integer kept in Value (raw), and give a
Deleted record no value. The others must never fill Value.
"""
import tempfile
import unittest
import zlib
import struct
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import biomeDKEventStreams as parser

LABELLED = {
    'get_biomeDKDeviceIsLockedImputed': {0: 'Unlocked', 1: 'Locked'},
    'get_biomeDKDeviceLowPowerMode': {0: 'Off', 1: 'On'},
    'get_biomeDKDisplayOrientation': {0: 'Portrait', 1: 'Landscape', 2: 'Unknown'},
}
UNLABELLED = ['get_biomeDKAudioInputRoute', 'get_biomeDKAudioOutputRoute', 'get_biomeDKClockAlarm',
              'get_biomeDKSettingsDoNotDisturb', 'get_biomeDKSiriUi']
UNMAPPED = 7
WRITTEN, DELETED = 1, 3


def varint(value):
    out = bytearray()
    while value > 127:
        out.append((value & 127) | 128)
        value >>= 7
    out.append(value)
    return bytes(out)


def length_delimited(field, payload):
    return bytes([(field << 3) | 2]) + varint(len(payload)) + payload


def record(value):
    """Stream name (1.1), start and end dates (2, 3), integer value (4.4) unless None, identifier (5)."""
    inner = b'' if value is None else b'\x20' + varint(value)
    return (length_delimited(1, length_delimited(1, b'/stream'))
            + b'\x11' + struct.pack('<d', 900) + b'\x19' + struct.pack('<d', 1100)
            + length_delimited(4, inner) + length_delimited(5, b'ID'))


def segb_v2(entries):
    """Reader-format SEGB version 2 file from (payload, state) pairs."""
    body = bytearray()
    ends = []
    for payload, state in entries:
        body += struct.pack('<Ii', zlib.crc32(payload), 0) + payload
        ends.append((len(body), state))
        body += bytes(-len(body) % 4)
    trailer = b''.join(struct.pack('<iid', end, state, 1000) for end, state in ends)
    return struct.pack('<4sid16s', b'SEGB', len(ends), 1000, bytes(16)) + body + trailer


class DKEventValueLabelTest(unittest.TestCase):
    def run_entry(self, name, entries):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stream = root / 'Biome/streams/restricted/_DKEvent.Test/local/record'
            stream.parent.mkdir(parents=True)
            stream.write_bytes(segb_v2(entries))
            context = SimpleNamespace(get_files_found=lambda: [str(stream)],
                                      get_relative_path=lambda p: str(Path(p).relative_to(root)))
            headers, rows, _ = getattr(parser, name).__wrapped__(context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        value, raw, state = names.index('Value'), names.index('Value (raw)'), names.index('SEGB State')
        return [(row[state], row[value], row[raw]) for row in rows]

    def test_labelled_entry_points(self):
        for name, labels in LABELLED.items():
            stored = sorted(labels) + [UNMAPPED, None]
            entries = [(record(v), WRITTEN) for v in stored] + [(record(0), DELETED)]
            expected = ([('Written', labels[v], v) for v in sorted(labels)]
                        + [('Written', '', UNMAPPED), ('Written', '', ''), ('Deleted', None, None)])
            with self.subTest(entry=name):
                self.assertEqual(self.run_entry(name, entries), expected)

    def test_unlabelled_entry_points_leave_value_empty(self):
        entries = [(record(v), WRITTEN) for v in (0, 1, 2, UNMAPPED)]
        for name in UNLABELLED:
            with self.subTest(entry=name):
                rows = self.run_entry(name, entries)
                self.assertEqual([row[1] for row in rows], [''] * 4)
                self.assertEqual([row[2] for row in rows], [0, 1, 2, UNMAPPED])

    def test_every_entry_point_is_covered(self):
        entry_points = {n for n in dir(parser) if n.startswith('get_biomeDK')}
        self.assertEqual(entry_points, set(LABELLED) | set(UNLABELLED))


if __name__ == '__main__':
    unittest.main()
