"""Prove the source_path checker still detects the defects it exists to detect.

check_source_path.py fails when an artifact returns a string constant where the
report expects real paths. The class had already been swept out of iLEAPP once
(PRs #2022 and #2024) and had come back in two sibling cores by the time it was
made a check, so the check is the thing that has to keep working.

The negative cases matter as much as the positive ones. A check wired into CI that
fails correct code gets switched off, so the shapes that must stay silent are
pinned here too: an empty string on a branch that returns no rows never reaches a
report, and a variable holding a real path is not a literal.

The join check is pinned the same way. Each positive case below is a shape found
on main in 2026-10 (a ', ' or '; ' join, a '+' chain, a helper that returns the
joined string, a streamed result's source_path), and each negative case is a way
of building ONE path that must stay silent.
"""
import importlib.util
import pathlib
import sys
import tempfile
import textwrap
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_MODULE_PATH = REPO_ROOT / 'admin' / 'scripts' / 'check_source_path.py'

# admin/scripts is not a package, so load the module from its path.
_spec = importlib.util.spec_from_file_location('check_source_path', _MODULE_PATH)
csp = importlib.util.module_from_spec(_spec)
sys.modules['check_source_path'] = csp
_spec.loader.exec_module(csp)


def findings_for(source):
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / 'sample.py'
        path.write_text(textwrap.dedent(source), encoding='utf-8')
        violations, problem = csp.scan_module(str(path))
    if problem:
        raise AssertionError(problem)
    return violations


def joins_for(source):
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / 'sample.py'
        path.write_text(textwrap.dedent(source), encoding='utf-8')
        violations, problem = csp.scan_module_joins(str(path))
    if problem:
        raise AssertionError(problem)
    return [(line, separator) for _, _, line, separator in violations]


class Prose(unittest.TestCase):
    def test_flags_prose_in_the_return(self):
        found = findings_for('''
            @artifact_processor
            def demo(context):
                data_list = [1]
                return (), data_list, 'See source file(s) below'
        ''')
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][3], 'See source file(s) below')

    def test_flags_prose_reached_through_a_variable(self):
        """appGrouplisting's spelling: assigned once, then returned."""
        found = findings_for('''
            @artifact_processor
            def demo(context):
                source_path = 'Path column in the report'
                data_list = [1]
                return (), data_list, source_path
        ''')
        self.assertEqual(len(found), 1)

    def test_accepts_joined_real_paths(self):
        self.assertEqual(findings_for('''
            @artifact_processor
            def demo(context):
                source_paths = set()
                data_list = []
                for file_found in context.get_files_found():
                    source_paths.add(str(file_found))
                return (), data_list, '\\n'.join(sorted(source_paths))
        '''), [])


class MustStaySilent(unittest.TestCase):
    def test_empty_string_on_a_no_rows_branch_is_fine(self):
        """The wrapper writes no report when data_list is empty."""
        self.assertEqual(findings_for('''
            @artifact_processor
            def demo(context):
                if not context.get_files_found():
                    return (), [], ''
                return (), [1], '\\n'.join(sorted(paths))
        '''), [])

    def test_an_undecorated_helper_is_not_checked(self):
        self.assertEqual(findings_for('''
            def _helper(files_found):
                return (), [1], 'See source file(s) below'
        '''), [])

    def test_a_variable_built_from_paths_is_not_a_literal(self):
        self.assertEqual(findings_for('''
            @artifact_processor
            def demo(context):
                source_path = get_file_path(context.get_files_found(), 'x.db')
                return (), [1], source_path
        '''), [])


class SeparatorJoins(unittest.TestCase):
    def test_flags_a_comma_join_in_the_return(self):
        self.assertEqual(joins_for('''
            @artifact_processor
            def demo(context):
                sources = []
                return (), [1], ', '.join(sources)
        '''), [(5, ', ')])

    def test_flags_a_join_reached_through_a_variable(self):
        self.assertEqual(joins_for('''
            @artifact_processor
            def demo(context):
                source_path = '; '.join(dict.fromkeys(sources))
                return (), [1], source_path
        '''), [(4, '; ')])

    def test_flags_a_separator_named_by_a_module_constant(self):
        self.assertEqual(joins_for('''
            SEPARATOR = ', '

            @artifact_processor
            def demo(context):
                return (), [1], SEPARATOR.join(sources)
        '''), [(6, ', ')])

    def test_flags_a_join_returned_by_a_helper_and_unpacked(self):
        """sysShutdown's shape: the helper hands back rows and the joined string."""
        self.assertEqual(joins_for('''
            def _parse(context):
                sources = []
                return [1], [2], ', '.join(dict.fromkeys(sources))

            @artifact_processor
            def demo(context):
                rows, _other, source_path = _parse(context)
                return (), rows, source_path
        '''), [(4, ', ')])

    def test_flags_a_plus_chain(self):
        """The Chrome modules' shape."""
        self.assertEqual(joins_for('''
            @artifact_processor
            def demo(context):
                report_file = 'Unknown'
                for file_found in context.get_files_found():
                    report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found
                return (), [1], report_file
        '''), [(6, ', ')])

    def test_flags_an_fstring_and_an_augmented_assignment(self):
        self.assertEqual(joins_for('''
            @artifact_processor
            def demo(context):
                listed = f'{db_path}; {wal_path}'
                listed += ', ' + str(other)
                return (), [1], listed
        '''), [(4, '; '), (5, ', ')])

    def test_flags_a_streamed_results_source_path(self):
        self.assertEqual(joins_for('''
            @artifact_processor
            def demo(context):
                results = context.create_artifact_result(
                    headers=(), source_path=', '.join(sources))
                results.set_source_path(' '.join(str(x) for x in in_dirs))
                return results
        '''), [(5, ', '), (6, ' ')])

    def test_accepts_newline_joins(self):
        self.assertEqual(joins_for('''
            @artifact_processor
            def demo(context):
                source_path = '\\n'.join(dict.fromkeys(sources))
                return (), [1], '\\n'.join(sorted(set(sources))) if sources else source_path
        '''), [])

    def test_accepts_building_one_path(self):
        self.assertEqual(joins_for('''
            import os

            @artifact_processor
            def demo(context):
                first = '/'.join(parts)
                second = os.path.join(folder, name)
                third = f'{folder}/{name}'
                fourth = f'{archive} >> {member}'
                fifth = ''.join(pieces)
                return (), [1], '\\n'.join((first, second, third, fourth, fifth))
        '''), [])

    def test_ignores_a_nested_functions_return(self):
        """allTrails' shape: a nested helper returns a 3-tuple that is not the artifact's."""
        self.assertEqual(joins_for('''
            @artifact_processor
            def demo(context):
                def place(location_id):
                    names = ', '.join(parts)
                    return lat, lng, names
                return (), [1], source_path
        '''), [])

    def test_a_join_on_a_no_rows_branch_is_fine(self):
        self.assertEqual(joins_for('''
            @artifact_processor
            def demo(context):
                return (), [], ', '.join(sources)
        '''), [])


class TheRepoItself(unittest.TestCase):
    def test_no_artifact_in_this_repo_returns_prose(self):
        artifacts = REPO_ROOT / 'scripts' / 'artifacts'
        offenders = []
        for module in sorted(artifacts.glob('*.py')):
            violations, _ = csp.scan_module(str(module))
            offenders.extend(violations)
        self.assertEqual(offenders, [], f'{len(offenders)} artifact(s) return prose')

    def test_no_artifact_in_this_repo_lists_paths_with_another_separator(self):
        artifacts = REPO_ROOT / 'scripts' / 'artifacts'
        offenders = []
        for module in sorted(artifacts.glob('*.py')):
            violations, _ = csp.scan_module_joins(str(module))
            offenders.extend(violations)
        self.assertEqual(offenders, [], f'{len(offenders)} artifact join(s) found')


if __name__ == '__main__':
    unittest.main()
