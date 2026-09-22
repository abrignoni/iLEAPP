"""The WhatsApp metadata reader decodes fields 17 and 21 off the wire format and
never lets a blob it cannot walk stop the artifact.

Discussion #2203: one message whose ZMETADATA the schema-less guesser could not
walk raised DecodeError past the artifact's except tuple and ended the whole
messages artifact with no rows after a 14 hour run. The reader tested here
decodes only the two fields the artifact reports, skips everything else by the
length its wire type gives, and stops quietly at anything it does not walk.
"""
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts.whatsApp import _read_forward_fields  # pylint: disable=wrong-import-position

JID = b'15551234567@s.whatsapp.net'


def _varint(value):
    out = b''
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out += bytes([byte | 0x80])
        else:
            return out + bytes([byte])


def _field(number, wire, payload):
    tag = _varint((number << 3) | wire)
    if wire == 2:
        return tag + _varint(len(payload)) + payload
    return tag + payload


class WhatsAppMetadataReaderTests(unittest.TestCase):

    def test_field_17_is_read_as_a_varint(self):
        self.assertEqual(_read_forward_fields(_field(17, 0, _varint(3))), ('3', ''))

    def test_field_21_is_read_as_utf8(self):
        self.assertEqual(_read_forward_fields(_field(21, 2, JID)), ('', JID.decode()))

    def test_other_fields_of_every_wire_type_are_skipped(self):
        blob = (_field(1, 0, _varint(9)) + _field(2, 1, b'\x00' * 8) + _field(17, 0, _varint(4))
                + _field(3, 5, b'\x00' * 4) + _field(21, 2, JID) + _field(9, 2, b'\xff\xd8junk'))
        self.assertEqual(_read_forward_fields(blob), ('4', JID.decode()))

    def test_a_repeated_field_17_keeps_the_last_value(self):
        blob = _field(17, 0, _varint(1)) + _field(17, 0, _varint(7))
        self.assertEqual(_read_forward_fields(blob), ('7', ''))

    def test_the_blob_shape_from_discussion_2203_yields_nothing_and_does_not_raise(self):
        # field 1, length-delimited, declares 16 bytes and carries 1
        self.assertEqual(_read_forward_fields(b'\x0a\x10\x01'), ('', ''))

    def test_a_blob_cut_inside_a_later_field_keeps_what_came_before(self):
        blob = _field(17, 0, _varint(2)) + _field(21, 2, JID)[:6]
        self.assertEqual(_read_forward_fields(blob), ('2', ''))

    def test_a_field_21_that_is_not_utf8_reads_blank(self):
        self.assertEqual(_read_forward_fields(_field(21, 2, b'\xff\xfe\x00')), ('', ''))

    def test_a_group_wire_type_stops_the_read_quietly(self):
        blob = _field(17, 0, _varint(5)) + _field(4, 3, b'') + _field(21, 2, JID)
        self.assertEqual(_read_forward_fields(blob), ('5', ''))

    def test_an_empty_blob_yields_nothing(self):
        self.assertEqual(_read_forward_fields(b''), ('', ''))

    def test_a_value_that_is_not_a_blob_yields_nothing_and_does_not_raise(self):
        # SQLite does not enforce column types, so ZMETADATA can hold text or a number.
        # The previous decoder raised TypeError on a str, which the artifact caught; this
        # reader walked the value as bytes and the artifact ended with no rows.
        self.assertEqual(_read_forward_fields('not a blob'), ('', ''))
        self.assertEqual(_read_forward_fields(7), ('', ''))
        self.assertEqual(_read_forward_fields(bytearray(_field(17, 0, _varint(3)))), ('3', ''))

    def test_a_varint_with_the_top_bit_set_reads_as_the_signed_value(self):
        # matches the previous reader, which decoded field 17 as a signed 64-bit varint
        self.assertEqual(_read_forward_fields(_field(17, 0, _varint((1 << 64) - 1))), ('-1', ''))


if __name__ == '__main__':
    unittest.main()
