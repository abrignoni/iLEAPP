"""chromeShortcuts reads omni_box_shortcuts and names its enums (SYNTHETIC databases)."""
import datetime
import os
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from scripts.artifacts import chromeShortcuts as module

COLUMNS = ('id TEXT, text TEXT, fill_into_edit TEXT, url TEXT, document_type INTEGER, contents TEXT, '
           'contents_class TEXT, description TEXT, description_class TEXT, transition INTEGER, type INTEGER, '
           'keyword TEXT, last_access_time INTEGER, number_of_hits INTEGER')
TIME = 13_400_000_000_000_000


def make_store(root, relative, rows, version=2):
    path = os.path.join(root, relative)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    db = sqlite3.connect(path)
    db.execute(f'CREATE TABLE omni_box_shortcuts ({COLUMNS})')
    if version is not None:
        db.execute('CREATE TABLE meta (key TEXT, value TEXT)')
        db.execute("INSERT INTO meta VALUES ('version', ?)", (str(version),))
    for number, (match_type, transition) in enumerate(rows):
        db.execute('INSERT INTO omni_box_shortcuts VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, 1)',
                   (str(number), 'inp', 'input text', 'https://example.test/', 'input text', '0,0', '', '',
                    transition, match_type, 'example.test', TIME + number))
    db.commit()
    db.close()
    return path


def run(paths):
    context = SimpleNamespace(get_files_found=lambda: paths, get_relative_path=os.path.basename)
    with mock.patch.object(module, 'get_browser_name', return_value='Chrome'):
        return module.chromeShortcuts.__wrapped__(context)


class ShortcutsTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = temp.name
        self.chrome = 'Library/Application Support/Google/Chrome/Default/Shortcuts'

    def test_row_values_and_time(self):
        path = make_store(self.root, self.chrome, [(7, 5)])
        headers, rows, source = run([path])
        self.assertEqual(len(headers), len(rows[0]))
        expected = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=TIME)
        self.assertEqual(rows[0][0], expected)
        self.assertEqual(rows[0][1:3], ('inp', 'input text'))
        self.assertEqual(rows[0][6:8], ('7 (SEARCH_HISTORY)', '5 (GENERATED)'))
        self.assertEqual(rows[0][10], 'Default')
        self.assertEqual(source, path)

    def test_qualifier_bits_in_a_negative_stored_value(self):
        path = make_store(self.root, self.chrome, [(1, -0x7FFFFFFF)])
        self.assertEqual(run([path])[1][0][7], '1 (TYPED), qualifiers 0x80000000')

    def test_pre_migration_types_only_without_a_version(self):
        old = make_store(self.root, 'old/Chrome/Default/Shortcuts', [(9, 0)], version=None)
        new = make_store(self.root, 'new/Chrome/Default/Shortcuts', [(9, 0)])
        self.assertEqual(run([old])[1][0][6], '9 (SEARCH_OTHER_ENGINE, pre-migration numbering)')
        self.assertEqual(run([new])[1][0][6], '9 (SEARCH_SUGGEST_ENTITY)')

    def test_unknown_enum_keeps_the_number(self):
        path = make_store(self.root, self.chrome, [(99, 77)])
        self.assertEqual(run([path])[1][0][6:8], ('99', '77'))

    def test_sidecar_decoy_and_duplicate_are_not_read(self):
        path = make_store(self.root, self.chrome, [(7, 5)])
        sidecar = path + '-wal'
        open(sidecar, 'wb').close()
        decoy = make_store(self.root, 'Library/Application Support/Google/Chrome/Default/Nested/Shortcuts', [(7, 5)])
        self.assertEqual(len(run([path, path, sidecar, decoy])[1]), 1)

    def test_a_bad_store_does_not_lose_the_other(self):
        good = make_store(self.root, self.chrome, [(7, 5)])
        bad = os.path.join(self.root, 'Library/Application Support/Microsoft/Edge/Default/Shortcuts')
        os.makedirs(os.path.dirname(bad))
        sqlite3.connect(bad).close()
        with mock.patch.object(module, 'logfunc') as log:
            _, rows, source = run([bad, good])
        self.assertEqual(len(rows), 1)
        self.assertEqual(source, good)
        log.assert_called_once()


if __name__ == '__main__':
    unittest.main()
