"""Actual SEGB files cover structural retention without decoding Deleted payloads."""
import datetime
import pathlib
import os
import struct
import tempfile
import unittest
import zlib
from types import SimpleNamespace
from unittest.mock import patch

from scripts.artifacts import biomeNetworkingEdgeSelection as artifact

EPOCH = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
# Each string's protobuf length is explicit; no production encoder builds fixtures.
PAYLOAD = b'\x0a\x09192.0.2.0\x10\x04\x18\x18\x22\x03en0\x2a\x03LTE\x3a\x02US\x42\x03UTC'
VALUES = ('192.0.2.0', '4', '24', 'en0', 'LTE', '', 'US', 'UTC')


def binary(version, entries):
    """Return complete binary plus an independent state/time/offset/payload oracle.

    entries are (state, Cocoa seconds, bytes or None). None reuses the v2
    previous data area with a separate trailer entry, preserving repeated states.
    """
    oracle = []
    if version == 1:
        data = bytearray(56)
        data[52:56] = b'SEGB'
        for state, seconds, payload in entries:
            data += struct.pack('<iiddIi', len(payload), state, seconds, seconds + 2,
                                zlib.crc32(payload), 0)
            offset = len(data)
            data += payload
            data += b'\0' * (-len(data) % 8)
            oracle.append((state, seconds, offset, payload))
        data[:4] = struct.pack('<I', len(data))
    else:
        data = bytearray(struct.pack('<4sid16s', b'SEGB', len(entries), 0, b'\0' * 16))
        trailer = bytearray()
        previous = {}
        for state, seconds, payload in entries:
            if payload is None:
                assert previous
                end = previous['end']
                offset = previous['offset']
                payload = previous['payload']
            elif state in (0, 4):
                end, offset = 0, 0
            else:
                offset = len(data)
                data += struct.pack('<Ii', zlib.crc32(payload), 0) + payload
                end = len(data) - 32
                data += b'\0' * (-end % 4)
                previous = {'end': end, 'offset': offset, 'payload': payload}
            trailer += struct.pack('<2id', end, state, seconds)
            if state not in (0, 4):
                oracle.append((state, seconds, offset, payload))
        data += trailer
    return bytes(data), oracle


def context(files, root):
    return SimpleNamespace(get_files_found=lambda: list(map(str, files)),
                           get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))


class NetworkingEdgeDeletedTests(unittest.TestCase):
    def run_file(self, version, entries):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            p = root / 'segment'
            data, expected = binary(version, entries)
            p.write_bytes(data)
            with patch.object(artifact.blackboxprotobuf, 'decode_message',
                              wraps=artifact.blackboxprotobuf.decode_message) as decode:
                headers, rows, source = artifact.get_biomeNetworkingEdgeSelection.__wrapped__(
                    context([p], root))
            expected = [r for r in expected if r[0] in (1, 3)]
            self.assertEqual(len(rows), len(expected))
            self.assertEqual(len(headers), 12)
            self.assertEqual(source, str(root))
            self.assertEqual(decode.call_count, sum(r[0] == 1 for r in expected))
            for row, (state, seconds, offset, _) in zip(rows, expected):
                self.assertEqual(row, (EPOCH + datetime.timedelta(seconds=seconds),
                                      'Written' if state == 1 else 'Deleted',
                                      *(VALUES if state == 1 else (None,) * 8),
                                      p.name, offset))

    def test_v1_interleaved_repeats_unknown(self):
        self.run_file(1, [(1, 800000000, PAYLOAD), (3, 800000001, b'\xff'),
                          (4, 800000002, b'unknown'), (1, 800000000, PAYLOAD),
                          (3, 800000003, b'')])

    def test_v2_shared_end_offsets_and_reader_excluded(self):
        self.run_file(2, [(1, 800000000, PAYLOAD), (3, 800000001, None),
                          (3, 800000002, None), (0, 0, b''), (4, 0, b''),
                          (1, 800000000, PAYLOAD), (3, 800000003, b'\xff')])

    def test_v2_stale_trailer_stays_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            raw, oracle = binary(2, [(1, 800000000, PAYLOAD)])
            data = bytearray(raw)
            data[4:8] = struct.pack('<i', 2)
            data += struct.pack('<2id', 0, 3, 800000001)
            p = root / 'segment'
            p.write_bytes(data)
            _, rows, _ = artifact.get_biomeNetworkingEdgeSelection.__wrapped__(
                context([p], root))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][1], 'Written')
            self.assertEqual(rows[0][11], oracle[0][2])

    def test_same_physical_file_aliases_are_not_collapsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            first, second = root / 'first' / 'segment', root / 'alias' / 'segment'
            first.parent.mkdir()
            second.parent.mkdir()
            first.write_bytes(binary(1, [(3, 800000001, b'\xff')])[0])
            os.link(first, second)
            h, rows, _ = artifact.get_biomeNetworkingEdgeSelection.__wrapped__(
                context([first, second, first], root))
            self.assertEqual(h[-1], 'Source File')
            self.assertEqual([r[-1] for r in rows],
                             ['first/segment', 'alias/segment', 'first/segment'])
            self.assertEqual(rows[0][:-1], rows[1][:-1])

    def test_deleted_only_and_empty_both_formats(self):
        for version in (1, 2):
            self.run_file(version, [(3, 800000001, b'\xff')])
            self.run_file(version, [])

    def test_conditional_sources_and_multiplicity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            paths = [root / 'first' / 'segment', root / 'second' / 'segment',
                     root / 'other' / 'different', root / 'zero' / 'segment']
            for p in paths:
                p.parent.mkdir()
                p.write_bytes(binary(1, [] if p.parent.name == 'zero'
                                     else [(3, 800000001, b'\xff')])[0])
            h, rows, _ = artifact.get_biomeNetworkingEdgeSelection.__wrapped__(
                context([paths[0], paths[0], paths[2], paths[3]], root))
            self.assertEqual(len(h), 12)
            self.assertEqual(len(rows), 3)
            h, rows, _ = artifact.get_biomeNetworkingEdgeSelection.__wrapped__(
                context([paths[0], paths[1], paths[0], paths[2], paths[3]], root))
            self.assertEqual(h[-1], 'Source File')
            self.assertEqual([r[-1] for r in rows], ['first/segment', 'second/segment',
                                                   'first/segment', 'other/different'])

    def test_filters_and_caught_written_decode_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            paths = [root / 'good', root / '.dot', root / 'tombstone' / 'segment']
            for p in paths:
                p.parent.mkdir(exist_ok=True)
                p.write_bytes(binary(1, [(1, 800000000, b'\xff'),
                                         (3, 800000001, b'\xff')])[0])
            with patch.object(artifact, 'logfunc') as log:
                _, rows, _ = artifact.get_biomeNetworkingEdgeSelection.__wrapped__(
                    context(paths + [root, root / 'absent'], root))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][1], 'Deleted')
            self.assertEqual(log.call_count, 1)


if __name__ == '__main__':
    unittest.main()
