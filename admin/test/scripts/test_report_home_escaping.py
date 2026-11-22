"""Values read from the evidence are escaped on the report home page tabs."""
import copy
import os
import pathlib
import shutil
import tempfile
import unittest

from scripts import ilapfuncs

PAYLOAD = '<svg onload=document.title=1>'
MAIN_SCRIPT = pathlib.Path(__file__).resolve().parents[3] / 'ileapp.py'


class ReportHomeEscapingTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.devinfo = pathlib.Path(self.tmp) / 'DeviceInfo.html'
        saved_path = getattr(ilapfuncs.OutputParameters, 'screen_output_file_path_devinfo', None)
        saved_nl = getattr(ilapfuncs.OutputParameters, 'nl', None)
        saved = copy.deepcopy(ilapfuncs.identifiers)
        def restore():
            ilapfuncs.OutputParameters.screen_output_file_path_devinfo = saved_path
            ilapfuncs.OutputParameters.nl = saved_nl
            ilapfuncs.identifiers.clear()
            ilapfuncs.identifiers.update(saved)
        self.addCleanup(restore)
        ilapfuncs.OutputParameters.screen_output_file_path_devinfo = str(self.devinfo)
        ilapfuncs.OutputParameters.nl = os.linesep
        ilapfuncs.identifiers.clear()

    def test_every_device_info_field_is_escaped(self):
        for _ in range(2):  # the second call turns the entry into the list form
            ilapfuncs.device_info(PAYLOAD, PAYLOAD, PAYLOAD, 'x" onmouseover="alert(1)')
        ilapfuncs.device_info(PAYLOAD, 'single', PAYLOAD, 'x" onmouseover="alert(1)')
        ilapfuncs.write_device_info()
        text = self.devinfo.read_text(encoding='utf8')
        self.assertNotIn('<svg', text)
        self.assertNotIn('" onmouseover', text)
        self.assertIn('&lt;svg', text)

    def test_ordinary_values_are_written_unchanged(self):
        ilapfuncs.device_info('Device', 'Name', "Pat's phone", 'data/file.db')
        ilapfuncs.device_info('Device', 'Count', 7, 'data/file.db')
        ilapfuncs.write_device_info()
        text = self.devinfo.read_text(encoding='utf8')
        self.assertIn("<li><b>Name:</b> Pat's phone <span title=\"data/file.db\"", text)
        self.assertIn('<li><b>Count:</b> 7 <span', text)

    def test_stored_values_stay_raw(self):
        ilapfuncs.device_info('Device', 'Name', PAYLOAD, 'data/file.db')
        ilapfuncs.write_device_info()
        self.assertEqual(ilapfuncs.identifiers['Device']['Name']['value'], PAYLOAD)

    def test_html_text_keeps_quotes(self):
        self.assertEqual(ilapfuncs._html_text('a "b" \'c\' <d> & e'),  # pylint: disable=protected-access
                         'a "b" \'c\' &lt;d&gt; &amp; e')

    def test_processed_files_log_escapes_its_values(self):
        source = MAIN_SCRIPT.read_text(encoding='utf8')
        for expected in ('{esc(input_path)}', '{esc(plugin.name)}', '{esc(artifact_search_regex)}',
                         '{esc(Context.get_relative_path(display_path))}'):
            self.assertIn(expected, source)


if __name__ == '__main__':
    unittest.main()
