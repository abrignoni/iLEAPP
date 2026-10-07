"""Actual plist and SQLite cases for the retained Sheets tab comparison."""
import json
from pathlib import Path
import plistlib
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest

from scripts.artifacts.googleSheets import google_sheets_tabs


class TestGoogleSheetsTabs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def prefs(self, container, settings, keyed_null=False):
        path = self.root / container / 'Library/Preferences/com.google.Sheets.plist'
        path.parent.mkdir(parents=True, exist_ok=True)
        if keyed_null:
            archive = {'$objects': ['$null', 'kActiveSheetId',
                                   {'NS.keys': [plistlib.UID(1)],
                                    'NS.objects': [plistlib.UID(0)]}],
                       '$top': {'root': plistlib.UID(2)}}
        else:
            archive = settings
        blob = plistlib.dumps(archive, fmt=getattr(plistlib, 'FMT_BINARY'))
        path.write_bytes(plistlib.dumps({'settingsForSheet:doc': blob}))
        return str(path)

    def database(self, container, declarations):
        path = self.root / container / 'Documents/account/localStore/documents/doc/doc.db'
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as db:
            db.executescript('CREATE TABLE document_properties(record_id,name,type,value);'
                             'CREATE TABLE document_commands(part_id,revision,chunk_index,'
                             'serialized_commands);')
            db.execute('INSERT INTO document_properties VALUES(1,?,0,?)', ('title', b'Title'))
            for revision, tab, name, chunk in declarations:
                payload = [None, 0, 99, tab, {'1': [[None, None, None, name]]}, 10, 20]
                db.execute('INSERT INTO document_commands VALUES(?,?,0,?)',
                           ('top', revision, json.dumps([[213, payload]])))
                if chunk:
                    db.execute('INSERT INTO document_commands VALUES(?,9,0,?)',
                               ('chunk' + tab, '[]'))
        return str(path)

    def rows(self, files):
        context = SimpleNamespace(get_files_found=lambda: files,
                                  get_relative_path=lambda p: str(Path(p).relative_to(self.root)))
        return getattr(google_sheets_tabs, '__wrapped__')(context)[1]

    def test_stringification_precedes_comparison(self):
        for value, matching in [(0, '0'), (False, 'False'), ('0', '0')]:
            with self.subTest(value=value):
                container = str(type(value).__name__)
                prefs = self.prefs(container, {'kActiveSheetId': value})
                db = self.database(container, [(0, matching, 'Match', True),
                                               (1, 'other', 'Other', True)])
                self.assertEqual([row[7] for row in self.rows([prefs, db])], ['Yes', 'No'])

    def test_keyed_archive_time_node_keeps_existing_comparison(self):
        prefs = Path(self.prefs('time', {}))
        archive = {'$objects': ['$null', 'kActiveSheetId', {'NS.time': 0},
                               {'NS.keys': [plistlib.UID(1)],
                                'NS.objects': [plistlib.UID(2)]}],
                   '$top': {'root': plistlib.UID(3)}}
        blob = plistlib.dumps(archive, fmt=getattr(plistlib, 'FMT_BINARY'))
        prefs.write_bytes(plistlib.dumps({'settingsForSheet:doc': blob}))
        db = self.database('time', [(0, '0', 'Tab', True)])
        self.assertEqual(self.rows([str(prefs), db])[0][7], 'Yes')

    def test_missing_key_and_archived_null_render_empty(self):
        for container, keyed in [('missing', False), ('null', True)]:
            prefs = self.prefs(container, {}, keyed_null=keyed)
            db = self.database(container, [(0, 'tab', 'Tab', True)])
            row = self.rows([prefs, db])[0]
            self.assertEqual(row[7], '')
            self.assertEqual(row[:7], ('Title', 'doc', '0', 'Tab', 'tab', '10', '20'))
            self.assertEqual(row[8:10], (213, 'account'))

    def test_last_document_only_preference_and_missing_overwrite(self):
        first = self.prefs('first', {'kActiveSheetId': 'tab'})
        second = self.prefs('second', {})
        db = self.database('first', [(0, 'tab', 'Tab', True)])
        self.assertEqual(self.rows([first, second, db])[0][7], '')
        self.assertEqual(self.rows([second, first, db])[0][7], 'Yes')

    def test_chunk_membership_first_declaration_and_input_repeats(self):
        prefs = self.prefs('first', {'kActiveSheetId': 'tab'})
        db = self.database('first', [(2, 'tab', 'Later', True),
                                     (0, 'tab', 'First', True),
                                     (1, 'orphan', 'Orphan', False)])
        rows = self.rows([prefs, db, db])
        self.assertEqual(len(rows), 2)
        self.assertEqual([row[3] for row in rows], ['First', 'First'])
        self.assertEqual(rows[0], rows[1])


if __name__ == '__main__':
    unittest.main()
