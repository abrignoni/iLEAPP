"""Exercise both Biome artifacts with synthetic SEGB files and two device roots."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import struct
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zlib

from admin.test.scripts.synthetic_sms_deep import typedstream_bytes
from scripts.artifacts.biomeNotificationDelivery import get_biomeNotificationDelivery
from scripts.artifacts.biomeScreenshots import get_biomeScreenshots


def segb(entries):
    data = bytearray()
    trailer = bytearray()
    for state, payload in entries:
        data.extend(struct.pack('<Ii', zlib.crc32(payload), 0) + payload)
        trailer.extend(struct.pack('<iid', len(data), state, 777777777.125))
        data.extend(bytes(-len(data) % 4))
    return struct.pack('<4sid16s', b'SEGB', len(entries), 777777777, bytes(16)) + data + trailer


GUID = b'Synthetic-GUID'
BUNDLE = b'com.apple.MobileSMS'


def notification(seconds):
    return (b'\x0a' + bytes([len(GUID)]) + GUID + b'\x12' + bytes([len(BUNDLE)]) + BUNDLE
            + b'\x19' + struct.pack('<d', seconds))


class LocalStreamTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.files = []
        self.context = SimpleNamespace(get_files_found=lambda: self.files,
                                       get_relative_path=lambda p: Path(p).relative_to(self.root).as_posix())

    def file(self, device, name):
        path = self.root / device / 'private/var/mobile/Library' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        self.files.append(str(path))
        return path

    def stream(self, device, stream, filename, data):
        self.file(device, f'Biome/streams/restricted/{stream}/local/{filename}').write_bytes(data)

    def sms(self, device, attributed):
        with closing(sqlite3.connect(self.file(device, 'SMS/sms.db'))) as db:
            db.execute('create table handle(id text)')
            db.execute('insert into handle values (?)', (device,))
            db.execute('create table message(guid text, date integer, handle_id integer, '
                       'is_from_me integer, text text' + (', attributedBody blob)' if attributed else ')'))
            values = (GUID.decode(), 777777777123456000, 1, int(attributed), None if attributed else device)
            if attributed:
                values += (typedstream_bytes(device),)
            db.execute('insert into message values (' + ','.join('?' for _ in values) + ')', values)
            db.commit()

    def rows(self, artifact):
        headers, rows, _ = artifact.__wrapped__(self.context)
        columns = [h[0] if isinstance(h, tuple) else h for h in headers]
        return [dict(zip(columns, r, strict=True)) for r in rows]

    def test_only_the_device_database_can_supply_a_match(self):
        self.sms('second', False)
        self.sms('first', True)
        for device in ('first', 'second', 'missing'):
            self.stream(device, 'Notification.Delivery', 'same-name', segb([(1, notification(1700000000.123456))]))
        rows = self.rows(get_biomeNotificationDelivery)
        self.assertEqual(len(rows), 3)
        for row in rows:
            device = row['Source File'].split('/')[0]
            self.assertEqual(row['Delivery Date'].microsecond, 123456)
            if device == 'missing':
                self.assertIsNone(row['Matched Message Date'])
                self.assertFalse(row['Matched Message Text'])
            else:
                self.assertEqual(row['Matched Message Date'].microsecond, 123456)
                self.assertEqual(row['Matched Message Handle'], device)
                self.assertEqual(row['Matched Message Text'], device)
                self.assertEqual(row['Matched Message Direction'], 'Outgoing' if device == 'first' else 'Incoming')

    def test_bad_file_and_bad_payload_do_not_hide_other_notifications(self):
        self.stream('one', 'Notification.Delivery', 'incomplete', b'SEGB')
        self.stream('one', 'Notification.Delivery', 'intact', segb([
            (1, b'\xff'), (1, notification(float('nan'))), (3, b'\0'), (1, notification(1700000000.25))]))
        with patch('scripts.biome_stream_records.logfunc'), patch('scripts.artifacts.biomeNotificationDelivery.logfunc'):
            rows = self.rows(get_biomeNotificationDelivery)
        self.assertEqual([r['SEGB State'] for r in rows], ['Written', 'Written', 'Deleted', 'Written'])
        self.assertTrue(all(r['SEGB Timestamp'] for r in rows))
        self.assertTrue(all(r['Delivery Date'] is None for r in rows[:3]))
        self.assertEqual(rows[-1]['Delivery Date'].microsecond, 250000)

    def test_written_screenshots_preserve_binary_and_undecodable_payloads(self):
        self.stream('one', 'Screenshots.Screenshot', 'incomplete', b'SEGB')
        self.stream('one', 'Screenshots.Screenshot', 'intact', segb([(1, b'\x0a\x02\xff\xfe'), (1, b'\xff'), (3, b'\0')]))
        with patch('scripts.biome_stream_records.logfunc'), patch('scripts.artifacts.biomeScreenshots.logfunc'):
            rows = self.rows(get_biomeScreenshots)
        self.assertEqual(json.loads(rows[0]['Record Data']), {'1': {'hex': 'fffe'}})
        self.assertEqual(json.loads(rows[1]['Record Data']), {'raw_hex': 'ff'})
        self.assertIsNone(rows[2]['Record Data'])
        self.assertEqual(len({r['Offset'] for r in rows}), 3)


if __name__ == '__main__':
    unittest.main()
