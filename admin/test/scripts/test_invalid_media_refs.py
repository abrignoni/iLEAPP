"""Media column values that are not media references are logged and left blank (issue #1237).

A media column must hold IDs returned by check_in_media or check_in_embedded_media. A
module that leaves something else there, such as a file name or an ID from the source
database, used to crash get_data_list_with_media. That crash was fixed by skipping the
value in the HTML and TSV output, but the value still went into LAVA unchanged and
nothing was logged. These tests pin that the value is logged, that LAVA stores NULL in its
place, and that this holds for list-returning modules and for streamed rows.
"""
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.ilapfuncs import artifact_processor, OutputParameters  # pylint: disable=wrong-import-position

VALID_REF = 'a' * 40
OTHER_VALID_REF = 'b' * 40
HEADERS = ['Label', ('Media', 'media')]

__artifacts_v2__ = {
    'list_module_with_invalid_media': {
        'name': 'Invalid Media List', 'category': 'Probe Category', 'description': 'probe',
        'author': '@unit', 'creation_date': '2026-10-15', 'last_update_date': '2026-10-15',
        'notes': '', 'paths': ('*/nothing',), 'output_types': ['lava', 'tsv'],
    },
    'streaming_module_with_invalid_media': {
        'name': 'Invalid Media Streamed', 'category': 'Probe Category', 'description': 'probe',
        'author': '@unit', 'creation_date': '2026-10-15', 'last_update_date': '2026-10-15',
        'notes': '', 'paths': ('*/nothing',), 'output_types': 'lava_only',
    },
}

MODULE_ROWS = [
    ('valid', VALID_REF),
    ('file name', 'IMG_0001.HEIC'),
    ('mixed list', [VALID_REF, 'not-a-ref']),
    ('empty', ''),
]


@artifact_processor
def list_module_with_invalid_media(context):  # pylint: disable=unused-argument
    return HEADERS, list(MODULE_ROWS), 'probe.db'


@artifact_processor
def streaming_module_with_invalid_media(context):
    result = context.create_artifact_result(headers=HEADERS, source_path='probe.db')
    for row in MODULE_ROWS:
        result.add_row(row)
    return result


class InvalidMediaRefTestCase(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Context.clear()
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        for ref in (VALID_REF, OTHER_VALID_REF):
            lavafuncs.lava_db.execute(
                'INSERT INTO _lava_media_references (id, media_item_id, module_name, artifact_name, name) '
                'VALUES (?, NULL, ?, ?, ?)', (ref, 'unit_module', 'Unit Artifact', ''))
        self._saved_log_paths = {name: getattr(OutputParameters, name) for name in vars(OutputParameters)
                                 if name.startswith('screen_output_file_path')}
        Context.set_output_params(OutputParameters(self.tmpdir))
        patcher = mock.patch('scripts.ilapfuncs.logfunc')
        self.logfunc = patcher.start()
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

    def media_log_lines(self):
        return [c.args[0] for c in self.logfunc.call_args_list if 'media column' in c.args[0]]

    def stored_media(self, artifact_name):
        entry = next(a for a in lavafuncs.lava_data['artifacts']['Probe Category'] if a['name'] == artifact_name)
        table = lavafuncs.quote_sql_name(entry['tablename'])
        # lava_get_full_media_info leaves sqlite3.Row as the connection's row factory
        return [tuple(row) for row in
                lavafuncs.lava_db.execute(f'SELECT label, media FROM {table} ORDER BY rowid')]


class TestBlankInvalidMediaRefs(InvalidMediaRefTestCase):

    def check(self, rows):
        return list(lavafuncs.lava_blank_invalid_media_refs(rows, [1], 'Unit Artifact'))

    def test_a_valid_reference_row_is_returned_unchanged(self):
        row = ('valid', VALID_REF)
        self.assertIs(self.check([row])[0], row)
        self.assertEqual(self.media_log_lines(), [])

    def test_a_value_that_is_not_a_reference_becomes_none_and_is_logged(self):
        self.assertEqual(self.check([('bad', 'IMG_0001.HEIC')]), [('bad', None)])
        self.assertEqual(self.media_log_lines(), [
            "Unit Artifact: media column value 'IMG_0001.HEIC' is not a reference from check_in_media; left blank"])

    def test_a_list_keeps_only_the_references_that_exist(self):
        self.assertEqual(self.check([('list', [VALID_REF, 'nope', OTHER_VALID_REF])]),
                         [('list', [VALID_REF, OTHER_VALID_REF])])

    def test_a_list_with_no_reference_becomes_none(self):
        self.assertEqual(self.check([('list', ['nope', 'nada'])]), [('list', None)])

    def test_values_that_are_not_text_are_not_references(self):
        self.assertEqual(self.check([('int', 42), ('bytes', b'\x00')]), [('int', None), ('bytes', None)])

    def test_empty_values_are_left_alone(self):
        rows = [('none', None), ('empty', ''), ('empty list', [])]
        self.assertEqual(self.check(rows), rows)
        self.assertEqual(self.media_log_lines(), [])

    def test_each_value_is_logged_once_and_the_log_is_capped(self):
        self.check([('bad', 'same')] * 3)
        self.assertEqual(len(self.media_log_lines()), 1)
        self.check([('bad', f'value {n}') for n in range(10)])
        lines = self.media_log_lines()
        self.assertEqual(len(lines), lavafuncs._INVALID_MEDIA_REF_LOG_LIMIT + 1)  # pylint: disable=protected-access
        self.assertIn('not logging the rest', lines[-1])

    def test_a_long_value_is_shortened_in_the_log(self):
        self.check([('bad', 'x' * 500)])
        self.assertLess(len(self.media_log_lines()[0]), 200)


class TestArtifactOutputs(InvalidMediaRefTestCase):

    def test_a_list_module_stores_null_in_lava_and_blanks_the_tsv(self):
        # tsv() writes to '_TSV Exports' two folders above the report folder
        report_folder = pathlib.Path(self.tmpdir, 'Probe Category', 'Invalid Media List')
        report_folder.mkdir(parents=True)
        _, data_list, _ = list_module_with_invalid_media(  # pylint: disable=too-many-function-args
            [], str(report_folder), None, True, 'UTC')
        self.assertEqual(self.stored_media('Invalid Media List'), [
            ('valid', VALID_REF), ('file name', None), ('mixed list', f'["{VALID_REF}"]'), ('empty', '')])
        self.assertEqual(data_list[1], ('file name', None))
        tsv_files = list(pathlib.Path(self.tmpdir).rglob('*.tsv'))
        self.assertEqual(len(tsv_files), 1)
        tsv_text = tsv_files[0].read_text(encoding='utf-8')
        self.assertNotIn('IMG_0001.HEIC', tsv_text)
        self.assertNotIn('not-a-ref', tsv_text)
        self.assertEqual(len(self.media_log_lines()), 2)
        self.assertTrue(all(line.startswith('Invalid Media List: ') for line in self.media_log_lines()))

    def test_streamed_rows_store_null_in_lava(self):
        streaming_module_with_invalid_media(  # pylint: disable=too-many-function-args
            [], self.tmpdir, None, True, 'UTC')
        self.assertEqual(self.stored_media('Invalid Media Streamed'), [
            ('valid', VALID_REF), ('file name', None), ('mixed list', f'["{VALID_REF}"]'), ('empty', '')])
        self.assertEqual(len(self.media_log_lines()), 2)


if __name__ == '__main__':
    unittest.main()
