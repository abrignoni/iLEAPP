"""knowledgeC - Location Activity decodes the required string and its Maps payload by field.

A /app/locationActivity row names a place in its structured metadata. The user activity's
required string (v1.0/<type>/name=value&...) can carry a user-info value bs: a 4-byte
little-endian length, then bzip2 of a MapsActivity protobuf. All values here are synthetic.
"""
import base64
import bz2
import pathlib
import plistlib
import sqlite3
import struct
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import knowledgeC  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

L = 'Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__'
A = 'Z_DKAPPLICATIONACTIVITYMETADATAKEY__'
PLACE = (10.5, 20.25)
PIN = (10.75, 20.5)
CAMERA = (11.0, 21.0)
WAYPOINT = (12.5, 22.5)
PIN_TIME = 780000030.5


def _varint(value):
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _double(field, value):
    return _varint(field << 3 | 1) + struct.pack('<d', value)


def _number(field, value):
    return _varint(field << 3) + _varint(value)


def _message(field, body):
    return _varint(field << 3 | 2) + _varint(len(body)) + body


def _pair(lat, lon):
    return _double(1, lat) + _double(2, lon)


def _map_item(name):
    localized = _message(3, name.encode())
    entity = _message(10, localized)
    value = _message(1, entity)
    component = _message(8, value)
    return _message(1, _message(4, component))


def _payload():
    camera = _message(5, _pair(*CAMERA))
    pin = _message(1, _pair(*PIN)) + _double(3, PIN_TIME)
    typed = _message(1, _number(5, 1))
    waypoint = typed + _message(2, _map_item('Synthetic Stop')) + _message(3, _pair(*WAYPOINT))
    plan = _message(1, _message(1, waypoint))
    return (_message(1, camera) + _message(3, b'synthetic search')
            + _message(4, _map_item('Synthetic Result')) + _message(4, _map_item('Second Result'))
            + _message(7, plan) + _message(8, pin) + _message(11, _map_item('Synthetic Place')))


def _framed(payload, declared=None):
    size = len(payload) if declared is None else declared
    return struct.pack('<I', size) + bz2.compress(payload)


def _required_string(data):
    return ("v1.0/com.example.activity/t='Synthetic%20Title'&u={'bs'=$"
            + base64.b64encode(data).decode() + "$,'other'='x'}")


def _phones(*numbers):
    objects = ['$null', {'NS.objects': [plistlib.UID(i + 2) for i in range(len(numbers))]}, *numbers]
    return plistlib.dumps({'$top': {'root': plistlib.UID(1)}, '$objects': objects}, fmt=plistlib.FMT_BINARY)


class TestPayloadHelpers(unittest.TestCase):
    decode = staticmethod(knowledgeC._location_activity_payload)  # pylint: disable=protected-access

    def test_fields_are_read_by_name(self):
        message, status = self.decode(_required_string(_framed(_payload())))
        self.assertEqual(status, 'Decoded')
        first = knowledgeC._maps_first  # pylint: disable=protected-access
        self.assertEqual(first(message, 'searchString'), 'synthetic search')
        self.assertEqual(first(message, 'droppedPin', 'latLng', 'lat'), PIN[0])
        self.assertEqual(first(message, 'droppedPin', 'timestamp'), PIN_TIME)
        self.assertEqual(len(message['searchPlaces']), 2)
        self.assertNotIn('displayOptions', message)

    def test_absent_values(self):
        for text in (None, '', "v1.0/com.example.activity/t='x'&u={}", "v1.0/com.example.activity/t='x'"):
            self.assertEqual(self.decode(text), (None, 'Not present'))

    def test_a_bs_text_outside_user_info_is_not_a_payload(self):
        encoded = base64.b64encode(_framed(_payload())).decode()
        self.assertEqual(self.decode(f"v1.0/com.example.activity/t='bs'&url=$" + encoded + '$'),
                         (None, 'Not present'))

    def test_wrong_length_is_reported(self):
        self.assertEqual(self.decode(_required_string(_framed(_payload(), declared=0))),
                         (None, 'Not decoded (length mismatch)'))

    def test_bad_compressed_data_is_reported(self):
        self.assertEqual(self.decode(_required_string(b'\x00' * 12)), (None, 'Not decoded (bzip2)'))

    def test_bad_protobuf_is_reported(self):
        self.assertEqual(self.decode(_required_string(_framed(b'\xff' * 8))),
                         (None, 'Not decoded (protobuf)'))

    def test_malformed_strings_do_not_hang(self):
        for text in ("v1.0/x/u=(abc", "v1.0/x/u={'a'", 'v2.0/x/u={}', 'v1.0/noslash'):
            self.assertEqual(self.decode(text), (None, 'Not decoded (activity string)'))

    def test_undecodable_phone_blob_keeps_its_bytes(self):
        self.assertEqual(knowledgeC._keyed_archive_strings(b'\x01\x02'),  # pylint: disable=protected-access
                         'undecoded: 0102')


class TestLocationActivityRows(unittest.TestCase):

    def _run(self, with_uuid_column=True):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'knowledgeC.db'
            db = sqlite3.connect(path)
            uuid_col = f', {A}USERACTIVITYUUID TEXT' if with_uuid_column else ''
            db.execute('CREATE TABLE Z_PRIMARYKEY (Z_ENT INTEGER, Z_NAME TEXT)')
            db.execute("INSERT INTO Z_PRIMARYKEY VALUES (5, 'Event'), (6, 'Other')")
            db.execute('CREATE TABLE ZSOURCE (Z_PK INTEGER PRIMARY KEY, ZDEVICEID TEXT)')
            db.execute(f'CREATE TABLE ZSTRUCTUREDMETADATA (Z_PK INTEGER PRIMARY KEY, {L}LOCATIONNAME TEXT, '
                       f'{L}DISPLAYNAME TEXT, {L}FULLYFORMATTEDADDRESS TEXT, {L}LATITUDE REAL, '
                       f'{L}LONGITUDE REAL, {L}PHONENUMBERS BLOB, {A}USERACTIVITYREQUIREDSTRING TEXT{uuid_col})')
            db.execute('CREATE TABLE ZOBJECT (Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, ZSTARTDATE REAL, ZENDDATE REAL, '
                       'ZCREATIONDATE REAL, ZLOCALCREATIONDATE REAL, ZSECONDSFROMGMT INTEGER, ZVALUESTRING TEXT, '
                       'ZVALUEINTEGER INTEGER, ZVALUEDOUBLE REAL, ZUUID TEXT, ZSTREAMNAME TEXT, ZSOURCE INTEGER, '
                       'ZSTRUCTUREDMETADATA INTEGER)')
            values = [1, 'Synthetic Place', 'Synthetic Display', '1 Example Road', *PLACE, _phones('555-0100', '555-0101'),
                      _required_string(_framed(_payload()))]
            if with_uuid_column:
                values.append('ABC')
            db.execute(f'INSERT INTO ZSTRUCTUREDMETADATA VALUES ({",".join("?" * len(values))})', values)
            insert = 'INSERT INTO ZOBJECT VALUES (?, ?, ?, ?, ?, NULL, 0, ?, NULL, NULL, ?, ?, NULL, ?)'
            db.execute(insert, (1, 5, 780000000, 780000000, 780000040.25, 'com.example.app', 'U1',
                                '/app/locationActivity', 1))
            db.execute(insert, (2, 5, 780000060, 780000070, 780000070, 'com.example.app', 'U2', '/app/usage', None))
            db.execute(insert, (3, 6, 780000000, 780000000, 780000000, 'com.example.app', 'U3',
                                '/app/locationActivity', 1))
            db.commit()
            db.close()
            Context.clear()
            Context.set_files_found([str(path)])
            headers, data_list, source = knowledgeC.knowledgeC_LocationActivity.__wrapped__(Context)
        return headers, data_list, source, str(path)

    def test_row_reports_each_field_under_its_name(self):
        headers, data_list, source, path = self._run()
        self.assertEqual(source, path)
        self.assertEqual(len(data_list), 1)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        self.assertEqual(len(names), len(data_list[0]))
        row = dict(zip(names, data_list[0]))
        self.assertEqual((row['Place Latitude'], row['Place Longitude']), PLACE)
        self.assertEqual((row['Dropped Pin Latitude'], row['Dropped Pin Longitude']), PIN)
        self.assertEqual(row['Dropped Pin Time'].isoformat(), '2025-09-19T18:40:30.500000+00:00')
        self.assertEqual(row['Created'].microsecond, 250000)
        self.assertEqual(row['Phone Numbers'], '555-0100; 555-0101')
        self.assertEqual(row['Maps Search String'], 'synthetic search')
        self.assertEqual(row['Presented Map Item'], 'Synthetic Place')
        self.assertEqual(row['Search Places in Payload'], 2)
        self.assertEqual(row['Directions Waypoints'],
                         f'Synthetic Stop | {WAYPOINT[0]}, {WAYPOINT[1]} | is_current_location=1')
        self.assertEqual(row['Payload Status'], 'Decoded')
        self.assertEqual(row['Activity UUID'], 'ABC')
        self.assertEqual(row['Bundle ID'], 'com.example.app')
        self.assertNotIn(str(CAMERA[0]), ' '.join(str(value) for value in data_list[0]))

    def test_a_missing_metadata_column_is_reported_blank(self):
        headers, data_list, _, _ = self._run(with_uuid_column=False)
        row = dict(zip([h[0] if isinstance(h, tuple) else h for h in headers], data_list[0]))
        self.assertIsNone(row['Activity UUID'])
        self.assertEqual(row['Location Name'], 'Synthetic Place')


if __name__ == '__main__':
    unittest.main()
