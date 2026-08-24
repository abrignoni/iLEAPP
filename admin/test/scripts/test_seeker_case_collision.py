"""Pin the seeker's dest-guard for case-variant evidence files (issue #1948).

An iOS extraction can hold com.apple.MobileSMS.plist and com.apple.mobileSMS.plist
in one directory as two different files. On a case-insensitive report volume both
sources fold to one destination under data/, and before the guard the second copy
silently destroyed the first, so the preserved file at a cited path could hold the
other file's bytes.

The guard writes the colliding copy to name~case-<tag>.ext instead, where the tag
is derived from the evidence-relative source path. These tests pin three
properties: both byte streams survive, the alternate name is a pure function of
the source (stable across re-searches, seeker instances and force=True), and
directory members never mint a tagged twin.

The claims logic folds keys only when the data folder's volume folds case, which
CI runners may not. Tests that need folding force the seeker's probed flag, which
exercises the identical code path on any filesystem.
"""
import hashlib
import os
import pathlib
import shutil
import sys
import tempfile
import unittest
import zipfile
from functools import lru_cache

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.search_files import (  # pylint: disable=wrong-import-position
    FileSeekerZip, _case_variant_digest, _disambiguated_data_path,
    _probe_volume_case_insensitive)
import scripts.search_files  # pylint: disable=wrong-import-position

PREF = 'private/var/mobile/Library/Preferences/'
UPPER = PREF + 'com.apple.MobileSMS.plist'
LOWER = PREF + 'com.apple.mobileSMS.plist'
UPPER_CONTENT = b'upper spelling bytes'
LOWER_CONTENT = b'lower spelling bytes'
PATTERN = '*/mobile/Library/Preferences/com.apple.[Mm]obileSMS.plist'


def _expected_tag(member):
    return hashlib.sha256(member.encode('utf-8')).hexdigest()[:8]


def _tree_files(base):
    found = {}
    for root, _dirs, files in os.walk(base):
        for name in files:
            full = os.path.join(root, name)
            with open(full, 'rb') as fin:
                found[os.path.relpath(full, base).replace(os.sep, '/')] = fin.read()
    return found


class TestDisambiguatorUnit(unittest.TestCase):
    """The claims logic, exercised directly with both volume behaviours."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _dest(self, name):
        return os.path.join(self.tmpdir, name)

    def test_case_sensitive_volume_keeps_both_plain_names(self):
        claims = {}
        first = _disambiguated_data_path(self._dest('A.plist'), 'src/A.plist',
                                         claims, False)
        second = _disambiguated_data_path(self._dest('a.plist'), 'src/a.plist',
                                          claims, False)
        self.assertEqual(os.path.basename(first), 'A.plist')
        self.assertEqual(os.path.basename(second), 'a.plist')

    def test_folding_volume_tags_the_second_source(self):
        claims = {}
        first = _disambiguated_data_path(self._dest('A.plist'), 'src/A.plist',
                                         claims, True)
        second = _disambiguated_data_path(self._dest('a.plist'), 'src/a.plist',
                                          claims, True)
        self.assertEqual(os.path.basename(first), 'A.plist')
        self.assertEqual(os.path.basename(second),
                         f'a~case-{_expected_tag("src/a.plist")}.plist')

    def test_same_source_returns_the_same_path_every_time(self):
        claims = {}
        _disambiguated_data_path(self._dest('A.plist'), 'src/A.plist', claims, True)
        paths = {_disambiguated_data_path(self._dest('a.plist'), 'src/a.plist',
                                          claims, True)
                 for _ in range(4)}
        self.assertEqual(len(paths), 1)

    def test_tag_is_derived_from_hash_source_when_given(self):
        claims = {}
        _disambiguated_data_path(self._dest('A.plist'), '/mnt/evidence/A.plist',
                                 claims, True, hash_source='rel/A.plist')
        second = _disambiguated_data_path(self._dest('a.plist'),
                                          '/mnt/evidence/a.plist', claims, True,
                                          hash_source='rel/a.plist')
        self.assertEqual(os.path.basename(second),
                         f'a~case-{_expected_tag("rel/a.plist")}.plist')

    def test_separator_and_leading_slash_do_not_change_the_tag(self):
        self.assertEqual(_case_variant_digest('a\\b/C.plist'),
                         _case_variant_digest('/a/b/C.plist'))
        self.assertNotEqual(_case_variant_digest('a/b/C.plist'),
                            _case_variant_digest('a/b/c.plist'))

    def test_squatted_short_tag_falls_through_to_the_full_digest(self):
        claims = {}
        _disambiguated_data_path(self._dest('A.plist'), 'src/A.plist', claims, True)
        digest = _case_variant_digest('src/a.plist')
        squatter = self._dest(f'a~case-{digest[:8]}.plist')
        with open(squatter, 'wb') as fout:
            fout.write(b'evidence file that owns the short name')
        second = _disambiguated_data_path(self._dest('a.plist'), 'src/a.plist',
                                          claims, True)
        self.assertEqual(os.path.basename(second), f'a~case-{digest}.plist')


class TestZipCaseCollision(unittest.TestCase):
    """FileSeekerZip with the folding path forced, so it runs on any volume."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.zip_path = os.path.join(self.tmpdir, 'fs-full.zip')
        with zipfile.ZipFile(self.zip_path, 'w') as z:
            z.writestr(UPPER, UPPER_CONTENT)
            z.writestr(LOWER, LOWER_CONTENT)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _seeker(self, subdir):
        data_folder = os.path.join(self.tmpdir, subdir)
        os.makedirs(data_folder, exist_ok=True)
        seeker = FileSeekerZip(self.zip_path, data_folder)
        seeker._data_folder_folds_case = True  # pylint: disable=protected-access
        return seeker, data_folder

    def test_both_sources_survive_under_distinct_names(self):
        seeker, data_folder = self._seeker('data')
        try:
            paths = [str(p) for p in seeker.search(PATTERN)]
            self.assertEqual(len(paths), 2)
            names = sorted(os.path.basename(p) for p in paths)
            self.assertEqual(names, ['com.apple.MobileSMS.plist',
                                     f'com.apple.mobileSMS~case-{_expected_tag(LOWER)}.plist'])
            contents = sorted(_tree_files(data_folder).values())
            self.assertEqual(contents, sorted([UPPER_CONTENT, LOWER_CONTENT]))
        finally:
            seeker.cleanup()

    def test_file_infos_keep_the_true_source_for_the_tagged_copy(self):
        seeker, _data_folder = self._seeker('data')
        try:
            paths = [str(p) for p in seeker.search(PATTERN)]
            tagged = [p for p in paths if '~case-' in p]
            self.assertEqual(len(tagged), 1)
            self.assertEqual(seeker.file_infos[tagged[0]].source_path, LOWER)
        finally:
            seeker.cleanup()

    def test_forced_research_returns_stable_paths_and_mints_nothing(self):
        seeker, data_folder = self._seeker('data')
        try:
            first = sorted(str(p) for p in seeker.search(PATTERN))
            for _ in range(3):
                again = sorted(str(p) for p in seeker.search(PATTERN, force=True))
                self.assertEqual(again, first)
            self.assertEqual(len(_tree_files(data_folder)), 2)
        finally:
            seeker.cleanup()

    def test_two_seeker_instances_produce_identical_names(self):
        seeker_a, folder_a = self._seeker('data_a')
        seeker_b, folder_b = self._seeker('data_b')
        try:
            seeker_a.search(PATTERN)
            seeker_b.search(PATTERN)
            names_a = sorted(_tree_files(folder_a))
            names_b = sorted(_tree_files(folder_b))
            self.assertEqual(names_a, names_b)
        finally:
            seeker_a.cleanup()
            seeker_b.cleanup()

    def test_directory_members_never_mint_a_tagged_twin(self):
        late_dir_zip = os.path.join(self.tmpdir, 'late-dir.zip')
        with zipfile.ZipFile(late_dir_zip, 'w') as z:
            z.writestr('a/b/file.txt', b'content')
            z.writestr(zipfile.ZipInfo('a/b/'), b'')
        data_folder = os.path.join(self.tmpdir, 'data_dirs')
        os.makedirs(data_folder)
        seeker = FileSeekerZip(late_dir_zip, data_folder)
        seeker._data_folder_folds_case = True  # pylint: disable=protected-access
        try:
            seeker.search('*/a/b*')
            entries = []
            for _root, dirs, files in os.walk(data_folder):
                entries.extend(dirs)
                entries.extend(files)
            self.assertFalse([e for e in entries if '~case-' in e], entries)
        finally:
            seeker.cleanup()


class TestZipCaseCollisionRealVolume(unittest.TestCase):
    """No forcing: whatever this volume does, both byte streams must survive."""

    def test_both_byte_streams_exist_on_disk(self):
        tmpdir = tempfile.mkdtemp()
        try:
            zip_path = os.path.join(tmpdir, 'fs-full.zip')
            with zipfile.ZipFile(zip_path, 'w') as z:
                z.writestr(UPPER, UPPER_CONTENT)
                z.writestr(LOWER, LOWER_CONTENT)
            data_folder = os.path.join(tmpdir, 'data')
            os.makedirs(data_folder)
            seeker = FileSeekerZip(zip_path, data_folder)
            try:
                seeker.search(PATTERN)
            finally:
                seeker.cleanup()
            contents = sorted(_tree_files(data_folder).values())
            self.assertEqual(contents, sorted([UPPER_CONTENT, LOWER_CONTENT]))
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestWindowsPatternFold(unittest.TestCase):
    """With Windows-style normcase, the bracket pattern still matches both members.

    os.path.normcase on Windows lowercases and flips separators. The seeker caches
    it at import; simulate it here to pin that both case-variant archive members
    match and both are preserved, which is what a Windows run does at the matching
    layer.
    """

    def setUp(self):
        self._saved = scripts.search_files.normcase
        scripts.search_files.normcase = lru_cache(maxsize=None)(
            lambda s: s.replace('/', '\\').lower())

    def tearDown(self):
        scripts.search_files.normcase = self._saved

    def test_bracket_pattern_matches_both_spellings(self):
        tmpdir = tempfile.mkdtemp()
        try:
            zip_path = os.path.join(tmpdir, 'fs-full.zip')
            with zipfile.ZipFile(zip_path, 'w') as z:
                z.writestr(UPPER, UPPER_CONTENT)
                z.writestr(LOWER, LOWER_CONTENT)
            data_folder = os.path.join(tmpdir, 'data')
            os.makedirs(data_folder)
            seeker = FileSeekerZip(zip_path, data_folder)
            seeker._data_folder_folds_case = True  # pylint: disable=protected-access
            try:
                paths = [str(p) for p in seeker.search(PATTERN)]
            finally:
                seeker.cleanup()
            self.assertEqual(len(paths), 2)
            contents = sorted(_tree_files(data_folder).values())
            self.assertEqual(contents, sorted([UPPER_CONTENT, LOWER_CONTENT]))
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestVolumeProbe(unittest.TestCase):
    """The probe reports the volume truthfully and cleans up after itself."""

    def test_probe_is_boolean_and_leaves_nothing(self):
        tmpdir = tempfile.mkdtemp()
        try:
            result = _probe_volume_case_insensitive(tmpdir)
            self.assertIsInstance(result, bool)
            self.assertEqual([f for f in os.listdir(tmpdir) if 'probe' in f], [])
            # A volume where aA resolves after writing only Aa folds case.
            with open(os.path.join(tmpdir, 'Aa'), 'w', encoding='utf-8') as fout:
                fout.write('x')
            self.assertEqual(result, os.path.exists(os.path.join(tmpdir, 'aA')))
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
