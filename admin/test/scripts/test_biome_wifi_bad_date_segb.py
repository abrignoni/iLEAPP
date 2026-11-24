"""A real SEGB v2 file whose first Wi-Fi record holds a NaN End Date: the row is kept and the next record still parses.

From iLEAPP #2864 (closed in favour of #2865). Unlike the mocked test in #2865, the SEGB reader and the
protobuf decoder run for real here. It asserts only the rows, so it does not depend on where the helper
lives or what it logs; #2865's own test checks the log line.
"""
import datetime
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import biomeWifi as parser

EPOCH = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)


def length_delimited(field, payload):
    return bytes([(field << 3) | 2, len(payload)]) + payload


def double(field, value):
    return bytes([(field << 3) | 1]) + struct.pack('<d', value)


def wifi_record(start, end):
    """Fields the Wi-Fi module reads: 1.1 stream name, 2 and 3 dates, 4.3 value, 5 identifier."""
    return (length_delimited(1, length_delimited(1, b'/wifi/connection'))
            + double(2, start) + double(3, end)
            + length_delimited(4, length_delimited(3, b'name'))
            + length_delimited(5, b'ID'))


def segb_v2(payloads):
    """Reader-format SEGB version 2 file, every record Written."""
    body = bytearray()
    ends = []
    for payload in payloads:
        body += struct.pack('<Ii', zlib.crc32(payload), 0) + payload
        ends.append(len(body))
        body += bytes(-len(body) % 4)
    trailer = b''.join(struct.pack('<iid', end, 1, 1000) for end in ends)
    return struct.pack('<4sid16s', b'SEGB', len(ends), 1000, bytes(16)) + body + trailer


class WifiBadEndDateSegbTest(unittest.TestCase):
    def test_bad_end_date_keeps_the_row_and_the_next_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stream = root / 'Biome/streams/restricted/_DKEvent.Wifi.Connection/local/record'
            stream.parent.mkdir(parents=True)
            stream.write_bytes(segb_v2([wifi_record(900, float('nan')), wifi_record(1000, 1100)]))
            context = SimpleNamespace(get_files_found=lambda: [str(stream)],
                                      get_relative_path=lambda p: str(Path(p).relative_to(root)))
            headers, rows, _ = parser.get_biomeWifi.__wrapped__(context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        start, end = names.index('Start Date'), names.index('End Date')
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows[0]), len(headers))
        self.assertEqual(rows[0][start], EPOCH + datetime.timedelta(seconds=900))
        self.assertIn(rows[0][end], (None, ''))
        self.assertEqual(rows[1][end], EPOCH + datetime.timedelta(seconds=1100))


if __name__ == '__main__':
    unittest.main()
