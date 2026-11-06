#!/usr/bin/env python3
"""Focused regression tests for App Snapshots path and manifest joins."""

import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts.appSnapshots import (
    _bundle_id_from_path,
    _manifest_record,
    _snapshot_group_from_path,
)


class AppSnapshotPathTest(unittest.TestCase):
    def test_bundle_directory_wins_over_scene_directory(self):
        path = Path(
            '/private/var/mobile/Library/SplashBoard/Snapshots/com.apple.camera/'
            'sceneID:com.apple.camera-default/ABC@3x.ktx')
        self.assertEqual(_bundle_id_from_path(path), 'com.apple.camera')

    def test_scene_only_layout_yields_bundle_identifier(self):
        path = Path(
            '/private/var/mobile/Containers/Data/Application/UUID/Library/SplashBoard/'
            'Snapshots/sceneID:com.google.Keep-default/ABC@3x.ktx')
        self.assertEqual(_bundle_id_from_path(path), 'com.google.Keep')

    def test_scene_identifier_suffix_is_not_part_of_bundle(self):
        path = Path(
            '/private/var/mobile/Containers/Data/Application/UUID/Library/SplashBoard/'
            'Snapshots/sceneID:com.example.app-19F2E62F-A756-4397-9E92-2DD765BDB306/'
            'ABC@3x.ktx')
        self.assertEqual(_bundle_id_from_path(path), 'com.example.app')

    def test_scene_prefix_spellings_give_the_same_bundle_and_group(self):
        # The manifest keeps the colon; extractions seen so far write an
        # underscore or drop it.
        for scene_dir in ('sceneID:com.apple.Maps-default',
                          'sceneID_com.apple.Maps-default',
                          'sceneIDcom.apple.Maps-default'):
            for variant in ('', 'downscaled/'):
                with self.subTest(scene_dir=scene_dir, variant=variant):
                    path = Path(
                        '/private/var/mobile/Containers/Data/Application/UUID/Library/'
                        f'SplashBoard/Snapshots/{scene_dir}/{variant}ABC@3x.ktx')
                    self.assertEqual(_bundle_id_from_path(path), 'com.apple.Maps')
                    self.assertEqual(
                        _snapshot_group_from_path(path),
                        'sceneID:com.apple.Maps-default')

    def test_colon_less_scene_with_uuid_suffix(self):
        path = Path(
            '/Snapshots/sceneIDcom.apple.mobilecal-19F2E62F-A756-4397-9E92-2DD765BDB306/'
            'ABC@3x.ktx')
        self.assertEqual(_bundle_id_from_path(path), 'com.apple.mobilecal')

    def test_bundle_directory_is_not_rewritten(self):
        path = Path('/Snapshots/com.apple.camera/ABC@3x.ktx')
        self.assertEqual(_bundle_id_from_path(path), 'com.apple.camera')
        self.assertEqual(_snapshot_group_from_path(path), 'com.apple.camera')

    def test_downscaled_variant_keeps_owning_scene(self):
        path = Path(
            '/private/var/mobile/Library/SplashBoard/Snapshots/com.apple.camera/'
            'sceneID:com.apple.camera-default/downscaled/ABC@3x.ktx')
        self.assertEqual(
            _snapshot_group_from_path(path),
            'sceneID:com.apple.camera-default')


class AppSnapshotManifestJoinTest(unittest.TestCase):
    def test_duplicate_filename_prefers_matching_bundle_and_group(self):
        wanted = SimpleNamespace(
            bundleID='com.example.two', snapshot_group='sceneID:com.example.two-default')
        other = SimpleNamespace(
            bundleID='com.example.one', snapshot_group='sceneID:com.example.one-default')
        index = {'ABC@3x.ktx': [other, wanted]}

        result = _manifest_record(
            index,
            Path('/Snapshots/sceneID:com.example.two-default/ABC@3x.ktx'),
            'com.example.two',
            'sceneID:com.example.two-default')

        self.assertIs(result, wanted)

    def test_duplicate_filename_joins_through_colon_less_scene_directory(self):
        wanted = SimpleNamespace(
            bundleID='com.example.two', snapshot_group='sceneID:com.example.two-default')
        other = SimpleNamespace(
            bundleID='com.example.one', snapshot_group='sceneID:com.example.one-default')
        index = {'ABC@3x.ktx': [other, wanted]}
        path = Path('/Snapshots/sceneIDcom.example.two-default/ABC@3x.ktx')

        result = _manifest_record(
            index, path, _bundle_id_from_path(path), _snapshot_group_from_path(path))

        self.assertIs(result, wanted)


if __name__ == '__main__':
    unittest.main()
