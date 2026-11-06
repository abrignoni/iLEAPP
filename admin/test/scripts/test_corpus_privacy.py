"""Pin how the tooling reads a corpus registry entry's privacy designation.

A registry entry can carry allow_fixtures and allow_public_metadata as true,
false or null (terms not established), or not carry them at all (no
designation recorded). The validator reports a cited key whose
allow_public_metadata is false as an error and null as a warning, and the case
cutter refuses an input whose allow_fixtures is false or null. An entry
without the fields is left alone by both, and so is an input the registry does
not hold. Every registry below is synthetic and written to a temporary folder.
"""
import importlib
import importlib.util
import json
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
sys.path.append(os.path.dirname(__file__))

from admin.scripts import corpus_privacy  # noqa: E402  pylint: disable=wrong-import-position

CUTTER_NAME = ('make_case_data'
               if os.path.exists(os.path.join(os.path.dirname(__file__), 'make_case_data.py'))
               else 'make_test_data')


def _load_validator():
    script = REPO_ROOT / 'admin' / 'scripts' / 'validate_sample_data.py'
    spec = importlib.util.spec_from_file_location('validate_sample_data', script)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DESIGNATIONS = {
    'open_key': {'private': False, 'allow_fixtures': True, 'allow_public_metadata': True,
                 'privacy_basis': 'synthetic: published image'},
    'closed_key': {'private': True, 'allow_fixtures': False, 'allow_public_metadata': False,
                   'privacy_basis': 'synthetic: provider designated private'},
    'unsettled_key': {'private': None, 'allow_fixtures': False, 'allow_public_metadata': None,
                      'privacy_basis': 'synthetic: terms not established'},
    'null_fixtures_key': {'private': None, 'allow_fixtures': None, 'allow_public_metadata': None,
                          'privacy_basis': 'synthetic: terms not established'},
    'citable_key': {'private': True, 'allow_fixtures': False, 'allow_public_metadata': True,
                    'privacy_basis': 'synthetic: key citable, content private'},
    'undesignated_key': {},
}


class RegistryFixture(unittest.TestCase):
    """A registry with one small file per entry, each with distinct content."""

    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        samples = {}
        for index, (name, fields) in enumerate(DESIGNATIONS.items()):
            member = self.root / 'images' / f'{name}.zip'
            member.parent.mkdir(parents=True, exist_ok=True)
            member.write_bytes(f'synthetic image {index}'.encode())
            entry = {'match': {'zip': f'images/{name}.zip',
                               'sha256': corpus_privacy._sha256(member)}}  # pylint: disable=protected-access
            entry.update(fields)
            samples[name] = entry
        self.registry = {'samples': samples}
        self.registry_path = self.root / 'samples.json'
        self.registry_path.write_text(json.dumps(self.registry), encoding='utf-8')

    def image(self, name):
        return self.root / 'images' / f'{name}.zip'


class TestFieldState(unittest.TestCase):

    def test_recorded_values_and_absence_are_distinct(self):
        self.assertIs(corpus_privacy.field_state({'f': True}, 'f'), True)
        self.assertIs(corpus_privacy.field_state({'f': False}, 'f'), False)
        self.assertIsNone(corpus_privacy.field_state({'f': None}, 'f'))
        self.assertEqual(corpus_privacy.field_state({}, 'f'), corpus_privacy.ABSENT)
        self.assertEqual(corpus_privacy.field_state(None, 'f'), corpus_privacy.ABSENT)

    def test_a_value_outside_the_schema_reads_as_not_established(self):
        self.assertIsNone(corpus_privacy.field_state({'f': 'no'}, 'f'))
        self.assertIsNone(corpus_privacy.field_state({'f': 0}, 'f'))

    def test_refuses_false_and_null_only(self):
        self.assertTrue(corpus_privacy.refuses({'f': False}, 'f'))
        self.assertTrue(corpus_privacy.refuses({'f': None}, 'f'))
        self.assertFalse(corpus_privacy.refuses({'f': True}, 'f'))
        self.assertFalse(corpus_privacy.refuses({}, 'f'))

    def test_describe_names_the_key_value_and_basis(self):
        line = corpus_privacy.describe('k', DESIGNATIONS['unsettled_key'], 'allow_public_metadata')
        self.assertIn("'k'", line)
        self.assertIn('null (terms not established)', line)
        self.assertIn('synthetic: terms not established', line)


class TestFindEntry(RegistryFixture):

    def test_found_by_registered_path(self):
        name, _ = corpus_privacy.find_entry(self.registry, self.registry_path,
                                            self.image('closed_key'))
        self.assertEqual(name, 'closed_key')

    def test_found_through_a_symlink(self):
        link = self.root / 'link.zip'
        try:
            link.symlink_to(self.image('closed_key'))
        except (OSError, NotImplementedError):
            self.skipTest('symlinks unavailable')
        name, _ = corpus_privacy.find_entry(self.registry, self.registry_path, link)
        self.assertEqual(name, 'closed_key')

    def test_a_moved_copy_is_found_by_content(self):
        copy = self.root / 'elsewhere' / 'renamed.zip'
        copy.parent.mkdir()
        shutil.copyfile(self.image('closed_key'), copy)
        name, _ = corpus_privacy.find_entry(self.registry, self.registry_path, copy)
        self.assertEqual(name, 'closed_key')

    def test_an_unregistered_file_is_not_found(self):
        other = self.root / 'other.zip'
        other.write_bytes(b'not registered anywhere')
        self.assertEqual(corpus_privacy.find_entry(self.registry, self.registry_path, other),
                         (None, None))

    def test_same_size_different_content_is_not_found(self):
        # 'synthetic image 1' and 'synthetic image 9' have the same length.
        other = self.root / 'same_size.zip'
        other.write_bytes(b'synthetic image 9')
        self.assertEqual(corpus_privacy.find_entry(self.registry, self.registry_path, other),
                         (None, None))


class TestValidatorRegistryStep(RegistryFixture):

    def run_check(self, cited):
        validator = _load_validator()
        artifacts = {f'art_{key}': ('module.py', {'sample_data': {key: '1 row'}})
                     for key in cited}
        report = validator.Report()
        validator.check_registry(artifacts, self.registry, self.registry_path, False, report)
        return report

    def test_false_is_an_error(self):
        report = self.run_check(['closed_key'])
        self.assertEqual(len(report.errors), 1)
        self.assertIn("'closed_key'", report.errors[0])
        self.assertEqual(report.warnings, [])

    def test_null_is_a_warning(self):
        report = self.run_check(['unsettled_key'])
        self.assertEqual(report.errors, [])
        self.assertEqual(len(report.warnings), 1)
        self.assertIn("'unsettled_key'", report.warnings[0])

    def test_true_and_absent_are_not_reported(self):
        report = self.run_check(['open_key', 'citable_key', 'undesignated_key'])
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_one_finding_per_key_not_per_citation(self):
        validator = _load_validator()
        artifacts = {f'art_{n}': ('module.py', {'sample_data': {'unsettled_key': '1 row'}})
                     for n in range(5)}
        report = validator.Report()
        validator.check_registry(artifacts, self.registry, self.registry_path, False, report)
        self.assertEqual(len(report.warnings), 1)
        self.assertIn('5 artifact(s)', report.warnings[0])


class TestCutterRefusal(RegistryFixture):

    @classmethod
    def setUpClass(cls):
        cls.cutter = importlib.import_module(CUTTER_NAME)

    def refusal(self, name):
        return self.cutter.fixture_refusal(str(self.image(name)), str(self.registry_path))

    def test_false_and_null_are_refused(self):
        for name in ('closed_key', 'unsettled_key', 'citable_key', 'null_fixtures_key'):
            with self.subTest(name=name):
                self.assertIn(f"'{name}'", self.refusal(name) or '')

    def test_true_and_absent_are_allowed(self):
        self.assertIsNone(self.refusal('open_key'))
        self.assertIsNone(self.refusal('undesignated_key'))

    def test_no_registry_means_no_check(self):
        self.assertIsNone(self.cutter.fixture_refusal(str(self.image('closed_key')), None))

    def test_an_unregistered_input_is_allowed(self):
        other = self.root / 'contributor_image.zip'
        other.write_bytes(b'a contributor image')
        self.assertIsNone(self.cutter.fixture_refusal(str(other), str(self.registry_path)))


if __name__ == '__main__':
    unittest.main()
