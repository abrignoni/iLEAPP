"""Exercise native plist values and retained person occurrences."""
import base64
from datetime import datetime
import json
from pathlib import Path
import plistlib
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts import icloudSharedalbums as artifact  # pylint: disable=wrong-import-position


class Context:
    """Minimal undecorated parser input context."""
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def safe_people(binary=False):
    """Keep old display values safe while retaining native later/scalar fields."""
    values = ['later@example.test', 'later@example.test', '', False, 0,
              2**64 - 1, -(2**63), -0.0, float('inf'), float('-inf'), float('nan'),
              b'\x00\xffdata', datetime(2020, 1, 2, 3, 4, 5),
              {'present': True, 'value': {'type': 'string', 'value': 'collision'},
               'type': 'array', 'ordered': ['two', 'one', 'two']}]
    if binary:
        values.extend([None, plistlib.UID(2**63 + 9)])
    return {
        'same-id': {'emails': ['first@example.test'] + values,
                    'email': {'not-an-address': values}, 'firstName': 'Quoted "\t\n雪', 'lastName': 'Last', 'fullName': 'Full Name'},
        'missing': {},
        'empty-array': {'emails': [], 'email': 'fallback@example.test'},
        'empty-dict': {'emails': {}, 'email': ''},
        'empty-text': {'emails': '', 'email': 'scalar@example.test'},
        'false': {'emails': False, 'email': 'scalar@example.test'},
        'zero': {'emails': 0, 'email': 'scalar@example.test'},
        'string': {'emails': 'abc', 'email': 'overridden@example.test'},
        'duplicate-address': {'emails': ['first@example.test', 'first@example.test']},
        'not-a-person': 'existing skip',
        **({'null': {'emails': None, 'email': 'fallback@example.test'}} if binary else {}),
    }


def write_people(root):
    paths = []
    for tag, fmt in [('XML', plistlib.PlistFormat.FMT_XML), ('BINARY', plistlib.PlistFormat.FMT_BINARY)]:
        path = Path(root) / ('private/var/mobile/Media/PhotoData/'
                            f'PhotoCloudSharingData/{tag}/cloudSharedPersonInfos.plist')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(plistlib.dumps(safe_people(tag == 'BINARY'), fmt=fmt, sort_keys=False))
        path.chmod(0o444)
        paths.append(path)
    return paths


def decoded_node(node):
    """Independent inverse of the approved wire representation for tests."""
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
        return [decoded_node(v) for v in value]
    if kind == 'dictionary':
        return {decoded_node(k): decoded_node(v) for k, v in value}
    raise AssertionError(kind)


class TestPersonFields(unittest.TestCase):
    def assert_native_equal(self, left, right):
        self.assertIs(type(left), type(right))
        if isinstance(left, float):
            self.assertEqual(struct.pack('>d', left), struct.pack('>d', right))
        elif isinstance(left, list):
            self.assertEqual(len(left), len(right))
            for a, b in zip(left, right):
                self.assert_native_equal(a, b)
        elif isinstance(left, dict):
            self.assertEqual(list(left), list(right))
            for key in left:
                self.assert_native_equal(left[key], right[key])
        else:
            self.assertEqual(left, right)

    def test_actual_xml_and_binary_round_trip_and_old_cells(self):
        with tempfile.TemporaryDirectory() as root:
            files = write_people(root)
            headers, rows, sources = artifact.icloudSharedPersonInfo.__wrapped__(Context(root, files))
            self.assertEqual(len(headers), 7)
            expected = []
            for path in files:
                people = plistlib.loads(path.read_bytes())
                for identifier, person in people.items():
                    if not isinstance(person, dict):
                        continue
                    email = person.get('email', '')
                    if person.get('emails'):
                        email = person['emails'][0]
                    expected.append((email, person.get('firstName', ''), person.get('lastName', ''),
                                     person.get('fullName', ''), identifier))
                    row = rows[len(expected) - 1]
                    for offset, key in [(5, 'emails'), (6, 'email')]:
                        encoded = json.loads(row[offset])
                        self.assertIs(encoded['present'], key in person)
                        self.assertNotIn(' ', row[offset].replace('not-an-address', ''))
                        if key in person:
                            self.assert_native_equal(person[key], decoded_node(encoded['value']))
                        else:
                            self.assertEqual(encoded, {'present': False})
            self.assertEqual([r[:5] for r in rows], expected)
            self.assertEqual(len(rows), 19)
            self.assertEqual([r[4] for r in rows].count('same-id'), 2)
            self.assertEqual(sources, ', '.join(str(p.relative_to(root)) for p in files))

    def test_native_binary_null_uid_and_float_bits(self):
        original = {'value': [None, plistlib.UID(2**64 - 1), 2**64 - 1, -(2**63),
                              -0.0, struct.unpack('>d', bytes.fromhex('fff8000000000001'))[0]]}
        parsed = plistlib.loads(plistlib.dumps(original, fmt=plistlib.PlistFormat.FMT_BINARY))
        envelope = json.loads(artifact._person_field_json(parsed, 'value'))  # pylint: disable=protected-access
        self.assert_native_equal(parsed['value'], decoded_node(envelope['value']))
        self.assertIsNone(parsed['value'][0])
        self.assertIsInstance(parsed['value'][1], plistlib.UID)

    def test_missing_empty_and_marker_collision_do_not_merge(self):
        values = [{}, {'email': None}, {'email': ''}, {'email': []}, {'email': {}},
                  {'email': False}, {'email': 0}, {'email': '0'},
                  {'email': {'type': 'null', 'value': None}}, {'email': {'present': False}}]
        outputs = [artifact._person_field_json(v, 'email') for v in values]  # pylint: disable=protected-access
        self.assertEqual(len(set(outputs)), len(values))
        with self.assertRaises(TypeError):
            artifact._person_field_json({'email': object()}, 'email')  # pylint: disable=protected-access


if __name__ == '__main__':
    unittest.main()
