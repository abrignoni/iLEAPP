"""Prove the Biome reference check fails on a contradiction and only on a contradiction.

The planted cases edit copies of real modules, one for each way modules consume a name
(.get, a helper call, a version-keyed table, a DK metadata table), so the proof runs
through the shapes on main and not only through fixtures written for the extractor.
"""
import importlib.util
import json
import pathlib
import sys
import tempfile
import textwrap
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_MODULE_PATH = REPO_ROOT / 'admin' / 'scripts' / 'check_biome_reference.py'
_spec = importlib.util.spec_from_file_location('check_biome_reference', _MODULE_PATH)
cbr = importlib.util.module_from_spec(_spec)
sys.modules['check_biome_reference'] = cbr
_spec.loader.exec_module(cbr)

ARTIFACTS = REPO_ROOT / 'scripts' / 'artifacts'


def run_on(files, exceptions=None):
    """Run the check over a temporary tree holding only the given {name: source}."""
    with tempfile.TemporaryDirectory() as folder:
        root = pathlib.Path(folder)
        target = root / 'scripts' / 'artifacts'
        target.mkdir(parents=True)
        for name, source in files.items():
            (target / name).write_text(source, encoding='utf-8')
        waivers = root / 'exceptions.json'
        waivers.write_text(json.dumps(exceptions or []), encoding='utf-8')
        return cbr.check(str(root), cbr.REFERENCE, str(waivers))


def planted(name, old, new):
    source = (ARTIFACTS / name).read_text(encoding='utf-8')
    assert source.count(old) >= 1, f'{old!r} is no longer in {name}'
    return {name: source.replace(old, new, 1)}


def different(items, kind):
    return [i for i in items if i.kind == kind and i.status == cbr.DIFFERENT]


def synthetic(body, path='*/Biome/streams/public/Backlight/local/*', notes=''):
    return {'biomeSynthetic.py': textwrap.dedent(f'''\
        __artifacts_v2__ = {{
            "get_biomeSynthetic": {{
                "name": "Synthetic", "notes": {notes!r}, "paths": ({path!r},),
            }}
        }}
        ''') + textwrap.dedent(body)}


class PlantedInRealModules(unittest.TestCase):
    def test_wrong_class_for_the_stream(self):
        items, _ = run_on(planted('biomeBacklight.py', 'BMDeviceBacklight class', 'BMAppInFocus class'))
        self.assertEqual(len(different(items, 'stream')), 1)

    def test_wrong_wire_type_on_a_field(self):
        items, _ = run_on(planted('biomeBacklight.py', "'2': {'type': 'int'", "'2': {'type': 'double'"))
        self.assertEqual([i.item.split()[-1] for i in different(items, 'field')], ['2'])

    def test_wrong_wire_type_on_a_dk_field(self):
        source = (ARTIFACTS / 'biomeSafari.py').read_text(encoding='utf-8')
        self.assertIn("'2': {'type': 'double'", source)
        items, _ = run_on({'biomeSafari.py': source.replace("'2': {'type': 'double'", "'2': {'type': 'int'", 1)})
        self.assertTrue(different(items, 'field'))

    def test_wrong_field_name_for_a_number(self):
        items, _ = run_on(planted('biomeAppWebUsage.py', '(usageState)', '(webDomain)'))
        self.assertEqual(len(different(items, 'field_name')), 1)

    def test_wrong_enum_name_read_through_get(self):
        items, _ = run_on(planted('biomeMotionActivity.py', "1: 'Low'", "1: 'Lowest'"))
        self.assertEqual([i.key for i in different(items, 'enum')], ['1'])

    def test_wrong_enum_name_read_through_a_helper(self):
        items, _ = run_on(planted('biomeAppleIntelligence.py', "'StatusRestricted'", "'StatusPermitted'"))
        self.assertEqual([(i.item, i.key) for i in different(items, 'enum')], [('_AVAIL_STATUS', '2')])

    def test_swapped_enum_numbers(self):
        source = (ARTIFACTS / 'biomeMotionActivity.py').read_text(encoding='utf-8')
        swapped = source.replace("1: 'Low'", "1: 'TEMP'", 1).replace("2: 'Medium'", "2: 'Low'", 1)
        swapped = swapped.replace("1: 'TEMP'", "1: 'Medium'", 1)
        self.assertNotEqual(source, swapped)
        items, _ = run_on({'biomeMotionActivity.py': swapped})
        self.assertEqual(sorted(i.key for i in different(items, 'enum')), ['1', '2'])

    def test_wrong_name_in_a_version_keyed_table(self):
        items, _ = run_on(planted('biomeUserFocus.py', "_ORIGIN_V2 = {0: 'Unknown', 1: 'None'",
                                  "_ORIGIN_V2 = {0: 'Unknown', 1: 'Nothing'"))
        self.assertEqual([(i.item, i.key) for i in different(items, 'version_enum')], [('_ORIGIN_V2', '1')])

    def test_wrong_dk_metadata_label(self):
        source = (ARTIFACTS / 'biomeDKEventStreams.py').read_text(encoding='utf-8')
        self.assertIn("8007: 'routeChangeReason'", source)
        items, _ = run_on({'biomeDKEventStreams.py': source.replace(
            "8007: 'routeChangeReason'", "8007: 'routeName'", 1)})
        self.assertEqual([i.key for i in different(items, 'dk_label')], ['8007'])


class CouldNotCheckIsNotAFailure(unittest.TestCase):
    def assert_no_difference(self, items, kind):
        self.assertFalse([i for i in items if i.status == cbr.DIFFERENT])
        self.assertTrue([i for i in items if i.kind == kind and i.status == cbr.UNCHECKED])

    def test_stream_absent_from_the_reference(self):
        items, _ = run_on(synthetic('', path='*/Biome/streams/public/Not.A.Stream/local/*'))
        self.assert_no_difference(items, 'stream')

    def test_field_number_absent_from_the_class(self):
        items, _ = run_on(synthetic("T = {'99': {'type': 'int', 'name': ''}}\n"))
        self.assert_no_difference(items, 'field')

    def test_inner_table_with_no_version_data(self):
        body = """
            _STATE_V9 = {0: 'First', 1: 'Second', 2: 'Third'}
            _STATE = {9: _STATE_V9}
            """
        items, _ = run_on(synthetic(body))
        self.assert_no_difference(items, 'version_enum')

    def test_generic_table_binds_to_nothing(self):
        items, _ = run_on(synthetic("ON_OFF = {0: 'Off', 1: 'On'}\n"))
        self.assert_no_difference(items, 'enum')

    def test_prose_where_the_number_belongs_to_another_field(self):
        source = (ARTIFACTS / 'biomeAppIntentsTranscript.py').read_text(encoding='utf-8')
        self.assertIn('bundleURL of the parameter title (field 4)', source)
        items, _ = run_on({'biomeAppIntentsTranscript.py': source})
        self.assertFalse(different(items, 'field_name'))

    def test_local_typedef_key_is_not_a_field_name_claim(self):
        items, _ = run_on(synthetic("T = {'1': {'type': 'double', 'name': 'when'}}\n"))
        self.assertFalse([i for i in items if i.status == cbr.DIFFERENT])


class Exceptions(unittest.TestCase):
    FILES = planted('biomeMotionActivity.py', "1: 'Low'", "1: 'Lowest'")

    def entry(self, key='1'):
        found = different(run_on(self.FILES)[0], 'enum')[0]
        return {'module': found.module, 'kind': found.kind, 'item': found.item, 'key': key,
                'reason': 'test'}

    def test_exact_exception_clears_only_that_item(self):
        items, stale = run_on(self.FILES, [self.entry()])
        self.assertFalse(different(items, 'enum'))
        self.assertEqual(stale, [])

    def test_exception_for_another_key_does_not_clear_it(self):
        items, stale = run_on(self.FILES, [self.entry('3')])
        self.assertTrue(different(items, 'enum'))
        self.assertEqual(len(stale), 1)

    def test_exception_that_matches_nothing_is_stale(self):
        source = (ARTIFACTS / 'biomeMotionActivity.py').read_text(encoding='utf-8')
        _, stale = run_on({'biomeMotionActivity.py': source}, [self.entry()])
        self.assertEqual(len(stale), 1)


class CurrentTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items, cls.stale = cbr.check()

    def test_no_contradiction_on_this_tree(self):
        found = [f'{i.module} {i.kind} {i.item} {i.key}: {i.detail}' for i in self.items
                 if i.status == cbr.DIFFERENT]
        self.assertEqual(found, [])
        self.assertEqual(self.stale, [])

    def test_every_kind_checked_something(self):
        for kind in cbr.KINDS:
            self.assertTrue([i for i in self.items if i.kind == kind and i.status == cbr.CONFIRMED],
                            f'{kind} confirmed nothing, so the extractor is broken')


class CommittedReference(unittest.TestCase):
    def test_holds_no_local_path_or_address(self):
        text = pathlib.Path(cbr.REFERENCE).read_text(encoding='utf-8')
        for marker in ('/Users', '/Volumes', 'Downloads', '@', 'storePath', 'colerr'):
            self.assertNotIn(marker, text)

    def test_every_field_has_a_measured_wire_type(self):
        data = json.loads(pathlib.Path(cbr.REFERENCE).read_text(encoding='utf-8'))
        for name, rows in data['classes'].items():
            for row in rows:
                self.assertIn(row[2], (0, 1, 2, 5), f'{name} field {row[0]}')


if __name__ == '__main__':
    unittest.main()
