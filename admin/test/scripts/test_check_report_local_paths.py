"""Prove the local-path checker still detects the defects it exists to detect.

check_report_local_paths.py reads artifact source and reports staged paths that reach
report output. It is itself a script and can rot. Two of its own rules were wrong before
they were right in the session that introduced it, and only a run against known input
caught either:

  * `pathlib.Path(file_found)` was not recognised as passing taint through, because the
    passthrough set was consulted only for bare `Path(...)` and not for an attribute call.
    That hid a real leak in appGrouplisting.
  * clearing taint on any untainted assignment made `db_files = []` race the later
    `db_files.append(file_found)` on every pass of the fixed point, so the loop over that
    list was never seen as tainted. That hid a real leak in ZangiMessenger.

Both shapes are pinned below, so an edit that reintroduces either fails here instead of
shipping a checker that quietly passes everything.

The false-negative cases matter as much as the positives: a checker wired into CI that
flags correct code gets disabled, so the shapes that must stay silent are pinned too.
"""
import importlib.util
import pathlib
import sys
import tempfile
import textwrap
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_MODULE_PATH = REPO_ROOT / 'admin' / 'scripts' / 'check_report_local_paths.py'

# admin/scripts is not a package, so load the module from its path.
_spec = importlib.util.spec_from_file_location('check_report_local_paths', _MODULE_PATH)
crlp = importlib.util.module_from_spec(_spec)
sys.modules['check_report_local_paths'] = crlp
_spec.loader.exec_module(crlp)


def findings_for(source):
    """The violations the checker reports for one module's source text."""
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / 'sample.py'
        path.write_text(textwrap.dedent(source), encoding='utf-8')
        violations, problem = crlp.scan_module(str(path))
    if problem:
        raise AssertionError(problem)
    return violations


class RowValues(unittest.TestCase):
    def test_flags_a_staged_path_placed_in_a_row(self):
        found = findings_for('''
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    data_list.append(('a', file_found))
                return (), data_list, ''
        ''')
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][3], 'row-value')

    def test_get_relative_path_is_accepted(self):
        self.assertEqual(findings_for('''
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    data_list.append(('a', context.get_relative_path(file_found)))
                return (), data_list, ''
        '''), [])

    def test_basename_is_accepted(self):
        self.assertEqual(findings_for('''
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    data_list.append(('a', os.path.basename(file_found)))
                return (), data_list, ''
        '''), [])

    def test_the_returned_source_path_is_not_reported(self):
        """The wrapper normalizes the third element, so it is not a leak."""
        self.assertEqual(findings_for('''
            @artifact_processor
            def demo(context):
                data_list = []
                source_path = ''
                for file_found in context.get_files_found():
                    source_path = file_found
                    data_list.append(('a', 'b'))
                return (), data_list, source_path
        '''), [])


class ShapesThatOnceHidALeak(unittest.TestCase):
    def test_pathlib_path_passes_taint_through(self):
        """appGrouplisting: fileloc = str(pathlib.Path(file_found).parents[1])."""
        found = findings_for('''
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    p = pathlib.Path(file_found)
                    data_list.append(('a', str(p.parents[1])))
                return (), data_list, ''
        ''')
        self.assertEqual(len(found), 1, 'pathlib.Path must pass taint through')

    def test_a_list_built_by_appending_stays_tainted(self):
        """ZangiMessenger: db_files = [] then db_files.append(file_found)."""
        found = findings_for('''
            @artifact_processor
            def demo(context):
                data_list = []
                db_files = []
                for file_found in context.get_files_found():
                    db_files.append(file_found)
                for main_db in db_files:
                    data_list.append(('a', main_db))
                return (), data_list, ''
        ''')
        self.assertEqual(len(found), 1, 'an initializer must not clear container taint')


class LocatedAt(unittest.TestCase):
    def test_flags_a_staged_path_handed_to_the_report_writer(self):
        found = findings_for('''
            @artifact_processor
            def demo(context):
                for file_found in context.get_files_found():
                    report.write_artifact_data_table(headers, rows, file_found)
                return (), [], ''
        ''')
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][3], 'located-at')


class MustStaySilent(unittest.TestCase):
    def test_an_undecorated_helper_is_not_checked(self):
        """A helper carrying a full path between functions is normal and correct."""
        self.assertEqual(findings_for('''
            def _helper(files_found):
                rows = []
                for file_found in files_found:
                    rows.append(('a', file_found))
                return rows
        '''), [])

    def test_a_regex_match_is_not_a_path(self):
        """protonVPN: re.search(...) must not be read as seeker.search(...)."""
        self.assertEqual(findings_for('''
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    hostname = re.search(r'node.+', line)
                    data_list.append((hostname[0], 'b'))
                return (), data_list, ''
        '''), [])

    def test_a_path_component_is_not_a_path(self):
        """installedapps: Path(file_found).parts[-4] is the Android user id."""
        self.assertEqual(findings_for('''
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    user = pathlib.Path(file_found).parts[-4]
                    data_list.append((user, 'b'))
                return (), data_list, ''
        '''), [])

    def test_an_email_message_walk_is_not_os_walk(self):
        """mailprotect: message.walk() yields MIME parts, not filesystem paths."""
        self.assertEqual(findings_for('''
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    names = ', '.join(p.get_filename() for p in message.walk())
                    data_list.append((names, 'b'))
                return (), data_list, ''
        '''), [])


class Allowlist(unittest.TestCase):
    def test_an_allowlisted_expression_is_not_reported(self):
        source = '''
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    data_list.append(('a', file_found))
                return (), data_list, ''
        '''
        self.assertEqual(len(findings_for(source)), 1)
        crlp.ALLOWLIST['sample.py:demo:file_found'] = 'pinned by this test'
        try:
            self.assertEqual(findings_for(source), [])
        finally:
            del crlp.ALLOWLIST['sample.py:demo:file_found']


class TheRepoItself(unittest.TestCase):
    def test_no_artifact_in_this_repo_leaks_a_local_path(self):
        self.assertEqual(crlp.main.__module__, 'check_report_local_paths')
        artifacts = REPO_ROOT / 'scripts' / 'artifacts'
        offenders = []
        for module in sorted(artifacts.glob('*.py')):
            violations, _ = crlp.scan_module(str(module))
            offenders.extend(violations)
        self.assertEqual(offenders, [], f'{len(offenders)} local path(s) reach report output')


if __name__ == '__main__':
    unittest.main()
