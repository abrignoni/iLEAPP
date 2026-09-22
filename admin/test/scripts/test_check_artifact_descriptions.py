"""Prove the description checker fails on each shape it exists to catch and passes
the shapes it must leave alone.

The mechanical defects are exact: a description that is missing, empty, more than one
line, identical to the artifact's name, or identical to a sibling's in the same module.
Each gets a fixture that fails and a neighbouring fixture that passes, because a gate
that has only ever been seen green has not been shown to gate anything.

Two negative cases matter as much as the positives. Identical descriptions in two
different modules are not flagged, since the rule is scoped to one module, where a
duplicate is a copy left unfinished. And the review listing is not a gate: its helper
returns the conceding sentences and nothing here asserts on them as failures.

Expected values are written out as literals rather than derived from the module under
test, so a fixture cannot move with a bug in the code it checks.
"""
import importlib.util
import pathlib
import sys
import tempfile
import textwrap
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_MODULE_PATH = REPO_ROOT / 'admin' / 'scripts' / 'check_artifact_descriptions.py'

# admin/scripts is not a package, so load the module from its path.
_spec = importlib.util.spec_from_file_location('check_artifact_descriptions', _MODULE_PATH)
cad = importlib.util.module_from_spec(_spec)
sys.modules['check_artifact_descriptions'] = cad
_spec.loader.exec_module(cad)


def violations_for(source, filename='sample.py'):
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / filename
        path.write_text(textwrap.dedent(source), encoding='utf-8')
        found, problem = cad.check_module(str(path))
    if problem:
        raise AssertionError(problem)
    return [(key, reason) for _module, key, reason in found]


def block(entries):
    """An __artifacts_v2__ module source from {key: {field: value}}."""
    lines = ['__artifacts_v2__ = {']
    for key, fields in entries.items():
        lines.append(f'    {key!r}: {{')
        for field, value in fields.items():
            lines.append(f'        {field!r}: {value!r},')
        lines.append('    },')
    lines.append('}')
    return '\n'.join(lines) + '\n'


class MechanicalDefects(unittest.TestCase):
    def test_missing_description_fails(self):
        found = violations_for(block({'a': {'name': 'Thing'}}))
        self.assertEqual(found, [('a', 'description is missing or not a string')])

    def test_non_string_description_fails(self):
        found = violations_for(block({'a': {'name': 'Thing', 'description': 7}}))
        self.assertEqual(found, [('a', 'description is missing or not a string')])

    def test_empty_description_fails(self):
        found = violations_for(block({'a': {'name': 'Thing', 'description': '   '}}))
        self.assertEqual(found, [('a', 'description is empty')])

    def test_multiline_description_fails(self):
        found = violations_for(block({'a': {'name': 'Thing',
                                             'description': 'Rows from x.\nMore.'}}))
        self.assertEqual(found, [('a', 'description runs to more than one line')])

    def test_description_equal_to_name_fails(self):
        found = violations_for(block({'a': {'name': 'Samsung Notes',
                                             'description': 'Samsung Notes'}}))
        self.assertEqual(found, [('a', 'description only repeats the name')])

    def test_name_match_ignores_case_and_spacing(self):
        found = violations_for(block({'a': {'name': 'Samsung  Notes',
                                             'description': 'samsung notes '}}))
        self.assertEqual(found, [('a', 'description only repeats the name')])

    def test_duplicate_within_module_fails_on_the_second(self):
        found = violations_for(block({
            'contacts': {'name': 'Romeo Contacts', 'description': 'Parses Romeo contacts'},
            'accounts': {'name': 'Romeo Accounts', 'description': 'Parses Romeo contacts'},
        }))
        self.assertEqual(found, [('accounts',
                                  "description duplicates 'contacts' in the same module")])

    def test_duplicate_match_ignores_case(self):
        found = violations_for(block({
            'a': {'name': 'A', 'description': 'Kik notifications from FCM'},
            'b': {'name': 'B', 'description': 'kik Notifications from fcm'},
        }))
        self.assertEqual([k for k, _ in found], ['b'])


class ShapesLeftAlone(unittest.TestCase):
    def test_distinct_one_line_descriptions_pass(self):
        found = violations_for(block({
            'a': {'name': 'JusTalk - Calls', 'description': 'Calls from the JusTalk store'},
            'b': {'name': 'JusTalk Kids - Calls',
                  'description': 'Calls from the JusTalk Kids store'},
        }))
        self.assertEqual(found, [])

    def test_description_that_extends_the_name_passes(self):
        found = violations_for(block({'a': {'name': 'Samsung Notes',
                                             'description': 'Notes from Samsung Notes, with media'}}))
        self.assertEqual(found, [])

    def test_same_description_in_two_modules_is_not_flagged(self):
        source = block({'a': {'name': 'A', 'description': 'Chess database'}})
        self.assertEqual(violations_for(source, 'one.py'), [])
        self.assertEqual(violations_for(source, 'two.py'), [])

    def test_unparseable_module_is_reported_not_crashed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'broken.py'
            path.write_text('__artifacts_v2__ = {\n', encoding='utf-8')
            found, problem = cad.check_module(str(path))
        self.assertEqual(found, [])
        self.assertIn('could not parse', problem)


class ReviewListing(unittest.TestCase):
    def test_conceding_sentences_are_selected(self):
        notes = ('One row per entry. Whether every file is recorded was not established. '
                 'Times are UTC. A blank value is not evidence of absence.')
        limits = cad.concession_sentences(notes)
        self.assertEqual(limits, ['Whether every file is recorded was not established.',
                                  'A blank value is not evidence of absence.'])

    def test_non_string_notes_yield_nothing(self):
        self.assertEqual(cad.concession_sentences(None), [])


if __name__ == '__main__':
    unittest.main()
