"""A module's own HTML rows survive a media column (#1202).

A module can return (plain rows, HTML rows) so the HTML report shows formatting, such as
line breaks between phone numbers, that the text outputs should not carry. When the
artifact also had a media column, the wrapper rebuilt the HTML rows from the plain ones, so
the module's formatting was lost and the columns it lists in html_columns were written
unescaped from the plain values instead. These tests run a probe artifact through the
wrapper and read back the HTML and TSV files it writes.
"""
import pathlib
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.ilapfuncs import (  # pylint: disable=wrong-import-position
    artifact_processor, check_in_embedded_media, OutputParameters)

PNG = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR' + b'\x00' * 48
HEADERS = ('Numbers', ('Picture', 'media'), 'Note')

__artifacts_v2__ = {
    'html_rows_with_media': {
        'name': 'HTML Rows With Media', 'category': 'Probe Category', 'description': 'probe',
        'author': '@unit', 'creation_date': '2026-10-31', 'last_update_date': '2026-10-31',
        'notes': '', 'paths': ('*/nothing',), 'output_types': ['html', 'tsv', 'lava'],
        'html_columns': ['Numbers'],
    },
}


@artifact_processor
def html_rows_with_media(context):
    source = context.get_files_found()[0]
    ref = check_in_embedded_media(source, PNG, 'picture.png')
    plain = [('+1 555 0100, +1 555 0199', ref, '<b>as stored</b>')]
    html = [('+1 555 0100<br>+1 555 0199', ref, '<b>as stored</b>')]
    return HEADERS, (plain, html), source


class MediaColumnKeepsModuleHtmlTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Context.clear()
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        self._saved_log_paths = {name: getattr(OutputParameters, name) for name in vars(OutputParameters)
                                 if name.startswith('screen_output_file_path')}
        self.output_params = OutputParameters(self.tmpdir)
        Context.set_output_params(self.output_params)
        patcher = mock.patch('scripts.ilapfuncs.logfunc')
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        for name, value in self._saved_log_paths.items():
            setattr(OutputParameters, name, value)
        lavafuncs.lava_db.close()
        lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        lavafuncs.lava_db_path = None
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def run_probe(self):
        report_folder = pathlib.Path(self.output_params.output_folder_base, '_HTML', 'Probe Category')
        report_folder.mkdir(parents=True, exist_ok=True)
        source = pathlib.Path(self.output_params.data_folder, 'probe.db')
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(b'probe')
        seeker = types.SimpleNamespace(file_infos={}, directory=self.tmpdir)
        html_rows_with_media([str(source)], str(report_folder), seeker, True, 'UTC')  # pylint: disable=too-many-function-args
        html_files = list(pathlib.Path(self.tmpdir).rglob("*.temphtml"))
        tsv_files = list(pathlib.Path(self.tmpdir).rglob('*.tsv'))
        self.assertEqual((len(html_files), len(tsv_files)), (1, 1))
        return html_files[0].read_text(encoding='utf-8'), tsv_files[0].read_text(encoding='utf-8')

    def test_the_html_report_is_built_from_the_module_s_html_rows(self):
        html, _ = self.run_probe()

        self.assertIn('+1 555 0100<br>+1 555 0199', html)
        self.assertNotIn('+1 555 0100, +1 555 0199', html)
        self.assertIn('<img', html)

    def test_a_column_not_listed_as_html_is_still_escaped(self):
        html, _ = self.run_probe()

        self.assertIn('&lt;b&gt;as stored&lt;/b&gt;', html)
        self.assertNotIn('<b>as stored</b>', html)

    def test_the_text_outputs_keep_the_plain_rows(self):
        _, tsv = self.run_probe()

        self.assertIn('+1 555 0100, +1 555 0199', tsv)
        self.assertNotIn('<br>', tsv)
        self.assertIn('media/', tsv)


if __name__ == '__main__':
    unittest.main()
