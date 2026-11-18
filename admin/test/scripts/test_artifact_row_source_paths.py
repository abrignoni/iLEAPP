"""Artifacts that name their rows' files through get_device_file_path return those files as source paths.

They used to return a sentence pointing at the Source File Name column, which the
report printed as the location of the evidence and LAVA recorded as a path.
"""
import importlib
import pathlib
import sys
import unittest
from types import SimpleNamespace

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

MODULES = [name for name in ('lidl_plus', 'waze')
           if (REPO_ROOT / 'scripts' / 'artifacts' / f'{name}.py').exists()]


def context(data_folder, artifact):
    seeker = SimpleNamespace(data_folder=data_folder)
    return SimpleNamespace(get_seeker=lambda: seeker, get_artifact_name=lambda: artifact,
                           get_relative_path=lambda p: p.removeprefix(data_folder + '/'))


class RowSourcePaths(unittest.TestCase):

    def test_the_converted_files_are_returned_once_each_in_order(self):
        for name in MODULES:
            with self.subTest(module=name):
                module = importlib.import_module(f'scripts.artifacts.{name}')
                ctx = context('/case/data', 'one')
                module.get_device_file_path('/case/data/private/var/b.db', ctx)
                module.get_device_file_path('/case/data/private/var/a.db', ctx)
                module.get_device_file_path('/case/data/private/var/b.db', ctx)
                self.assertEqual(module._row_source_paths(ctx),  # pylint: disable=protected-access
                                 '/case/data/private/var/b.db\n/case/data/private/var/a.db')
                self.assertEqual(module._row_source_paths(ctx), '')  # pylint: disable=protected-access

    def test_artifacts_and_runs_keep_their_own_files(self):
        for name in MODULES:
            with self.subTest(module=name):
                module = importlib.import_module(f'scripts.artifacts.{name}')
                first, other, later = (context('/case/data', 'one'), context('/case/data', 'two'),
                                       context('/case2/data', 'one'))
                module.get_device_file_path('/case/data/x.db', first)
                module.get_device_file_path('/case/data/y.db', other)
                module.get_device_file_path('/case2/data/z.db', later)
                self.assertEqual(module._row_source_paths(first), '/case/data/x.db')  # pylint: disable=protected-access
                self.assertEqual(module._row_source_paths(other), '/case/data/y.db')  # pylint: disable=protected-access
                self.assertEqual(module._row_source_paths(later), '/case2/data/z.db')  # pylint: disable=protected-access

    def test_the_column_shows_the_path_inside_the_extraction(self):
        """No device path is rebuilt: no /private/ or /sdcard/ prefix, no leading slash."""
        for name in MODULES:
            with self.subTest(module=name):
                module = importlib.import_module(f'scripts.artifacts.{name}')
                ctx = context('/case/data', 'column')
                for staged, shown in (('/case/data/var/mobile/a.db', 'var/mobile/a.db'),
                                      ('/case/data/Dump/data/data/com.waze/user', 'Dump/data/data/com.waze/user'),
                                      ('/case/data/storage/emulated/0/x.jpg', 'storage/emulated/0/x.jpg')):
                    self.assertEqual(module.get_device_file_path(staged, ctx), shown)
                module._row_source_paths(ctx)  # pylint: disable=protected-access

    def test_no_file_no_source(self):
        for name in MODULES:
            with self.subTest(module=name):
                module = importlib.import_module(f'scripts.artifacts.{name}')
                ctx = context('/case/data', 'empty')
                self.assertEqual(module.get_device_file_path('', ctx), '')
                self.assertEqual(module._row_source_paths(ctx), '')  # pylint: disable=protected-access


if __name__ == '__main__':
    unittest.main()
