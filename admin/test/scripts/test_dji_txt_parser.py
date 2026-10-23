"""Focused binary-decoding tests. Run from ALEAPP with unittest.

Fixtures here are synthetic, not casework and not DF020 corpus validation.
The CRC check is the published crc64 crate vector; XOR fixture uses a
precomputed key independently checked against pydjirecord's table decoder.
"""
import datetime
import math
import struct
import unittest
from scripts.artifacts import djiFlightRecordTxt as module


TIME_MS = 1530000000123


def details(old_layout=False):
    result = bytearray(436)
    result[40:48] = b'TestCity'
    struct.pack_into('<qddfifffiq', result, 91, TIME_MS, -105.0, 40.0,
                     100.0, 20000, 10.0, 5.0, 2.0, 7, 95)
    if old_layout:
        struct.pack_into('<f', result, 352, 12.5)
        result[277], result[348], result[349:352] = 13, 1, bytes((3, 1, 11))
        result[278:283], result[267:271] = b'Plane', b'A123'
        result[318:322], result[328:332], result[338:342] = b'C123', b'R123', b'B123'
    else:
        struct.pack_into('<f', result, 267, 12.5)
        result[271], result[376], result[377:380] = 13, 2, bytes((4, 2, 16))
        result[280:285], result[312:316] = b'Plane', b'A123'
        result[328:332], result[344:348], result[360:364] = b'C123', b'R123', b'B123'
    return bytes(result)


def record(kind, payload, version):
    if version >= 7:
        # Known key for record 5, first byte 65, computed by independent decoder.
        keys = {5: bytes.fromhex('3f1bb88a0f511ff5')}
        key = keys[kind]
        payload = b'\x41' + bytes(b ^ key[i % 8] for i, b in enumerate(payload)) + b'\0'
    return bytes((kind, len(payload))) + payload + b'\xff'


def log(version, records=b''):
    prefix_size = 12 if version < 6 else 100
    prefix = bytearray(prefix_size)
    detail_offset = prefix_size + len(records) if version < 12 else 100
    struct.pack_into('<QHB', prefix, 0, detail_offset, 436, version)
    block = details(old_layout=version <= 5)
    return bytes(prefix) + (records + block if version < 12 else block + records)


def osd(lat=40, lon=-105):
    result = bytearray(50)
    struct.pack_into('<dd7h', result, 0, math.radians(lon), math.radians(lat),
                     123, 30, 40, -10, 25, -35, 905)
    result[36], result[40] = 12, 87
    struct.pack_into('<H', result, 42, 155)
    return bytes(result)


class ParserTests(unittest.TestCase):
    def test_crc_known_vector(self):
        self.assertEqual(module._crc64(0, b'123456789'), 0xE9C6D914C4B8D9CA)  # pylint: disable=protected-access

    def test_units_and_coordinates(self):
        summary, rows = module.parse_txt(log(6, record(1, osd(), 6)))
        row = rows[0]
        self.assertAlmostEqual(row['latitude'], 40)
        self.assertAlmostEqual(row['longitude'], -105)
        self.assertEqual((row['altitude'], row['speed'], row['heading']), (12.3, 5.0, 90.5))
        self.assertEqual((row['satellites'], row['battery'], row['flight_time']), (12, 87, 15.5))
        self.assertIsNone(row['timestamp'])
        self.assertEqual(summary['timestamp'].tzinfo, datetime.timezone.utc)

    def test_version_layouts(self):
        for version in (1, 5, 6, 12):
            payload = struct.pack('<ffq', 5, 2, TIME_MS)
            # v12 XOR is covered separately below.
            records = record(5, b'\0\0' + payload, 6 if version < 7 else 12)
            summary, rows = module.parse_txt(log(version, records))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['timestamp'], summary['timestamp'])

    def test_xor_versions(self):
        for version in (7, 8, 9, 10, 11, 12):
            raw = b'\0\0' + struct.pack('<ffq', 5, 2, TIME_MS)
            _, rows = module.parse_txt(log(version, record(5, raw, version)))
            self.assertEqual(rows[0]['custom_speed'], 5)
            self.assertEqual(rows[0]['custom_distance'], 2)
            self.assertIsNotNone(rows[0]['timestamp'])

    def test_timestamp_attribution(self):
        records = record(1, osd(), 6) + record(5, b'\0\0' + struct.pack('<ffq', 5, 2, TIME_MS), 6) + record(1, osd(), 6)
        _, rows = module.parse_txt(log(6, records))
        self.assertIsNone(rows[0]['timestamp'])
        self.assertEqual(rows[1]['timestamp'], rows[2]['timestamp'])
        self.assertEqual(rows[2]['timestamp_basis'], 'Preceding Custom record')
        self.assertNotIn('latitude', rows[1])

    def test_invalid_timestamp_clears_previous(self):
        good = record(5, b'\0\0' + struct.pack('<ffq', 5, 2, TIME_MS), 6)
        bad = record(5, b'\0\0' + struct.pack('<ffq', 5, 2, -1), 6)
        _, rows = module.parse_txt(log(6, good + bad + record(1, osd(), 6)))
        self.assertIsNone(rows[-1]['timestamp'])

    def test_invalid_gps_not_plotted(self):
        for lat, lon in ((0, 0), (91, 1), (float('nan'), 1)):
            _, rows = module.parse_txt(log(6, record(1, osd(lat, lon), 6)))
            self.assertIsNone(rows[0]['latitude'])
            self.assertEqual(rows[0]['altitude'], 12.3)

    def test_gimbal(self):
        _, rows = module.parse_txt(log(6, record(3, struct.pack('<3h', -450, 10, 900), 6)))
        self.assertEqual((rows[0]['gimbal_pitch'], rows[0]['gimbal_roll'], rows[0]['gimbal_yaw']), (-45, 1, 90))

    def test_home_keeps_position_separate_from_aircraft(self):
        payload = struct.pack('<ddfBBH', math.radians(-105), math.radians(40), 125, 1, 0, 60)
        _, rows = module.parse_txt(log(6, record(2, payload, 6)))
        row = rows[0]
        self.assertAlmostEqual(row['home_latitude'], 40)
        self.assertAlmostEqual(row['home_longitude'], -105)
        self.assertEqual((row['home_altitude'], row['home_recorded'], row['return_height']), (12.5, True, 60))
        self.assertNotIn('latitude', row)

    def test_controller_raw_units_and_buttons(self):
        payload = struct.pack('<5H3B', 1024, 1100, 990, 1010, 1200, 0, 8, 192)
        _, rows = module.parse_txt(log(6, record(4, payload, 6)))
        row = rows[0]
        self.assertEqual((row['rc_aileron'], row['rc_elevator'], row['rc_throttle'], row['rc_rudder'], row['rc_gimbal']), (1024, 1100, 990, 1010, 1200))
        self.assertTrue(row['rc_return'] and row['rc_shutter'] and row['rc_record'])

    def test_smart_battery_offsets_and_units(self):
        payload = bytearray(30)
        struct.pack_into('<H', payload, 0, 340)
        struct.pack_into('<H', payload, 24, 15200)
        payload[26] = 87
        _, rows = module.parse_txt(log(6, record(8, payload, 6)))
        self.assertEqual((rows[0]['battery_voltage'], rows[0]['battery_time'], rows[0]['battery_percent']), (15.2, 340, 87))

    def test_camera_photo_state_is_not_any_nonzero_enum(self):
        for state in range(8):
            payload = bytearray(24)
            payload[0], payload[1], payload[4] = (state << 3) | 64, 2, 1
            struct.pack_into('<H', payload, 21, 45)
            _, rows = module.parse_txt(log(6, record(25, payload, 6)))
            self.assertEqual(rows[0]['camera_photo'], state == 1)
            self.assertEqual((rows[0]['camera_recording'], rows[0]['camera_sd'], rows[0]['camera_record_time']), (True, True, 45))

    def test_short_camera_does_not_invent_extended_fields(self):
        _, rows = module.parse_txt(log(6, record(25, b'\0\0', 6)))
        self.assertNotIn('camera_mode', rows[0])

    def test_new_record_truncation_preserves_payload(self):
        for kind in (2, 4, 8, 25):
            _, rows = module.parse_txt(log(6, record(kind, b'\x01', 6)))
            self.assertTrue(rows[0]['status'].startswith('Short'))
            self.assertEqual(rows[0]['payload_hex'], '01')

    def test_defined_undecoded_type_keeps_payload(self):
        _, rows = module.parse_txt(log(6, record(19, b'abcd', 6)))
        self.assertEqual((rows[0]['name'], rows[0]['payload_hex']), ('MC Parameters', '61626364'))

    def test_undefined_type_counted_not_reported(self):
        gimbal = record(3, struct.pack('<3h', -450, 10, 900), 6)
        summary, rows = module.parse_txt(log(6, record(99, b'abcd', 6) + record(99, b'ef', 6) + gimbal))
        self.assertEqual([row['type'] for row in rows], [3])
        self.assertEqual(summary['not_reported'], 'type 99: 2')

    def test_bad_record_stops_without_resync(self):
        valid = record(3, struct.pack('<3h', -450, 10, 900), 6)
        summary, rows = module.parse_txt(log(6, valid + b'\x01\xfe\0' + valid))
        self.assertEqual(len(rows), 1)
        self.assertEqual(summary['warnings'], ['Record at offset 109 declares 257 bytes; 12 remain before the end of the record area'])
        self.assertTrue(summary['status'].startswith('Parsing stopped 12 bytes before the end'))

    def test_missing_terminator_stops(self):
        valid = record(3, struct.pack('<3h', -450, 10, 900), 6)
        summary, rows = module.parse_txt(log(6, valid + valid[:-1] + b'\0' + valid))
        self.assertEqual(len(rows), 1)
        self.assertEqual(summary['warnings'], ['Record at offset 109 lacks its 0xFF terminator'])
        self.assertTrue(summary['status'].startswith('Parsing stopped 18 bytes before the end'))

    def test_incomplete_last_record_reports_remaining_bytes(self):
        valid = record(3, struct.pack('<3h', -450, 10, 900), 6)
        summary, rows = module.parse_txt(log(6, valid + b'\x39\x30\0\0'))
        self.assertEqual(len(rows), 1)
        self.assertEqual(summary['warnings'], ['Record at offset 109 declares 51 bytes; 4 remain before the end of the record area'])
        self.assertTrue(summary['status'].startswith('Parsing stopped 4 bytes before the end'))

    def test_short_payload_keeps_record(self):
        _, rows = module.parse_txt(log(6, record(1, b'abc', 6)))
        self.assertEqual(rows[0]['status'], 'Short OSD payload')

    def test_jpeg_framing(self):
        _, rows = module.parse_txt(log(6, b'\xff\xd8test\xff\xd9' + record(19, b'abc', 6)))
        self.assertEqual([(row['type'], row['name']) for row in rows], [(None, 'Embedded JPEG'), (19, 'MC Parameters')])

    def test_reject_truncation(self):
        for value in (b'', b'csv,not,evidence', log(6)[:120]):
            with self.assertRaises(ValueError):
                module.parse_txt(value)

    def test_reject_unknown_version(self):
        with self.assertRaises(ValueError):
            module.parse_txt(log(15))

    def test_encrypted_auxiliary_metadata(self):
        # Key independently checked against pydjirecord's CRC table decoder.
        key = bytes.fromhex('e3c6b4f466514c5d')
        info = b'\x01' + struct.pack('<H', len(details())) + details() + b'\0\0'
        payload = b'\x41' + bytes(b ^ key[i % 8] for i, b in enumerate(info))
        auxiliary = b'\0' + struct.pack('<H', len(payload)) + payload
        aux_version = b'\x01\x03\0\x02\0\x03'
        for version in (13, 14):
            for recover in (False, True):
                prefix = bytearray(100)
                start = 100 + len(auxiliary) + len(aux_version)
                struct.pack_into('<QHB', prefix, 0, 0 if recover else start, 436, version)
                summary, rows = module.parse_txt(bytes(prefix) + auxiliary + aux_version + b'encrypted bytes')
                self.assertEqual(rows, [])
                self.assertEqual(summary['city'], 'TestCity')
                self.assertEqual(summary['latitude'], 40)
                self.assertEqual(summary['longitude'], -105)
                self.assertIn('Encrypted', summary['status'])
                self.assertEqual(summary['timestamp'].microsecond, 123000)

    def test_encrypted_truncated_auxiliary(self):
        prefix = bytearray(104)
        struct.pack_into('<QHB', prefix, 0, 110, 436, 14)
        struct.pack_into('<H', prefix, 101, 436)
        with self.assertRaisesRegex(ValueError, 'encrypted'):
            module.parse_txt(bytes(prefix))

    def test_details_identifiers_both_layouts(self):
        for version, platform, app_version in ((5, 'IOS (1)', '3.1.11'), (6, 'Android (2)', '4.2.16'), (12, 'Android (2)', '4.2.16')):
            summary, _ = module.parse_txt(log(version))
            self.assertEqual((summary['aircraft_name'], summary['product_type'], summary['aircraft_sn']),
                             ('Plane', 'MavicPro (13)', 'A123'))
            self.assertEqual((summary['camera_sn'], summary['rc_sn'], summary['battery_sn']), ('C123', 'R123', 'B123'))
            self.assertEqual((summary['app_platform'], summary['app_version']), (platform, app_version))
            self.assertEqual((summary['takeoff_altitude'], summary['photo_count'], summary['video_time_s']), (12.5, 7, 95))

    def test_unknown_enum_value_kept(self):
        block = bytearray(details())
        block[271], block[376] = 250, 99
        prefix = bytearray(100)
        struct.pack_into('<QHB', prefix, 0, 100, 436, 12)
        summary, _ = module.parse_txt(bytes(prefix) + bytes(block))
        self.assertEqual((summary['product_type'], summary['app_platform']), ('Unknown (250)', 'Unknown (99)'))

    def test_app_gps_latitude_first(self):
        _, rows = module.parse_txt(log(6, record(14, struct.pack('<dd', 39.96, -106.21) + b'\0' * 4, 6)))
        self.assertEqual((rows[0]['app_latitude'], rows[0]['app_longitude']), (39.96, -106.21))

    def test_rc_gps(self):
        payload = struct.pack('<3BH2B4iBfH', 10, 2, 22, 2017, 10, 9, 399612576, -1062161792, 0, 0, 9, 1.5, 1)
        _, rows = module.parse_txt(log(6, record(11, payload, 6)))
        row = rows[0]
        self.assertEqual(row['rc_gps_time'], '2017-10-09 10:02:22')
        self.assertAlmostEqual(row['rc_latitude'], 39.9612576)
        self.assertAlmostEqual(row['rc_longitude'], -106.2161792)
        self.assertEqual((row['rc_satellites'], row['rc_accuracy'], row['rc_valid']), (9, 1.5, 1))

    def test_rc_gps_zero_position_not_plotted(self):
        payload = struct.pack('<3BH2B4iBfH', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0)
        _, rows = module.parse_txt(log(6, record(11, payload, 6)))
        self.assertIsNone(rows[0]['rc_latitude'])

    def test_component_serial_and_firmware(self):
        serial = struct.pack('<HB', 2, 6) + b'SN0001'
        firmware = bytes((1, 0, 2, 8, 56, 0))
        _, rows = module.parse_txt(log(6, record(40, serial, 6) + record(15, firmware, 6)))
        self.assertEqual((rows[0]['component'], rows[0]['serial']), ('Aircraft (2)', 'SN0001'))
        self.assertEqual(rows[0]['component'], 'Aircraft (2)')
        self.assertEqual(rows[1]['firmware'], 'Camera (1) / 0: 2.8.56')
        self.assertNotIn('component', rows[1])

    def test_firmware_lists_every_entry(self):
        payload = bytes((1, 0, 2, 8, 56, 68, 3, 6, 3, 2, 44, 7, 9, 0, 0, 1, 0, 1))
        _, rows = module.parse_txt(log(6, record(15, payload, 6)))
        self.assertEqual(rows[0]['firmware'], 'Camera (1) / 0: 2.8.56; MC (3) / 6: 3.2.44; Unknown (9) / 0: 0.1.0')
        self.assertEqual(rows[0]['status'], 'Decoded')

    def test_firmware_trailing_bytes_noted(self):
        _, rows = module.parse_txt(log(6, record(15, bytes((11, 0, 1, 0, 7, 32, 4, 0)), 6)))
        self.assertEqual(rows[0]['firmware'], 'Battery (11) / 0: 1.0.7')
        self.assertEqual(rows[0]['status'], 'Decoded; 2 trailing bytes are not a whole entry')

    def test_short_component_serial(self):
        _, rows = module.parse_txt(log(6, record(40, struct.pack('<HB', 2, 9) + b'SN', 6)))
        self.assertEqual(rows[0]['status'], 'Short Component Serial payload')

    def test_ios_v8_prefixed_jpeg_cluster(self):
        images = b'\xff\xd8first\xff\xd9\xff\xd8second\xff\xd9'
        summary, rows = module.parse_txt(log(8, b'\x39\x30\0\0' + images))
        self.assertEqual([r['name'] for r in rows], ['Embedded JPEG', 'Embedded JPEG'])
        self.assertEqual(summary['status'], 'Parsed offline')
        self.assertEqual(summary['warnings'], [])
        self.assertTrue(all(r['timestamp'] is None for r in rows))

    def test_ios_prefix_does_not_skip_unconfirmed_data(self):
        summary, rows = module.parse_txt(log(8, b'\x39\x30\0\0not-jpeg'))
        self.assertEqual(rows, [])
        self.assertTrue(summary['warnings'])

    def test_ios_prefixed_truncated_jpeg_is_explicit(self):
        summary, rows = module.parse_txt(log(8, b'\x39\x30\0\0\xff\xd8truncated'))
        self.assertEqual(rows, [])
        self.assertIn('no end marker', summary['warnings'][0])


if __name__ == '__main__':
    unittest.main()
