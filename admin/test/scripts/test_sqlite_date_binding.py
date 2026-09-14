"""Guard the report writers against sqlite3's deprecated default date and datetime adapters.

The LAVA table writer, the LAVA media item writer and kmlgen receive date and datetime objects.
sqlite3 converts those to text through default adapters that are deprecated as of Python 3.12
and warn on every value
(https://docs.python.org/3/library/sqlite3.html#default-adapters-and-converters-deprecated).
The writers now bind the text themselves through lavafuncs.bind_dates_as_text, which returns
str(value): exactly what the adapters returned, isoformat(" ") for a datetime and isoformat()
for a date. These tests pin both halves, no adapter warning and the same stored text.
"""
import datetime
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import types
import unittest
import warnings

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import ilapfuncs  # pylint: disable=wrong-import-position
from scripts import lavafuncs  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

UTC = datetime.timezone.utc
VALUES = [
    datetime.datetime(2022, 3, 4, 12, 34, 56, tzinfo=UTC),
    datetime.datetime(2022, 3, 4, 12, 34, 56, 123456, tzinfo=UTC),
    datetime.datetime(2022, 3, 4, 12, 34, 56),
    datetime.datetime(2022, 3, 4, 12, 34, 56, tzinfo=datetime.timezone(datetime.timedelta(hours=-4))),
    datetime.date(2022, 3, 4),
]
# Written out by hand, so the expectation does not come from the code under test.
EXPECTED_TEXT = [
    '2022-03-04 12:34:56+00:00',
    '2022-03-04 12:34:56.123456+00:00',
    '2022-03-04 12:34:56',
    '2022-03-04 12:34:56-04:00',
    '2022-03-04',
]
EXPECTED_EPOCH = 1646397296  # 2022-03-04 12:34:56 UTC


def adapter_warnings(caught):
    return [w for w in caught if issubclass(w.category, DeprecationWarning) and 'adapter' in str(w.message)]


class TestSqliteDateBinding(unittest.TestCase):
    """Dates and datetimes reach SQLite as text without sqlite3's default adapters."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')

    def tearDown(self):
        if lavafuncs.lava_db is not None:
            lavafuncs.lava_db.close()
            lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_default_adapter_wrote_the_expected_text(self):
        """Control: the text sqlite3's own default adapters produce for VALUES."""
        db = sqlite3.connect(':memory:')
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            adapted = [db.execute('SELECT ?', (value,)).fetchone()[0] for value in VALUES]
        db.close()
        self.assertEqual(adapted, EXPECTED_TEXT)
        if sys.version_info >= (3, 12):
            self.assertEqual(len(adapter_warnings(caught)), len(VALUES))

    def test_bind_dates_as_text(self):
        bind = lavafuncs.bind_dates_as_text
        self.assertEqual([bind(value) for value in VALUES], EXPECTED_TEXT)
        for other in (None, '', 'N/A', 0, 1.5, b'x', '2022-03-04 12:34:56'):
            self.assertIs(bind(other), other)

    def test_lava_insert_binds_untyped_dates_as_text(self):
        headers = ['Label', 'Moment', ('Stamp', 'datetime')]
        table_name, column_map, object_columns = lavafuncs.lava_create_sqlite_table('date_binding', headers)
        rows = [(f'row {index}', value, VALUES[0]) for index, value in enumerate(VALUES)]
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            lavafuncs.lava_insert_sqlite_data(table_name, rows, object_columns, headers, column_map)
        self.assertEqual(adapter_warnings(caught), [])
        stored = lavafuncs.lava_db.execute(
            f'SELECT moment, typeof(moment), stamp FROM "{table_name}" ORDER BY rowid').fetchall()
        self.assertEqual([row[0] for row in stored], EXPECTED_TEXT)
        self.assertEqual({row[1] for row in stored}, {'text'})
        self.assertEqual({row[2] for row in stored}, {EXPECTED_EPOCH})

    def test_media_item_binds_dates_as_text(self):
        items = [types.SimpleNamespace(id=f'media-{index}', source_path='source', extraction_path='extracted',
                                       mimetype='image/jpeg', metadata='{}', created_at=value, updated_at=value,
                                       is_embedded=0)
                 for index, value in enumerate(VALUES)]
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            for item in items:
                lavafuncs.lava_insert_sqlite_media_item(item)
        self.assertEqual(adapter_warnings(caught), [])
        stored = lavafuncs.lava_db.execute(
            'SELECT created_at, typeof(created_at), updated_at FROM _lava_media_items ORDER BY rowid').fetchall()
        self.assertEqual([row[0] for row in stored], EXPECTED_TEXT)
        self.assertEqual({row[1] for row in stored}, {'text'})
        self.assertEqual([row[2] for row in stored], EXPECTED_TEXT)

    def test_kmlgen_binds_placemark_times_as_text(self):
        report_folder = pathlib.Path(self.tmpdir, 'category', 'artifact')
        report_folder.mkdir(parents=True)
        headers = ['Timestamp', 'Latitude', 'Longitude']
        rows = [(value, 1.5, 2.5) for value in VALUES]
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            ilapfuncs.kmlgen(str(report_folder), 'Date Binding', rows, headers)
        self.assertEqual(adapter_warnings(caught), [])
        db = sqlite3.connect(pathlib.Path(self.tmpdir, '_KML Exports', '_latlong.db'))
        stored = [row[0] for row in db.execute('SELECT timestamp FROM data ORDER BY rowid')]
        db.close()
        self.assertEqual(stored, EXPECTED_TEXT)


if __name__ == '__main__':
    unittest.main()
