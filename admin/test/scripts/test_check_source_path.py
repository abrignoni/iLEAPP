"""Prove the source_path checker still detects the defects it exists to detect.

check_source_path.py fails when an artifact returns a string constant where the
report expects real paths. The class had already been swept out of iLEAPP once
(PRs #2022 and #2024) and had come back in two sibling cores by the time it was
made a check, so the check is the thing that has to keep working.

The negative cases matter as much as the positive ones. A check wired into CI that
fails correct code gets switched off, so the shapes that must stay silent are
pinned here too: an empty string on a branch that returns no rows never reaches a
report, and a variable holding a real path is not a literal.
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


class TheRepoItself(unittest.TestCase):
    def test_no_artifact_in_this_repo_returns_prose(self):
        artifacts = REPO_ROOT / 'scripts' / 'artifacts'
        offenders = []
        for module in sorted(artifacts.glob('*.py')):
            violations, _ = csp.scan_module(str(module))
            offenders.extend(violations)
        self.assertEqual(offenders, [], f'{len(offenders)} artifact(s) return prose')


if __name__ == '__main__':
    unittest.main()
