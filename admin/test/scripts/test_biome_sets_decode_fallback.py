"""The Set.db reader's fallback typedef follows a record's own top-level framing."""
# pylint: disable=protected-access
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import blackboxprotobuf
from scripts.artifacts import biomeSetsStores
from scripts.artifacts.biomeSetsStores import _nested, _top_level_typedef


class TestTopLevelTypedef(unittest.TestCase):

    def test_types_follow_wire_types(self):
        # field 1 bytes "ab", field 2 varint 150, field 3 fixed32, field 4 fixed64, field 5 bytes twice
        blob = (b'\x0a\x02ab' + b'\x10\x96\x01' + b'\x1d\x01\x00\x00\x00'
                + b'\x21' + b'\x02' + b'\x00' * 7 + b'\x2a\x01x' + b'\x2a\x01y')
        typedef = _top_level_typedef(blob)
        self.assertEqual({k: v['type'] for k, v in typedef.items()},
                         {'1': 'bytes', '2': 'int', '3': 'fixed32', '4': 'fixed64', '5': 'bytes'})
        message, _ = blackboxprotobuf.decode_message(blob, typedef)
        self.assertEqual(message['1'], b'ab')
        self.assertEqual(message['5'], [b'x', b'y'])

    def test_bytes_that_look_like_a_message_stay_bytes(self):
        inner = b'\x0a\x01z'
        blob = b'\x0a' + bytes([len(inner)]) + inner
        message, _ = blackboxprotobuf.decode_message(blob, _top_level_typedef(blob))
        self.assertEqual(message['1'], inner)

    def test_truncated_record_raises(self):
        with self.assertRaises(ValueError):
            _top_level_typedef(b'\x0a\x05ab')

    def test_invalid_wire_type_raises(self):
        with self.assertRaises(ValueError):
            _top_level_typedef(b'\x0f\x00')


class TestSetRecordsFallback(unittest.TestCase):

    def test_a_repeated_field_guessed_as_a_message_keeps_the_record(self):
        # Field 5 appears twice. Its first value parses as a message ("\x0a\x01z"), so the
        # schema-less decoder reuses that guess for the second value, which does not parse.
        first, second = b'\x0a\x01z', b'\x0f'
        blob = (b'\x0a\x03abc' + b'\x2a' + bytes([len(first)]) + first
                + b'\x2a' + bytes([len(second)]) + second)
        with self.assertRaises(biomeSetsStores._DECODE_ERRORS):
            blackboxprotobuf.decode_message(blob)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'Set.db'
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE content (content_hash INTEGER, content BLOB)')
                db.execute('CREATE TABLE metacontent_provenance (content_hash INTEGER, written_date INTEGER)')
                db.execute('INSERT INTO content VALUES (1, ?)', (blob,))
                db.execute('INSERT INTO metacontent_provenance VALUES (1, 1700000000000000)')
            with patch.object(biomeSetsStores, 'logfunc'):
                records = list(biomeSetsStores._set_records(str(path)))
        self.assertEqual(len(records), 1)
        message = records[0][1]
        self.assertEqual(message['1'], b'abc')
        self.assertEqual(message['5'], [first, second])

    def test_nested_decodes_a_field_kept_as_bytes(self):
        self.assertEqual(_nested({'2': b'\x0a\x01z'}, '2'), {'1': b'z'})
        self.assertEqual(_nested({'2': b'\x0f'}, '2'), {})
        self.assertEqual(_nested({'2': {'1': b'z'}}, '2'), {'1': b'z'})


if __name__ == '__main__':
    unittest.main()
