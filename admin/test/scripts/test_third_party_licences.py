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

    def test_no_gpl_or_lgpl_text_ships(self):
        for path in LICENSES.iterdir():
            text = path.read_text(encoding='utf-8', errors='replace')
            self.assertNotIn('GNU GENERAL PUBLIC LICENSE', text.upper(), path.name)
            self.assertNotIn('GNU LESSER GENERAL PUBLIC LICENSE', text.upper(), path.name)

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
                 'heicreader/bin/heicreader.exe', '_internal/PIL/_imaging.pyd']
        self.assertEqual(licences.gpl_codecs(names), sorted(names[:2]))
        with self.assertRaises(SystemExit):
            licences.refuse_gpl_codecs(names)
        licences.refuse_gpl_codecs(names[2:])


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
        for path in LICENSES.iterdir():
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


class ReleaseWorkflowTests(unittest.TestCase):

    def setUp(self):
        self.release = (REPO_ROOT / '.github' / 'workflows' / 'release.yml').read_text(encoding='utf-8')

    def test_no_source_archives_are_fetched_any_more(self):
        self.assertNotIn('fetch-sources', self.release)

    def test_the_windows_zip_carries_the_licences_beside_the_executable(self):
        zips = re.findall(r'Compress-Archive -Path ([^ ]+)', self.release)
        self.assertTrue(zips, 'no Windows zip step found, so the test proves nothing')
        self.assertTrue(all("'LICENSES'" in path for path in zips), zips)


if __name__ == '__main__':
    unittest.main()
