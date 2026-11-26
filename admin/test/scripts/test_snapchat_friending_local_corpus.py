#!/usr/bin/env python3
"""Opt-in structural checks of Snapchat - Friending Badges against a local extraction (see
admin/docs/testing/local_corpus_tests.md). Only shapes and timestamp sanity are asserted; no value
from the image is recorded.

    ILEAPP_LOCAL_IMAGE=/path/to/extraction.zip \
        python -m pytest admin/test/scripts/test_snapchat_friending_local_corpus.py -v
"""

import shutil
import unittest
import zipfile
from pathlib import Path

from admin.test.scripts.test_local_corpus_artifacts import LOCAL_IMAGE, LocalCorpusTestCase
from scripts.artifacts import snapchatFriending as module

_STORES = ('/Documents/friending_badge_data.db', '/Documents/friending_notification_snapchatter.db',
           '/DocObjects/primary.docobjects')
_SOURCES = ('BADGE', 'FRIEND', 'SUGGESTION', 'REQUEST')


class _Context:
    def __init__(self, paths):
        self.paths = [str(path) for path in paths]

    def get_files_found(self):
        return self.paths

    def get_relative_path(self, path):
        return Path(path).name


@unittest.skipUnless(LOCAL_IMAGE, 'set ILEAPP_LOCAL_IMAGE to run local corpus tests')
class SnapchatFriendingLocalTest(LocalCorpusTestCase):
    def stage(self):
        """Copy the three stores and their -wal files, keeping each app container's own folder."""
        staged = []
        source = Path(LOCAL_IMAGE)
        root = Path(self.temp_dir.name)
        if source.is_dir():
            for path in source.rglob('*'):
                text = str(path).replace('\\', '/')
                if path.is_file() and text.endswith(_STORES) and '/Data/Application/' in text:
                    target = root / text[text.index('/Data/Application/') + 1:]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, target)
                    wal = path.with_name(path.name + '-wal')
                    if wal.exists():
                        shutil.copy2(wal, target.with_name(target.name + '-wal'))
                    staged.append(target)
            return staged
        with zipfile.ZipFile(source) as archive:
            names = set(archive.namelist())
            for name in sorted(names):
                if not name.endswith(_STORES) or '/Data/Application/' not in name:
                    continue
                target = root / name[name.index('/Data/Application/') + 1:]
                target.parent.mkdir(parents=True, exist_ok=True)
                for suffix in ('', '-wal'):
                    if name + suffix in names:
                        with archive.open(name + suffix) as member, open(str(target) + suffix, 'wb') as out:
                            shutil.copyfileobj(member, out)
                staged.append(target)
        return staged

    def test_structure(self):
        stores = self.stage()
        friending = [s for s in stores if s.name != 'primary.docobjects']
        if not friending:
            self.skipTest('no Snapchat friending store in the local image')
        headers, rows, source = module.snapchatFriendingBadges.__wrapped__(_Context(stores))
        read = set(source.split('\n')) if source else set()
        for store in friending:
            self.assertIn(str(store), read, 'every staged friending store was read')
        self.assert_row_shape(headers, rows)
        for row in rows:
            if row[0]:
                self.assert_plausible_timestamp(row[0])
            if row[1]:
                self.assertTrue(any(word in row[1] for word in _SOURCES), _redact_shape(row[1]))
            self.assertTrue(row[2], 'every row names a user id')


def _redact_shape(value):
    return 'badge source of an unexpected shape: ' + ''.join('#' if c.isalnum() else c for c in str(value))


if __name__ == '__main__':
    unittest.main()
