"""Digest handling in the unifiedlog_iterator fetch script must be case-insensitive.

A Windows examiner following the run-from-source instructions got a hard DIGEST MISMATCH
refusal on a byte-identical download: upstream's Windows .sha256 file is UPPERCASE
(PowerShell Get-FileHash style) while Python's hexdigest() is lowercase, and the
comparison was case-sensitive. The values were equal; only the presentation differed.
Upstream's files also sometimes print the digest twice on one line. Neither quirk is
evidence of tampering, and neither may block a verified download again.
"""
import importlib.util
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

_SPEC = importlib.util.spec_from_file_location(
    'fetch_unifiedlog_iterator',
    REPO_ROOT / 'admin' / 'scripts' / 'fetch_unifiedlog_iterator.py')
fetch = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(fetch)

# The normalizer is module-private; the tests exist precisely to pin its behavior.
normalize = fetch._normalize_digest  # pylint: disable=protected-access

LOWER = '749731fc09d0d107958d777188c99682db8f2d7810835d6afe46172e1d0d9d36'
UPPER = LOWER.upper()


class TestNormalizeDigest(unittest.TestCase):
    """Every formatting variant upstream has actually shipped must normalize equal."""

    def test_uppercase_windows_style(self):
        # The exact failure a Windows user reported: right value, wrong case.
        self.assertEqual(normalize(UPPER), LOWER)

    def test_lowercase_passes_through(self):
        self.assertEqual(normalize(LOWER), LOWER)

    def test_doubled_digest_folds(self):
        # Some of upstream's .sha256 files print the digest twice on one line.
        self.assertEqual(normalize(LOWER + LOWER), LOWER)

    def test_doubled_uppercase_folds_and_lowers(self):
        self.assertEqual(normalize(UPPER + UPPER), LOWER)

    def test_filename_suffix_and_whitespace_stripped(self):
        # shasum-style "digest  filename" lines and stray CR/LF.
        self.assertEqual(normalize(f'{UPPER}  some-file.zip\r\n'), LOWER)

    def test_empty_input_is_empty_not_crash(self):
        self.assertEqual(normalize('  \n'), '')

    def test_distinct_halves_are_not_folded(self):
        # 128 hex chars whose halves differ is NOT the doubled-digest quirk; folding it
        # would hide a genuinely malformed published file.
        other = 'a' * 64 + 'b' * 64
        self.assertEqual(normalize(other), other)


class TestPinnedDigests(unittest.TestCase):
    """The pin table is the trust anchor; keep it in a state comparisons can rely on."""

    def test_every_platform_is_pinned(self):
        # With every digest pinned, the published .sha256 fallback (and its formatting
        # quirks) is out of the trust path entirely for the pinned version.
        for key, (asset, digest) in fetch.ASSETS.items():
            with self.subTest(platform=key):
                self.assertIsNotNone(digest, f'{key} ({asset}) has no pinned digest')

    def test_pins_are_normalized_lowercase_hex(self):
        for key, (_, digest) in fetch.ASSETS.items():
            with self.subTest(platform=key):
                self.assertEqual(digest, digest.lower())
                self.assertEqual(len(digest), 64)
                int(digest, 16)  # raises if not hex

    def test_windows_pin_matches_upstreams_uppercase_publication(self):
        # Upstream publishes this one in uppercase; the pin must be its lowercase form.
        self.assertEqual(fetch.ASSETS['windows-x86_64'][1], LOWER)


if __name__ == '__main__':
    unittest.main()
