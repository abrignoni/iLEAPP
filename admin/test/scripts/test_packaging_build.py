"""packaging/build.py and packaging/ileapp.spec must bundle everything a built iLEAPP has
been found to die without, and refuse to build what may not be shipped.

The build itself is exercised by `python packaging/build.py smoke`, which the test_builds
workflow runs on every platform, since a PyInstaller run takes minutes. What is checked
here is what build.py decides and what the spec asks PyInstaller for, which is where each
requirement lives.

The requirements carried over from the six specs this replaced, each learned from a build
that crashed on startup or shipped without something:

- leapp_functions and assets/ were missing from the CLI builds (ModuleNotFoundError:
  leapp_functions.parsers on first run).
- google.protobuf and PIL submodules were never collected (ModuleNotFoundError:
  google.protobuf.internal, then an ImportError from PIL). The spec still collects both,
  and every artifact module is now a hidden import, so what the artifacts import is
  followed instead of listed by hand.
- The Unified Log parser must be bundled when it has been fetched, and never without its
  Apache-2.0 licence and its third-party notices: this project is MIT, section 4(a) of
  that licence requires anyone receiving a redistribution to receive the licence too, and
  the binary statically links Rust crates under their own licences.

The spec is plain Python that PyInstaller exec's, so it is exec'd here with PyInstaller's
names stubbed out, and what it passed to them inspected.
"""
import functools
import hashlib
import importlib.util
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PACKAGING = REPO_ROOT / 'packaging'
DRIVER = PACKAGING / 'build.py'
SPEC = PACKAGING / 'ileapp.spec'


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_driver():
    return _load(DRIVER, 'ileapp_build_driver_under_test')


def _run_driver(*args):
    return subprocess.run([sys.executable, str(DRIVER), *args],
                          capture_output=True, text=True, check=False)


# -- the spec, exec'd with PyInstaller stubbed out -----------------------------------------

class _Call:
    """Stands in for Analysis, PYZ, EXE, COLLECT and BUNDLE, recording how each was called."""

    def __init__(self, kind, calls, *args, **kwargs):
        self.kind, self.args, self.kwargs = kind, args, kwargs
        # What the spec reads back from an Analysis, as sentinels it can pass on.
        self.pure, self.scripts = ['<a.pure>'], ['<a.scripts>']
        self.binaries, self.datas = ['<a.binaries>'], ['<a.datas>']
        calls.append(self)


class _Struct:
    """Stands in for PyInstaller's Windows version-resource classes."""

    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs


def _pyinstaller_stubs():
    """The PyInstaller modules the spec imports. collect_submodules returns a sentinel, so
    what is checked is that the spec asks for a package's submodules, the part a
    regenerated spec loses, rather than whatever a local PyInstaller resolves them to."""
    hooks = types.ModuleType('PyInstaller.utils.hooks')
    hooks.collect_submodules = lambda package: [f'<collect_submodules:{package}>']
    versioninfo = types.ModuleType('PyInstaller.utils.win32.versioninfo')
    for name in ('VSVersionInfo', 'FixedFileInfo', 'StringFileInfo', 'StringTable',
                 'StringStruct', 'VarFileInfo', 'VarStruct'):
        setattr(versioninfo, name, type(name, (_Struct,), {}))
    win32 = types.ModuleType('PyInstaller.utils.win32')
    win32.versioninfo = versioninfo
    utils = types.ModuleType('PyInstaller.utils')
    utils.hooks, utils.win32 = hooks, win32
    root = types.ModuleType('PyInstaller')
    root.utils = utils
    return {'PyInstaller': root, 'PyInstaller.utils': utils, 'PyInstaller.utils.hooks': hooks,
            'PyInstaller.utils.win32': win32, 'PyInstaller.utils.win32.versioninfo': versioninfo}


def _run_spec(platform, onefile):
    """Execute the spec as PyInstaller would on `platform`, returning the calls it made."""
    calls = []
    namespace = {kind: functools.partial(_Call, kind, calls)
                 for kind in ('Analysis', 'PYZ', 'EXE', 'COLLECT', 'BUNDLE')}
    namespace.update(SPECPATH=str(PACKAGING), __file__=str(SPEC))
    env = {'ILEAPP_ONEFILE': '1' if onefile else '0'}
    with mock.patch.dict(sys.modules, _pyinstaller_stubs()), \
            mock.patch.dict('os.environ', env), \
            mock.patch.object(sys, 'platform', platform):
        exec(compile(SPEC.read_text(encoding='utf-8'), str(SPEC), 'exec'),  # pylint: disable=exec-used
             namespace)  # nosec B102
    return {call.kind: call for call in calls}, calls


class TestSpec(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = _load_driver()

    def test_one_executable_starts_from_the_entry_point(self):
        calls, _ = _run_spec('linux', onefile=False)
        analysis = calls['Analysis']
        self.assertEqual(analysis.args[0], [str(self.driver.ENTRYPOINT)])
        self.assertEqual(analysis.kwargs['pathex'], [str(REPO_ROOT)])
        self.assertEqual(calls['EXE'].kwargs['name'], 'ileapp')
        # The command line has to print and return its exit code.
        self.assertTrue(calls['EXE'].kwargs['console'])

    def test_what_is_bundled_comes_from_the_driver(self):
        analysis = _run_spec('linux', onefile=False)[0]['Analysis'].kwargs
        self.assertEqual(analysis['binaries'], self.driver.bundle_binaries())
        self.assertEqual(analysis['datas'], self.driver.bundle_datas())
        hidden = analysis['hiddenimports']
        for name in self.driver.hidden_imports():
            self.assertIn(name, hidden)

    def test_protobuf_and_pil_are_collected(self):
        hidden = _run_spec('linux', onefile=False)[0]['Analysis'].kwargs['hiddenimports']
        self.assertIn('<collect_submodules:google.protobuf>', hidden,
                      'frozen builds crash on startup without google.protobuf')
        self.assertIn('<collect_submodules:PIL>', hidden)

    def test_the_folder_build_is_iLEAPP_with_ileapp_inside(self):  # pylint: disable=invalid-name
        calls, _ = _run_spec('linux', onefile=False)
        exe = calls['EXE']
        self.assertTrue(exe.kwargs['exclude_binaries'])
        self.assertEqual(exe.kwargs['contents_directory'], self.driver.CONTENTS)
        collect = calls['COLLECT']
        self.assertEqual(collect.kwargs['name'], 'iLEAPP')
        self.assertIn(['<a.binaries>'], collect.args)
        self.assertIn(['<a.datas>'], collect.args)
        self.assertNotIn('BUNDLE', calls)

    def test_the_onefile_build_carries_everything_in_the_executable(self):
        for platform in ('linux', 'darwin', 'win32'):
            with self.subTest(platform=platform):
                calls, _ = _run_spec(platform, onefile=True)
                self.assertIn(['<a.binaries>'], calls['EXE'].args)
                self.assertIn(['<a.datas>'], calls['EXE'].args)
                self.assertNotIn('COLLECT', calls)
                self.assertNotIn('BUNDLE', calls)

    def test_macos_gets_a_bundle_that_shows_in_the_dock(self):
        bundle = _run_spec('darwin', onefile=False)[0]['BUNDLE'].kwargs
        number = self.driver.numeric_version(self.driver.read_version())
        self.assertEqual(bundle['name'], 'iLEAPP.app')
        self.assertEqual(bundle['bundle_identifier'], 'org.leapps.iLEAPP')
        self.assertEqual(bundle['icon'], str(self.driver.ICNS))
        plist = bundle['info_plist']
        self.assertEqual(plist['CFBundleShortVersionString'], number)
        self.assertEqual(plist['CFBundleVersion'], number)
        # console=True makes PyInstaller mark the bundle background-only, which leaves the
        # window without a Dock icon or a menu bar.
        self.assertIs(plist['LSBackgroundOnly'], False)

    def test_windows_gets_the_icon_the_version_and_a_hidden_console(self):
        exe = _run_spec('win32', onefile=False)[0]['EXE'].kwargs
        self.assertEqual(exe['icon'], str(self.driver.ICO))
        self.assertEqual(exe['hide_console'], 'hide-early')
        fields = self.driver.windows_version_fields(self.driver.read_version())
        fixed = exe['version'].kwargs['ffi'].kwargs
        self.assertEqual(fixed['filevers'], fields['numbers'])
        self.assertEqual(fixed['prodvers'], fields['numbers'])
        table = exe['version'].kwargs['kids'][0].args[0][0]
        strings = {struct.args[0]: struct.args[1] for struct in table.args[1]}
        self.assertEqual(strings, fields['strings'])

    def test_the_console_is_hidden_only_on_windows(self):
        for platform in ('linux', 'darwin'):
            with self.subTest(platform=platform):
                exe = _run_spec(platform, onefile=False)[0]['EXE'].kwargs
                self.assertIsNone(exe['hide_console'])
                self.assertNotIn('version', exe)


# -- the driver --------------------------------------------------------------------------

class TestDriver(unittest.TestCase):

    def setUp(self):
        self.driver = _load_driver()

    def test_help_lists_every_phase(self):
        result = _run_driver('--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        for word in ('exe', 'smoke', 'installer', 'all', 'verify'):
            self.assertIn(word, result.stdout)

    def test_version_matches_the_app_without_importing_it(self):
        from scripts.version_info import leapp_version  # pylint: disable=import-outside-toplevel
        self.assertEqual(self.driver.read_version(), leapp_version)

    def test_numeric_version_keeps_only_the_leading_numbers(self):
        self.assertEqual(self.driver.numeric_version('2026.4.2-dev'), '2026.4.2')
        self.assertEqual(self.driver.numeric_version('2.6.0-dev.0'), '2.6.0')
        self.assertEqual(self.driver.numeric_version('1.2.3.4.5'), '1.2.3.4')
        with self.assertRaises(SystemExit):
            self.driver.numeric_version('dev')

    def test_the_windows_version_resource_takes_four_numbers_and_the_full_string(self):
        fields = self.driver.windows_version_fields('2026.4.2-dev')
        self.assertEqual(fields['numbers'], (2026, 4, 2, 0))
        self.assertEqual(fields['strings']['FileVersion'], '2026.4.2-dev')
        self.assertEqual(fields['strings']['ProductVersion'], '2026.4.2-dev')
        self.assertEqual(fields['strings']['OriginalFilename'], 'ileapp.exe')

    def test_all_refuses_onefile_because_the_installer_packages_a_folder(self):
        result = _run_driver('all', '--onefile')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('one-folder', result.stdout + result.stderr)

    def test_all_refuses_a_sign_tool_because_the_executable_would_be_unsigned(self):
        result = _run_driver('all', '--sign-tool', 'anything')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unsigned', result.stdout + result.stderr)

    def test_every_installer_needs_the_folder_build_from_phase_one(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(self.driver, 'DIST', pathlib.Path(tmp) / 'dist'):
            for build in ('_build_inno', '_build_dmg', '_build_appimage'):
                with self.subTest(installer=build), self.assertRaises(SystemExit) as caught:
                    getattr(self.driver, build)(*([None] if build == '_build_inno' else []))
                self.assertIn("run 'exe' first", str(caught.exception))

    @unittest.skipIf(sys.platform == 'win32', 'the Sign Tool is what Windows uses')
    def test_a_sign_tool_is_refused_off_windows_with_the_right_pointer(self):
        with self.assertRaises(SystemExit) as caught:
            self.driver.build_installer('anything')
        self.assertIn('codesign', str(caught.exception))

    def test_clean_leaves_the_rest_of_dist_alone(self):
        """dist/ is where release zips get made by hand; --clean removes only the build's own output."""
        with tempfile.TemporaryDirectory() as tmp:
            dist, build = pathlib.Path(tmp) / 'dist', pathlib.Path(tmp) / 'build'
            with mock.patch.object(self.driver, 'DIST', dist), \
                    mock.patch.object(self.driver, 'BUILD', build):
                (dist / 'iLEAPP').mkdir(parents=True)
                (dist / 'iLEAPP' / 'ileapp').write_text('a previous folder build')
                (dist / 'iLEAPP.app').mkdir()
                keep = dist / 'ileappGUI-v2026.4.2-Windows_x86_64.zip'
                keep.write_text('made by hand')
                build.mkdir()
                self.driver.clean()
                self.assertEqual(list(dist.iterdir()), [keep])
                self.assertFalse(build.exists())

    def test_a_onefile_build_refuses_to_replace_a_folder_build(self):
        """On a case-insensitive file system dist/ileapp is dist/iLEAPP/, and PyInstaller
        would delete the folder build there without a word."""
        with tempfile.TemporaryDirectory() as tmp:
            dist = pathlib.Path(tmp)
            with mock.patch.object(self.driver, 'DIST', dist):
                (dist / self.driver.exe_name('ileapp')).mkdir()
                with self.assertRaises(SystemExit) as caught:
                    self.driver.refuse_collision(onefile=True)
                self.assertIn('--clean', str(caught.exception))

    def test_a_folder_build_refuses_to_replace_a_onefile_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = pathlib.Path(tmp)
            with mock.patch.object(self.driver, 'DIST', dist):
                (dist / 'iLEAPP').write_text('a one-file build')
                with self.assertRaises(SystemExit):
                    self.driver.refuse_collision(onefile=False)


class TestBundleContents(unittest.TestCase):
    """What the spec hands PyInstaller, decided by the driver."""

    def setUp(self):
        self.driver = _load_driver()
        self.tmp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.addCleanup(self.tmp.cleanup)
        # An empty bin/, so nothing depends on whether the parser was fetched here.
        self.bin = pathlib.Path(self.tmp.name) / 'bin'
        self.bin.mkdir()
        patcher = mock.patch.object(self.driver, 'BIN', self.bin)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _parser(self, licence=True, notices=True):
        binary = self.bin / self.driver.exe_name('unifiedlog_iterator')
        binary.write_bytes(b'not a real binary')
        binary.chmod(0o755)
        if licence:
            (self.bin / 'LICENSE-unifiedlog_iterator').write_text('Apache-2.0')
        if notices:
            (self.bin / 'THIRD-PARTY-NOTICES-unifiedlog_iterator.txt').write_text('notices')
        return binary

    def _bin_datas(self):
        return [src for src, dest in self.driver.bundle_datas() if dest == 'bin']

    def test_no_parser_means_no_parser_and_no_licence(self):
        self.assertEqual(self.driver.bundle_binaries(), [])
        self.assertEqual(self._bin_datas(), [])

    def test_the_parser_ships_as_a_binary_with_its_licence_and_notices(self):
        binary = self._parser()
        # A binary, not data: only binaries keep their execute permission.
        self.assertEqual(self.driver.bundle_binaries(), [(str(binary), 'bin')])
        self.assertEqual(sorted(pathlib.Path(p).name for p in self._bin_datas()),
                         ['LICENSE-unifiedlog_iterator',
                          'THIRD-PARTY-NOTICES-unifiedlog_iterator.txt'])

    def test_the_parser_without_its_licence_is_refused(self):
        self._parser(licence=False)
        with self.assertRaises(SystemExit):
            self.driver.bundle_datas()

    def test_the_parser_without_its_notices_is_refused(self):
        self._parser(notices=False)
        with self.assertRaises(SystemExit):
            self.driver.bundle_datas()

    def test_the_committed_notices_file_is_where_the_driver_looks(self):
        # The notices file is committed, not fetched, so a checkout always has it.
        real = _load_driver()
        self.assertEqual(real.BIN, REPO_ROOT / 'bin')
        self.assertTrue((real.BIN / 'THIRD-PARTY-NOTICES-unifiedlog_iterator.txt').is_file())

    def test_scripts_leapp_functions_and_assets_ship_as_files(self):
        datas = self.driver.bundle_datas()
        destinations = {dest for _, dest in datas}
        for dest in ('scripts/artifacts', 'scripts/_elements', 'leapp_functions', 'assets'):
            self.assertIn(dest, destinations)
        shipped = {(pathlib.Path(src).name, dest) for src, dest in datas}
        # The plugin loader reads every artifact from its source file.
        for artifact in (REPO_ROOT / 'scripts' / 'artifacts').glob('*.py'):
            self.assertIn((artifact.name, 'scripts/artifacts'), shipped)
        # The window's icon and logos.
        for image in ('icon.png', 'iLEAPP_logo.png', 'settings.png', 'leapps_i_logo.png'):
            self.assertIn((image, 'assets'), shipped)

    def test_no_bytecode_cache_or_finder_file_ships(self):
        for src, dest in self.driver.bundle_datas():
            with self.subTest(src=src):
                self.assertNotIn('__pycache__', pathlib.Path(src).parts)
                self.assertNotIn('__pycache__', dest)
                self.assertFalse(src.endswith(('.pyc', '.pyo', '.DS_Store')))

    def test_every_artifact_module_is_a_hidden_import(self):
        stems = {p.stem for p in (REPO_ROOT / 'scripts' / 'artifacts').glob('*.py')}
        expected = {f'scripts.artifacts.{stem}' for stem in stems if stem.isidentifier()}
        self.assertEqual(set(self.driver.artifact_modules()), expected)
        hidden = self.driver.hidden_imports()
        self.assertTrue(expected <= set(hidden))
        self.assertIn('pillow_heif', hidden)


class TestRuntimeAndBuildAgreeOnLocation(unittest.TestCase):
    """The build puts the parser in bin/; scripts/unifiedlogs.py has to look there."""

    def test_the_bundle_destination_is_searched_in_a_frozen_build(self):
        from scripts import unifiedlogs  # pylint: disable=import-outside-toplevel
        driver = _load_driver()
        with tempfile.TemporaryDirectory() as tmp:
            binary = pathlib.Path(tmp) / driver.exe_name('unifiedlog_iterator')
            binary.write_bytes(b'x')
            with mock.patch.object(driver, 'BIN', pathlib.Path(tmp)):
                ((_, dest),) = driver.bundle_binaries()
        frozen = pathlib.Path(tempfile.gettempdir()) / 'frozen'
        with mock.patch.object(sys, '_MEIPASS', str(frozen), create=True):
            searched = [pathlib.Path(d) for d in unifiedlogs._bundled_binary_dirs()]  # pylint: disable=protected-access
        self.assertEqual(searched[0], frozen / dest)

    def test_the_repository_bin_is_searched_from_source(self):
        from scripts import unifiedlogs  # pylint: disable=import-outside-toplevel
        searched = [pathlib.Path(d) for d in unifiedlogs._bundled_binary_dirs()]  # pylint: disable=protected-access
        self.assertIn(REPO_ROOT / 'bin', searched)


# -- the entry point ---------------------------------------------------------------------

class TestEntryPoint(unittest.TestCase):
    """No arguments opens the window; arguments are the command line, as they always were."""

    def setUp(self):
        self.entry = _load(PACKAGING / 'entrypoint.py', 'ileapp_entrypoint_under_test')

    def test_no_arguments_opens_the_window_where_one_can_open(self):
        for platform in ('win32', 'darwin'):
            with self.subTest(platform=platform):
                self.assertTrue(self.entry.wants_window([], platform, environ={}))
        self.assertTrue(self.entry.wants_window([], 'linux', environ={'DISPLAY': ':0'}))
        self.assertTrue(self.entry.wants_window([], 'linux', environ={'WAYLAND_DISPLAY': 'w-0'}))

    def test_no_arguments_and_no_display_is_the_command_line(self):
        """Over SSH there is no window to open, and the command line prints its help."""
        self.assertFalse(self.entry.wants_window([], 'linux', environ={}))

    def test_any_argument_is_the_command_line(self):
        for args in (['-t', 'fs', '-i', 'in', '-o', 'out'], ['--help'], ['--version'], ['-p']):
            with self.subTest(args=args):
                self.assertFalse(self.entry.wants_window(args, 'win32', environ={}))

    def test_selfcheck_goes_to_the_window_code(self):
        self.assertTrue(self.entry.wants_window(['--selfcheck'], 'linux', environ={'DISPLAY': ':0'}))

    def test_the_finder_serial_number_is_not_an_argument(self):
        self.assertEqual(self.entry.user_arguments(['-psn_0_12345']), [])
        self.assertEqual(self.entry.user_arguments(['-t', 'fs']), ['-t', 'fs'])

    def test_the_command_line_runs_from_the_entry_point(self):
        result = subprocess.run([sys.executable, str(PACKAGING / 'entrypoint.py'), '--version'],
                                capture_output=True, text=True, check=False)
        from scripts.version_info import leapp_version  # pylint: disable=import-outside-toplevel
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), f'iLEAPP {leapp_version}')


@unittest.skipUnless(sys.platform in ('win32', 'darwin') or 'DISPLAY' in os.environ,
                     'the window needs a display')
class TestSelfCheck(unittest.TestCase):
    """The window's --selfcheck, which the smoke test runs in every build, from source."""

    def test_it_loads_every_artifact_and_exits_before_drawing(self):
        from scripts.plugin_loader import PluginLoader  # pylint: disable=import-outside-toplevel
        # From source the window finds assets/ from the working directory.
        result = subprocess.run([sys.executable, 'ileappGUI.py', '--selfcheck'], cwd=REPO_ROOT,
                                capture_output=True, text=True, timeout=600, check=False)
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        found = re.search(r'selfcheck passed: (\d+) artifacts', result.stdout)
        self.assertIsNotNone(found, result.stdout[-2000:])
        self.assertEqual(int(found.group(1)), len(PluginLoader()))


# -- phase 2 -----------------------------------------------------------------------------

def _dmg_settings():
    names = {'defines': {'app': '/x/dist/iLEAPP.app', 'icon': 'i.icns', 'background': 'b.png'}}
    code = (PACKAGING / 'dmg_settings.py').read_text(encoding='utf-8')
    exec(compile(code, 'dmg_settings.py', 'exec'), names, names)  # pylint: disable=exec-used
    return names


class TestDiskImageLayout(unittest.TestCase):
    """The .dmg opens on the app and an Applications link, either side of the arrow."""

    def test_the_app_and_applications_sit_either_side_of_the_arrow(self):
        settings = _dmg_settings()
        self.assertEqual(settings['files'], ['/x/dist/iLEAPP.app'])
        self.assertEqual(settings['symlinks'], {'Applications': '/Applications'})
        self.assertEqual(set(settings['icon_locations']), {'iLEAPP.app', 'Applications'})
        self.assertEqual(settings['background'], 'b.png')

    def test_the_window_is_as_wide_as_its_background(self):
        from PIL import Image  # pylint: disable=import-outside-toplevel
        with Image.open(PACKAGING / 'dmg_background.png') as img:
            width, height = img.size
        (_, _), (win_w, win_h) = _dmg_settings()['window_rect']
        self.assertEqual(win_w, width)
        self.assertGreaterEqual(win_h, height)

    def test_the_icons_sit_either_side_of_the_arrow(self):
        """A new background that moves the arrow, as the one of 2026-10-01 did by 44 points,
        leaves the icons off centre unless the settings move with it. The arrow is the only
        dark mark in its band."""
        from PIL import Image  # pylint: disable=import-outside-toplevel
        with Image.open(PACKAGING / 'dmg_background.png') as img:
            rgb = img.convert('RGB')
            dark = [x for y in range(250, 320) for x in range(rgb.width)
                    if sum(rgb.getpixel((x, y))) < 600]
        arrow_centre = (min(dark) + max(dark)) / 2
        locations = _dmg_settings()['icon_locations']
        (app_x, app_y), (apps_x, apps_y) = locations['iLEAPP.app'], locations['Applications']
        self.assertEqual(app_y, apps_y)
        self.assertLess(app_x, min(dark))
        self.assertGreater(apps_x, max(dark))
        self.assertLessEqual(abs((app_x + apps_x) / 2 - arrow_centre), 2)

    def test_the_retina_background_is_exactly_twice_the_size(self):
        """dmgbuild joins dmg_background@2x.png to the background with tiffutil
        -cathidpicheck, which refuses a pair that is not exactly 1x and 2x, and the disk
        image then fails to build."""
        from PIL import Image  # pylint: disable=import-outside-toplevel
        with Image.open(PACKAGING / 'dmg_background.png') as img:
            width, height = img.size
        with Image.open(PACKAGING / 'dmg_background@2x.png') as img:
            self.assertEqual(img.size, (2 * width, 2 * height))


class TestAppImage(unittest.TestCase):

    def setUp(self):
        self.driver = _load_driver()

    def test_the_architecture_names_are_appimage_s(self):
        for machine, arch in (('x86_64', 'x86_64'), ('AMD64', 'x86_64'),
                              ('aarch64', 'aarch64'), ('arm64', 'aarch64')):
            with self.subTest(machine=machine):
                self.assertEqual(self.driver.appimage_arch(machine), arch)
        with self.assertRaises(SystemExit):
            self.driver.appimage_arch('riscv64')

    def test_the_tools_are_pinned_releases_with_digests(self):
        for url in (self.driver.APPIMAGETOOL_URL, self.driver.APPIMAGE_RUNTIME_URL):
            self.assertNotIn('continuous', url)
            self.assertTrue(url.startswith('https://github.com/AppImage/'))
        for arch, digests in self.driver.APPIMAGE_DIGESTS.items():
            for tool in ('appimagetool', 'runtime'):
                with self.subTest(arch=arch, tool=tool):
                    self.assertRegex(digests[tool], r'^[0-9a-f]{64}$')

    def test_a_download_with_the_wrong_digest_is_refused(self):
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'not the pinned tool'
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(self.driver.urllib.request, 'urlopen', return_value=response):
            dest = pathlib.Path(tmp) / 'tool'
            with self.assertRaises(SystemExit):
                self.driver.fetch_verified('https://example.invalid/tool', dest, '0' * 64)
            self.assertFalse(dest.exists())

    def test_a_cached_download_is_checked_and_reused(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(self.driver.urllib.request, 'urlopen') as urlopen:
            dest = pathlib.Path(tmp) / 'tool'
            dest.write_bytes(b'cached')
            self.driver.fetch_verified('https://example.invalid/tool', dest,
                                       hashlib.sha256(b'cached').hexdigest())
            urlopen.assert_not_called()

    def test_the_desktop_entry_opens_the_window(self):
        entry = self.driver.appimage_desktop_entry()
        lines = entry.splitlines()
        self.assertEqual(lines[0], '[Desktop Entry]')
        for line in ('Type=Application', 'Name=iLEAPP', 'Exec=ileapp', 'Icon=ileapp',
                     'Terminal=false', 'Categories=Utility;'):
            self.assertIn(line, lines)

    @unittest.skipIf(sys.platform == 'win32', 'an AppDir is made on Linux, with symlinks')
    def test_the_appdir_runs_the_folder_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp) / 'iLEAPP'
            (folder / '_internal').mkdir(parents=True)
            (folder / 'ileapp').write_text('the executable')
            (folder / '_internal' / 'lib').write_text('its libraries')
            appdir = self.driver.make_appdir(folder, pathlib.Path(tmp) / 'iLEAPP.AppDir')
            self.assertTrue((appdir / 'AppRun').is_symlink())
            self.assertEqual((appdir / 'AppRun').resolve(), (appdir / 'usr' / 'bin' / 'ileapp').resolve())
            self.assertTrue((appdir / 'usr' / 'bin' / '_internal' / 'lib').is_file())
            self.assertTrue((appdir / 'ileapp.desktop').is_file())
            self.assertTrue((appdir / 'ileapp.png').is_file())
            self.assertEqual((appdir / '.DirIcon').resolve(), (appdir / 'ileapp.png').resolve())


if __name__ == '__main__':
    unittest.main()
