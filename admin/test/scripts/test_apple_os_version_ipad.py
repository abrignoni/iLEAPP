"""iPad lookups in Context.get_apple_os_version: iPadOS group first, iOS fallback."""
import unittest
from unittest.mock import patch

from scripts.context import Context

COLLECTION = 'apple_build_id_to_os_version'

FIXTURE = {
    'iOS': {
        '16A366': 'iOS 12.0',
        '17A508': 'iOS 13.0',
        '17A844': 'iOS 13.1',
        '19A344': 'iOS 15.0',
        '21D50': 'iOS 17.3',
        '17X999': ' iOS 13.9',      # malformed label: leading space
    },
    'iPadOS': {
        '17A844': 'iPadOS 13.1',
        '19A344': 'iPadOS 15.0 RC',  # iPad version differs from iPhone
        '21E188': 'iPadOS 17.4',     # iPad-only build
    },
    'macOS': {
        '23A344': 'macOS 14.0',
    },
}

LEGACY_FIXTURE = {'iOS': FIXTURE['iOS']}  # data file without an iPadOS group


def lookup(build, family, data=FIXTURE):
    with patch.dict(Context._metadata, {COLLECTION: data}):
        return Context.get_apple_os_version(build, family)


class TestIPadLookup(unittest.TestCase):
    def test_ipad_only_build_is_resolved(self):
        self.assertEqual(lookup('21E188', 'iPad13,1'), 'iPadOS 17.4')

    def test_ipados_group_takes_precedence_over_ios(self):
        self.assertEqual(lookup('19A344', 'iPad8,1'), 'iPadOS 15.0 RC')
        self.assertEqual(lookup('17A844', 'iPad7,5'), 'iPadOS 13.1')

    def test_pre_ipados_build_falls_back_to_ios(self):
        self.assertEqual(lookup('16A366', 'iPad6,11'), 'iOS 12.0')

    def test_recent_build_missing_from_ipados_is_renamed(self):
        self.assertEqual(lookup('17A508', 'iPad7,5'), 'iPadOS 13.0')

    def test_rename_only_applies_to_leading_ios(self):
        self.assertEqual(lookup('17X999', 'iPad7,5'), ' iOS 13.9')

    def test_unknown_or_invalid_build_returns_empty_string(self):
        self.assertEqual(lookup('ZZZ', 'iPad7,5'), '')
        self.assertEqual(lookup(None, 'iPad7,5'), '')
        self.assertEqual(lookup('', 'iPad7,5'), '')

    def test_legacy_data_without_ipados_group(self):
        self.assertEqual(lookup('17A844', 'iPad7,5', LEGACY_FIXTURE), 'iPadOS 13.1')
        self.assertEqual(lookup('19A344', 'iPad8,1', LEGACY_FIXTURE), 'iPadOS 15.0')
        self.assertEqual(lookup('16A366', 'iPad6,11', LEGACY_FIXTURE), 'iOS 12.0')
        self.assertEqual(lookup('21E188', 'iPad13,1', LEGACY_FIXTURE), '')


class TestOtherFamiliesUnchanged(unittest.TestCase):
    def test_iphone_uses_ios_group_only(self):
        self.assertEqual(lookup('21D50', 'iPhone12,1'), 'iOS 17.3')
        self.assertEqual(lookup('19A344', 'iPhone12,1'), 'iOS 15.0')
        self.assertEqual(lookup('21E188', 'iPhone12,1'), '')

    def test_mac(self):
        self.assertEqual(lookup('23A344', 'Mac14,2'), 'macOS 14.0')

    def test_unknown_family_searches_all_groups(self):
        self.assertEqual(lookup('17A844', ''), 'iOS 13.1 or iPadOS 13.1')
        self.assertEqual(lookup('21E188', ''), 'iPadOS 17.4')


class TestShippedData(unittest.TestCase):
    """Sanity checks against scripts/data/apple_build_id_to_os_version.json."""

    def setUp(self):
        self.data = Context.get_metadata(COLLECTION)

    def test_ipados_group_present(self):
        self.assertIn('iPadOS', self.data)
        self.assertTrue(self.data['iPadOS'])

    def test_ipados_labels_are_not_double_renamed(self):
        for build in self.data['iPadOS']:
            label = Context.get_apple_os_version(build, 'iPad')
            self.assertNotIn('iPadiPadOS', label, build)
            self.assertTrue(label.startswith('iPadOS '), (build, label))

    def test_ipad_only_build_from_shipped_data(self):
        self.assertEqual(Context.get_apple_os_version('21E188', 'iPad13,1'), 'iPadOS 17.4')


if __name__ == '__main__':
    unittest.main()
