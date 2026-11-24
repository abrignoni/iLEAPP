# pylint: disable=protected-access
"""Payload and container readers of biomeUseractmeta.

The real fixtures are records from the public Cellebrite CTF 2023 (Abe) image. Their expected
values agree with macOS's decode of the same records (NSUserActivity on macOS 27.2.1); the
text layout is the reader's.
"""
import unittest
from unittest.mock import patch

from scripts.artifacts import biomeUseractmeta as parser

# Abe payload: a date (extension type 3), integers, an array and strings.
PAYLOAD_DATE = bytes.fromhex(
    '4d50030585a974696d657374616d70d703b5f9d1059c18c541ae636f6c6c656374696f6e5479706502ad73'
    '656c6563746564555549447391d92441444344383146332d393441462d343036422d423937342d3938364436'
    '39323446424438b1636f6c6c656374696f6e53756274797065ccd1a9616c62756d55554944d9243332343841'
    '4443442d353032392d343435372d394444332d374134354434393431393436')
# Abe payload: a UUID (extension type 1) and a nested map.
PAYLOAD_UUID = bytes.fromhex(
    '4d50030582b0756e697175654964656e746966696572d8019548cd81968d4fb59ff26de5fe541949b9636f6d'
    '2e6170706c652e5361666172692e436c6f756454616281a355524cb668747470733a2f2f7777772e7961686f'
    '6f2e636f6d2f')
# Reader-format fixture (not from an image): extension type 0, as Abe's Maps payloads write
# it (C7 05 00 then a MessagePack string), with a neutral URL.
PAYLOAD_URL = b'MP\x03\x05\x81\xa3url\xc7\x05\x00\xb4https://example.com/'

# Abe container: one UTF-8 string.
CONTAINER_ONE = bytes.fromhex(
    'deba00010000ab000000960000001d000000f0960000000000960000007500000003006a000000250000005f'
    '5f636c6173733a435353656172636861626c654974656d417474726962757465536574003300000001002a00'
    '000001001a00000053656520796f7572206c61746573742061637469766974792e0000000100000000005c00'
    '0000f427000000f400000000e250000000f112006b4d444974656d4465736372697074696f6e00')
# Abe container: four strings and a date (tag 0x13).
CONTAINER_DATE = bytes.fromhex(
    'deba00010000970100001e0100001d000000f01e01000000001e010000fd0000000300f20000002500000'
    '05f5f636c6173733a435353656172636861626c654974656d41747472696275746553657400bb0000000500'
    '8200000007000c0000007075626c69632e6974656d0016000000616265727564646572373740676d61696c'
    '2e636f6d00000000802329c5411e000000636f6d706f73652d616265727564646572373740676d61696c2e'
    '636f6d001e000000636f6d706f73652d616265727564646572373740676d61696c2e636f6d000000000002'
    '0004000400040005000500430000008e000000f4000000005c000000f458000000b0000000f41500000'
    '06c000000f42a000000860000001327000000f400000000e250000000f112006b4d444974656d436f6e7465'
    '6e74547970650012006b4d444974656d4465736372697074696f6e0016005f6b4d444974656d4578706972'
    '6174696f6e446174650012005f6b4d444974656d45787465726e616c4944001e006b4d444974656d52656c'
    '61746564556e697175654964656e74696669657200')


def wrapped(container):
    """contentAttributeSetData as the property list carries it: NS.data holding a plist."""
    import plistlib
    return {'NS.data': plistlib.dumps({'container': container}, fmt=plistlib.PlistFormat.FMT_BINARY)}


class PayloadTests(unittest.TestCase):
    def test_date_integers_array_and_strings(self):
        self.assertEqual(parser._payload_text(PAYLOAD_DATE, 'test'), '\n'.join([
            'timestamp = 2023-06-07 22:11:23.640433+00:00',
            'collectionType = 2',
            'selectedUUIDs[0] = ADCD81F3-94AF-406B-B974-986D6924FBD8',
            'collectionSubtype = 209',
            'albumUUID = 3248ADCD-5029-4457-9DD3-7A45D4941946',
        ]))

    def test_uuid_and_nested_map(self):
        self.assertEqual(parser._payload_text(PAYLOAD_UUID, 'test'), '\n'.join([
            'uniqueIdentifier = 9548CD81-968D-4FB5-9FF2-6DE5FE541949',
            'com.apple.Safari.CloudTab.URL = https://www.yahoo.com/',
        ]))

    def test_url_extension_reads_the_string_after_it(self):
        self.assertEqual(parser._payload_text(PAYLOAD_URL, 'test'), 'url = https://example.com/')

    def test_long_bytes_are_shown_in_part_with_their_length(self):
        payload = b'MP\x03\x05\x81\xa1b\xc5\x01\x2c' + bytes(range(256)) + bytes(44)
        self.assertEqual(parser._payload_text(payload, 'test'),
                         f'b = <300 bytes, first 256 shown> {bytes(range(256)).hex()}')

    def test_truncated_payload_keeps_the_raw_bytes_and_logs(self):
        with patch.object(parser, 'logfunc') as log:
            self.assertEqual(parser._payload_text(PAYLOAD_DATE[:-5], 'test'), PAYLOAD_DATE[:-5])
        log.assert_called_once()

    def test_trailing_bytes_keep_the_raw_bytes_and_log(self):
        with patch.object(parser, 'logfunc') as log:
            self.assertEqual(parser._payload_text(PAYLOAD_URL + b'\x00', 'test'), PAYLOAD_URL + b'\x00')
        log.assert_called_once()


class ContainerTests(unittest.TestCase):
    def test_one_string(self):
        self.assertEqual(parser._container_text(wrapped(CONTAINER_ONE), 'test'),
                         'kMDItemDescription = See your latest activity.')

    def test_strings_and_date_sorted_by_key(self):
        self.assertEqual(parser._container_text(wrapped(CONTAINER_DATE), 'test'), '\n'.join([
            '_kMDItemExpirationDate = 2023-07-03 00:00:00+00:00',
            '_kMDItemExternalID = compose-aberudder77@gmail.com',
            'kMDItemContentType = public.item',
            'kMDItemDescription = aberudder77@gmail.com',
            'kMDItemRelatedUniqueIdentifier = compose-aberudder77@gmail.com',
        ]))

    def test_wrong_length_keeps_the_raw_bytes_and_logs(self):
        damaged = CONTAINER_ONE + b'\x00'
        with patch.object(parser, 'logfunc') as log:
            self.assertEqual(parser._container_text(wrapped(damaged), 'test'), damaged)
        log.assert_called_once()

    def test_unknown_tag_is_shown_not_dropped(self):
        damaged = bytearray(CONTAINER_ONE)
        tag_at = damaged.index(bytes.fromhex('5c000000f4')) + 4
        damaged[tag_at] = 0x77
        self.assertEqual(parser._container_text(wrapped(bytes(damaged)), 'test'),
                         'kMDItemDescription = <tag 0x77, value 92, not decoded>')

    def test_missing_container_keeps_the_field_and_logs(self):
        import plistlib
        field = {'NS.data': plistlib.dumps({'other': 1}, fmt=plistlib.PlistFormat.FMT_BINARY)}
        with patch.object(parser, 'logfunc') as log:
            self.assertEqual(parser._container_text(field, 'test'), field['NS.data'])
        log.assert_called_once()

    def test_absent_field_is_empty(self):
        self.assertEqual(parser._container_text('', 'test'), '')
        self.assertEqual(parser._container_text(None, 'test'), '')


if __name__ == '__main__':
    unittest.main()
