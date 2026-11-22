"""ZIP substring filtering must preserve fnmatch and staging semantics."""
# These regressions intentionally exercise the private filtering/matcher boundary.
# pylint: disable=protected-access
import contextlib
import fnmatch
import io
import ntpath
import os
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.search_files as sf  # pylint: disable=wrong-import-position


class RequiredLiteralTests(unittest.TestCase):
    """The necessary-substring condition must never reject a fnmatch hit."""
    def test_literal_segments_and_conservative_fallback(self):
        """Keep only required text and reject ambiguous bracket syntax."""
        cases = [('', ''), ('*', ''), ('???', ''),
                 ('*/Library/Safari/History.db', '/Library/Safari/History.db'),
                 ('root/a?b*.db', 'root/a'), ('a**longest?z', 'longest'),
                 ('*[a-z]/History.db', ''), ('*[]abc]', ''), ('*[[]*', ''),
                 ('*unfinished[', ''), ('*literal]', ''), ('*é🙂*', 'é🙂')]
        for pattern, expected in cases:
            with self.subTest(pattern=pattern):
                self.assertEqual(sf._required_literal(pattern), expected)

    def test_generated_patterns_never_filter_out_a_match(self):
        """Compare the filter to independent fnmatch under two normalizations."""
        rng = random.Random(20261119)
        chars = 'abAB/\\._é🙂\n[]!?*'
        pairs = [('*/History.db', 'root/a/History.db'),
                 ('*[]abc]', 'root/a'), ('*[[]*', 'root/[abc]'),
                 ('root/*/History.db', 'root/a/b/History.db')]
        for _ in range(6000):
            name = 'root/' + ''.join(rng.choices(chars, k=rng.randrange(1, 35)))
            pattern = ''.join('*' if rng.random() < .18 else
                              '?' if rng.random() < .12 else c for c in name)
            pairs.extend([(pattern, name),
                          (pattern, ''.join(rng.choices(chars, k=rng.randrange(40))))])
        for normalize in (lambda value: value, ntpath.normcase):
            for pattern, name in pairs:
                pattern, name = normalize(pattern), normalize(name)
                required = sf._required_literal(pattern)
                expected = fnmatch.fnmatchcase(name, pattern)
                actual = (not required or required in name) and fnmatch.fnmatchcase(name, pattern)
                self.assertEqual(actual, expected, (pattern, name))


class ZipLiteralFilterTests(unittest.TestCase):
    """Exercise filtering through real ZIP staging and seeker state."""
    NAMES = ('__MACOSX/skip.db', 'z/History.db', 'a/History.db',
             'q/History.db-wal', 'q/History.db-shm', 'other/NO.db',
             'brackets/[abc].db', 'brackets/a.db', 'unicode/é🙂.db',
             'Case/MIXED.db', 'folder/')

    def setUp(self):
        # unittest owns this context and exits it through test cleanup.
        self.tmp = self.enterContext(
            tempfile.TemporaryDirectory(prefix='leapp_literal_filter_'))  # pylint: disable=consider-using-with
        self.archive = Path(self.tmp) / 'input.zip'
        with zipfile.ZipFile(self.archive, 'w') as output:
            for index, name in enumerate(self.NAMES):
                output.writestr(zipfile.ZipInfo(name, (2024, 1, 2, 3, 4, 6)),
                                b'' if name.endswith('/') else f'entry-{index}'.encode())
        self.seeker = sf.FileSeekerZip(str(self.archive), str(Path(self.tmp) / 'data'))
        self.addCleanup(self.seeker.cleanup)

    def sources(self, paths):
        """Return evidence member names in the order handed to artifacts."""
        return [self.seeker.file_infos[p].source_path for p in paths]

    def test_ordered_results_and_staged_bytes_match_independent_fnmatch(self):
        """Preserve member order, sidecars, directory hits, and staged bytes."""
        patterns = ('*', '*/History.db*', '*/History.db', '*[[]abc].db',
                    '*/[!b].db', '*[]abc]*', '*unfinished[', '*literal]',
                    '*é?.db', '*/MIXED.db', 'root/*/History.db', '*/missing.db', '*/folder/')
        for pattern in patterns:
            with self.subTest(pattern=pattern):
                normalized = os.path.normcase(pattern)
                expected = [name for name in self.NAMES
                            if not name.startswith('__MACOSX')
                            and fnmatch.fnmatchcase(os.path.normcase('root/') +
                                                   os.path.normcase(name), normalized)]
                found = self.seeker.search(pattern, force=True)
                self.assertEqual(self.sources(found), expected)
                for path in found:
                    source = self.seeker.file_infos[path].source_path
                    if not source.endswith('/'):
                        self.assertEqual(Path(path).read_bytes(),
                                         f'entry-{self.NAMES.index(source)}'.encode())

    def test_first_hit_and_cached_partial_result_remain_unchanged(self):
        """Keep the existing partial-cache behavior after an early return."""
        first = self.seeker.search('*/History.db', return_on_first_hit=True)
        self.assertEqual(self.sources([first]), ['z/History.db'])
        self.assertEqual(self.seeker.search('*/History.db'), [first])
        all_paths = self.seeker.search('*/History.db', force=True)
        self.assertEqual(self.sources(all_paths), ['z/History.db', 'a/History.db'])
        self.assertEqual(self.seeker.search('*/History.db', return_on_first_hit=True), first)

    def test_force_restages_and_cached_search_does_not(self):
        """Only force should replace an already staged file."""
        found = self.seeker.search('*/History.db')
        Path(found[0]).write_bytes(b'modified staged copy')
        self.assertEqual(self.seeker.search('*/History.db'), found)
        self.assertEqual(Path(found[0]).read_bytes(), b'modified staged copy')
        self.assertEqual(self.seeker.search('*/History.db', force=True), found)
        self.assertEqual(Path(found[0]).read_bytes(), b'entry-1')

    def test_no_hit_first_search_stays_an_empty_list(self):
        """Keep the established empty-list result even in first-hit mode."""
        self.assertEqual(self.seeker.search('*/missing.db', return_on_first_hit=True), [])
        self.assertEqual(self.seeker.search('*/missing.db'), [])

    def test_literal_filter_avoids_unnecessary_matcher_calls(self):
        """Reject irrelevant names cheaply but confirm candidates with fnmatch."""
        original = sf._compile_pattern
        calls = []

        def compile_counted(pattern):
            match = original(pattern)

            def counted(name):
                calls.append(name)
                return match(name)
            return counted

        with mock.patch.object(sf, '_compile_pattern', side_effect=compile_counted):
            found = self.seeker.search('*/History.db')
        self.assertEqual(self.sources(found), ['z/History.db', 'a/History.db'])
        # Includes sidecars in the candidate set; the real matcher rejects them.
        self.assertEqual(len(calls), 4)

    def test_bracket_pattern_uses_full_matcher_for_every_eligible_member(self):
        """Bracket syntax must fall back rather than guess at required text."""
        original = sf._compile_pattern
        calls = []

        def compile_counted(pattern):
            match = original(pattern)

            def counted(name):
                calls.append(name)
                return match(name)
            return counted

        with mock.patch.object(sf, '_compile_pattern', side_effect=compile_counted):
            found = self.seeker.search('*[[]abc].db')
        self.assertEqual(self.sources(found), ['brackets/[abc].db'])
        self.assertEqual(len(calls), len(self.NAMES) - 1)

    def test_first_hit_continues_after_corrupt_matching_member(self):
        """A failed matching entry must not hide a later valid first hit."""
        extract = self.seeker._extract_member

        def damaged(member, *args, **kwargs):
            if member == 'z/History.db':
                raise zipfile.BadZipFile('constructed corrupt-entry condition')
            return extract(member, *args, **kwargs)

        with mock.patch.object(self.seeker, '_extract_member', side_effect=damaged), \
                contextlib.redirect_stdout(io.StringIO()):
            first = self.seeker.search('*/History.db', return_on_first_hit=True)
        self.assertEqual(self.sources([first]), ['a/History.db'])


if __name__ == '__main__':
    unittest.main()
