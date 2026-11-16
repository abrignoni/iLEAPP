"""MapsSync placeRequest payloads embedded in storage BLOBs yield the sent and raw query text."""
import base64
import inspect
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import mapsSync


def _length_delim(field, value):
    key = field << 3 | 2
    head = b''
    while True:
        part = key & 0x7F
        key >>= 7
        head += bytes([part | (0x80 if key else 0)])
        if not key:
            break
    return head + bytes([len(value)]) + value


def place_request_payload(sent=None, raw=None):
    """Build a request with field 8.1.3 = sent text and field 8.1.7.10000 = raw text."""
    inner = b''
    if sent is not None:
        inner += _length_delim(3, sent.encode() if isinstance(sent, str) else sent)
    if raw is not None:
        inner += _length_delim(7, _length_delim(10000, raw.encode() if isinstance(raw, str) else raw))
    return _length_delim(8, _length_delim(1, inner))


def embed(payload):
    return b'https://gsp.apple.com/path?placeRequest=' + base64.b64encode(payload) + b'&other=1'


def make_store(path, mapitem_blob=None, journey_blob=None, with_lat1=True):
    """A modern store, or with with_lat1=False the iOS 16 and 17 shape that has no ZLATITUDE1."""
    connection = sqlite3.connect(path)
    second = 'ZLATITUDE1, ZLONGITUDE1, ' if with_lat1 else ''
    connection.execute('CREATE TABLE ZHISTORYITEM (Z_PK, ZCREATETIME, ZMODIFICATIONTIME, ZQUERY, '
                       'ZLATITUDE, ZLONGITUDE, ZMAPITEM, Z_ENT, ZLOCATIONDISPLAY, ' + second +
                       'ZROUTEREQUESTSTORAGE)')
    connection.execute('CREATE TABLE ZMIXINMAPITEM (Z_PK, ZMAPITEMSTORAGE)')
    connection.execute('INSERT INTO ZMIXINMAPITEM VALUES (1, ?)', (mapitem_blob,))
    filler = 'NULL, NULL, ' if with_lat1 else ''
    connection.execute('INSERT INTO ZHISTORYITEM VALUES (1, 700000000, 700000001, NULL, 40, -74, 1, 20, '
                       "'display', " + filler + '?)', (journey_blob,))
    connection.execute('CREATE TABLE Z_PRIMARYKEY (Z_ENT, Z_NAME)')
    connection.execute("INSERT INTO Z_PRIMARYKEY VALUES (20, 'HistoryPlaceItem')")
    connection.commit()
    return connection


def run_module(main):
    context = SimpleNamespace(get_files_found=lambda: [str(main)],
                              get_relative_path=lambda path: Path(path).name)
    headers, rows, _ = inspect.unwrap(mapsSync.mapsSync)(context)
    return headers, rows


class TestMapsSyncPlaceQueries(unittest.TestCase):
    def check_row(self, mapitem_blob, journey_blob, expected, with_lat1=True):
        with tempfile.TemporaryDirectory() as directory:
            main = Path(directory) / 'MapsSync_0.0.1'
            connection = make_store(main, mapitem_blob, journey_blob, with_lat1)
            try:
                headers, rows = run_module(main)
                self.assertEqual(len(rows), 1)
                self.assertEqual((rows[0][7], rows[0][8]), expected)
            finally:
                connection.close()
        return headers

    def test_mapitem_blob_sent_and_raw(self):
        headers = self.check_row(embed(place_request_payload('Sample Diner', 'Samp')),
                                 None, ('Sample Diner', 'Samp'))
        self.assertEqual(headers[7:9], ('Query (Sent)', 'Query (Raw)'))

    def test_journey_blob_carries_queries_when_mapitem_empty(self):
        self.check_row(None, embed(place_request_payload('Springfield, ZZ Testland', 'Spring')),
                       ('Springfield, ZZ Testland', 'Spring'))

    def test_sent_only_when_raw_field_absent(self):
        self.check_row(embed(place_request_payload('example town')), None, ('example town', ''))

    def test_no_payload_yields_empty_columns(self):
        self.check_row(b'blob without any request', None, ('', ''))

    def test_first_payload_without_query_skipped_for_later_one(self):
        earlier = _length_delim(8, _length_delim(1, _length_delim(2, b'other')))
        self.check_row(embed(earlier) + b'&x=2&' + embed(place_request_payload('test cafes', 'test')),
                       None, ('test cafes', 'test'))

    def test_undecodable_payload_yields_empty_columns(self):
        self.check_row(b'placeRequest=A', None, ('', ''))

    def test_non_utf8_query_decodes_without_crash(self):
        self.check_row(embed(place_request_payload(b'\xff\xfe bad')),
                       None, ('\ufffd\ufffd bad', ''))

    def test_store_without_latitude1_still_reads_blobs(self):
        self.check_row(embed(place_request_payload('Springfield, ZZ Testland', 'Spring')), None,
                       ('Springfield, ZZ Testland', 'Spring'), with_lat1=False)

    def test_text_that_parses_as_a_message_is_kept_as_text(self):
        # 'h1h2h3' is also a valid protobuf message (field 13, three varints).
        self.check_row(embed(place_request_payload('Springfield, ZZ', 'h1h2h3')), None, ('Springfield, ZZ', 'h1h2h3'))

    def test_distinct_queries_from_every_payload_are_joined(self):
        self.check_row(embed(place_request_payload('test cafes', 'test')),
                       embed(place_request_payload('Springfield, ZZ', 'Spr')) +
                       embed(place_request_payload('test cafes', 'test')),
                       ('Springfield, ZZ; test cafes', 'Spr; test'))  # journey BLOB first


if __name__ == '__main__':
    unittest.main()
