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

A third audit (2026-09-06) scanned real report output and found 122 leaking cells the
checker had passed, through `unique_files()`, `or`, and paths handed back by module
helpers. Those shapes, and the correct forms that must stay silent, are pinned in
ThirdAuditShapes.

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

    def test_a_formatter_passes_taint_through(self):
        """torrentResumeinfo: textwrap.fill(file_found, width=25) published the path."""
        found = findings_for("""
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    data_list.append((textwrap.fill(file_found, width=25), 'b'))
                return (), data_list, ''
        """)
        self.assertEqual(len(found), 1, 'a formatter must not launder a path')

    def test_strip_does_not_reduce_a_path(self):
        """strip() hands back the whole path, so it cannot clear the taint."""
        found = findings_for("""
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    data_list.append((file_found.strip(), 'b'))
                return (), data_list, ''
        """)
        self.assertEqual(len(found), 1, 'strip() must not clear the taint')

    def test_str_format_carries_the_path_into_the_result(self):
        """A constant receiver means the path arrives as an argument, not a receiver."""
        found = findings_for("""
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    data_list.append(('{}'.format(file_found), 'b'))
                return (), data_list, ''
        """)
        self.assertEqual(len(found), 1, 'str.format must carry the path through')

    def test_stacked_launderers_still_report(self):
        """torrentinfo carried both at once: textwrap.fill(file_found.strip(), ...)."""
        found = findings_for("""
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    data_list.append((textwrap.fill(file_found.strip(), width=25), 'b'))
                return (), data_list, ''
        """)
        self.assertEqual(len(found), 1, 'stacked launderers must not hide a path')


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

    def test_a_split_component_is_still_accepted(self):
        """split() genuinely returns a piece of the string, so it stays silent."""
        self.assertEqual(findings_for("""
            @artifact_processor
            def demo(context):
                data_list = []
                for file_found in context.get_files_found():
                    data_list.append((file_found.split('/')[-1], 'b'))
                return (), data_list, ''
        """), [])

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


class ThirdAuditShapes(unittest.TestCase):
    """Shapes a 2026-09-06 scan of real report output found leaking while this check
    reported clean: 122 cells in four ALEAPP modules. Each positive here is one of those
    shapes or a sibling of it, and each negative is the correct form that must stay
    silent, because a checker that flags correct code gets disabled."""

    def _cols(self, source):
        return sorted((f, col) for _m, f, _l, _k, _e, col in findings_for(source))

    def test_unique_files_is_a_taint_source(self):
        """torThumbs and xiaohongshu leaked through the repo's own dedupe helper."""
        self.assertEqual(self._cols('''
            @artifact_processor
            def leak(context):
                data_list = []
                for file_found in unique_files(context):
                    data_list.append(('a', file_found))
                return (), data_list, ''
        '''), [('leak', 1)])

    def test_unique_files_reduced_is_accepted(self):
        self.assertEqual(findings_for('''
            @artifact_processor
            def fine(context):
                data_list = []
                for file_found in unique_files(context):
                    data_list.append(('a', context.get_relative_path(file_found)))
                return (), data_list, ''
        '''), [])

    def test_or_and_and_pass_the_path_through(self):
        """xiaohongshu's account artifact leaked through `source = source or file_found`."""
        self.assertEqual(self._cols('''
            @artifact_processor
            def leak(files_found, seeker, report_folder):
                data_list = []
                source = ''
                for file_found in files_found:
                    source = source or file_found
                    both = file_found and file_found
                    data_list.append((source, both))
                return (), data_list, source
        '''), [('leak', 0), ('leak', 1)])

    def test_a_conditional_expression_passes_the_path_through(self):
        self.assertEqual(self._cols('''
            @artifact_processor
            def leak(files_found, seeker, report_folder):
                data_list = []
                for file_found in files_found:
                    data_list.append(('a', file_found if file_found else ''))
                return (), data_list, ''
        '''), [('leak', 1)])

    def test_tuple_unpacking_binds_only_the_path_position(self):
        """`a, b = file_found, 1` taints a and not b, in the loop and in the assignment."""
        self.assertEqual(self._cols('''
            @artifact_processor
            def leak(files_found, seeker, report_folder):
                data_list = []
                pairs = [(f, 1) for f in files_found]
                for path, num in pairs:
                    a, b = path, num
                    data_list.append((num, b, a, path))
                return (), data_list, ''
        '''), [('leak', 2), ('leak', 3)])

    def test_dict_store_walrus_and_augmented_assignment_propagate(self):
        self.assertEqual(self._cols('''
            @artifact_processor
            def leak(files_found, seeker, report_folder):
                data_list = []
                store = {}
                acc = ''
                for file_found in files_found:
                    store['p'] = file_found
                    acc += file_found
                    if (p := file_found):
                        data_list.append((store['p'], acc, p))
                return (), data_list, ''
        '''), [('leak', 0), ('leak', 1), ('leak', 2)])

    def test_a_helper_returning_paths_is_a_source(self):
        self.assertEqual(self._cols('''
            def _paths(context):
                return [str(p) for p in unique_files(context)]

            @artifact_processor
            def leak(context):
                data_list = []
                for p in _paths(context):
                    data_list.append(('a', p))
                return (), data_list, ''
        '''), [('leak', 1)])

    def test_a_helper_returning_records_is_tracked_by_position(self):
        """The path field of a record is tainted; its other fields are not."""
        self.assertEqual(self._cols('''
            def _stores(context):
                out = []
                for file_found in unique_files(context):
                    out.append((file_found, 'parsed', 3))
                return out

            @artifact_processor
            def leak(context):
                data_list = []
                for path, parsed, count in _stores(context):
                    data_list.append((parsed, count, path))
                return (), data_list, ''

            @artifact_processor
            def fine(context):
                data_list = []
                for path, parsed, count in _stores(context):
                    data_list.append((parsed, count, context.get_relative_path(path)))
                return (), data_list, ''
        '''), [('leak', 2)])

    def test_a_helper_returning_reduced_paths_is_not_a_source(self):
        """A comprehension is judged by its element, not by what it iterates."""
        self.assertEqual(findings_for('''
            def _reduced(context):
                return [context.get_relative_path(p) for p in unique_files(context)]

            @artifact_processor
            def fine(context):
                data_list = []
                for p in _reduced(context):
                    data_list.append(('a', p))
                return (), data_list, ''
        '''), [])

    def test_a_database_row_read_from_a_store_is_not_a_path(self):
        """Fields unpacked from a record whose path position is unknown stay silent.
        weChat, hldPrivacySafe and keychain rows would otherwise all be reported."""
        self.assertEqual(findings_for('''
            def _rows(context):
                out = []
                for file_found in unique_files(context):
                    for row in query(file_found):
                        out.append((row, file_found))
                return out

            @artifact_processor
            def fine(context):
                data_list = []
                for row, path in _rows(context):
                    name, value, count = row
                    data_list.append((name or '', value if value else '', count,
                                      context.get_relative_path(path)))
                return (), data_list, ''
        '''), [])

    def test_replacing_the_data_folder_out_of_a_path_reduces_it(self):
        """get_relative_path written by hand, as FacebookMessenger once did."""
        self.assertEqual(findings_for('''
            @artifact_processor
            def fine(files_found, seeker, report_folder):
                data_list = []
                for file_found in files_found:
                    data_list.append(('a', file_found.replace(seeker.data_folder, '')))
                return (), data_list, ''
        '''), [])

    def test_a_slice_of_a_path_is_a_piece_of_it(self):
        self.assertEqual(findings_for('''
            def _user(file_found):
                start = file_found.find('/user/') + 6
                return file_found[start:start + 3]

            @artifact_processor
            def fine(files_found, seeker, report_folder):
                data_list = []
                for file_found in files_found:
                    data_list.append((_user(file_found), 'a'))
                return (), data_list, ''
        '''), [])

    def test_a_working_list_that_never_reaches_the_report_is_not_a_row_list(self):
        """dmss collects (name, name, path) records under a *_data_list name, then
        builds the real rows from them with the path reduced."""
        self.assertEqual(findings_for('''
            @artifact_processor
            def fine(files_found, seeker, report_folder, context):
                media_data_list = []
                for file_found in files_found:
                    record = ('n', 'n', file_found)
                    media_data_list.append(record)
                data_list = []
                for item in media_data_list:
                    data_list.append((item[0], context.get_relative_path(item[2])))
                return (), data_list, ''
        '''), [])

    def test_a_record_appended_by_name_reports_its_path_position(self):
        self.assertEqual(self._cols('''
            @artifact_processor
            def leak(files_found, seeker, report_folder):
                data_list = []
                for file_found in files_found:
                    record = ('n', file_found)
                    data_list.append(record)
                return (), data_list, ''
        '''), [('leak', 1)])


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
