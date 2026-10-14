"""Pin what admin/scripts/check_vendored.py treats as drift.

The guard compares each vendored file against the hash recorded in
scripts/vendor/vendored.json and against the upstream file at the pinned commit,
read from a checkout given with --upstream or fetched from GitHub. A changed byte
has to fail, a matching file has to pass, and a file that opens with a vendoring
banner is compared to upstream below that banner.

It also pins the split between the two outcomes. An upstream that cannot be read
was never compared, so it is reported under its own headline and its own exit
code rather than as drift. That exit code still has to be non-zero: an upstream
that cannot be read must never read as a pass.

Everything here runs against a temporary tree; the fetch is patched, never made.
"""
import hashlib
import importlib.util
import io
import json
import pathlib
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / 'admin' / 'scripts' / 'check_vendored.py'

_spec = importlib.util.spec_from_file_location('check_vendored', SCRIPT)
check_vendored = importlib.util.module_from_spec(_spec)
sys.modules['check_vendored'] = check_vendored
_spec.loader.exec_module(check_vendored)

BODY = b'"""A vendored module."""\n\nVALUE = 1\n'
BANNER = (b'# ---------------------------------------------------------------------------\n'
          b'# Vendored from example (github.com/example/example), unchanged below this banner.\n'
          b'#   * upstream commit 0123456789abcdef0123456789abcdef01234567.\n'
          b'# ---------------------------------------------------------------------------\n')


class CheckVendoredTest(unittest.TestCase):
    """The outcomes, and the exit code each one uses."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        (self.root / 'scripts' / 'vendor').mkdir(parents=True)
        self.vendored = self.root / 'scripts' / 'vendor' / 'module.py'
        self.vendored.write_bytes(BODY)
        self.bannered = self.root / 'scripts' / 'bannered.py'
        self.bannered.write_bytes(BANNER + BODY)
        self.upstream = self.root / 'upstream'
        self.upstream.mkdir()
        (self.upstream / 'module.py').write_bytes(BODY)
        (self.upstream / 'bannered.py').write_bytes(BODY)

        self.manifest_path = self.root / 'scripts' / 'vendor' / 'vendored.json'
        self._write_manifest()

        self._repo, self._manifest = check_vendored.REPO, check_vendored.MANIFEST
        check_vendored.REPO = str(self.root)
        check_vendored.MANIFEST = str(self.manifest_path)
        self.addCleanup(setattr, check_vendored, 'REPO', self._repo)
        self.addCleanup(setattr, check_vendored, 'MANIFEST', self._manifest)

    def _entry(self, path, upstream_file, data, **extra):
        entry = {'path': path, 'name': 'example', 'version': '1.0',
                 'upstream': 'https://github.com/example/example', 'upstream_file': upstream_file,
                 'commit': '0123456789abcdef0123456789abcdef01234567',
                 'sha256': hashlib.sha256(data).hexdigest()}
        entry.update(extra)
        return entry

    def _write_manifest(self):
        entries = [self._entry('scripts/vendor/module.py', 'module.py', BODY),
                   self._entry('scripts/bannered.py', 'bannered.py', BANNER + BODY, banner=True)]
        self.manifest_path.write_text(json.dumps({'vendored': entries}), encoding='utf-8')

    def _run(self, argv=None):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = check_vendored.main(argv or [])
        return rc, buf.getvalue()

    # ---- hashes alone -------------------------------------------------------

    def test_matching_files_pass_offline(self):
        rc, out = self._run(['--offline'])
        self.assertIn('all matching what was recorded', out)
        self.assertEqual(rc, 0)

    def test_one_changed_byte_is_drift(self):
        self.vendored.write_bytes(BODY.replace(b'VALUE = 1', b'VALUE = 2'))
        rc, out = self._run(['--offline'])
        self.assertIn('have drifted', out)
        self.assertNotIn('could not be checked', out)
        self.assertEqual(rc, 1)

    def test_a_missing_file_is_drift(self):
        self.vendored.unlink()
        rc, out = self._run(['--offline'])
        self.assertIn('not on disk', out)
        self.assertEqual(rc, 1)

    def test_a_banner_edit_changes_the_recorded_hash(self):
        # The banner is part of the copy, so re-vendoring means updating it and
        # then re-recording the hash with --update, in that order.
        self.bannered.write_bytes(BANNER.replace(b'unchanged', b'UNCHANGED') + BODY)
        rc, out = self._run(['--offline'])
        self.assertIn('have drifted', out)
        self.assertEqual(rc, 1)

    # ---- against a checkout -------------------------------------------------

    def test_matching_a_checkout_passes(self):
        rc, out = self._run(['--upstream', str(self.upstream)])
        self.assertIn('all matching what was recorded and the pinned upstream', out)
        self.assertEqual(rc, 0)

    def test_the_banner_is_ignored_when_comparing_to_upstream(self):
        rc, out = self._run(['--upstream', f'example={self.upstream}'])
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.count('and matches'), 2)

    def test_a_body_that_differs_from_the_checkout_is_drift(self):
        # The copy still hashes to what was recorded, so only the upstream
        # comparison can see this: someone edited the copy and re-recorded it.
        edited = BODY.replace(b'VALUE = 1', b'VALUE = 2')
        self.vendored.write_bytes(edited)
        manifest = json.loads(self.manifest_path.read_text(encoding='utf-8'))
        manifest['vendored'][0]['sha256'] = hashlib.sha256(edited).hexdigest()
        self.manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        rc, out = self._run(['--upstream', str(self.upstream)])
        self.assertIn('differs from the checkout at', out)
        self.assertIn('have drifted', out)
        self.assertEqual(rc, 1)

    def test_a_checkout_without_the_file_is_could_not_check(self):
        (self.upstream / 'module.py').unlink()
        rc, out = self._run(['--upstream', str(self.upstream)])
        self.assertIn('could not be checked', out)
        self.assertNotIn('have drifted', out)
        self.assertEqual(rc, 2)

    # ---- against GitHub (patched) --------------------------------------------

    def test_a_matching_fetch_passes(self):
        with mock.patch.object(check_vendored, 'fetch_upstream', return_value=BODY):
            rc, out = self._run()
        self.assertEqual(rc, 0, out)
        self.assertIn('and matches https://github.com/example/example@0123456', out)

    def test_a_fetch_that_differs_is_drift(self):
        with mock.patch.object(check_vendored, 'fetch_upstream',
                               return_value=BODY.replace(b'1', b'9')):
            rc, out = self._run()
        self.assertIn('does not match the upstream file at the pinned commit', out)
        self.assertIn('have drifted', out)
        self.assertEqual(rc, 1)

    def test_an_unreachable_upstream_is_could_not_check_not_a_pass(self):
        with mock.patch.object(check_vendored, 'fetch_upstream',
                               side_effect=urllib.error.URLError('no network')):
            rc, out = self._run()
        self.assertIn('could not be checked', out)
        self.assertNotIn('have drifted', out)
        self.assertEqual(rc, 2)

    def test_fetch_url_is_built_from_the_manifest(self):
        entry = json.loads(self.manifest_path.read_text(encoding='utf-8'))['vendored'][0]
        seen = {}

        class _Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        def fake_urlopen(url, timeout=0):
            seen['url'], seen['timeout'] = url, timeout
            return _Response(BODY)

        with mock.patch.object(check_vendored.urllib.request, 'urlopen', fake_urlopen):
            self.assertEqual(check_vendored.fetch_upstream(entry), BODY)
        self.assertEqual(seen['url'], 'https://raw.githubusercontent.com/example/example/'
                                      '0123456789abcdef0123456789abcdef01234567/module.py')

    # ---- --update -------------------------------------------------------------

    def test_update_records_the_hash_on_disk(self):
        changed = BODY.replace(b'1', b'2')
        self.vendored.write_bytes(changed)
        rc, out = self._run(['--update'])
        self.assertEqual(rc, 0, out)
        recorded = json.loads(self.manifest_path.read_text(encoding='utf-8'))['vendored'][0]['sha256']
        self.assertEqual(recorded, hashlib.sha256(changed).hexdigest())
        rc, _ = self._run(['--offline'])
        self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
