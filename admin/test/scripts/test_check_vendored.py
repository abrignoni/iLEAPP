"""Pin what admin/scripts/check_vendored.py treats as drift.

The guard compares a vendored file against its upstream with only the banner
removed, so a one-byte change anywhere below the banner has to fail, a banner-only
change has to pass, and a banner the script cannot read has to fail rather than
be skipped. Everything here runs against a local upstream directory, never the
network, so it holds on every CI runner.

It also pins the split between the two outcomes. "The upstream could not be read"
is not evidence that this copy drifted, so it is reported under its own headline
and its own exit code, and it still has to be non-zero: an unreachable upstream
must never read as a pass.
"""
import importlib.util
import io
import pathlib
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

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
        self.assertEqual(problems[0].kind, check_vendored.DRIFT)
        self.assertIn('does not match the upstream file', problems[0].text)

    def test_trailing_newline_counts(self):
        self.vendored.write_bytes(BANNER + BODY.rstrip(b'\n'))
        self.assertEqual(len(self._check()), 1)

    def test_banner_without_a_commit_fails_rather_than_skipping(self):
        broken = BANNER.replace(b'upstream commit ', b'commit ')
        self.vendored.write_bytes(broken + BODY)
        problems = self._check()
        self.assertEqual(len(problems), 1)
        self.assertEqual(problems[0].kind, check_vendored.DRIFT)
        self.assertIn('upstream commit <sha>', problems[0].text)

    def test_file_without_a_banner_fails(self):
        self.vendored.write_bytes(BODY)
        problems = self._check()
        self.assertEqual(len(problems), 1)
        self.assertEqual(problems[0].kind, check_vendored.DRIFT)
        self.assertIn('rule line', problems[0].text)

    # ---- "could not check" is not "has drifted" -------------------------------

    def _run_main(self, argv):
        """Run main() with VENDORED narrowed to the temp file; return (rc, output)."""
        buf = io.StringIO()
        with mock.patch.object(check_vendored, 'VENDORED', ['scripts/module.py']):
            with redirect_stdout(buf):
                rc = check_vendored.main(argv)
        return rc, buf.getvalue()

    def test_unreadable_upstream_is_blocked_not_drift(self):
        """The upstream being unreachable says nothing about this copy."""
        self.vendored.write_bytes(BANNER + BODY)
        problems = check_vendored.check_file('scripts/module.py',
                                             str(self.root / 'no-such-checkout'))
        self.assertEqual(len(problems), 1)
        self.assertEqual(problems[0].kind, check_vendored.BLOCKED)
        self.assertIn('could not read the upstream file', problems[0].text)

    def test_fetch_failure_is_blocked_not_drift(self):
        """A verify failure or an outage is the reported bug: it read as drift."""
        self.vendored.write_bytes(BANNER + BODY)
        boom = check_vendored.urllib.error.URLError('[SSL: CERTIFICATE_VERIFY_FAILED]')
        with mock.patch.object(check_vendored.urllib.request, 'urlopen', side_effect=boom):
            problems = check_vendored.check_file('scripts/module.py')
        self.assertEqual(len(problems), 1)
        self.assertEqual(problems[0].kind, check_vendored.BLOCKED)

    def test_blocked_run_does_not_print_the_drift_headline(self):
        self.vendored.write_bytes(BANNER + BODY)
        rc, out = self._run_main(['--upstream', str(self.root / 'no-such-checkout')])
        self.assertNotIn('have drifted', out)
        self.assertIn('could not be checked', out)
        self.assertEqual(rc, 2)

    def test_blocked_run_is_never_a_pass(self):
        """Exit 0 here would let a broken network silently stop guarding the file."""
        self.vendored.write_bytes(BANNER + BODY)
        rc, _ = self._run_main(['--upstream', str(self.root / 'no-such-checkout')])
        self.assertNotEqual(rc, 0)

    def test_drift_still_exits_1_under_its_own_headline(self):
        self.vendored.write_bytes(BANNER + BODY.replace(b'VALUE = 1', b'VALUE = 2'))
        rc, out = self._run_main(['--upstream', str(self.root / 'upstream')])
        self.assertIn('have drifted', out)
        self.assertNotIn('could not be checked', out)
        self.assertEqual(rc, 1)

    def test_matching_run_exits_0(self):
        self.vendored.write_bytes(BANNER + BODY)
        rc, out = self._run_main(['--upstream', str(self.root / 'upstream')])
        self.assertIn('all matching the pinned upstream commit', out)
        self.assertEqual(rc, 0)

    def test_drift_outranks_blocked_when_both_happen(self):
        """Two guarded files, one drifted and one unreachable: report both, exit 1."""
        (self.root / 'scripts' / 'other.py').write_bytes(
            BANNER.replace(b'pkg/module.py', b'pkg/missing.py') + BODY)
        self.vendored.write_bytes(BANNER + BODY.replace(b'VALUE = 1', b'VALUE = 2'))
        buf = io.StringIO()
        with mock.patch.object(check_vendored, 'VENDORED',
                               ['scripts/module.py', 'scripts/other.py']):
            with redirect_stdout(buf):
                rc = check_vendored.main(['--upstream', str(self.root / 'upstream')])
        out = buf.getvalue()
        self.assertIn('have drifted', out)
        self.assertIn('could not be checked', out)
        self.assertEqual(rc, 1)

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
