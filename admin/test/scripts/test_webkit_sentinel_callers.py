"""Callers of webkit_timestampsconv with NSDate sentinels, through real SEGB, protobuf and plist input.

webkit_timestampsconv returns '' for the exact NSDate.distantPast (-63114076800) and distantFuture
(63113904000) values. The four SEGB artifacts here report an absent time as None in the same column
(their Deleted rows), so a sentinel is kept as None there; a '' beside None would split the blank rows
when LAVA sorts the column. deviceDatam keeps the stored value as text instead. Every record is kept:
a sentinel time is a missing date, not a reason to drop the record.

All inputs are constructed here; none comes from an extraction.
"""
from pathlib import Path
import datetime
import plistlib
import struct
import tempfile
from types import SimpleNamespace
import sys
import unittest
import zlib

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import (biomeAppWebUsage, biomeDKInfocus, biomeTextinputses,  # pylint: disable=wrong-import-position
                               deviceDatam, notificationsDuet)

DISTANT_PAST = -63114076800.0
DISTANT_FUTURE = 63113904000.0
COCOA_SECONDS = 700000000.0
EXPECTED = datetime.datetime(2023, 3, 8, 20, 26, 40, tzinfo=datetime.timezone.utc)
WRITTEN, DELETED = 1, 3


def varint(value):
    out = bytearray()
    while value > 127:
        out.append((value & 127) | 128)
        value >>= 7
    return bytes(out) + bytes([value])


def f_bytes(number, value):
    return varint(number * 8 + 2) + varint(len(value)) + value


def f_str(number, value):
    return f_bytes(number, value.encode())


def f_double(number, value):
    return varint(number * 8 + 1) + struct.pack('<d', value)


def f_int(number, value):
    return varint(number * 8) + varint(value)


def stream(version, entries):
    """A SEGB v1 or v2 file holding (state, data) entries, laid out independently of the reader."""
    body = bytearray()
    if version == 1:
        for state, data in entries:
            body += struct.pack('<iiddIi', len(data), state, 1000, 1001, zlib.crc32(data), 0) + data
            body += bytes(-(56 + len(body)) % 8)
        return struct.pack('<I', 56 + len(body)) + bytes(48) + b'SEGB' + body
    trailer = []
    for state, data in entries:
        body += struct.pack('<Ii', zlib.crc32(data), 0) + data
        trailer.append((len(body), state))
        body += bytes(-len(body) % 4)
    header = struct.pack('<4sid16s', b'SEGB', len(entries), 1000, bytes(16))
    return header + body + b''.join(struct.pack('<iid', end, state, 1000) for end, state in trailer)


def run_segb(function, entries, relative='Biome/streams/public/Stream/local/record'):
    """Rows from the artifact for each SEGB version, with the file at a given evidence path."""
    results = []
    for version in (1, 2):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'record'
            path.write_bytes(stream(version, entries))
            ctx = SimpleNamespace(get_files_found=lambda value=path: [str(value)],
                                  get_relative_path=lambda p, rel=relative: rel)
            results.append(function.__wrapped__(ctx)[1])
    return results


def rows_of(result):
    """The machine rows of an artifact result: (rows, html_rows) or rows."""
    return result[0] if isinstance(result, tuple) else result


class BiomeAppWebUsage(unittest.TestCase):
    def record(self, timestamp=None):
        data = f_str(1, 'guid') + f_str(4, 'https://example.invalid/') + f_str(5, 'example.invalid')
        data += f_str(6, 'com.example.app') + f_int(3, 1)
        if timestamp is not None:
            data += f_double(2, timestamp)
        return data

    def test_sentinels_and_missing_times_are_none_and_every_record_is_kept(self):
        entries = [(WRITTEN, self.record(COCOA_SECONDS)), (WRITTEN, self.record(DISTANT_PAST)),
                   (WRITTEN, self.record(DISTANT_FUTURE)), (WRITTEN, self.record()),
                   (DELETED, self.record(COCOA_SECONDS))]
        for rows in map(rows_of, run_segb(biomeAppWebUsage.get_biomeAppWebUsage, entries)):
            self.assertEqual(len(rows), 5)
            self.assertEqual([r[1] for r in rows], [EXPECTED, None, None, None, None])
            self.assertEqual([r[2] for r in rows], ['Written'] * 4 + ['Deleted'])
            # the sentinel rows keep their other fields
            self.assertEqual([r[3] for r in rows[:4]], ['https://example.invalid/'] * 4)
            self.assertEqual([r[5] for r in rows[:4]], ['com.example.app'] * 4)


class BiomeTextInputSession(unittest.TestCase):
    def record(self, start):
        return f_double(1, 12.5) + f_double(2, start) + f_str(3, 'com.example.keyboard')

    def test_public_stream_sentinels_are_none(self):
        entries = [(WRITTEN, self.record(COCOA_SECONDS)), (WRITTEN, self.record(DISTANT_PAST)),
                   (WRITTEN, self.record(DISTANT_FUTURE)), (DELETED, self.record(COCOA_SECONDS))]
        for rows in map(rows_of, run_segb(biomeTextinputses.get_biomeTextinputses, entries)):
            self.assertEqual(len(rows), 4)
            self.assertEqual([r[1] for r in rows], [EXPECTED, None, None, None])
            self.assertEqual([(r[3], r[4]) for r in rows[:3]], [('com.example.keyboard', 12.5)] * 3)


class NotificationsDuet(unittest.TestCase):
    def record(self, first, second):
        inner = f_str(2, 'guid') + f_str(3, 'title') + f_str(8, 'com.example.app')
        if first is not None:
            inner = f_double(1, first) + inner
        data = f_bytes(1, inner) + f_str(4, 'guid-2')
        if second is not None:
            data += f_double(3, second)
        return data

    def test_sentinels_in_either_time_are_none(self):
        entries = [(WRITTEN, self.record(COCOA_SECONDS, COCOA_SECONDS)),
                   (WRITTEN, self.record(DISTANT_PAST, DISTANT_FUTURE)),
                   (WRITTEN, self.record(DISTANT_FUTURE, COCOA_SECONDS)),
                   (DELETED, self.record(COCOA_SECONDS, COCOA_SECONDS))]
        for rows in map(rows_of, run_segb(notificationsDuet.get_notificationsDuet, entries)):
            self.assertEqual(len(rows), 4)
            self.assertEqual([(r[1], r[2]) for r in rows],
                             [(EXPECTED, EXPECTED), (None, None), (None, EXPECTED), (None, None)])
            self.assertEqual([r[5] for r in rows[:3]], ['title'] * 3)


class BiomeDKInfocusRetention(unittest.TestCase):
    """A distantPast time used to raise inside the decode try and drop the record as a decode error;
    distantFuture converted to 4001-01-01."""

    def record(self, start, end, write):
        return (f_bytes(1, f_str(1, '/app/inFocus')) + f_double(2, start) + f_double(3, end)
                + f_bytes(4, f_str(3, 'com.example.app')) + f_str(5, 'action-guid')
                + f_double(8, write))

    def test_record_with_a_sentinel_time_is_kept(self):
        entries = [(WRITTEN, self.record(COCOA_SECONDS, COCOA_SECONDS, COCOA_SECONDS)),
                   (WRITTEN, self.record(DISTANT_PAST, COCOA_SECONDS, COCOA_SECONDS)),
                   (WRITTEN, self.record(COCOA_SECONDS, DISTANT_FUTURE, COCOA_SECONDS))]
        for rows in map(rows_of, run_segb(biomeDKInfocus.get_biomeDKInfocus, entries)):
            self.assertEqual(len(rows), 3)
            self.assertEqual([r[1:4] for r in rows], [(EXPECTED, EXPECTED, EXPECTED),
                                                       (None, EXPECTED, EXPECTED),
                                                       (EXPECTED, None, EXPECTED)])
            self.assertEqual([(r[5], r[6], r[12]) for r in rows],
                             [('/app/inFocus', 'com.example.app', 'action-guid')] * 3)


class DeviceDatam(unittest.TestCase):
    def run_plist(self, values):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'com.apple.commcenter.device_specific_nobackup.plist'
            path.write_bytes(plistlib.dumps(values))
            ctx = SimpleNamespace(get_files_found=lambda: [str(path)])
            return dict(deviceDatam.deviceDatam.__wrapped__(ctx)[1])

    def test_dates_sentinels_and_text_in_timestamp_keys(self):
        rows = self.run_plist({'AccountCreationTimestamp': COCOA_SECONDS,
                               'kEuiccTicketPrefetchTimestamp': DISTANT_PAST,
                               'AddOnRemotePlanListExpiryTime': DISTANT_FUTURE,
                               'SomeOtherKey': 'kept'})
        self.assertEqual(rows['AccountCreationTimestamp'],
                         '2023-03-08 20:26:40+00:00 (original: 700000000.0)')
        # a sentinel keeps the stored value as text, with no invented date
        self.assertEqual(rows['kEuiccTicketPrefetchTimestamp'], '-63114076800.0')
        self.assertEqual(rows['AddOnRemotePlanListExpiryTime'], '63113904000.0')
        self.assertEqual(rows['SomeOtherKey'], 'kept')
        self.assertTrue(all(isinstance(v, str) for v in rows.values()))

    def test_value_that_is_not_a_number_is_reported_as_stored(self):
        rows = self.run_plist({'AccountCreationTimestamp': 'not a number'})
        self.assertEqual(rows, {'AccountCreationTimestamp': 'not a number'})


if __name__ == '__main__':
    unittest.main()
