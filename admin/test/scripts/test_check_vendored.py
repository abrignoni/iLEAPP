"""Pin what admin/scripts/check_vendored.py treats as drift.

The guard compares a vendored file against its upstream with only the banner
removed, so a one-byte change anywhere below the banner has to fail, a banner-only
change has to pass, and a banner the script cannot read has to fail rather than
be skipped. Everything here runs against a local upstream directory, never the
network, so it holds on every CI runner.
"""
import importlib.util
import pathlib
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / 'admin' / 'scripts' / 'check_vendored.py'

_spec = importlib.util.spec_from_file_location('check_vendored', SCRIPT)
check_vendored = importlib.util.module_from_spec(_spec)
sys.modules['check_vendored'] = check_vendored
_spec.loader.exec_module(check_vendored)

BANNER = (
    b'# ---------------------------------------------------------------------------\n'
    b'# Vendored into this repo from example (github.com/example-owner/example-repo)\n'
    b'#   * upstream commit 0123456789abcdef0123456789abcdef01234567 (2026-01-01).\n'
    b'#   * upstream file pkg/module.py.\n'
    b'# ---------------------------------------------------------------------------\n'
)
BODY = b'"""A module."""\n\nVALUE = 1\n'


class CheckVendoredTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        (self.root / 'upstream' / 'pkg').mkdir(parents=True)
        (self.root / 'upstream' / 'pkg' / 'module.py').write_bytes(BODY)
        (self.root / 'scripts').mkdir()
        self.vendored = self.root / 'scripts' / 'module.py'
        # Point the module at the temp tree so check_file resolves paths there.
        self._repo = check_vendored.REPO
        check_vendored.REPO = str(self.root)
        self.addCleanup(setattr, check_vendored, 'REPO', self._repo)

    def _check(self):
        return check_vendored.check_file('scripts/module.py', str(self.root / 'upstream'))

    def test_matching_body_passes(self):
        self.vendored.write_bytes(BANNER + BODY)
        self.assertEqual(self._check(), [])

    def test_banner_text_is_ignored(self):
        edited = BANNER.replace(b'2026-01-01', b'2026-02-02')
        self.vendored.write_bytes(edited + BODY)
        self.assertEqual(self._check(), [])

    def test_one_byte_below_the_banner_fails(self):
        self.vendored.write_bytes(BANNER + BODY.replace(b'VALUE = 1', b'VALUE = 2'))
        problems = self._check()
        self.assertEqual(len(problems), 1)
        self.assertIn('does not match the upstream file', problems[0])

    def test_trailing_newline_counts(self):
        self.vendored.write_bytes(BANNER + BODY.rstrip(b'\n'))
        self.assertEqual(len(self._check()), 1)

    def test_banner_without_a_commit_fails_rather_than_skipping(self):
        broken = BANNER.replace(b'upstream commit ', b'commit ')
        self.vendored.write_bytes(broken + BODY)
        problems = self._check()
        self.assertEqual(len(problems), 1)
        self.assertIn('upstream commit <sha>', problems[0])

    def test_file_without_a_banner_fails(self):
        self.vendored.write_bytes(BODY)
        problems = self._check()
        self.assertEqual(len(problems), 1)
        self.assertIn('rule line', problems[0])

    def test_banner_fields_are_read_as_written(self):
        info = check_vendored.parse_banner(BANNER)
        self.assertEqual(info, {'owner': 'example-owner', 'repo': 'example-repo',
                                'commit': '0123456789abcdef0123456789abcdef01234567',
                                'file': 'pkg/module.py'})

    def test_every_listed_file_carries_a_readable_banner(self):
        """The real vendored files in this repo, checked without the network."""
        for rel_path in check_vendored.VENDORED:
            data = (pathlib.Path(self._repo) / rel_path).read_bytes()
            banner, body = check_vendored.split_banner(data)
            info = check_vendored.parse_banner(banner)
            self.assertEqual(len(info['commit']), 40, rel_path)
            self.assertTrue(body.strip(), rel_path)


if __name__ == '__main__':
    unittest.main()
