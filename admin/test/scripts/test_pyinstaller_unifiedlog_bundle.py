"""Every PyInstaller spec must bundle the Unified Log parser, and its license with it.

There are six spec files, one per (CLI, GUI) x (Windows, macOS, Linux). A new spec, or a
spec someone regenerates with `pyi-makespec`, silently goes back to `binaries=[]`, and the
only symptom is that native Apple Unified Log support quietly disappears from that one
platform's release. Nothing else in the test suite would notice.

The specs are plain Python evaluated by PyInstaller, so they are exec'd here with stubbed
PyInstaller globals and the resulting Analysis arguments inspected.

The license check is not decoration. unifiedlog_iterator is Apache-2.0 and this project is
MIT; section 4(a) requires that anyone receiving a redistribution also receives the
license. A build that ships the binary without it is a licensing defect, so the helper
raises rather than quietly omitting it.
"""
import pathlib
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / 'scripts' / 'pyinstaller'))

import unifiedlog_binary  # pylint: disable=wrong-import-position

SPEC_DIR = REPO_ROOT / 'scripts' / 'pyinstaller'
EXPECTED_SPECS = {
    'ileapp.spec', 'ileappGUI.spec',
    'ileapp_Linux.spec', 'ileappGUI_Linux.spec',
    'ileapp_macOS.spec', 'ileappGUI_macOS.spec',
}


class _Inert:
    """Stands in for PYZ/EXE/COLLECT/BUNDLE, which the specs only pass around."""

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        pass


class _CapturedAnalysis:
    """Stands in for PyInstaller's Analysis, recording what the spec asked for.

    Only Analysis records itself. The other stubs must not, or the last thing the spec
    constructs (EXE, or COLLECT/BUNDLE in the macOS specs) would be what gets inspected.
    """

    last = None

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        # Positional args are the scripts list; only the keywords matter here.
        self.kwargs = kwargs
        self.pure = self.zipped_data = self.scripts = []
        self.binaries = self.zipfiles = self.datas = []
        _CapturedAnalysis.last = self


def _run_spec(path):
    """Execute one spec with PyInstaller's globals stubbed out, returning Analysis kwargs."""
    _CapturedAnalysis.last = None
    namespace = {
        'Analysis': _CapturedAnalysis, 'PYZ': _Inert, 'EXE': _Inert,
        'COLLECT': _Inert, 'BUNDLE': _Inert,
        'SPECPATH': str(SPEC_DIR), '__file__': str(path),
    }
    # Spec files are Python that PyInstaller exec's; running them is the only way to
    # see what they actually pass to Analysis.
    exec(compile(path.read_text(encoding='utf-8'), str(path), 'exec'),  # pylint: disable=exec-used
         namespace)  # nosec B102
    if _CapturedAnalysis.last is None:
        raise AssertionError(f'{path.name} never called Analysis()')
    return _CapturedAnalysis.last.kwargs


class TestSpecsBundleTheParser(unittest.TestCase):
    """All six specs must pick up the binary and its license when both are present."""

    @classmethod
    def setUpClass(cls):
        # Point the helper at a throwaway bin/ so the result does not depend on whether
        # the developer has run the fetch script.
        cls.tmpdir = tempfile.mkdtemp()
        cls.original_bin_dir = unifiedlog_binary.BIN_DIR
        unifiedlog_binary.BIN_DIR = cls.tmpdir
        for name in ('unifiedlog_iterator', 'unifiedlog_iterator.exe'):
            path = pathlib.Path(cls.tmpdir) / name
            path.write_bytes(b'not a real binary')
            path.chmod(0o755)
        (pathlib.Path(cls.tmpdir) / unifiedlog_binary.LICENSE_NAME).write_text('Apache-2.0')

    @classmethod
    def tearDownClass(cls):
        unifiedlog_binary.BIN_DIR = cls.original_bin_dir

    def test_the_expected_specs_exist(self):
        # A spec added without being added here would not be covered by the checks below.
        self.assertEqual({p.name for p in SPEC_DIR.glob('*.spec')}, EXPECTED_SPECS)

    def test_every_spec_bundles_binary_and_license(self):
        for name in sorted(EXPECTED_SPECS):
            with self.subTest(spec=name):
                kwargs = _run_spec(SPEC_DIR / name)
                binaries = kwargs['binaries']
                datas = kwargs['datas']
                self.assertTrue(
                    any(dest == 'bin' and 'unifiedlog_iterator' in src for src, dest in binaries),
                    f'{name} does not bundle the parser: {binaries}')
                self.assertTrue(
                    any(dest == 'bin' and unifiedlog_binary.LICENSE_NAME in src
                        for src, dest in datas),
                    f'{name} bundles the parser without its Apache-2.0 license')

    def test_specs_keep_their_own_datas(self):
        # The license is appended to each spec's existing datas; dropping the originals
        # would ship a build with no scripts or assets.
        for name in sorted(EXPECTED_SPECS):
            with self.subTest(spec=name):
                datas = _run_spec(SPEC_DIR / name)['datas']
                self.assertTrue(any('scripts' in str(dest) for _, dest in datas),
                                f'{name} lost its scripts data entry: {datas}')


class TestBuildsWithoutTheBinary(unittest.TestCase):
    """A checkout that has not run the fetch script must still build."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_bin_dir = unifiedlog_binary.BIN_DIR
        unifiedlog_binary.BIN_DIR = self.tmpdir
        self.addCleanup(setattr, unifiedlog_binary, 'BIN_DIR', self.original_bin_dir)

    def test_absent_binary_yields_empty_lists(self):
        self.assertEqual(unifiedlog_binary.unifiedlog_binaries(), [])
        self.assertEqual(unifiedlog_binary.unifiedlog_datas(), [])

    def test_every_spec_still_evaluates(self):
        for name in sorted(EXPECTED_SPECS):
            with self.subTest(spec=name):
                self.assertEqual(_run_spec(SPEC_DIR / name)['binaries'], [])

    def test_binary_without_license_is_refused(self):
        path = pathlib.Path(self.tmpdir) / 'unifiedlog_iterator'
        path.write_bytes(b'x')
        path.chmod(0o755)
        with self.assertRaises(SystemExit):
            unifiedlog_binary.unifiedlog_datas()


class TestRuntimeAndBuildAgreeOnLocation(unittest.TestCase):
    """The specs put the binary in 'bin'; scripts/unifiedlogs.py has to look there."""

    def test_bundle_destination_matches_runtime_search_path(self):
        from scripts import unifiedlogs  # pylint: disable=import-outside-toplevel
        searched = [pathlib.Path(d).name for d in unifiedlogs._bundled_binary_dirs()]  # pylint: disable=protected-access
        self.assertIn('bin', searched)

    def test_repo_bin_directory_is_searched_in_a_source_checkout(self):
        from scripts import unifiedlogs  # pylint: disable=import-outside-toplevel
        searched = [pathlib.Path(d) for d in unifiedlogs._bundled_binary_dirs()]  # pylint: disable=protected-access
        self.assertIn(REPO_ROOT / 'bin', searched)


if __name__ == '__main__':
    unittest.main()
