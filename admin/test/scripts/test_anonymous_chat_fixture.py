"""Prove sample archives match a fresh metadata-only build, without case inputs."""

import importlib.util
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
BUILDER_PATH = HERE / 'build_anonymous_chat_fixture.py'
SPEC = importlib.util.spec_from_file_location('anonymous_chat_fixture_builder', BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


def sqlite_snapshot(payload, root, name):
    """Compare SQLite schema/data while ignoring version-specific header bytes."""
    path = root / name.replace('/', '_').replace('\\', '_')
    path.write_bytes(payload)
    with sqlite3.connect(path) as db:
        tables = [row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
        snapshot = []
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            columns = tuple(row[1:] for row in db.execute(f'PRAGMA table_info({quoted})'))
            rows = tuple(db.execute(f'SELECT * FROM {quoted}'))
            snapshot.append((table, columns, rows))
    return tuple(snapshot)


class AnonymousChatFixtureTests(unittest.TestCase):
    def test_published_samples_are_exact_subsets_of_a_fresh_synthetic_build(self):
        with tempfile.TemporaryDirectory(prefix='anonymouschat-synthetic-provenance-') as root:
            generated = BUILDER.build_fixture(Path(root) / 'extraction')
            with zipfile.ZipFile(generated) as archive:
                fresh = {name: archive.read(name) for name in archive.namelist()}
            self.assertEqual(len(fresh), 8)
            self.assertTrue(all(Path(name).suffix in ('.db', '.sqlite', '.json', '.plist')
                                for name in fresh))
            case_dir = HERE.parent / 'cases/data/anonymousChat'
            if not case_dir.is_dir():
                self.skipTest('The runtime-contract sparse checkout omits case archives')
            samples = sorted(case_dir.glob('*.zip'))
            self.assertEqual(len(samples), 6)
            with tempfile.TemporaryDirectory(prefix='anonymouschat-synthetic-sqlite-') as sql_root:
                sql_root = Path(sql_root)
                for sample in samples:
                    with self.subTest(sample=sample.name), zipfile.ZipFile(sample) as archive:
                        names = archive.namelist()
                        self.assertEqual(len(names), len(set(names)))
                        self.assertTrue(names)
                        for name in names:
                            self.assertIn(name, fresh)
                            if Path(name).suffix.lower() in ('.db', '.sqlite'):
                                self.assertEqual(
                                    sqlite_snapshot(archive.read(name), sql_root, name),
                                    sqlite_snapshot(fresh[name], sql_root, 'fresh_' + name),
                                    name)
                            else:
                                self.assertEqual(archive.read(name), fresh[name], name)

    def test_manifest_json_is_written_with_lf_bytes(self):
        with tempfile.TemporaryDirectory(prefix='anonymouschat-synthetic-manifest-') as root:
            generated = BUILDER.build_fixture(Path(root) / 'extraction')
            with zipfile.ZipFile(generated) as archive:
                manifest = next(archive.read(name) for name in archive.namelist()
                                if name.endswith('/manifest.json'))
            self.assertNotIn(b'\r\n', manifest)
            self.assertIn(b'\n', manifest)

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
