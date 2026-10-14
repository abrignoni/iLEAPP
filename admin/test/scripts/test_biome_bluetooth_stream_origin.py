"""Use actual SEGB records to check evidence-folder origin and staging invariance."""
import datetime
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import biomeBluetooth


ANCHOR = 'Biome/streams/restricted/Device.Wireless.Bluetooth'
MAC = b'AA:BB:CC:DD:EE:FF'
NAME = b'fixture speaker'
WIRE = b'\x0a' + bytes([len(MAC)]) + MAC + b'\x12' + bytes([len(NAME)]) + NAME


def segb_fixture(version):
    """Return reader-format bytes and independently declared written/deleted offsets."""
    if version == 1:
        body = bytearray()
        offsets = []
        for state in [1, 3, 1]:
            offsets.append(56 + len(body) + 32)
            body += struct.pack('<iiddIi', len(WIRE), state, 1000, 1001,
                                zlib.crc32(WIRE), 0) + WIRE
            body += bytes(-(56 + len(body)) % 8)
        header = struct.pack('<I', 56 + len(body)) + bytes(48) + b'SEGB'
        return header + body, offsets
    entry = struct.pack('<Ii', zlib.crc32(WIRE), 0) + WIRE
    end = len(entry)
    aligned = entry + bytes(-len(entry) % 4)
    body = aligned + entry
    second_end = len(body)
    body += bytes(-len(body) % 4)
    trailer = b''.join(struct.pack('<iid', offset, state, 1000)
                       for offset, state in [(end, 1), (end, 3), (second_end, 1)])
    return struct.pack('<4sid16s', b'SEGB', 3, 1000, bytes(16)) + body + trailer, [
        32, 32, 32 + len(aligned)]


def context(files, relative):
    return SimpleNamespace(get_files_found=lambda: files, get_relative_path=relative)


class TestBluetoothStreamOrigin(unittest.TestCase):
    def test_actual_versions_and_staging_invariance(self):
        stamp = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
        stamp += datetime.timedelta(seconds=1000)
        for version in [1, 2]:
            content, offsets = segb_fixture(version)
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for staging in ['neutral', 'remote/unrelated-host-folder']:
                    for evidence, origin in [(ANCHOR + '/local/record', 'Local'),
                                             (ANCHOR + '/remote/stored-folder/record',
                                              'Remote (stored-folder)')]:
                        path = root/staging/evidence
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(content)
                        ctx = context([str(path)], lambda _path, value=evidence: value)
                        headers, rows, source = biomeBluetooth.get_biomeBluetooth.__wrapped__(ctx)
                        self.assertEqual(len(headers), 7)
                        self.assertEqual(source, str(path.parent))
                        expected = [(stamp, state, None if state == 'Deleted' else MAC.decode(),
                                     None if state == 'Deleted' else NAME.decode(), origin,
                                     'record', offset)
                                    for state, offset in zip(['Written', 'Deleted', 'Written'], offsets)]
                        self.assertEqual(rows, expected)
                        windows = context([str(path)], lambda _path, value=evidence:
                                          value.replace('/', '\\'))
                        self.assertEqual(biomeBluetooth.get_biomeBluetooth.__wrapped__(windows)[1],
                                         expected)
                        repeated = context([str(path), str(path)], ctx.get_relative_path)
                        self.assertEqual(biomeBluetooth.get_biomeBluetooth.__wrapped__(repeated)[1],
                                         expected + expected)

    def test_relative_layout_boundaries(self):
        cases = [(f'remote/prefix/{ANCHOR}/local/remote/name', 'Local'),
                 (f'{ANCHOR}/remote/name', 'Remote'),
                 (f'{ANCHOR}/remote/stored/remote/name', 'Remote (stored)'),
                 (f'{ANCHOR}/other/name', 'Unknown'),
                 (f'{ANCHOR}/local', 'Unknown'),
                 (f'{ANCHOR}/remote', 'Unknown'),
                 (f'{ANCHOR}/local/', 'Unknown'),
                 (f'{ANCHOR}/remote//name', 'Unknown'),
                 (f'{ANCHOR}/local/{ANCHOR}/remote/other/name', 'Unknown'),
                 (f'/{ANCHOR}/local/name', 'Unknown'),
                 (f'C:\\{ANCHOR}\\local\\name', 'Unknown'),
                 (f'\\\\host\\{ANCHOR}\\local\\name', 'Unknown'),
                 (f'prefix/../{ANCHOR}/local/name', 'Unknown'),
                 ('unrecognized/local/name', 'Unknown'), ('', 'Unknown'), (None, 'Unknown')]
        for evidence, expected in cases:
            with self.subTest(evidence=evidence):
                self.assertEqual(biomeBluetooth._sync_origin(evidence), expected)  # pylint: disable=protected-access

    def test_unknown_rows_and_existing_skips(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contents, _ = segb_fixture(1)
            good = root/'record'
            hidden = root/'.hidden'
            tombstone = root/'tombstone-record'
            for path in [good, hidden, tombstone]:
                path.write_bytes(contents)
            relative = {str(good): 'unknown/record', str(hidden): ANCHOR + '/local/.hidden',
                        str(tombstone): ANCHOR + '/local/tombstone-record', str(root): 'directory'}
            ctx = context([str(good), str(hidden), str(tombstone), str(root)], relative.__getitem__)
            _, rows, source = biomeBluetooth.get_biomeBluetooth.__wrapped__(ctx)
            self.assertEqual([r[4] for r in rows], ['Unknown'] * 3)
            self.assertEqual([r[1] for r in rows], ['Written', 'Deleted', 'Written'])
            self.assertEqual(source, str(root))


if __name__ == '__main__':
    unittest.main()
