"""applicationStateDB and appInventory decode both blob forms on the supported Pythons.

Each _parse_blob had a branch for Python older than 3.9 that read a plain plist with
biplist. The project requires 3.11, so that branch never ran; it is removed with the biplist
import. These tests pin both paths that remain: a plain binary plist through plistlib and an
NSKeyedArchiver through nska_deserialize.
"""
import plistlib
import unittest

from scripts.alternate_artifacts import appInventory
from scripts.artifacts import applicationStateDB

PLAIN = plistlib.dumps({'compatibilityInfo': 'plain'}, fmt=plistlib.PlistFormat.FMT_BINARY)
KEYED = plistlib.dumps({
    '$version': 100000, '$archiver': 'NSKeyedArchiver', '$top': {'root': plistlib.UID(1)},
    '$objects': ['$null', {'NS.keys': [plistlib.UID(2)], 'NS.objects': [plistlib.UID(3)],
                           '$class': plistlib.UID(4)},
                 'compatibilityInfo', 'keyed',
                 {'$classname': 'NSDictionary', '$classes': ['NSDictionary', 'NSObject']}]},
    fmt=plistlib.PlistFormat.FMT_BINARY)


class ApplicationStateBlobTest(unittest.TestCase):

    def test_application_state_db_reads_both_forms(self):
        self.assertEqual(applicationStateDB._parse_blob('app', 'key', PLAIN),  # pylint: disable=protected-access
                         {'compatibilityInfo': 'plain'})
        self.assertEqual(applicationStateDB._parse_blob('app', 'key', KEYED),  # pylint: disable=protected-access
                         {'compatibilityInfo': 'keyed'})

    def test_app_inventory_reads_both_forms(self):
        self.assertEqual(appInventory._parse_blob('app', PLAIN),  # pylint: disable=protected-access
                         {'compatibilityInfo': 'plain'})
        self.assertEqual(appInventory._parse_blob('app', KEYED),  # pylint: disable=protected-access
                         {'compatibilityInfo': 'keyed'})


if __name__ == '__main__':
    unittest.main()
