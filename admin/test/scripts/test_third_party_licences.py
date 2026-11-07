"""The third-party licences in LICENSES/ ship with every packaged build and match heicreader.

HEIC images are read with heicreader (MIT), whose helper is built from MIT and BSD-3-Clause
code. packaging/licenses.py puts LICENSES/ in every build, refuses a build whose installed
heicreader is not the version requirements.txt pins or whose licence texts differ from the
committed copies, and refuses to package a GPL video codec. These tests check the committed
folder, requirements.txt, the build's data and binaries, the refusals, and the release
workflow. The file is the same in all five LEAPP cores.
"""
import importlib.util
import pathlib
import re
import tempfile
import types
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
LICENSES = REPO_ROOT / 'LICENSES'
PLATFORMS = {
    ('darwin', 'arm64'): 'macosx_12_0_arm64',
    ('darwin', 'x86_64'): 'macosx_12_0_x86_64',
    ('win32', 'AMD64'): 'win_amd64',
    ('win32', 'ARM64'): 'win_arm64',
    ('linux', 'x86_64'): 'manylinux_2_17_x86_64',
    ('linux', 'aarch64'): 'manylinux_2_17_aarch64',
}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


licences = load('leapp_licenses_under_test', REPO_ROOT / 'packaging' / 'licenses.py')


class CommittedFolderTests(unittest.TestCase):

    def setUp(self):
        self.notice = (LICENSES / licences.NOTICES).read_text(encoding='utf-8')

    def test_every_licence_text_the_notice_names_is_in_the_folder(self):
        named = set(re.findall(r'[\w.+-]+\.(?:txt|md)', self.notice))
        self.assertTrue(named, 'the notice names no licence files, so the test proves nothing')
        missing = sorted(name for name in named if not (LICENSES / name).is_file())
        self.assertEqual(missing, [])

    def test_the_committed_texts_are_not_gpl_or_lgpl(self):
        # The committed folder covers heicreader and the packages without licence files, all
        # permissive. The GPL and LGPL texts of bundled packages are written into
        # LICENSES/bundled/ at build time (CollectBundledTests), not committed here.
        paths = licences.license_files() + sorted(licences.FALLBACKS.iterdir())
        self.assertGreater(len(paths), len(licences.license_files()))
        for path in paths:
            text = path.read_text(encoding='utf-8', errors='replace').upper()
            self.assertNotIn('GNU GENERAL PUBLIC LICENSE', text, path.name)
            self.assertNotIn('GNU LESSER GENERAL PUBLIC LICENSE', text, path.name)

    def test_each_fallback_text_says_where_it_came_from(self):
        for path in sorted(licences.FALLBACKS.iterdir()):
            first = path.read_text(encoding='utf-8').splitlines()[0]
            self.assertTrue(first.startswith(path.stem + ' '), path.name)
            self.assertIn('ships no licence file', first, path.name)
            self.assertNotIn('—', path.read_text(encoding='utf-8'), path.name)

    def test_the_notice_names_the_pinned_version(self):
        self.assertIn(f'heicreader {licences.pinned_version()}', self.notice)

    def test_the_notice_has_no_em_dash(self):
        self.assertNotIn('—', self.notice)


class RequirementsTests(unittest.TestCase):

    def setUp(self):
        self.text = (REPO_ROOT / 'requirements.txt').read_text(encoding='utf-8')

    def test_pillow_heif_is_gone(self):
        self.assertIsNone(re.search(r'^\s*pillow[-_]heif', self.text, re.M | re.I))

    def test_one_heicreader_wheel_for_each_platform(self):
        lines = [line.strip() for line in self.text.splitlines() if line.strip().startswith('heicreader @')]
        self.assertEqual(len(lines), len(PLATFORMS), lines)
        version = licences.pinned_version()
        self.assertIsNotNone(version)
        for (system, machine), tag in PLATFORMS.items():
            matching = [line for line in lines
                        if f'sys_platform == "{system}"' in line and f'platform_machine == "{machine}"' in line]
            self.assertEqual(len(matching), 1, (system, machine))
            url = matching[0].split('@', 1)[1].split(';', 1)[0].strip()
            self.assertTrue(url.startswith(
                f'https://github.com/abrignoni/heicreader/releases/download/v{version}/'
                f'heicreader-{version}-py3-none-{tag}'), url)
            self.assertTrue(url.endswith('.whl'), url)


class BuildTests(unittest.TestCase):

    def test_the_build_ships_every_file_in_the_folder_under_licenses(self):
        build = load('leapp_build_under_test', REPO_ROOT / 'packaging' / 'build.py')
        shipped = {pathlib.Path(src).name for src, dest in build.bundle_datas() if dest == 'LICENSES'}
        on_disk = {p.name for p in LICENSES.iterdir() if p.is_file() and not p.name.startswith('.')}
        self.assertEqual(shipped, on_disk)

    def test_heicreader_is_a_hidden_import_and_pillow_heif_is_not(self):
        build = load('leapp_build_hidden_under_test', REPO_ROOT / 'packaging' / 'build.py')
        hidden = build.hidden_imports()
        self.assertIn('heicreader', hidden)
        self.assertNotIn('pillow_heif', hidden)

    def test_the_spec_bundles_the_helper(self):
        spec = next((REPO_ROOT / 'packaging').glob('*.spec')).read_text(encoding='utf-8')
        self.assertIn('licenses.heicreader_binaries()', spec)

    def test_the_helper_goes_where_heicreader_looks_for_it(self):
        with mock.patch.object(licences, 'helper_binary', return_value=pathlib.Path('/x/heicreader')):
            self.assertEqual(licences.heicreader_binaries(), [(str(pathlib.Path('/x/heicreader')), 'heicreader/bin')])
        with mock.patch.object(licences, 'helper_binary', return_value=None):
            self.assertEqual(licences.heicreader_binaries(), [])

    def test_gpl_codecs_are_found_by_name(self):
        names = ['_internal/pillow_heif/libx265-217-abc.dll', 'lib/libx264.so.164',
                 '_internal/libreadline.so.8',
                 'heicreader/bin/heicreader.exe', '_internal/PIL/_imaging.pyd',
                 '_internal/libedit.3.dylib']
        self.assertEqual(licences.gpl_codecs(names), sorted(names[:3]))
        with self.assertRaises(SystemExit):
            licences.refuse_gpl_codecs(names)
        licences.refuse_gpl_codecs(names[3:])

    def test_the_spec_leaves_out_readline(self):
        self.assertIn('readline', licences.EXCLUDES)
        spec = next((REPO_ROOT / 'packaging').glob('*.spec')).read_text(encoding='utf-8')
        self.assertIn('excludes=driver.licenses.EXCLUDES,', spec)


class InstalledVersionTests(unittest.TestCase):

    def _dist(self, version, licence_files):
        folder = pathlib.Path(tempfile.mkdtemp())
        files = []
        for name, data in licence_files.items():
            path = folder / 'heicreader-x.dist-info' / 'licenses' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            files.append(pathlib.PurePosixPath(path.relative_to(folder).as_posix()))
        return types.SimpleNamespace(version=version, files=files, locate_file=lambda f: folder / f)

    def _matching_licences(self):
        found = {}
        for path in licences.license_files():
            if path.name == licences.NOTICES:
                continue
            if path.name == 'heicreader-LICENSE.txt':
                found['LICENSE'] = path.read_bytes()
            elif path.name == 'heicreader-THIRD-PARTY-NOTICES.md':
                found['LICENSES/THIRD-PARTY-NOTICES.md'] = path.read_bytes()
            else:
                found[f'LICENSES/{path.name}'] = path.read_bytes()
        return found

    def _problems(self, dist, binary=pathlib.Path('/x/heicreader')):
        with mock.patch.object(licences.metadata, 'distribution', return_value=dist), \
                mock.patch.object(licences, 'helper_binary', return_value=binary):
            return licences.problems()

    def test_the_pinned_version_with_the_same_licences_passes(self):
        dist = self._dist(licences.pinned_version(), self._matching_licences())
        self.assertEqual(self._problems(dist), [])

    def test_another_version_is_refused(self):
        found = self._problems(self._dist('0.0.1', self._matching_licences()))
        self.assertEqual(len(found), 1)
        self.assertIn('0.0.1 is installed', found[0])

    def test_a_changed_licence_text_is_refused(self):
        files = self._matching_licences()
        files['LICENSES/go-LICENSE.txt'] = b'something else'
        found = self._problems(self._dist(licences.pinned_version(), files))
        self.assertEqual(len(found), 1)
        self.assertIn('go-LICENSE.txt differs', found[0])

    def test_no_helper_for_the_platform_is_refused(self):
        dist = self._dist(licences.pinned_version(), self._matching_licences())
        self.assertIn('no helper', self._problems(dist, binary=None)[0])

    def test_heicreader_not_installed_is_refused(self):
        with mock.patch.object(licences.metadata, 'distribution',
                               side_effect=licences.metadata.PackageNotFoundError('heicreader')):
            self.assertIn('not installed', licences.problems()[0])
            with self.assertRaises(SystemExit):
                licences.check()


class _Meta(dict):

    def get_all(self, key, default=None):
        value = self.get(key)
        return value if isinstance(value, list) else default


class _Dist:
    """An installed distribution with the RECORD, metadata and licence files given."""

    def __init__(self, site, name, version, files, licence_files=(), direct_url=None, **meta):
        self.site, self.version, self.direct_url = site, version, direct_url
        self.metadata = _Meta(Name=name, **meta)
        info = f'{name}-{version}.dist-info'
        self.files = [pathlib.PurePosixPath(f) for f in files]
        for rel in files:
            path = site / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('# code\n', encoding='utf-8')
        for rel, text in licence_files:
            path = site / info / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
            self.files.append(pathlib.PurePosixPath(f'{info}/{rel}'))

    def locate_file(self, entry):
        return self.site / str(entry)

    def read_text(self, name):
        return self.direct_url if name == 'direct_url.json' else None


class CollectBundledTests(unittest.TestCase):

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.site = self.tmp / 'site-packages'
        self.out = self.tmp / 'out'
        self.pyinstaller = _Dist(self.site, 'pyinstaller', '6.0', ['PyInstaller/loader/x.py'],
                                 [('licenses/COPYING.txt', 'Bootloader Exception')])

    def tearDown(self):
        import shutil  # pylint: disable=import-outside-toplevel
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _collect(self, dists, toc):
        with mock.patch.object(licences.metadata, 'distribution', return_value=self.pyinstaller):
            return licences.collect_bundled([toc], 'TOOL', '1.2.3', out=self.out,
                                            distributions=dists + [self.pyinstaller])

    def _entry(self, rel):
        return (rel, str(self.site / rel), 'DATA')

    def test_only_packages_with_a_file_in_the_bundle_are_listed(self):
        used = _Dist(self.site, 'usedpkg', '1.0', ['usedpkg/__init__.py'],
                     [('licenses/LICENSE', 'MIT text')], **{'License-Expression': 'MIT'})
        unused = _Dist(self.site, 'unusedpkg', '2.0', ['unusedpkg/__init__.py'],
                       [('licenses/LICENSE', 'MIT text')])

        entries = self._collect([used, unused], [self._entry('usedpkg/__init__.py')])

        index = (self.out / 'INDEX.md').read_text(encoding='utf-8')
        self.assertIn('| usedpkg | 1.0 | MIT | packages/usedpkg-1.0/LICENSE |', index)
        self.assertNotIn('unusedpkg', index)
        self.assertEqual((self.out / 'packages/usedpkg-1.0/LICENSE').read_text(), 'MIT text')
        dests = {dest for dest, _, _ in entries}
        self.assertIn('LICENSES/bundled/INDEX.md', dests)
        self.assertIn('LICENSES/bundled/packages/usedpkg-1.0/LICENSE', dests)
        self.assertIn('LICENSES/bundled/python/LICENSE.txt', dests)
        self.assertIn('LICENSES/bundled/pyinstaller/COPYING.txt', dests)
        self.assertIn('LICENSES/bundled/repository/LICENSE', dests)
        self.assertTrue(all(dest.startswith('LICENSES/bundled/') for dest in dests))
        self.assertTrue(all(pathlib.Path(src).is_file() for _, src, _ in entries))

    def test_an_lgpl_package_is_named_with_its_source(self):
        lgpl = _Dist(self.site, 'kmlpkg', '1.3.6', ['kmlpkg/__init__.py'],
                     [('licenses/LICENSE.txt', 'GNU LESSER GENERAL PUBLIC LICENSE')],
                     License='GNU Lesser General Public License v3+')

        self._collect([lgpl], [self._entry('kmlpkg/__init__.py')])

        index = (self.out / 'INDEX.md').read_text(encoding='utf-8')
        self.assertIn('## Packages with copyleft terms', index)
        self.assertIn('- kmlpkg 1.3.6 (GNU Lesser General Public License v3+): '
                      'https://pypi.org/project/kmlpkg/1.3.6/#files', index)

    def test_a_package_from_a_url_is_named_with_that_url(self):
        url = 'https://example.org/lgplpkg-2.0-py3-none-any.whl'
        lgpl = _Dist(self.site, 'lgplpkg', '2.0', ['lgplpkg/__init__.py'],
                     [('licenses/COPYING', 'GNU LESSER GENERAL PUBLIC LICENSE')],
                     direct_url='{"url": "%s", "archive_info": {}}' % url, License='MIT')

        self._collect([lgpl], [self._entry('lgplpkg/__init__.py')])

        self.assertIn(f'- lgplpkg 2.0 (MIT): {url}', (self.out / 'INDEX.md').read_text(encoding='utf-8'))

    def test_a_permissive_package_is_not_named_as_copyleft(self):
        # Prose that mentions the GPL, as heicreader's and Pillow's notices do, is not a GPL text.
        mit = _Dist(self.site, 'mitpkg', '1.0', ['mitpkg/__init__.py'],
                    [('licenses/LICENSE', 'Permission is hereby granted. None of this is the GPL; '
                                          'see the GNU Lesser General Public License for that.')],
                    License='MIT')

        self._collect([mit], [self._entry('mitpkg/__init__.py')])

        self.assertNotIn('copyleft terms', (self.out / 'INDEX.md').read_text(encoding='utf-8'))

    def test_a_package_without_a_licence_file_takes_the_committed_text(self):
        name = sorted(licences.FALLBACKS.iterdir())[0].stem
        bare = _Dist(self.site, name, '0.1', [f'{name}/__init__.py'], License='MIT')

        self._collect([bare], [self._entry(f'{name}/__init__.py')])

        copied = self.out / f'packages/{name}-0.1/LICENSE-from-LICENSES-packages.txt'
        self.assertEqual(copied.read_bytes(), (licences.FALLBACKS / f'{name}.txt').read_bytes())

    def test_a_package_without_any_licence_text_stops_the_build(self):
        bare = _Dist(self.site, 'nolicencepkg', '0.1', ['nolicencepkg/__init__.py'])
        with self.assertRaises(SystemExit) as raised:
            self._collect([bare], [self._entry('nolicencepkg/__init__.py')])
        self.assertIn('nolicencepkg 0.1', str(raised.exception))

    def test_a_file_from_no_package_is_listed(self):
        stray = self.tmp / 'elsewhere' / 'libstray.so'
        stray.parent.mkdir()
        stray.write_bytes(b'\x7fELF')

        self._collect([], [('libstray.so', str(stray), 'BINARY')])

        index = (self.out / 'INDEX.md').read_text(encoding='utf-8')
        self.assertIn('## Files from no Python package', index)
        self.assertIn('- libstray.so', index)

    def test_a_bundled_repository_file_with_a_gpl_header_is_named(self):
        gpl = next((p for p in sorted((REPO_ROOT / 'scripts').rglob('*.py'))
                    if 'GNU GENERAL PUBLIC LICENSE' in p.read_text(encoding='utf-8', errors='replace')[:8192]),
                   None)
        if gpl is None:
            self.skipTest('no repository file carries a GPL header')
        mine = REPO_ROOT / 'scripts' / 'ilapfuncs.py'

        self._collect([], [('a', str(gpl), 'PYMODULE'), ('b', str(mine), 'PYMODULE')])

        index = (self.out / 'INDEX.md').read_text(encoding='utf-8')
        self.assertIn(f'- {gpl.relative_to(REPO_ROOT).as_posix()}', index)
        self.assertNotIn('ilapfuncs.py', index)

    def test_the_spec_adds_the_collected_licences_to_the_bundle(self):
        spec = next((REPO_ROOT / 'packaging').glob('*.spec')).read_text(encoding='utf-8')
        self.assertIn('a.datas += driver.licenses.collect_bundled(', spec)
        self.assertLess(spec.index('collect_bundled('), spec.index('pyz = PYZ(a.pure)'))


class ReleaseWorkflowTests(unittest.TestCase):

    def setUp(self):
        self.release = (REPO_ROOT / '.github' / 'workflows' / 'release.yml').read_text(encoding='utf-8')

    def test_no_source_archives_are_fetched_any_more(self):
        self.assertNotIn('fetch-sources', self.release)

    def test_the_windows_zip_carries_the_licences_beside_the_executable(self):
        zips = re.findall(r'Compress-Archive -Path ([^ ]+)', self.release)
        self.assertTrue(zips, 'no Windows zip step found, so the test proves nothing')
        self.assertTrue(all("'LICENSES'" in path for path in zips), zips)

    def test_the_windows_zip_carries_the_collected_licences(self):
        copy = "Copy-Item -Recurse 'build/licences/bundled' 'LICENSES/bundled'; Compress-Archive"
        self.assertEqual(self.release.count(copy), 1)
        self.assertEqual(licences.GENERATED.relative_to(REPO_ROOT).as_posix(), 'build/licences/bundled')


if __name__ == '__main__':
    unittest.main()
