"""The third-party licences in LICENSES/ ship with every packaged build and match what it bundles.

pillow-heif's binary wheels bundle libheif and libde265 (LGPL-3.0) and x265
(GPL-2.0-or-later). packaging/licenses.py puts LICENSES/ in every build, refuses a build
whose installed pillow-heif is not the version LICENSES/ describes, and fetches the source
archives a release attaches. These tests check the committed folder, the build's data
list, the refusals, and the release workflow's two steps. The file is the same in all five
LEAPP cores.
"""
import hashlib
import importlib.util
import json
import pathlib
import re
import tempfile
import types
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
LICENSES = REPO_ROOT / 'LICENSES'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


licences = load('leapp_licenses_under_test', REPO_ROOT / 'packaging' / 'licenses.py')


class CommittedFolderTests(unittest.TestCase):

    def setUp(self):
        self.sources = json.loads((LICENSES / 'sources.json').read_text(encoding='utf-8'))
        self.notice = (LICENSES / 'THIRD-PARTY-NOTICES.md').read_text(encoding='utf-8')

    def test_every_licence_text_the_notice_names_is_in_the_folder(self):
        named = set(re.findall(r'[\w.+-]+\.txt', self.notice))
        self.assertTrue(named, 'the notice names no licence files, so the test proves nothing')
        missing = sorted(name for name in named if not (LICENSES / name).is_file())
        self.assertEqual(missing, [])

    def test_requirements_pin_the_version_the_folder_describes(self):
        text = (REPO_ROOT / 'requirements.txt').read_text(encoding='utf-8')
        pins = re.findall(r'^pillow[-_]heif==([\w.]+)\s*$', text, re.M | re.I)
        self.assertEqual(pins, [self.sources['pillow-heif']])
        unpinned = re.findall(r'^pillow[-_]heif\s*$', text, re.M | re.I)
        self.assertEqual(unpinned, [])

    def test_the_notice_names_every_source_archive_and_version(self):
        for entry in self.sources['sources']:
            self.assertIn(entry['asset'], self.notice)
            self.assertIn(entry['version'], self.notice)
            self.assertRegex(entry['sha256'], r'^[0-9a-f]{64}$')
            self.assertTrue(entry['url'].startswith('https://'))

    def test_the_bundled_list_names_the_versions_sources_json_fetches(self):
        bundled = (LICENSES / licences.BUNDLED_LIST).read_text(encoding='utf-8')
        for entry in self.sources['sources']:
            if entry['name'] == 'pillow-heif':
                continue
            self.assertIn(f"/tree/{'' if entry['name'] == 'x265' else 'v'}{entry['version']}", bundled)

    def test_the_notice_has_no_em_dash(self):
        self.assertNotIn('—', self.notice)


class BuildDataTests(unittest.TestCase):

    def test_the_build_ships_every_file_in_the_folder_under_licenses(self):
        build = load('leapp_build_under_test', REPO_ROOT / 'packaging' / 'build.py')
        shipped = {pathlib.Path(src).name for src, dest in build.bundle_datas() if dest == 'LICENSES'}
        on_disk = {p.name for p in LICENSES.iterdir() if p.is_file() and not p.name.startswith('.')}
        self.assertEqual(shipped, on_disk)
        self.assertIn('THIRD-PARTY-NOTICES.md', shipped)

    def test_the_smoke_names_are_relative_to_the_bundle(self):
        names = licences.bundled_names()
        self.assertIn('LICENSES/THIRD-PARTY-NOTICES.md', names)
        self.assertTrue(all(name.startswith('LICENSES/') for name in names))


class InstalledVersionTests(unittest.TestCase):

    def _distribution(self, version, bundled_text):
        folder = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(lambda: [p.unlink() for p in folder.iterdir()] and folder.rmdir())
        (folder / 'LICENSES_bundled.txt').write_text(bundled_text, encoding='utf-8')
        listed = types.SimpleNamespace(name='LICENSES_bundled.txt')
        return types.SimpleNamespace(version=version, files=[listed],
                                     locate_file=lambda _f: folder / 'LICENSES_bundled.txt')

    def test_the_pinned_version_with_the_same_list_passes(self):
        pinned = licences.sources()['pillow-heif']
        same = (LICENSES / licences.BUNDLED_LIST).read_text(encoding='utf-8')
        with mock.patch.object(licences.metadata, 'distribution',
                               return_value=self._distribution(pinned, same)):
            self.assertEqual(licences.problems(), [])

    def test_another_version_is_refused(self):
        same = (LICENSES / licences.BUNDLED_LIST).read_text(encoding='utf-8')
        with mock.patch.object(licences.metadata, 'distribution',
                               return_value=self._distribution('0.0.1', same)):
            found = licences.problems()
        self.assertEqual(len(found), 1)
        self.assertIn('0.0.1 is installed', found[0])
        with mock.patch.object(licences.metadata, 'distribution',
                               return_value=self._distribution('0.0.1', same)):
            with self.assertRaises(SystemExit):
                licences.check()

    def test_the_pinned_version_with_another_list_is_refused(self):
        pinned = licences.sources()['pillow-heif']
        with mock.patch.object(licences.metadata, 'distribution',
                               return_value=self._distribution(pinned, 'Name: something else\n')):
            found = licences.problems()
        self.assertEqual(len(found), 1)
        self.assertIn('other bundled libraries', found[0])

    def test_pillow_heif_not_installed_is_refused(self):
        with mock.patch.object(licences.metadata, 'distribution',
                               side_effect=licences.metadata.PackageNotFoundError('pillow-heif')):
            self.assertIn('not installed', licences.problems()[0])


class FetchSourcesTests(unittest.TestCase):

    def _sources(self, payload, sha256):
        folder = pathlib.Path(tempfile.mkdtemp())
        archive = folder / 'archive.tar.gz'
        archive.write_bytes(payload)
        listing = {'pillow-heif': '1.0', 'sources': [
            {'name': 'x', 'version': '1', 'license': 'MIT', 'asset': 'source-x-1.tar.gz',
             'url': archive.as_uri(), 'sha256': sha256}]}
        return folder, listing

    def test_a_matching_archive_is_kept_under_its_asset_name(self):
        payload = b'archive bytes'
        folder, listing = self._sources(payload, hashlib.sha256(payload).hexdigest())
        out = folder / 'out'
        with mock.patch.object(licences, 'sources', return_value=listing):
            fetched = licences.fetch_sources(out)
        self.assertEqual([p.name for p in fetched], ['source-x-1.tar.gz'])
        self.assertEqual((out / 'source-x-1.tar.gz').read_bytes(), payload)

    def test_an_archive_with_another_hash_is_refused_and_removed(self):
        folder, listing = self._sources(b'changed upstream', '0' * 64)
        out = folder / 'out'
        with mock.patch.object(licences, 'sources', return_value=listing):
            with self.assertRaises(SystemExit):
                licences.fetch_sources(out)
        self.assertFalse((out / 'source-x-1.tar.gz').exists())


class ReleaseWorkflowTests(unittest.TestCase):

    def setUp(self):
        self.release = (REPO_ROOT / '.github' / 'workflows' / 'release.yml').read_text(encoding='utf-8')

    def test_the_release_attaches_the_source_archives_before_the_checksums(self):
        fetch = self.release.find('packaging/licenses.py fetch-sources release-assets')
        sums = self.release.find('sha256sum * > SHA256SUMS.txt')
        self.assertNotEqual(fetch, -1)
        self.assertNotEqual(sums, -1)
        self.assertLess(fetch, sums)

    def test_the_windows_zip_carries_the_licences_beside_the_executable(self):
        zips = re.findall(r'Compress-Archive -Path ([^ ]+)', self.release)
        self.assertTrue(zips, 'no Windows zip step found, so the test proves nothing')
        self.assertTrue(all("'LICENSES'" in path for path in zips), zips)


if __name__ == '__main__':
    unittest.main()
