#!/usr/bin/env python3
"""Focused tests for how the Widgets artifact names a snapshot's folders."""

import unittest

from scripts.artifacts.widgets import _cache_folders

CACHE = 'private/var/mobile/Library/Caches/com.apple.chrono/snapshot-cache'


class WidgetCacheFoldersTest(unittest.TestCase):
    def test_both_folders_are_reported_as_stored(self):
        self.assertEqual(
            _cache_folders(f'{CACHE}/com.example.app.WidgetExtension/today/ABC.snapshot'),
            ('com.example.app.WidgetExtension', 'today'))

    def test_hyphen_and_space_are_kept(self):
        # The previous App Name cut at the first hyphen and the first space.
        self.assertEqual(
            _cache_folders(f'{CACHE}/com.example.notion-keyboard.Widget/My Widget-2/A.snapshot'),
            ('com.example.notion-keyboard.Widget', 'My Widget-2'))

    def test_deeper_file_keeps_the_first_two_folders(self):
        # The pattern's * also crosses /, so a deeper file can match.
        self.assertEqual(
            _cache_folders(f'{CACHE}/com.example.app.Widget/kind/downscaled/A.snapshot'),
            ('com.example.app.Widget', 'kind'))

    def test_windows_separators(self):
        path = f'{CACHE}/com.example.app.Widget/kind/A.snapshot'.replace('/', '\\')
        self.assertEqual(_cache_folders(path), ('com.example.app.Widget', 'kind'))

    def test_last_snapshot_cache_segment_is_used(self):
        self.assertEqual(
            _cache_folders(f'snapshot-cache/case/{CACHE}/com.example.app.Widget/kind/A.snapshot'),
            ('com.example.app.Widget', 'kind'))

    def test_path_without_cache_folder(self):
        self.assertEqual(_cache_folders('private/var/mobile/A.snapshot'), ('', ''))


if __name__ == '__main__':
    unittest.main()
