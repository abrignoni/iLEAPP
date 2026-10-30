"""Pin which -t input type validate_sample_data.py --emit picks: raw for an extension that names only a disk image
or evidence container, never for .bin, .img, .dd or .raw unless --input-type says so."""
import importlib.util
import pathlib
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / 'admin' / 'scripts' / 'validate_sample_data.py'


def _load():
    spec = importlib.util.spec_from_file_location('validate_sample_data', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EmitInputTypeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vsd = _load()

    def pick(self, name, declared=None):
        return self.vsd.emit_input_type(pathlib.Path('/nowhere') / name, declared)

    def test_container_extensions_are_raw_in_any_case(self):
        for name in ('case.E01', 'case.e01', 'disk.vhdx', 'disk.VMDK', 'split.001', 'logical.AD1', 'mac.dmg'):
            with self.subTest(name=name):
                self.assertEqual(self.pick(name), 'raw')

    def test_ambiguous_extensions_are_not_guessed(self):
        for name in ('nand.bin', 'disk.img', 'disk.dd', 'disk.raw'):
            with self.subTest(name=name):
                self.assertIsNone(self.pick(name))

    def test_input_type_wins(self):
        self.assertEqual(self.pick('nand.bin', 'raw'), 'raw')
        self.assertEqual(self.pick('case.E01', 'zip'), 'zip')

    def test_archives_and_folders_are_unchanged(self):
        self.assertEqual(self.pick('a.zip'), 'zip')
        self.assertEqual(self.pick('a.tar.gz'), 'gz')
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(self.vsd.emit_input_type(pathlib.Path(folder)), 'fs')

    def test_run_mode_still_never_guesses_raw(self):
        self.assertIsNone(self.vsd.input_type_for(pathlib.Path('/nowhere/case.E01')))


if __name__ == '__main__':
    unittest.main()
