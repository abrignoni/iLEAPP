__artifacts_v2__ = {
    'djiFlightRecordTxtRecords': {
        'name': 'DJI Drone - TXT Flight Records',
        'description': 'Reads DJI GO, DJI GO 4 and DJI Fly TXT flight records offline. Versions 1 to 12 '
                       'give one row per record of a defined type; version 13 and later give no '
                       'record rows (see the Summary artifact).',
        'author': 'Neal (@Blackwater1224), @AlexisBrignoni, Claude',
        'creation_date': '2026-10-23',
        'last_update_date': '2026-10-23',
        'requirements': 'none',
        'category': 'DJI Drone',
        'notes': 'Versions 1-6 are read as stored and 7-12 use local XOR decoding. Version 13+ '
                 'telemetry is encrypted and is not decrypted; see TXT Flight Log Summary. '
                 'Record types, layouts, units and enum names follow dji-log-parser v0.5.7 '
                 '(https://github.com/lvauvillier/dji-log-parser, MIT). A record of a type it does '
                 'not define is not listed; each log\'s count of those is in the summary\'s Records '
                 'Not Reported column. A header without a unit, or marked as stored or raw, has no unit '
                 'documented there. Camera Mode is shown as the stored number; dji-log-parser '
                 'defines names for it that are not applied. Horizontal Speed is derived from Speed X and Speed Y. '
                 'Timestamp comes from Custom records in UTC. Other records use the preceding '
                 'Custom timestamp, labeled in Timestamp Basis; records before it have no timestamp. '
                 'Telemetry is not carried between rows. Relative Height is the OSD altitude field. '
                 'dji-log-parser adds the Home altitude to it to get absolute altitude and '
                 'pydjirecord describes it as height above the take-off point. It is not '
                 'altitude above sea level. '
                 'Latitude and Longitude are the aircraft (OSD) position and are the only '
                 'coordinates in the KML; Home, App GPS (the mobile device) and RC GPS (the remote '
                 'controller) keep their own columns. '
                 'App GPS is read latitude first. dji-log-parser and pydjirecord name the first '
                 'value longitude, but in the three DF020 Android logs (df020_mavic_pro_android, '
                 'read with ALEAPP) the first value is the latitude of the site the OSD and Home '
                 'positions in the same log place the flight. '
                 'RC GPS coordinates are the stored integers divided by 1e7 and RC GPS Accuracy is '
                 'in metres, per pydjirecord (https://github.com/rembish/pydjirecord, MIT). '
                 'RC GPS Date and Time is shown as stored; the record holds no zone. '
                 'Both references define the Firmware record as one 6-byte entry: sender, sub '
                 'sender and four version bytes, of which they show the first three. Firmware '
                 'Entries lists every whole entry as sender (number) / sub sender: version, in '
                 'stored order, with the version read as the references read it. Senders outside '
                 'the references\' list show as Unknown with the number. Bytes past the last whole '
                 'entry are noted in Decode Status. '
                 'OSD Battery has no documented unit; Battery Percent is the Smart Battery percent. '
                 'Payloads are kept as hex on every record row; Embedded JPEG rows carry none. '
                 'Four bytes 39 30 00 00 directly before a JPEG start marker are skipped; no other '
                 'search for a next record is made after damaged framing. Images stay in the source and are not extracted. '
                 'In df020_mavic_pro_ios (DJI GO 4, TXT version 8): App GPS Latitude, App GPS '
                 'Longitude, RC GPS Date and Time, RC GPS Latitude, RC GPS Longitude, RC GPS '
                 'Satellites, RC GPS Accuracy (m), RC GPS Valid Data, Component and Serial Number are '
                 'empty, because the log holds no App GPS, RC GPS or Component Serial records; Log '
                 'Version held 8 on all rows; RC Return Button, RC Shutter Button and RC Record '
                 'Button are identical, false on all 631 RC rows and blank on other record types; Home Recorded held true on all 218 Home rows; Camera SD '
                 'Present held true on all 491 Camera rows. They remain separate fields because '
                 'each reads a different stored value. '
                 'Real logs: version 8 in df020_mavic_pro_ios; versions 9 and 11 in the DF020 Android '
                 'logs with ALEAPP\'s copy of this decoder; the public pydjirecord version 14 example '
                 'yields no records. Other versions are covered by synthetic tests only. On iOS only '
                 'DJI GO 4 has been run; DJI GO and DJI Fly have not.',
        'paths': ('*/Documents/FlightRecords/DJIFlightRecord*.txt',),
        'output_types': 'all',
        'artifact_icon': 'map-pin',
        'sample_data': {
            'df020_mavic_pro_ios': 'iOS 10.3.2 | DJI GO 4 (com.dji.go build 2952), TXT v8 | '
                '16441 rows: 16433 records and 8 Embedded JPEG rows; 4515 OSD positions',
        },
    },
    'djiFlightRecordTxtSummary': {
        'name': 'DJI Drone - TXT Flight Log Summary',
        'description': 'Reports unencrypted flight metadata, aircraft and component identifiers, '
                       'encryption and parsing status.',
        'author': 'Neal (@Blackwater1224), @AlexisBrignoni, Claude',
        'creation_date': '2026-10-23',
        'last_update_date': '2026-10-23',
        'requirements': 'none',
        'category': 'DJI Drone',
        'notes': 'Metadata is from Details, locally XOR-decoded from Auxiliary Info on version 13+. '
                 'No network requests, API keys, external executable or CSV import. '
                 'Offsets, units and enum names follow dji-log-parser v0.5.7 layout/details.rs '
                 '(https://github.com/lvauvillier/dji-log-parser, MIT). Product Type and App '
                 'Platform show its enum name with the stored number, or Unknown with the number. '
                 'Version 5 and earlier use different identifier offsets, covered by synthetic '
                 'tests only. Takeoff Altitude has no documented unit and is shown as stored. '
                 'Latitude and Longitude are the Details position; the reference does not say '
                 'when in the flight it is taken. In df020_mavic_pro_ios it matched the first OSD '
                 'position with a fix. Video Time is documented in seconds by dji-log-parser; '
                 'pydjirecord reports no consistent unit. In df020_mavic_pro_ios it held 429 while '
                 'the largest Camera Record Time in the same log was 312. '
                 'Records Not Reported counts records of types dji-log-parser does not define. '
                 'When parsing stops early, Status gives how many bytes of the record area were '
                 'left unread and Warnings says why. In df020_mavic_pro_ios the log parsed to the '
                 'end of the record area and Warnings is empty. RC Serial Number is empty in that '
                 'log, Street and Area are empty, and Sub Street and City held the same string. '
                 'Location columns retain the source Details strings when present. On iOS only '
                 'DJI GO 4 has been run; DJI GO and DJI Fly have not.',
        'paths': ('*/Documents/FlightRecords/DJIFlightRecord*.txt',),
        'output_types': ['html', 'tsv', 'lava', 'timeline'],
        'artifact_icon': 'file-text',
        'sample_data': {
            'df020_mavic_pro_ios': 'iOS 10.3.2 | DJI GO 4 (com.dji.go build 2952), TXT v8 | '
                '1 row; 2718 records of undefined types counted; no warnings',
        },
    },
}

# Author: Neal (@Blackwater1224), https://github.com/Blackwater1224
# Developed with AI assistance from OpenAI Codex for Python implementation,
# test development, and validation.
# Record layouts and XOR key derivation adapted from dji-log-parser v0.5.7.
# Copyright (c) Luc Vauvillier and other contributors (MIT).
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# RC GPS coordinate scale and accuracy unit from pydjirecord, commit
# cabbce1bb8c24bb00bd861af80aac7601c03e5f6, Copyright (c) 2025 pydjirecord
# contributors (MIT); no code is copied from it.

import datetime
import math
import os
import struct
from collections import Counter
from functools import lru_cache

from scripts.ilapfuncs import artifact_processor, logfunc

# Record type numbers and names from dji-log-parser v0.5.7 record/mod.rs.
# A type outside this table is not defined there and is counted, not reported.
_RECORD_NAMES = {1: 'OSD', 2: 'Home', 3: 'Gimbal', 4: 'RC', 5: 'Custom', 6: 'Deform',
                 7: 'Center Battery', 8: 'Smart Battery', 9: 'App Tip', 10: 'App Warning',
                 11: 'RC GPS', 13: 'Recover', 14: 'App GPS', 15: 'Firmware',
                 19: 'MC Parameters', 22: 'Smart Battery Group', 24: 'App Serious Warning',
                 25: 'Camera', 33: 'Virtual Stick', 40: 'Component Serial', 49: 'OFDM',
                 50: 'Key Storage Recover', 56: 'Key Storage', 62: 'RC Display'}

# Enum names exactly as dji-log-parser v0.5.7 spells them:
# ProductType and Platform in layout/details.rs, ComponentType in
# record/component_serial.rs, SenderType in record/firmware.rs.
_PRODUCT_TYPES = {
    0: 'None', 1: 'Inspire1', 2: 'Phantom3Standard', 3: 'Phantom3Advanced', 4: 'Phantom3Pro',
    5: 'OSMO', 6: 'Matrice100', 7: 'Phantom4', 8: 'LB2', 9: 'Inspire1Pro', 10: 'A3',
    11: 'Matrice600', 12: 'Phantom34K', 13: 'MavicPro', 14: 'ZenmuseXT', 15: 'Inspire1RAW',
    16: 'A2', 17: 'Inspire2', 18: 'OSMOPro', 19: 'OSMORaw', 20: 'OSMOPlus', 21: 'Mavic',
    22: 'OSMOMobile', 23: 'OrangeCV600', 24: 'Phantom4Pro', 25: 'N3FC', 26: 'Spark',
    27: 'Matrice600Pro', 28: 'Phantom4Advanced', 29: 'Phantom3SE', 30: 'AG405',
    31: 'Matrice200', 33: 'Matrice210', 34: 'Matrice210RTK', 38: 'MavicAir', 42: 'Mavic2',
    44: 'Phantom4ProV2', 46: 'Phantom4RTK', 57: 'Phantom4Multispectral',
    58: 'Mavic2Enterprise', 59: 'MavicMini', 60: 'Matrice200V2', 61: 'Matrice210V2',
    62: 'Matrice210RTKV2', 67: 'MavicAir2', 70: 'Matrice300RTK', 73: 'FPV', 75: 'MavicAir2S',
    76: 'Mini2', 77: 'Mavic3', 96: 'MiniSE', 103: 'Mini3Pro', 111: 'Mavic3Pro',
    113: 'Mini2SE', 116: 'Matrice30', 118: 'Mavic3Enterprise', 121: 'Avata',
    126: 'Mini4Pro', 152: 'Avata2', 170: 'Matrice350RTK'}
_PLATFORMS = {1: 'IOS', 2: 'Android', 6: 'DJIFly', 10: 'Windows', 11: 'Mac', 12: 'Linux'}
_COMPONENTS = {1: 'Camera', 2: 'Aircraft', 3: 'RC', 4: 'Battery'}
_SENDERS = {0: 'None', 1: 'Camera', 3: 'MC', 4: 'Gimbal', 6: 'RC', 11: 'Battery'}

# Details offsets after the four location strings, from layout/details.rs.
# Version 6 and later read these fields in sequence; version 5 and earlier
# seek to fixed offsets. Values are (offset, size).
_DETAIL_IDS = {
    True: {'takeoff_altitude': (267, 4), 'product_type': (271, 1), 'aircraft_name': (280, 32),
           'aircraft_sn': (312, 16), 'camera_sn': (328, 16), 'rc_sn': (344, 16),
           'battery_sn': (360, 16), 'app_platform': (376, 1), 'app_version': (377, 3)},
    False: {'takeoff_altitude': (352, 4), 'product_type': (277, 1), 'aircraft_name': (278, 24),
            'aircraft_sn': (267, 10), 'camera_sn': (318, 10), 'rc_sn': (328, 10),
            'battery_sn': (338, 10), 'app_platform': (348, 1), 'app_version': (349, 3)},
}


def _utc(milliseconds):
    try:
        value = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=milliseconds)
        return value if 2010 < value.year < 2100 else None
    except (OverflowError, ValueError):
        return None


def _crc64(value, data):
    """CRC64/Jones reflected recurrence, caller-supplied seed, no final XOR."""
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ (0x95AC9329AC4BC9B5 if value & 1 else 0)
    return value


@lru_cache(maxsize=65536)
def _xor_key(record_type, first):
    magic = (0x123456789ABCDEF0 * first) & 0xFFFFFFFFFFFFFFFF
    return _crc64((first + record_type) & 255, struct.pack('<Q', magic)).to_bytes(8, 'little')


def _xor(record_type, payload):
    if not payload:
        raise ValueError('XOR payload lacks key byte')
    key = _xor_key(record_type, payload[0])
    return bytes(byte ^ key[i % 8] for i, byte in enumerate(payload[1:]))


def _decode(record_type, payload, version):
    if version <= 6:
        return payload
    if len(payload) < 2:
        raise ValueError('XOR payload lacks framing bytes')
    return _xor(record_type, payload[:-1])


def _number(value):
    return value if math.isfinite(value) else None


def _position(lat, lon):
    """Return (lat, lon) when plottable, else (None, None)."""
    if (math.isfinite(lat) and math.isfinite(lon) and abs(lat) <= 90 and abs(lon) <= 180
            and (lat != 0 or lon != 0)):
        return lat, lon
    return None, None


def _text(data, offset, size):
    return data[offset:offset + size].split(b'\0')[0].decode('utf-8', errors='replace')


def _enum(table, value):
    return f'{table[value]} ({value})' if value in table else f'Unknown ({value})'


def _detail_ids(detail_data, version):
    """Identifiers stored after the flight totals; blank when the block is too short."""
    layout = _DETAIL_IDS[version >= 6]
    values = {}
    for name, (offset, size) in layout.items():
        if offset + size > len(detail_data):
            values[name] = None
        elif name == 'takeoff_altitude':
            values[name] = _number(struct.unpack_from('<f', detail_data, offset)[0])
        elif name == 'product_type':
            values[name] = _enum(_PRODUCT_TYPES, detail_data[offset])
        elif name == 'app_platform':
            values[name] = _enum(_PLATFORMS, detail_data[offset])
        elif name == 'app_version':
            values[name] = '.'.join(str(byte) for byte in detail_data[offset:offset + size])
        else:
            values[name] = _text(detail_data, offset, size)
    return values


def parse_txt(data):
    """Return (summary dictionary, record dictionaries). Never consult external keys.

    Stop at damaged framing: scanning for a plausible next record would risk
    reporting random bytes as evidence. Earlier valid records remain available.
    """
    if len(data) < 12:
        raise ValueError('Truncated DJI TXT prefix')
    detail_offset, detail_length, version = struct.unpack_from('<QHB', data)
    if not 1 <= version <= 14:
        raise ValueError(f'Unsupported DJI TXT version {version}')
    start = 12 if version < 6 else 100 if version < 12 else 536 if version == 12 else detail_offset
    end = detail_offset if version < 12 else len(data)
    details = detail_offset if version < 12 else 100
    if version >= 13:
        if len(data) < 104 or data[100] != 0:
            raise ValueError('Missing Auxiliary Info; records are encrypted')
        size = struct.unpack_from('<H', data, 101)[0]
        aux_end = 103 + size
        if aux_end > len(data):
            raise ValueError('Truncated Auxiliary Info; records are encrypted')
        auxiliary = _xor(0, data[103:aux_end])
        if len(auxiliary) < 5:
            raise ValueError('Short Auxiliary Info; records are encrypted')
        info_length = struct.unpack_from('<H', auxiliary, 1)[0]
        if 3 + info_length + 2 > len(auxiliary):
            raise ValueError('Truncated auxiliary Details; records are encrypted')
        detail_data = auxiliary[3:3 + info_length]
        if start == 0:
            if aux_end + 3 > len(data) or data[aux_end] != 1:
                raise ValueError('Missing Auxiliary Version; records are encrypted')
            start = aux_end + 3 + struct.unpack_from('<H', data, aux_end + 1)[0]
        if start < aux_end:
            raise ValueError('Records overlap Auxiliary Info; records are encrypted')
    else:
        detail_data = data[details:len(data) if version < 12 else start]
    # Require the known metadata prefix; never pad damaged evidence with zeros.
    detail_end = len(data) if version < 12 else start
    if not (12 <= details <= detail_end <= len(data)) or len(detail_data) < 139:
        raise ValueError('Invalid or truncated DJI Details section')
    if not (start <= end <= len(data)) or (version >= 6 and start < 100):
        raise ValueError('Invalid DJI record bounds')
    if version < 12 and start > details:
        raise ValueError('Records overlap Details section')
    summary = {'version': version, 'detail_length': detail_length,
               'timestamp': _utc(struct.unpack_from('<q', detail_data, 91)[0]),
               'status': 'Encrypted records; DJI keychain required; telemetry not decoded' if version >= 13 else 'Parsed offline',
               'record_count': 0, 'timestamped_count': 0, 'warnings': [], 'not_reported': ''}
    for name, offset in (('sub_street', 0), ('street', 20), ('city', 40), ('area', 60)):
        summary[name] = _text(detail_data, offset, 20)
    lon, lat, distance, duration, height, hs, vs, photos = struct.unpack_from('<ddfifffi', detail_data, 99)
    summary.update(latitude=_number(lat) if abs(lat) <= 90 else None,
                   longitude=_number(lon) if abs(lon) <= 180 else None,
                   distance_m=_number(distance), duration_s=duration / 1000,
                   max_height_m=_number(height), max_horizontal_speed_ms=_number(hs),
                   max_vertical_speed_ms=_number(vs), photo_count=photos,
                   video_time_s=struct.unpack_from('<q', detail_data, 139)[0] if len(detail_data) >= 147 else None)
    summary.update(_detail_ids(detail_data, version))
    if summary['timestamp'] is None:
        summary['warnings'].append('Invalid Details start timestamp')
    rows = []
    if version >= 13:
        return summary, rows
    pos, timestamp, stopped = start, None, None
    not_reported = Counter()
    while pos < end:
        # DF020 iOS v8 stores this four-byte prefix before eight raw JPEGs.
        # Match the observed prefix and SOI exactly; do not scan past corruption.
        if data[pos:pos + 6] == b'\x39\x30\x00\x00\xff\xd8':
            pos += 4
        # Embedded JPEGs have separate framing, not the binary record length.
        if data[pos:pos + 2] == b'\xff\xd8':
            jpeg_end = data.find(b'\xff\xd9', pos + 2, end)
            if jpeg_end < 0:
                summary['warnings'].append(f'JPEG at offset {pos} has no end marker before the end of the record area')
                stopped = pos
                break
            rows.append({'offset': pos, 'type': None, 'name': 'Embedded JPEG',
                         'timestamp': timestamp, 'timestamp_basis': 'Preceding Custom record' if timestamp else 'Unavailable',
                         'status': 'Image retained in source; not extracted'})
            pos = jpeg_end + 2
            continue
        if pos + 3 > end:
            summary['warnings'].append(f'{end - pos} bytes at offset {pos} are too few for a record header')
            stopped = pos
            break
        kind, length = data[pos:pos + 2]
        next_pos = pos + 3 + length
        if next_pos > end:
            summary['warnings'].append(f'Record at offset {pos} declares {3 + length} bytes; '
                                       f'{end - pos} remain before the end of the record area')
            stopped = pos
            break
        if data[next_pos - 1] != 255:
            summary['warnings'].append(f'Record at offset {pos} lacks its 0xFF terminator')
            stopped = pos
            break
        if kind not in _RECORD_NAMES:
            not_reported[kind] += 1
            pos = next_pos
            continue
        row = {'offset': pos, 'type': kind, 'name': _RECORD_NAMES[kind],
               'timestamp': timestamp, 'timestamp_basis': 'Preceding Custom record' if timestamp else 'Unavailable',
               'status': 'Decoded', 'payload_hex': ''}
        try:
            payload = _decode(kind, data[pos + 2:next_pos - 1], version)
            row['payload_hex'] = payload.hex()
            if kind == 1:
                if len(payload) < 50:
                    raise ValueError('Short OSD payload')
                lon, lat, altitude, sx, sy, sz, pitch, roll, yaw = struct.unpack_from('<dd7h', payload)
                lat, lon = _position(math.degrees(lat), math.degrees(lon))
                row.update(latitude=lat, longitude=lon,
                           altitude=altitude / 10, speed=math.hypot(sx, sy) / 10,
                           speed_x=sx / 10, speed_y=sy / 10, speed_z=sz / 10,
                           pitch=pitch / 10, roll=roll / 10, heading=yaw / 10,
                           satellites=payload[36], battery=payload[40], flight_time=struct.unpack_from('<H', payload, 42)[0] / 10)
                if lat is None:
                    row['status'] = 'Decoded; position unavailable or invalid'
            elif kind == 3:
                if len(payload) < 6:
                    raise ValueError('Short Gimbal payload')
                p, r, y = struct.unpack_from('<3h', payload)
                row.update(gimbal_pitch=p / 10, gimbal_roll=r / 10, gimbal_yaw=y / 10)
            elif kind == 2:
                if len(payload) < 24:
                    raise ValueError('Short Home payload')
                lon, lat, altitude = struct.unpack_from('<ddf', payload)
                lat, lon = _position(math.degrees(lat), math.degrees(lon))
                row.update(home_latitude=lat, home_longitude=lon,
                           home_altitude=_number(altitude / 10), home_recorded=bool(payload[20] & 1),
                           return_height=struct.unpack_from('<H', payload, 22)[0])
            elif kind == 4:
                if len(payload) < 13:
                    raise ValueError('Short RC payload')
                a, e, t, r, g = struct.unpack_from('<5H', payload)
                row.update(rc_aileron=a, rc_elevator=e, rc_throttle=t, rc_rudder=r, rc_gimbal=g,
                           rc_return=bool(payload[11] & 8), rc_shutter=bool(payload[12] & 64),
                           rc_record=bool(payload[12] & 128))
            elif kind == 8:
                if len(payload) < 27:
                    raise ValueError('Short Smart Battery payload')
                row.update(battery_time=struct.unpack_from('<H', payload)[0],
                           battery_voltage=struct.unpack_from('<H', payload, 24)[0] / 1000,
                           battery_percent=payload[26])
            elif kind == 25:
                if len(payload) < 2:
                    raise ValueError('Short Camera payload')
                # Photo state is a multibit enum: only state 1 means single photo.
                row.update(camera_photo=((payload[0] & 56) >> 3) == 1,
                           camera_recording=bool(payload[0] & 192), camera_sd=bool(payload[1] & 2))
                if len(payload) >= 24:
                    row.update(camera_mode=payload[4], camera_record_time=struct.unpack_from('<H', payload, 21)[0])
            elif kind == 5:
                if len(payload) < 18:
                    raise ValueError('Short Custom payload')
                hs, distance, ms = struct.unpack_from('<ffq', payload, 2)
                timestamp = _utc(ms)
                row.update(timestamp=timestamp, timestamp_basis='Custom record UTC' if timestamp else 'Invalid Custom timestamp',
                           custom_speed=_number(hs), custom_distance=_number(distance))
                if timestamp is None:
                    row['status'] = 'Invalid Custom timestamp'
            elif kind == 14:
                if len(payload) < 16:
                    raise ValueError('Short App GPS payload')
                # dji-log-parser and pydjirecord name the first double longitude, and
                # neither frame builder reads it. In all three DF020 logs the first
                # double is the latitude of the same site as OSD, Home and RC GPS.
                lat, lon = _position(*struct.unpack_from('<dd', payload))
                row.update(app_latitude=lat, app_longitude=lon)
                if lat is None:
                    row['status'] = 'Decoded; position unavailable or invalid'
            elif kind == 11:
                if len(payload) < 30:
                    raise ValueError('Short RC GPS payload')
                hour, minute, second, year, month, day, lat, lon = struct.unpack_from('<3BH2B2i', payload)
                lat, lon = _position(lat / 1e7, lon / 1e7)
                row.update(rc_gps_time=f'{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}',
                           rc_latitude=lat, rc_longitude=lon, rc_satellites=payload[23],
                           rc_accuracy=_number(struct.unpack_from('<f', payload, 24)[0]),
                           rc_valid=struct.unpack_from('<H', payload, 28)[0])
                if lat is None:
                    row['status'] = 'Decoded; position unavailable or invalid'
            elif kind == 40:
                if len(payload) < 3 or len(payload) < 3 + payload[2]:
                    raise ValueError('Short Component Serial payload')
                row.update(component=_enum(_COMPONENTS, struct.unpack_from('<H', payload)[0] & 255),
                           serial=_text(payload, 3, payload[2]))
            elif kind == 15:
                if len(payload) < 6:
                    raise ValueError('Short Firmware payload')
                # The references read one 6-byte entry; DF020 payloads hold several.
                whole = len(payload) - len(payload) % 6
                row['firmware'] = '; '.join(
                    f'{_enum(_SENDERS, payload[k])} / {payload[k + 1]}: '
                    + '.'.join(str(byte) for byte in payload[k + 2:k + 5])
                    for k in range(0, whole, 6))
                if whole < len(payload):
                    row['status'] = f'Decoded; {len(payload) - whole} trailing bytes are not a whole entry'
            elif kind in (9, 10, 24):
                row['message'] = payload.decode('utf-8', errors='replace').rstrip('\0')
            else:
                row['status'] = 'Payload retained; fields not yet implemented'
        except (ValueError, struct.error) as exc:
            row['status'] = str(exc)
            if kind == 5:
                timestamp = None
                row.update(timestamp=None, timestamp_basis='Invalid Custom record')
        rows.append(row)
        pos = next_pos
    summary['record_count'] = len(rows)
    summary['timestamped_count'] = sum(row.get('timestamp') is not None for row in rows)
    summary['not_reported'] = '; '.join(f'type {kind}: {count}' for kind, count in sorted(not_reported.items()))
    if stopped is not None:
        summary['status'] = f'Parsing stopped {end - stopped} bytes before the end of the record area; see Warnings'
    return summary, rows


def _files(context):
    for path in dict.fromkeys(str(p) for p in context.get_files_found()):
        if not os.path.basename(path).startswith('DJIFlightRecord') or not path.lower().endswith('.txt'):
            continue
        if os.path.isdir(path):
            continue
        relative = str(context.get_relative_path(path)).replace('\\', '/')
        try:
            with open(path, 'rb') as handle:
                summary, rows = parse_txt(handle.read())
            yield path, relative, summary, rows
        except (OSError, ValueError, struct.error) as exc:
            logfunc(f'DJI TXT: {relative}: {exc}')
            yield path, relative, {'status': f'Could not parse: {exc}'}, []


@artifact_processor
def djiFlightRecordTxtRecords(context):
    fields = ('timestamp', 'latitude', 'longitude', 'altitude', 'speed', 'heading',
              'gimbal_pitch', 'gimbal_roll', 'gimbal_yaw', 'speed_x', 'speed_y', 'speed_z',
              'pitch', 'roll', 'satellites', 'battery', 'flight_time',
              'home_latitude', 'home_longitude', 'home_altitude', 'home_recorded', 'return_height',
              'app_latitude', 'app_longitude',
              'rc_gps_time', 'rc_latitude', 'rc_longitude', 'rc_satellites', 'rc_accuracy', 'rc_valid',
              'component', 'serial', 'firmware',
              'rc_aileron', 'rc_elevator', 'rc_throttle', 'rc_rudder', 'rc_gimbal',
              'rc_return', 'rc_shutter', 'rc_record', 'battery_percent', 'battery_voltage', 'battery_time',
              'camera_photo', 'camera_recording', 'camera_sd', 'camera_mode', 'camera_record_time',
              'custom_speed', 'custom_distance',
              'type', 'name', 'offset', 'timestamp_basis', 'status', 'message', 'payload_hex')
    headers = (('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Relative Height (m)',
               'Horizontal Speed (m/s, derived)', 'Yaw (degrees)', 'Gimbal Pitch (degrees)',
               'Gimbal Roll (degrees)', 'Gimbal Yaw (degrees)', 'Speed X (m/s)', 'Speed Y (m/s)',
               'Speed Z (m/s)', 'Pitch (degrees)', 'Roll (degrees)', 'GPS Satellites',
               'OSD Battery (as stored)', 'Flight Time (s)',
               'Home Latitude', 'Home Longitude', 'Home Altitude (m)', 'Home Recorded', 'Return Height (m)',
               'App GPS Latitude', 'App GPS Longitude',
               'RC GPS Date and Time (as stored)', 'RC GPS Latitude', 'RC GPS Longitude',
               'RC GPS Satellites', 'RC GPS Accuracy (m)', 'RC GPS Valid Data (as stored)',
               'Component', 'Serial Number', 'Firmware Entries',
               'RC Aileron (raw)', 'RC Elevator (raw)', 'RC Throttle (raw)', 'RC Rudder (raw)', 'RC Gimbal (raw)',
               'RC Return Button', 'RC Shutter Button', 'RC Record Button',
               'Battery Percent', 'Battery Voltage (stored / 1000)', 'Battery Useful Time (as stored)',
               'Camera Single Photo', 'Camera Recording', 'Camera SD Present', 'Camera Mode (raw)', 'Camera Record Time (s)',
               'Custom Horizontal Speed (as stored)', 'Custom Distance (as stored)',
               'Record Type', 'Record Name',
               'Record Offset', 'Timestamp Basis', 'Decode Status', 'Message', 'Decoded Payload Hex',
               'Log Version', 'Source File')
    output, sources = [], []
    for path, relative, summary, rows in _files(context):
        sources.append(path)
        output.extend(tuple(row.get(field) for field in fields)
                      + (summary['version'], relative) for row in rows)
    return headers, output, '\n'.join(sources)


@artifact_processor
def djiFlightRecordTxtSummary(context):
    fields = ('timestamp', 'version', 'status', 'aircraft_name', 'product_type', 'aircraft_sn',
              'camera_sn', 'rc_sn', 'battery_sn', 'app_platform', 'app_version',
              'record_count', 'timestamped_count',
              'latitude', 'longitude', 'distance_m', 'duration_s', 'max_height_m',
              'max_horizontal_speed_ms', 'max_vertical_speed_ms', 'photo_count', 'video_time_s',
              'takeoff_altitude', 'sub_street', 'street', 'city', 'area', 'not_reported')
    headers = (('Timestamp', 'datetime'), 'Log Version', 'Status', 'Aircraft Name', 'Product Type',
               'Aircraft Serial Number', 'Camera Serial Number', 'RC Serial Number',
               'Battery Serial Number', 'App Platform', 'App Version',
               'Record Count', 'Timestamped Records',
               'Latitude', 'Longitude', 'Total Distance (m)', 'Total Time (s)',
               'Maximum Height (m)', 'Maximum Horizontal Speed (m/s)',
               'Maximum Vertical Speed (m/s)', 'Photos Taken', 'Video Time (s, as stored)',
               'Takeoff Altitude (as stored)', 'Sub Street', 'Street', 'City', 'Area',
               'Records Not Reported', 'Warnings', 'Source File')
    output, sources = [], []
    for path, relative, summary, _ in _files(context):
        sources.append(path)
        output.append(tuple(summary.get(field) for field in fields)
                      + ('; '.join(summary.get('warnings', [])), relative))
    return headers, output, '\n'.join(sources)
