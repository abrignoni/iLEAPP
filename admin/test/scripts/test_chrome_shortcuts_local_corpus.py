#!/usr/bin/env python3
"""Opt-in structural checks of Omnibox Shortcuts against a local extraction (see
admin/docs/testing/local_corpus_tests.md). Only shapes and timestamp sanity are asserted; no value
from the image is recorded.

    ILEAPP_LOCAL_IMAGE=/path/to/extraction.zip \
        python -m pytest admin/test/scripts/test_chrome_shortcuts_local_corpus.py -v
"""

import shutil
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from admin.test.scripts.test_local_corpus_artifacts import LOCAL_IMAGE, LocalCorpusTestCase
from scripts.artifacts import chromeShortcuts as module

MATCH_TYPE = r'^\d+( \([A-Z_]+(, pre-migration numbering)?\))?$'
TRANSITION = r'^\d+( \([A-Z_]+\))?(, qualifiers 0x[0-9A-F]{8})?$'


class _Context:
    def __init__(self, paths):
        self.paths = [str(path) for path in paths]

    def get_files_found(self):
        return self.paths

    def get_relative_path(self, path):
        return Path(path).name


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class ChromeShortcutsLocalTest(LocalCorpusTestCase):
    def stage(self):
        """Copy each Chrome Shortcuts database and its -wal into its own profile folder."""
        staged = []
        source = Path(LOCAL_IMAGE)
        if source.is_dir():
            hits = [path for path in source.rglob('Shortcuts')
                    if path.is_file() and path.parent.parent.name == 'Chrome']
            for number, path in enumerate(hits):
                target = Path(self.temp_dir.name) / str(number) / 'Chrome' / 'Default'
                target.mkdir(parents=True)
                shutil.copy2(path, target / 'Shortcuts')
                wal = path.with_name('Shortcuts-wal')
                if wal.exists():
                    shutil.copy2(wal, target / 'Shortcuts-wal')
                staged.append(target / 'Shortcuts')
            return staged
        with zipfile.ZipFile(source) as archive:
            names = set(archive.namelist())
            hits = [name for name in names if name.endswith('/Shortcuts') and '/Google/Chrome/' in name]
            for number, name in enumerate(sorted(hits)):
                target = Path(self.temp_dir.name) / str(number) / 'Chrome' / 'Default'
                target.mkdir(parents=True)
                for suffix in ('', '-wal'):
                    if name + suffix in names:
                        with archive.open(name + suffix) as member, open(target / f'Shortcuts{suffix}', 'wb') as out:
                            shutil.copyfileobj(member, out)
                staged.append(target / 'Shortcuts')
        return staged

    def test_structure(self):
        stores = self.stage()
        if not stores:
            self.skipTest('no Chrome Shortcuts database in the local image')
        with mock.patch.object(module, 'get_browser_name', return_value='Chrome'):
            headers, rows, source = module.chromeShortcuts.__wrapped__(_Context(stores))
        self.assertEqual(set(source.split('\n')), {str(store) for store in stores},
                         'every staged store was read')
        self.assert_row_shape(headers, rows)
        for row in rows:
            self.assert_plausible_timestamp(row[0])
            self.assert_matches(row[6], MATCH_TYPE, 'match type')
            self.assert_matches(row[7], TRANSITION, 'transition')


if __name__ == '__main__':
    unittest.main()
