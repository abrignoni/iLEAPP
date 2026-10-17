"""The command line's checks on several input paths, before anything is read.

validate_args is taken from the entry point's source and run on its own: several
paths are accepted only with -t raw, and never with logical evidence among them.
"""
import argparse
import ast
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.raw_image as raw_image  # pylint: disable=wrong-import-position

ENTRY_POINT = next(path for path in REPO_ROOT.glob('*leapp.py') if not path.name.endswith('GUI.py'))
FIXTURES = REPO_ROOT / 'admin' / 'test' / 'data' / 'raw_images'


class _Args(argparse.Namespace):
    """Parsed options; one a core adds and this test does not set is left unset (None)."""

    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError(name)
        return None


def _validate_args():
    tree = ast.parse(ENTRY_POINT.read_text(encoding='utf-8'))
    wanted = [node for node in tree.body
              if isinstance(node, ast.FunctionDef) and node.name == 'validate_args']
    namespace = {'argparse': argparse, 'os': os,
                 'validate_output_folder_available': lambda _o, _n: (True, ''),
                 'logical_among': raw_image.logical_among,
                 'logical_refusal': raw_image.logical_refusal}
    try:
        import pytz  # pylint: disable=import-outside-toplevel
        namespace['pytz'] = pytz
    except ImportError:
        pass
    exec(compile(ast.Module(body=wanted, type_ignores=[]), str(ENTRY_POINT), 'exec'),  # pylint: disable=exec-used
         namespace)
    return namespace['validate_args']


class SeveralInputPathsTest(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix='cli_multi_')
        self.addCleanup(shutil.rmtree, self.folder, True)
        self.images = []
        for name in ('disk0.img', 'disk1.img'):
            path = os.path.join(self.folder, name)
            with open(path, 'wb') as handle:
                handle.write(b'\0' * 4096)
            self.images.append(path)
        self.validate = _validate_args()

    def _args(self, paths, kind):
        return _Args(
            artifact_paths=False, create_profile_casedata=None, input_path=paths[0],
            input_paths=list(paths), output_path=self.folder, t=kind,
            custom_output_folder=None, load_case_data=None, load_profile=None,
            timezone='UTC')

    def test_several_images_are_accepted_with_raw(self):
        self.validate(self._args(self.images, 'raw'))

    def test_several_paths_are_refused_for_any_other_type(self):
        for kind in ('zip', 'tar', 'fs', 'file'):
            with self.subTest(kind), self.assertRaisesRegex(argparse.ArgumentError,
                                                            'only with -t raw'):
                self.validate(self._args(self.images, kind))

    def test_a_missing_second_path_is_refused(self):
        with self.assertRaisesRegex(argparse.ArgumentError, 'does not exist'):
            self.validate(self._args([self.images[0], self.images[0] + '.gone'], 'raw'))

    def test_logical_evidence_among_several_images_is_refused(self):
        ad1 = str(FIXTURES / 'lean-multi-ntfs-c9.ad1')
        with self.assertRaisesRegex(argparse.ArgumentError, 'is logical evidence'):
            self.validate(self._args([self.images[0], ad1], 'raw'))

    def test_one_path_is_checked_as_before(self):
        self.validate(self._args(self.images[:1], 'raw'))


if __name__ == '__main__':
    unittest.main()
