"""Google Chat reads an attachment name from every annotation entry, list or single.

The annotation field holds one entry, or a list of them when a message has several. A list
used to be labelled 'Group List' with every string in it put in the Media column, where the
report could not show it, and an attachment in it was never looked for. These tests decode
constructed annotations with the module's own protobuf decoder.
"""
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import blackboxprotobuf  # pylint: disable=wrong-import-position
from scripts.artifacts import googleChat  # pylint: disable=wrong-import-position


def _field(number, payload):
    """A length-delimited protobuf field; enough for the small values used here."""
    tag = (number << 3) | 2
    key = bytes([tag]) if tag < 0x80 else bytes([(tag & 0x7f) | 0x80, tag >> 7])
    return key + bytes([len(payload)]) + payload


def _attachment(name):
    return _field(1, _field(10, _field(3, name.encode())))


def _other():
    return _field(1, _field(16, b'other'))


def _names(blob):
    decoded, _ = blackboxprotobuf.decode_message(blob)
    return googleChat._attachment_names(decoded.get('1'))  # pylint: disable=protected-access


class GoogleChatAttachmentNamesTests(unittest.TestCase):

    def test_a_single_attachment(self):
        self.assertEqual(_names(_attachment('photo.jpg')), ['photo.jpg'])

    def test_an_attachment_inside_a_list(self):
        self.assertEqual(_names(_other() + _attachment('photo.jpg')), ['photo.jpg'])

    def test_several_attachments_keep_their_order(self):
        self.assertEqual(_names(_attachment('a.jpg') + _attachment('b.png')), ['a.jpg', 'b.png'])

    def test_entries_without_an_attachment_give_nothing(self):
        self.assertEqual(_names(_other()), [])
        self.assertEqual(_names(_other() + _other()), [])


if __name__ == '__main__':
    unittest.main()
