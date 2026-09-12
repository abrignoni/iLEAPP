"""Prove sample archives match a fresh metadata-only build, without case inputs."""

import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
BUILDER_PATH = HERE / 'build_anonymous_chat_fixture.py'
if not BUILDER_PATH.exists():
    BUILDER_PATH = HERE.parent / 'build_synthetic_fixture.py'
SPEC = importlib.util.spec_from_file_location('anonymous_chat_fixture_builder', BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class AnonymousChatFixtureTests(unittest.TestCase):
    def test_published_samples_are_exact_subsets_of_a_fresh_synthetic_build(self):
        with tempfile.TemporaryDirectory(prefix='anonymouschat-synthetic-provenance-') as root:
            generated = BUILDER.build_fixture(Path(root) / 'extraction')
            with zipfile.ZipFile(generated) as archive:
                fresh = {name: archive.read(name) for name in archive.namelist()}
            self.assertEqual(len(fresh), 8)
            self.assertTrue(all(Path(name).suffix in ('.db', '.sqlite', '.json', '.plist')
                                for name in fresh))
            if HERE.name == 'scripts':
                case_dir = HERE.parent / 'cases/data/anonymousChat'
                if not case_dir.is_dir():
                    self.skipTest('The runtime-contract sparse checkout omits case archives')
                samples = sorted(case_dir.glob('*.zip'))
                self.assertEqual(len(samples), 6)
            else:
                samples = [HERE.parent / 'testdata/anonymousChat_synthetic_extraction.zip']
            for sample in samples:
                with self.subTest(sample=sample.name), zipfile.ZipFile(sample) as archive:
                    names = archive.namelist()
                    self.assertEqual(len(names), len(set(names)))
                    self.assertTrue(names)
                    for name in names:
                        self.assertIn(name, fresh)
                        self.assertEqual(archive.read(name), fresh[name], name)

    def test_builder_refuses_to_delete_existing_directory_contents(self):
        with tempfile.TemporaryDirectory(prefix='anonymouschat-synthetic-builder-') as root:
            folder = Path(root) / 'existing'
            folder.mkdir()
            marker = folder / 'invented-sentinel.txt'
            marker.write_text('Keep this synthetic sentinel', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                BUILDER.build_fixture(folder)
            self.assertEqual(marker.read_text(encoding='utf-8'), 'Keep this synthetic sentinel')

    def test_builder_refuses_to_replace_existing_archive(self):
        with tempfile.TemporaryDirectory(prefix='anonymouschat-synthetic-builder-') as root:
            archive = BUILDER.build_fixture(Path(root) / 'first')
            original_size = archive.stat().st_size
            with self.assertRaises(FileExistsError):
                BUILDER.build_fixture(Path(root) / 'second')
            self.assertEqual(archive.stat().st_size, original_size)


if __name__ == '__main__':
    unittest.main()
