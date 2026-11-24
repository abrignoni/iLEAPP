"""A DKEvent date no datetime can hold is left empty and logged, and the rest of the file still parses."""
# pylint: disable=protected-access
import datetime
import importlib
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

MODULES = ['biomeAirpMode', 'biomeWifi', 'biomeBattperc', 'biomeCarplayisconnected',
           'biomeDevplugin', 'biomeSafari']
BAD = [float('nan'), float('inf'), float('-inf'), 1e300, -1e300]
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


class CocoaDateHelperTest(unittest.TestCase):
    def test_bad_values_are_empty_and_logged_in_every_module(self):
        for name in MODULES:
            module = importlib.import_module(f'scripts.artifacts.{name}')
            for value in BAD:
                with self.subTest(module=name, value=value), patch.object(module, 'logfunc') as log:
                    self.assertIsNone(module._cocoa_date(value, 3, 64, 'stream'))
                    self.assertEqual(log.call_count, 1)
                    self.assertIn('offset 64 in stream', log.call_args[0][0])

    def test_good_values_and_the_sentinel_are_unchanged(self):
        for name in MODULES:
            module = importlib.import_module(f'scripts.artifacts.{name}')
            with self.subTest(module=name), patch.object(module, 'logfunc') as log:
                self.assertEqual(module._cocoa_date(900.0, 2, 0, 'f'),
                                 EPOCH + datetime.timedelta(seconds=900))
                self.assertIsNone(module._cocoa_date(63113904000.0, 2, 0, 'f'))  # distantFuture
                log.assert_not_called()


class WifiBadEndDateTest(unittest.TestCase):
    def test_bad_end_date_keeps_the_row_and_the_next_record(self):
        from scripts.artifacts import biomeWifi as parser
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stream = root / 'Biome/streams/restricted/_DKEvent.Wifi.Connection/local/record'
            stream.parent.mkdir(parents=True)
            stream.write_bytes(segb_v2([wifi_record(900, float('nan')), wifi_record(1000, 1100)]))
            context = SimpleNamespace(get_files_found=lambda: [str(stream)],
                                      get_relative_path=lambda p: str(Path(p).relative_to(root)))
            with patch.object(parser, 'logfunc') as log:
                headers, rows, _ = parser.get_biomeWifi.__wrapped__(context)
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows[0]), len(headers))
        self.assertEqual(rows[0][1], EPOCH + datetime.timedelta(seconds=900))
        self.assertIsNone(rows[0][2])
        self.assertEqual(rows[1][2], EPOCH + datetime.timedelta(seconds=1100))
        self.assertTrue(any('field 3 could not be converted' in c[0][0] for c in log.call_args_list))


if __name__ == '__main__':
    unittest.main()
