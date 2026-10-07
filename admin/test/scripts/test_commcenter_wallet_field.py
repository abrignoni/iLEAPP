"""Native plist wallet retention and unchanged legacy device-info behavior."""
import base64
import copy
from datetime import datetime
import json
from pathlib import Path
import plistlib
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts import imeiImsi as artifact  # pylint: disable=wrong-import-position
from scripts import ilapfuncs  # pylint: disable=wrong-import-position
from scripts.context import Context as GlobalContext  # pylint: disable=wrong-import-position


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def safe_content(binary=False):
    entitlement = {'lastGoodImsi': 'first-imsi',
                   'kEntitlementsSelfRegistrationUpdateImsi': 'update-imsi',
                   'kEntitlementsSelfRegistrationUpdateImei': 'update-imei'}
    extras = [False, 0, '0', 2**64 - 1, -(2**63), -0.0, float('inf'),
              float('-inf'), struct.unpack('>d', bytes.fromhex('fff8000000000001'))[0],
              b'\x00\xff', datetime(2020, 1, 2, 3, 4, 5),
              {'type': 'null', 'value': 'marker', 'present': False}, ['repeat', 'repeat']]
    if binary:
        extras += [None, plistlib.UID(2**64 - 1)]
    return {'PhoneNumber': 'test-number', 'LastKnownICCI': 'test-icci', 'Other': 'unchanged',
            'PersonalWallet': {
                'wallet "\t\n雪': {'CarrierEntitlements': entitlement, 'unknown': extras},
                'equal-values-distinct-key': {'CarrierEntitlements': entitlement},
                'conflicting': {'CarrierEntitlements': {'lastGoodImsi': 'different',
                                                       'unknown': extras}},
                'nonmapping': extras}}


def write_plist(root, content, binary=False, folder=''):
    path = Path(root) / folder / 'private/var/wireless/Library/Preferences/com.apple.commcenter.plist'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()  # Only temporary fixture files are rewritten.
    path.write_bytes(plistlib.dumps(content, fmt=(plistlib.PlistFormat.FMT_BINARY if binary
                                                 else plistlib.PlistFormat.FMT_XML), sort_keys=False))
    path.chmod(0o444)
    return path


def decode_node(node):
    kind, value = node['type'], node['value']
    if kind == 'null':
        return None
    if kind in ('bool', 'string'):
        return value
    if kind == 'integer':
        return int(value)
    if kind == 'real':
        return struct.unpack('>d', bytes.fromhex(value))[0]
    if kind == 'data':
        return base64.b64decode(value, validate=True)
    if kind == 'date':
        return datetime.fromisoformat(value)
    if kind == 'uid':
        return plistlib.UID(int(value))
    if kind == 'array':
        return [decode_node(item) for item in value]
    if kind == 'dictionary':
        return {decode_node(key): decode_node(item) for key, item in value}
    raise AssertionError(kind)


class TestWalletField(unittest.TestCase):
    def assert_native_equal(self, left, right):
        self.assertIs(type(left), type(right))
        if isinstance(left, float):
            self.assertEqual(struct.pack('>d', left), struct.pack('>d', right))
        elif isinstance(left, list):
            self.assertEqual(len(left), len(right))
            for first, second in zip(left, right):
                self.assert_native_equal(first, second)
        elif isinstance(left, dict):
            self.assertEqual(list(left), list(right))
            for key in left:
                self.assert_native_equal(left[key], right[key])
        else:
            self.assertEqual(left, right)

    def test_native_files_all_wallets_and_device_info_unchanged(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(ilapfuncs.identifiers, {}, clear=True), \
                patch.object(GlobalContext, '_data_folder', root):
            paths = [write_plist(root, safe_content(binary), binary, tag)
                     for binary, tag in [(False, 'XML'), (True, 'BINARY')]]
            for path in paths:
                context = Context(root, [path])
                legacy = artifact.imeiImsi.__wrapped__(context)
                state = copy.deepcopy(ilapfuncs.identifiers)
                _, rows, source = artifact.imeiImsiPersonalWallet.__wrapped__(context)
                self.assertEqual(ilapfuncs.identifiers, state)
                self.assertEqual(len(rows), 1)
                self.assertEqual(source, str(path.relative_to(root)))
                self.assertEqual(legacy[2], str(path))
                self.assertEqual(legacy[1][-3:], [('Last Good IMSI', 'first-imsi'),
                                                ('Self Registration Update IMSI', 'update-imsi'),
                                                ('Self Registration Update IMEI', 'update-imei')])
                actual = plistlib.loads(path.read_bytes())['PersonalWallet']
                envelope = json.loads(rows[0][0])
                self.assertIs(envelope['present'], True)
                self.assert_native_equal(actual, decode_node(envelope['value']))
            # Real legacy calls append equal values, with source and caller but no wallet key.
            stored = ilapfuncs.identifiers['Cellular']['Last Good IMSI']
            self.assertEqual(len(stored), 2)
            self.assertEqual([v['value'] for v in stored], ['first-imsi'] * 2)
            self.assertEqual([v['source_file'] for v in stored],
                             [str(p.relative_to(root)) for p in paths])
            self.assertTrue(all(v['artifact'] == 'imeiImsi' for v in stored))
            self.assertTrue(all(set(v) == {'value', 'source_file', 'artifact'} for v in stored))

    def test_first_selected_file_only_in_both_orders(self):
        with tempfile.TemporaryDirectory() as root:
            first_content, second_content = safe_content(), safe_content()
            first_key = next(iter(second_content['PersonalWallet']))
            second_content['PersonalWallet'][first_key]['CarrierEntitlements']['lastGoodImsi'] = 'second'
            first = write_plist(root, first_content, folder='one')
            second = write_plist(root, second_content, folder='two')
            for paths in [[first, second], [second, first]]:
                _, rows, source = artifact.imeiImsiPersonalWallet.__wrapped__(Context(root, paths))
                self.assertEqual(source, str(paths[0].relative_to(root)))
                self.assertEqual(len(rows), 1)
                with patch.dict(ilapfuncs.identifiers, {}, clear=True), \
                        patch.object(GlobalContext, '_data_folder', root):
                    legacy = artifact.imeiImsi.__wrapped__(Context(root, paths))
                self.assertEqual(legacy[2], str(paths[0]))
                self.assertEqual(legacy[1][-3][1], 'first-imsi' if paths[0] == first else 'second')
                self.assert_native_equal(plistlib.loads(paths[0].read_bytes())['PersonalWallet'],
                                         decode_node(json.loads(rows[0][0])['value']))

    def test_actual_binary_missing_empty_null_and_nonmapping_field(self):
        values = [{}, {'PersonalWallet': None}, {'PersonalWallet': {}}, {'PersonalWallet': []},
                  {'PersonalWallet': ''}, {'PersonalWallet': False}, {'PersonalWallet': 0},
                  {'PersonalWallet': '0'}, {'PersonalWallet': {'present': False}},
                  {'PersonalWallet': {'wallet': {'CarrierEntitlements': None}}}]
        outputs = []
        with tempfile.TemporaryDirectory() as root:
            for content in values:
                path = write_plist(root, content, binary=True)
                parsed = plistlib.loads(path.read_bytes())
                _, rows, _ = artifact.imeiImsiPersonalWallet.__wrapped__(Context(root, [path]))
                self.assertEqual(len(rows), 1)
                outputs.append(rows[0][0])
                envelope = json.loads(rows[0][0])
                self.assertIs(envelope['present'], 'PersonalWallet' in parsed)
                if envelope['present']:
                    self.assert_native_equal(parsed['PersonalWallet'], decode_node(envelope['value']))
                else:
                    self.assertEqual(envelope, {'present': False})
        self.assertEqual(len(set(outputs)), len(values))

    def test_nondictionary_root_is_not_reported_as_missing(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(ilapfuncs.identifiers, {}, clear=True):
            for content, binary in [(['PersonalWallet'], False), (None, True)]:
                path = write_plist(root, content, binary)
                with patch.object(artifact, 'logfunc') as log:
                    _, rows, source = artifact.imeiImsiPersonalWallet.__wrapped__(Context(root, [path]))
                self.assertEqual(rows, [])
                self.assertEqual(source, str(path.relative_to(root)))
                self.assertEqual(ilapfuncs.identifiers, {})
                message = log.call_args[0][0]
                self.assertIn('field presence was not evaluated', message)
                self.assertNotIn(root, message)
                self.assertEqual(log.call_count, 1)
        with self.assertRaises(TypeError):
            artifact._wallet_field_json({'PersonalWallet': object()})  # pylint: disable=protected-access


if __name__ == '__main__':
    unittest.main()
