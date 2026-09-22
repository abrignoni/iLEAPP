"""The HTML report holds back tables above the row limit and summarises oversized index tabs.

Every row used to go into the artifact's page, and the table script then read them all
back into memory. Measured 2026-09-19 in Chromium on a 16-column messages page: 100,000
rows were usable after 25.8 s with the browser at 1.7 GB, and at 150,000 the DataTables
call failed with "Maximum call stack size exceeded", left the loading spinner in place and
the browser at 9 GB. The index page copied the run log and the processed files list into
two tabs; a 43 MB list of 229,869 paths opened fast but clicking its tab blocked the page
for over a minute at 12 GB. These tests pin the notice written in place of a large table,
the complete TSV and LAVA output behind it, the index entry that lists it, and the
summarised tabs.
"""
import csv
import inspect
import os
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import types
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import artifact_report, ilapfuncs, lavafuncs, report  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

HEADERS = ('Timestamp', 'Value')


def _rows(count):
    return [(f'2026-09-19 00:00:{i % 60:02d}', f'value-{i}') for i in range(count)]


class TableRowLimitTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.report_folder = os.path.join(self.tmpdir, '_HTML', 'Category')
        os.makedirs(self.report_folder)
        self.saved_limit = artifact_report.HTML_TABLE_ROW_LIMIT
        artifact_report.set_html_row_limit(10)

    def tearDown(self):
        artifact_report.set_html_row_limit(self.saved_limit)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_page(self, rows, **kwargs):
        page = artifact_report.ArtifactHtmlReport('Test Table')
        page.start_artifact_report(self.report_folder, 'Test Table', 'a description')
        page.add_script()
        held_back = page.write_artifact_data_table(HEADERS, _rows(rows), 'a/b.db', **kwargs)
        page.end_artifact_report()
        with open(os.path.join(self.report_folder, 'Test Table.temphtml'), encoding='utf8') as fh:
            return held_back, fh.read()

    def test_a_table_over_the_limit_is_replaced_by_a_notice(self):
        held_back, html = self._write_page(11)
        self.assertTrue(held_back)
        self.assertIn('Total number of entries: 11', html)
        self.assertIn('This table has 11 rows, above the 10-row limit', html)
        self.assertIn('--html_row_limit 0', html)
        self.assertNotIn('<td>value-0</td>', html)
        self.assertNotIn('<table', html)

    def test_a_table_at_the_limit_is_written_in_full(self):
        held_back, html = self._write_page(10)
        self.assertFalse(held_back)
        self.assertEqual(html.count('<td>value-'), 10)

    def test_a_limit_of_zero_writes_every_table(self):
        artifact_report.set_html_row_limit(0)
        held_back, html = self._write_page(11)
        self.assertFalse(held_back)
        self.assertEqual(html.count('<td>value-'), 11)

    def test_the_notice_names_where_the_complete_rows_are(self):
        locations = [artifact_report.LAVA_DATABASE_LOCATION, artifact_report.tsv_export_location('Test Table')]
        _, html = self._write_page(11, full_data_locations=locations)
        self.assertIn('_lava_artifacts.db', html)
        self.assertIn('_TSV Exports/Test Table.tsv', html)

    def test_a_caller_that_names_no_locations_gets_the_general_notice(self):
        _, html = self._write_page(11)
        self.assertIn("the report's other outputs", html)

    def test_an_explicit_row_limit_overrides_the_module_setting(self):
        held_back, _ = self._write_page(11, row_limit=20)
        self.assertFalse(held_back)


class ArtifactProcessorHeldBackTests(unittest.TestCase):
    """A decorated artifact above the limit keeps its TSV and LAVA rows and is listed for the index."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        base = pathlib.Path(self.tmpdir)
        self.report_folder = base / '_HTML' / 'Category'
        self.report_folder.mkdir(parents=True)
        for folder in ('data', 'media', '_HTML/media'):
            (base / folder).mkdir(parents=True, exist_ok=True)
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        Context.set_output_params(types.SimpleNamespace(
            media_folder=str(base / 'media'), html_media_folder=str(base / '_HTML' / 'media'),
            data_folder=str(base / 'data')))
        self.saved_limit = artifact_report.HTML_TABLE_ROW_LIMIT
        artifact_report.set_html_row_limit(5)
        del ilapfuncs.html_tables_held_back[:]

    def tearDown(self):
        artifact_report.set_html_row_limit(self.saved_limit)
        del ilapfuncs.html_tables_held_back[:]
        if lavafuncs.lava_db is not None:
            try:
                lavafuncs.lava_db.close()
            except sqlite3.ProgrammingError:
                pass
            lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        Context.clear()
        Context.set_output_params(None)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run_artifact(self, rows):
        namespace = {
            '__name__': 'fake_big_table',
            '__artifacts_v2__': {'big_table': {
                'name': 'Big Table', 'category': 'Category', 'description': 'rows',
                'output_types': ['html', 'tsv', 'lava']}},
            '_rows': _rows, 'HEADERS': HEADERS,
        }
        exec(f'def big_table(context):\n    return HEADERS, _rows({rows}), "a/b.db"\n', namespace)  # pylint: disable=exec-used
        wrapped = ilapfuncs.artifact_processor(namespace['big_table'])
        seeker = types.SimpleNamespace(file_infos={})
        # The wrapper takes (files_found, report_folder, seeker, wrap_text) and, in the
        # cores that have one, a timezone offset; hand it as many as it declares.
        arguments = [[str(pathlib.Path(self.tmpdir) / 'data' / 'a' / 'b.db')], str(self.report_folder), seeker, False, 'UTC']
        declared = len(inspect.signature(wrapped, follow_wrapped=False).parameters)
        wrapped(*arguments[:declared])

    def test_an_artifact_over_the_limit_keeps_its_tsv_and_lava_rows(self):
        self._run_artifact(6)
        with open(self.report_folder / 'Big Table.temphtml', encoding='utf8') as fh:
            html = fh.read()
        self.assertIn('This table has 6 rows, above the 5-row limit', html)
        self.assertIn('_TSV Exports/Big Table.tsv', html)
        self.assertNotIn('<td>value-0</td>', html)
        with open(pathlib.Path(self.tmpdir) / '_TSV Exports' / 'Big Table.tsv', encoding='utf-8-sig') as fh:
            tsv_rows = list(csv.reader(fh, delimiter='\t'))
        self.assertEqual(len(tsv_rows), 7)  # header plus six rows
        tables = [r[0] for r in lavafuncs.lava_db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE '\\_%' ESCAPE '\\'")]
        self.assertEqual(len(tables), 1, tables)
        lava_rows = lavafuncs.lava_db.execute(f'SELECT COUNT(*) FROM "{tables[0]}"').fetchone()[0]
        self.assertEqual(lava_rows, 6)
        self.assertEqual(ilapfuncs.html_tables_held_back, [
            {'category': 'Category', 'artifact_name': 'Big Table', 'page': 'Big_Table.html', 'rows': 6}])

    def test_an_artifact_under_the_limit_is_not_listed(self):
        self._run_artifact(5)
        with open(self.report_folder / 'Big Table.temphtml', encoding='utf8') as fh:
            html = fh.read()
        self.assertEqual(html.count('<td>value-'), 5)
        self.assertEqual(ilapfuncs.html_tables_held_back, [])


class IndexTabTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.logs = pathlib.Path(self.tmpdir) / '_HTML' / '_Script_Logs'
        self.logs.mkdir(parents=True)
        (self.logs / 'DeviceInfo.html').write_text('device info<br>', encoding='utf8')
        self.saved_limit = report.INDEX_TAB_EMBED_LIMIT
        report.INDEX_TAB_EMBED_LIMIT = 2000
        del ilapfuncs.html_tables_held_back[:]

    def tearDown(self):
        report.INDEX_TAB_EMBED_LIMIT = self.saved_limit
        del ilapfuncs.html_tables_held_back[:]
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _index(self, run_log, files_log):
        (self.logs / 'Screen_Output.html').write_text(run_log, encoding='utf8')
        (self.logs / 'ProcessedFilesLog.html').write_text(files_log, encoding='utf8')
        # Cores without a LAVA-only tab take one parameter fewer.
        extra = {'lava_only': False} if 'lava_only' in inspect.signature(report.create_index_html).parameters else {}
        report.create_index_html(self.tmpdir, 1, '00:00:01', 'zip', '/cases/x.zip',
                                 '<a class="nav-link" href="index.html">Report Home</a>', {}, '', **extra)
        with open(pathlib.Path(self.tmpdir) / '_HTML' / 'index.html', encoding='utf8') as fh:
            return fh.read()

    @staticmethod
    def _files_log(path_count):
        paths = ''.join(f'<ul><li>private/var/mobile/file-{i:05d}.jpg</li></ul>' for i in range(path_count))
        return ('Extraction/Path selected: /cases/x.zip<br><br>'
                '<b>For firstArtifact artifact</b>'
                f'<ul><li>{path_count} files for regex <i>*/mobile/*.jpg</i> located at:{paths}</li></ul>'
                '<ul><li>No file found for regex <i>*/missing/*</i></li></ul>'
                '<b>For secondArtifact artifact</b>'
                '<ul><li>1 file for regex <i>*/one.db</i> located at:<ul><li>private/one.db</li></ul></li></ul>')

    def test_small_logs_are_copied_into_their_tabs(self):
        index = self._index('line one<br>\nline two<br>\n', self._files_log(3))
        self.assertIn('line two<br>', index)
        self.assertIn('file-00002.jpg', index)
        self.assertNotIn('_Script_Logs/ProcessedFilesLog.html', index)

    def test_a_large_processed_files_list_is_summarised_per_pattern(self):
        index = self._index('short<br>\n', self._files_log(500))
        self.assertIn('href="_Script_Logs/ProcessedFilesLog.html"', index)
        self.assertIn('500 files for regex <i>*/mobile/*.jpg</i> located at:', index)
        self.assertIn('file-00000.jpg', index)
        self.assertIn(f'file-{report.INDEX_TAB_PATHS_PER_PATTERN - 1:05d}.jpg', index)
        self.assertNotIn(f'file-{report.INDEX_TAB_PATHS_PER_PATTERN:05d}.jpg', index)
        self.assertIn(f'{500 - report.INDEX_TAB_PATHS_PER_PATTERN} more in the full list', index)
        self.assertIn('No file found for regex <i>*/missing/*</i>', index)
        self.assertIn('<b>For secondArtifact artifact</b>', index)
        self.assertIn('private/one.db', index)

    def test_a_large_run_log_keeps_both_ends(self):
        lines = ''.join(f'log line {i}<br>\n' for i in range(1000))
        index = self._index(lines, self._files_log(1))
        self.assertIn('href="_Script_Logs/Screen_Output.html"', index)
        self.assertIn('log line 0<br>', index)
        self.assertIn('log line 999<br>', index)
        self.assertNotIn('log line 500<br>', index)
        self.assertIn('lines not shown here', index)

    def test_held_back_tables_are_listed_on_the_details_tab(self):
        ilapfuncs.html_tables_held_back.append(
            {'category': 'Chats', 'artifact_name': 'Big Table', 'page': 'Big_Table.html', 'rows': 123456})
        index = self._index('short<br>\n', self._files_log(1))
        self.assertIn('<a href="Big_Table.html">Big Table</a> (Chats): 123,456 rows', index)
        self.assertIn(f'more than {artifact_report.HTML_TABLE_ROW_LIMIT:,} rows', index)


if __name__ == '__main__':
    unittest.main()
