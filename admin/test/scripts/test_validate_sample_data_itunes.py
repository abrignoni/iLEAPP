"""A corpus entry with input_type itunes is unpacked to a temporary folder and run with -t itunes on the
folder that holds the manifest; a member that would land outside that folder is refused, and the unpacked
copy is deleted after the run. All archives here are made up."""
# pylint: disable=protected-access
import importlib.util
import pathlib
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / 'admin' / 'scripts' / 'validate_sample_data.py'


def _load():
    spec = importlib.util.spec_from_file_location('validate_sample_data', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class _Report:
    def __init__(self):
        self.errors = []

    def error(self, message):
        self.errors.append(message)


def _zip(path, members):
    with zipfile.ZipFile(path, 'w') as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return path


class ItunesInputTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vsd = _load()

    def test_itunes_is_a_runnable_declared_type(self):
        self.assertEqual(self.vsd.input_type_for(pathlib.Path('/nowhere/b.zip'), 'itunes'), 'itunes')

    def test_the_backup_folder_inside_the_zip_is_returned(self):
        with tempfile.TemporaryDirectory() as folder:
            source = _zip(pathlib.Path(folder) / 'b.zip', {
                'udid/Manifest.db': b'x', 'udid/Manifest.plist': b'x', 'udid/ab/abcdef': b'x'})
            staged = pathlib.Path(folder) / 'staged'
            staged.mkdir()
            found = self.vsd.stage_itunes_backup(source, staged)
            self.assertEqual(found, (staged / 'udid').resolve())

    def test_members_that_escape_are_refused(self):
        for bad in ('/etc/x', '../x', 'udid/../../x', 'C:/x'):
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as folder:
                source = _zip(pathlib.Path(folder) / 'b.zip', {'udid/Manifest.db': b'x', bad: b'x'})
                staged = pathlib.Path(folder) / 'staged'
                staged.mkdir()
                with self.assertRaises(ValueError):
                    self.vsd.stage_itunes_backup(source, staged)
                self.assertEqual(list(staged.iterdir()), [])

    def test_a_zip_without_a_manifest_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            source = _zip(pathlib.Path(folder) / 'b.zip', {'udid/other': b'x'})
            staged = pathlib.Path(folder) / 'staged'
            staged.mkdir()
            with self.assertRaises(ValueError):
                self.vsd.stage_itunes_backup(source, staged)

    def test_the_run_gets_the_backup_folder_and_the_copy_is_deleted(self):
        seen = {}

        def fake(source, *_args, **kwargs):
            seen['source'] = source
            seen['type'] = kwargs.get('declared_type')
            seen['exists_during'] = source.is_dir()
            return {}, None, None

        with tempfile.TemporaryDirectory() as folder:
            source = _zip(pathlib.Path(folder) / 'b.zip', {'udid/Manifest.db': b'x'})
            with patch.object(self.vsd, '_execute_tool', side_effect=fake):
                self.vsd.execute_tool(source, 'label', 'log', _Report(), declared_type='itunes')
        self.assertEqual(seen['type'], 'itunes')
        self.assertTrue(seen['exists_during'])
        self.assertEqual(seen['source'].name, 'udid')
        self.assertFalse(seen['source'].exists())

    def test_a_bad_zip_is_reported_not_run(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / 'b.zip'
            source.write_bytes(b'not a zip')
            report = _Report()
            with patch.object(self.vsd, '_execute_tool') as inner:
                result = self.vsd.execute_tool(source, 'label', 'log', report, declared_type='itunes')
            inner.assert_not_called()
        self.assertEqual(result, (None, None, None))
        self.assertEqual(len(report.errors), 1)

    def test_a_zip_that_fails_while_extracting_is_reported_not_run(self):
        def corrupt_data(raw, info):
            start = info.header_offset + 30 + len(info.filename)
            raw[start] = 0xFF  # deflate block type 3 is invalid: zlib.error

        def set_encrypted(raw, info):
            raw[info.header_offset + 6] |= 1
            central = raw.rindex(b'PK\x01\x02')
            raw[central + 8] |= 1  # needs a password: RuntimeError

        for name, damage in (('zlib', corrupt_data), ('encrypted', set_encrypted)):
            with self.subTest(name), tempfile.TemporaryDirectory() as folder:
                source = pathlib.Path(folder) / 'b.zip'
                with zipfile.ZipFile(source, 'w', zipfile.ZIP_DEFLATED) as archive:
                    archive.writestr('udid/Manifest.db', b'x')
                    archive.writestr('udid/ab/abcdef', b'x' * 100)
                with zipfile.ZipFile(source) as archive:
                    info = archive.infolist()[-1]
                raw = bytearray(source.read_bytes())
                damage(raw, info)
                source.write_bytes(bytes(raw))
                report = _Report()
                made = []
                real_mkdtemp = tempfile.mkdtemp
                with patch.object(self.vsd, '_execute_tool') as inner, \
                        patch.object(self.vsd.tempfile, 'mkdtemp',
                                     side_effect=lambda **kw: made.append(real_mkdtemp(**kw)) or made[-1]):
                    result = self.vsd.execute_tool(source, 'label', 'log', report, declared_type='itunes')
                inner.assert_not_called()
                self.assertEqual(result, (None, None, None))
                self.assertEqual(len(report.errors), 1)
                self.assertIn('b.zip', report.errors[0])
                self.assertFalse(pathlib.Path(made[0]).exists())

    def test_other_types_are_passed_through_unchanged(self):
        with patch.object(self.vsd, '_execute_tool', return_value=('p', 'o', 'l')) as inner:
            result = self.vsd.execute_tool(pathlib.Path('/nowhere/a.zip'), 'label', 'log', _Report())
        self.assertEqual(result, ('p', 'o', 'l'))
        self.assertEqual(inner.call_args.kwargs.get('declared_type'), None)


if __name__ == '__main__':
    unittest.main()
