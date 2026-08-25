"""Tests for image location resolution in make_test_data.py.

The image manifest carries machine-independent identity; locations come from a
git-ignored admin/image_manifest.local.json or from an entry's legacy
local_image_paths list. Everything here runs against temporary files, except
the last class, which is a read-only structural check of the shipped manifest.
"""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

import make_test_data  # noqa: E402  pylint: disable=wrong-import-position


class LoadLocalImageConfigTests(unittest.TestCase):
    def test_missing_file_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = os.path.join(tmp, 'image_manifest.local.json')
            self.assertEqual(make_test_data.load_local_image_config(missing), {})

    def test_reads_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'image_manifest.local.json')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({'image_paths': {'a': '/x'}}, f)
            self.assertEqual(make_test_data.load_local_image_config(path),
                             {'image_paths': {'a': '/x'}})


class ResolveImagePathTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmpdir = tmp.name
        self.image_file = os.path.join(self.tmpdir, 'published_image.zip')
        with open(self.image_file, 'wb') as f:
            f.write(b'zip')

    def test_direct_mapping_by_image_name(self):
        entry = {'image_name': 'img_a', 'sample_data_key': 'key_a'}
        config = {'image_paths': {'img_a': self.image_file}}
        self.assertEqual(make_test_data.resolve_image_path(entry, config), self.image_file)

    def test_direct_mapping_by_sample_data_key(self):
        entry = {'image_name': 'img_a', 'sample_data_key': 'key_a'}
        config = {'image_paths': {'key_a': self.image_file}}
        self.assertEqual(make_test_data.resolve_image_path(entry, config), self.image_file)

    def test_mapped_but_missing_path_falls_through(self):
        entry = {'image_name': 'img_a',
                 'local_image_paths': [self.image_file]}
        config = {'image_paths': {'img_a': os.path.join(self.tmpdir, 'gone.zip')}}
        self.assertEqual(make_test_data.resolve_image_path(entry, config), self.image_file)

    def test_legacy_local_image_paths(self):
        entry = {'image_name': 'img_a',
                 'local_image_paths': [os.path.join(self.tmpdir, 'nope.zip'), self.image_file]}
        self.assertEqual(make_test_data.resolve_image_path(entry, {}), self.image_file)

    def test_search_roots_find_published_file_in_nested_dir(self):
        nested = os.path.join(self.tmpdir, 'a', 'b')
        os.makedirs(nested)
        target = os.path.join(nested, 'nested_only.zip')
        with open(target, 'wb') as f:
            f.write(b'zip')
        entry = {'image_name': 'img_a', 'published_file': 'nested_only.zip'}
        config = {'search_roots': [self.tmpdir]}
        self.assertEqual(make_test_data.resolve_image_path(entry, config), target)

    def test_nothing_resolves(self):
        entry = {'image_name': 'img_a', 'published_file': 'absent.zip'}
        config = {'search_roots': [self.tmpdir]}
        self.assertIsNone(make_test_data.resolve_image_path(entry, config))


class GetImageInfoTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmpdir = tmp.name
        self.image_file = os.path.join(self.tmpdir, 'img.zip')
        with open(self.image_file, 'wb') as f:
            f.write(b'zip')
        self.config_path = os.path.join(self.tmpdir, 'image_manifest.local.json')
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump({'image_paths': {'key_a': self.image_file}}, f)
        self.entry = {'image_name': 'legacy_name', 'sample_data_key': 'key_a'}

    def test_lookup_by_sample_data_key_resolves(self):
        with mock.patch.object(make_test_data, 'load_image_manifest',
                               return_value=[dict(self.entry)]):
            info = make_test_data.get_image_info('key_a', config_path=self.config_path)
        self.assertEqual(info['input_file'], self.image_file)

    def test_lookup_by_image_name_resolves(self):
        with mock.patch.object(make_test_data, 'load_image_manifest',
                               return_value=[dict(self.entry)]):
            info = make_test_data.get_image_info('legacy_name', config_path=self.config_path)
        self.assertEqual(info['input_file'], self.image_file)

    def test_unknown_image_raises_value_error(self):
        with mock.patch.object(make_test_data, 'load_image_manifest', return_value=[]):
            with self.assertRaises(ValueError):
                make_test_data.get_image_info('nope', config_path=self.config_path)

    def test_unresolvable_image_raises_file_not_found(self):
        entry = {'image_name': 'other', 'sample_data_key': 'key_b'}
        with mock.patch.object(make_test_data, 'load_image_manifest', return_value=[entry]):
            with self.assertRaises(FileNotFoundError):
                make_test_data.get_image_info('key_b', config_path=self.config_path)


class ShippedManifestTests(unittest.TestCase):
    """Structural checks on the committed manifest (read-only)."""

    @classmethod
    def setUpClass(cls):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        with open(os.path.join(repo_root, 'admin', 'image_manifest.json'),
                  encoding='utf-8') as f:
            cls.entries = json.load(f)['images']

    def test_every_entry_has_unique_names_and_keys(self):
        names = [e.get('image_name') for e in self.entries]
        keys = [e.get('sample_data_key') for e in self.entries]
        self.assertTrue(all(names) and all(keys))
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(keys), len(set(keys)))

    def test_every_entry_is_resolvable_in_principle(self):
        for e in self.entries:
            self.assertTrue(e.get('published_file') or e.get('local_image_paths'),
                            f"{e.get('image_name')} has no published_file or local_image_paths")

    def test_md5_values_are_lowercase_hex(self):
        for e in self.entries:
            md5 = (e.get('file_info') or {}).get('md5_hash')
            if md5:
                self.assertRegex(md5, r'^[0-9a-f]{32}$',
                                 f"{e.get('image_name')} md5 not lowercase hex")


if __name__ == '__main__':
    unittest.main()
