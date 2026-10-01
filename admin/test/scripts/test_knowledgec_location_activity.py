"""knowledgeC - Location Activity reports every coordinate pair in the compressed payload.

A /app/locationActivity row names a place in its structured metadata, and the user
activity's required string can carry a compressed protobuf ('bs'=$<base64>$: four bytes,
then bzip2) holding further coordinate pairs. A tool that reads coordinates from that
payload can show a place's name beside coordinates that are not the place's, so the
artifact lists the other pairs with their distance from the place coordinates.
"""
import base64
import bz2
import pathlib
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


def _message(field, body):
    return _varint(field << 3 | 2) + _varint(len(body)) + body


def _pair(lat, lon):
    return _double(1, lat) + _double(2, lon)


PLACE = (41.889727, -87.624258)
FAR = (48.858370, 2.294481)


def _payload():
    """Field 1.5 holds a pair far from the place, field 8.1 the place itself, field 3 a
    string, and the top level carries doubles in fields 1 and 2 that are not a nested pair."""
    body = (_double(1, 12.5) + _double(2, 45.0)
            + _message(1, _message(5, _pair(*FAR)))
            + _message(3, b'Marked Location')
            + _message(8, _message(1, _pair(*PLACE)))
            + _message(9, _message(1, _pair(95.0, 10.0))))
    return body


def _required_string(payload):
    raw = b'\x00\x00\x00\x00' + bz2.compress(payload)
    return ("v1.0/com.apple.Maps/t='Marked%20Location'&u={'bs'=$"
            + base64.b64encode(raw).decode() + "$}")


class TestPayloadHelpers(unittest.TestCase):

    def test_nested_pairs_are_found_with_their_paths(self):
        pairs = knowledgeC._pb_coordinate_pairs(_payload())  # pylint: disable=protected-access
        self.assertEqual([(p, round(a, 6), round(b, 6)) for p, a, b in pairs],
                         [('1.5', *FAR), ('8.1', *PLACE)])

    def test_truncated_bytes_give_no_pairs(self):
        self.assertEqual(knowledgeC._pb_coordinate_pairs(_payload()[:-3]), [])  # pylint: disable=protected-access

    def test_payload_statuses(self):
        decode = knowledgeC._location_activity_payload  # pylint: disable=protected-access
        self.assertEqual(decode("v1.0/com.apple.Maps/t='x'&u={}"), (None, 'Not present'))
        body, status = decode(_required_string(_payload()))
        self.assertEqual((body, status), (_payload(), 'Decoded'))
        wrong = "'bs'=$" + base64.b64encode(b'\x00' * 12).decode() + '$'
        self.assertEqual(decode(wrong), (None, 'Not decoded (no bzip2 header after the first 4 bytes)'))


class TestLocationActivityRows(unittest.TestCase):

    def _run(self, with_uuid_column=True):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'knowledgeC.db'
            db = sqlite3.connect(path)
            uuid_col = f', {A}USERACTIVITYUUID TEXT' if with_uuid_column else ''
            db.execute(f'CREATE TABLE ZSTRUCTUREDMETADATA (Z_PK INTEGER PRIMARY KEY, {L}LOCATIONNAME TEXT, '
                       f'{L}DISPLAYNAME TEXT, {L}FULLYFORMATTEDADDRESS TEXT, {L}LATITUDE REAL, '
                       f'{L}LONGITUDE REAL, {A}USERACTIVITYREQUIREDSTRING TEXT{uuid_col})')
            db.execute('CREATE TABLE ZOBJECT (Z_PK INTEGER PRIMARY KEY, ZSTARTDATE REAL, ZCREATIONDATE REAL, '
                       'ZVALUESTRING TEXT, ZSTREAMNAME TEXT, ZSTRUCTUREDMETADATA INTEGER)')
            values = [1, 'Marked Location', 'Marked Location', '400 N Michigan Ave, Chicago', *PLACE,
                      _required_string(_payload())]
            if with_uuid_column:
                values.append('ABC')
            db.execute(f'INSERT INTO ZSTRUCTUREDMETADATA VALUES ({",".join("?" * len(values))})', values)
            db.execute("INSERT INTO ZOBJECT VALUES (1, 780000000, 780000012.5, 'com.apple.Maps', "
                       "'/app/locationActivity', 1)")
            db.execute("INSERT INTO ZOBJECT VALUES (2, 780000060, 780000070, 'com.apple.Maps', "
                       "'/app/usage', NULL)")
            db.commit()
            db.close()
            Context.clear()
            Context.set_files_found([str(path)])
            headers, data_list, source = knowledgeC.knowledgeC_LocationActivity.__wrapped__(Context)
        return headers, data_list, source, str(path)

    def test_row_reports_the_place_and_the_far_pair(self):
        headers, data_list, source, path = self._run()
        self.assertEqual(source, path)
        self.assertEqual(len(data_list), 1)
        row = dict(zip([h[0] if isinstance(h, tuple) else h for h in headers], data_list[0]))
        self.assertEqual((row['Place Latitude'], row['Place Longitude']), PLACE)
        self.assertEqual(row['Compressed Payload'], 'Decoded')
        self.assertEqual(row['Activity UUID'], 'ABC')
        # the pair equal to the place (8.1) is left out; the far pair is listed with its distance
        self.assertEqual(row['Other Coordinate Pairs in Payload'].count('\n'), 0)
        self.assertIn('48.858370, 2.294481', row['Other Coordinate Pairs in Payload'])
        self.assertIn('field 1.5', row['Other Coordinate Pairs in Payload'])
        self.assertGreater(row['Farthest Other Pair (m)'], 6_000_000)

    def test_a_missing_metadata_column_is_reported_blank(self):
        headers, data_list, _, _ = self._run(with_uuid_column=False)
        row = dict(zip([h[0] if isinstance(h, tuple) else h for h in headers], data_list[0]))
        self.assertIsNone(row['Activity UUID'])
        self.assertEqual(row['Location Name'], 'Marked Location')


if __name__ == '__main__':
    unittest.main()
