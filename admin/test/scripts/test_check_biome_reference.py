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

    def test_inline_version_table_with_other_numbering(self):
        body = """
            _PLATFORM = {0: {0: 'iPad', 1: 'iPhone', 2: 'MacDesktop'},
                         1: {0: 'Unknown', 1: 'iPad', 2: 'iPhone'}}
            """
        path = '*/Biome/streams/public/Device.Metadata/local/*'
        items, _ = run_on(synthetic(body, path=path))
        self.assertFalse([i for i in items if i.status == cbr.DIFFERENT])

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


    def test_typedef_for_a_nested_payload_is_not_the_stream_class(self):
        body = """
            import blackboxprotobuf
            INNER = {'1': {'type': 'str', 'name': ''}}
            def get_biomeSynthetic(record, payload):
                return blackboxprotobuf.decode_message(payload, INNER)
            """
        items, _ = run_on(synthetic(body))
        self.assert_no_difference(items, 'field')

    def test_note_that_compares_with_another_class(self):
        notes = 'This stream is separate from the BMAppInFocus class.'
        items, _ = run_on(synthetic('', notes=notes))
        self.assert_no_difference(items, 'stream')

    def test_table_sharing_two_names_with_an_enum_is_not_bound(self):
        self.assertEqual(cbr.compare_table({0: 'Alpha', 1: 'Beta', 2: 'Other'},
                                           {'full': {0: 'Alpha', 1: 'Beta', 2: 'Gamma'}})[0],
                         cbr.UNCHECKED)

    def test_small_tables_that_disagree_are_listed(self):
        full = {'full': {0: 'Alpha', 1: 'Beta', 2: 'Gamma'}}
        status, key, conflicts = cbr.compare_table({0: 'Alpha', 1: 'Wrong'}, full)
        self.assertEqual((status, key), (cbr.UNCHECKED, 'full'))
        self.assertTrue(conflicts)

    def test_plain_tuple_in_another_order_is_not_a_swap(self):
        full = {'full': {0: 'Alpha', 1: 'Beta', 2: 'Gamma'}}
        table = {0: 'Beta', 1: 'Alpha', 2: 'Gamma'}
        self.assertNotEqual(cbr.compare_table(table, full, keyed=False)[0], cbr.DIFFERENT)


class TypedefBinding(unittest.TestCase):
    WRONG = "{'2': {'type': 'double', 'name': ''}}"

    def test_typedef_passed_through_a_helper_is_judged(self):
        body = f"""
            import blackboxprotobuf
            T = {self.WRONG}
            def _records(context, label, typess=None):
                for record in context:
                    yield blackboxprotobuf.decode_message(record.data, typess or {{}})
            def get_biomeSynthetic(context):
                return list(_records(context, 'x', T))
            """
        self.assertEqual(len(different(run_on(synthetic(body))[0], 'field')), 1)

    def test_default_typedef_of_a_helper_is_judged(self):
        body = f"""
            import blackboxprotobuf
            T = {self.WRONG}
            def _records(context, typess=None):
                typess = T if typess is None else typess
                for record in context:
                    yield blackboxprotobuf.decode_message(record.data, typess)
            def get_biomeSynthetic(context):
                return list(_records(context))
            """
        self.assertEqual(len(different(run_on(synthetic(body))[0], 'field')), 1)


class TableBinding(unittest.TestCase):
    def test_smaller_tied_enum_cannot_vouch_for_a_wrong_name(self):
        status = cbr.compare_table({0: 'Alpha', 1: 'Beta', 2: 'Delta', 3: 'Wrong'},
                                   {'full': {0: 'Alpha', 1: 'Beta', 2: 'Delta', 3: 'Gamma'},
                                    'small': {0: 'Alpha', 1: 'Beta', 2: 'Delta'}})[0]
        self.assertEqual(status, cbr.DIFFERENT)


    def test_two_numbers_swapped_in_a_small_enum(self):
        status, _, conflicts = cbr.compare_table({0: 'Alpha', 1: 'Gamma', 2: 'Beta'},
                                                 {'full': {0: 'Alpha', 1: 'Beta', 2: 'Gamma'}})
        self.assertEqual((status, sorted(conflicts)), (cbr.DIFFERENT, [1, 2]))


class Exceptions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.FILES = planted('biomeMotionActivity.py', "1: 'Low'", "1: 'Lowest'")

    def entry(self, key='1', value='Lowest'):
        found = different(run_on(self.FILES)[0], 'enum')[0]
        return {'module': found.module, 'kind': found.kind, 'item': found.item, 'key': key,
                'value': value, 'reason': 'test'}

    def test_exact_exception_clears_only_that_item(self):
        items, stale = run_on(self.FILES, [self.entry()])
        self.assertFalse(different(items, 'enum'))
        self.assertEqual(stale, [])

    def test_exception_for_another_key_does_not_clear_it(self):
        items, stale = run_on(self.FILES, [self.entry('3')])
        self.assertTrue(different(items, 'enum'))
        self.assertEqual(len(stale), 1)

    def test_exception_for_another_value_does_not_clear_it(self):
        items, stale = run_on(self.FILES, [self.entry(value='SomethingElse')])
        self.assertTrue(different(items, 'enum'))
        self.assertEqual(len(stale), 1)

    def test_exception_with_no_value_does_not_clear_it(self):
        entry = self.entry()
        del entry['value']
        items, stale = run_on(self.FILES, [entry])
        self.assertTrue(different(items, 'enum'))
        self.assertEqual(len(stale), 1)

    def test_exception_survives_a_line_added_above_a_typedef(self):
        files = planted('biomeBacklight.py', "'2': {'type': 'int'", "'2': {'type': 'double'")
        found = different(run_on(files)[0], 'field')[0]
        entry = {'module': found.module, 'kind': found.kind, 'item': found.item, 'key': found.key,
                 'value': found.stored, 'reason': 'test'}
        moved = {name: '# one more line\n' + source for name, source in files.items()}
        items, stale = run_on(moved, [entry])
        self.assertFalse(different(items, 'field'))
        self.assertEqual(stale, [])

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
