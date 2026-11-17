"""Shortcuts database artifacts on synthetic Shortcuts.sqlite files (values invented for the test)."""
import datetime
import json
import pathlib
import plistlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import shortcutsDatabase as parser  # noqa: E402

BASE = 'private/var/mobile/Library/Shortcuts/Shortcuts.sqlite'
SHORTCUT = '''CREATE TABLE ZSHORTCUT (Z_PK INTEGER PRIMARY KEY, ZCREATIONDATE TIMESTAMP, ZMODIFICATIONDATE TIMESTAMP,
    ZLASTRUNEVENTDATE TIMESTAMP, ZNAME VARCHAR, ZACTIONCOUNT INTEGER, ZRUNEVENTSCOUNT INTEGER, ZSOURCE VARCHAR,
    ZGALLERYIDENTIFIER VARCHAR, ZLASTSAVEDONDEVICENAME VARCHAR, ZTOMBSTONED INTEGER,
    ZHIDDENFROMLIBRARYANDSYNC INTEGER, ZWORKFLOWID VARCHAR)'''


def _build(path, unified):
    path.parent.mkdir(parents=True)
    db = sqlite3.connect(path)
    db.execute(SHORTCUT)
    run_cols = 'Z_PK INTEGER PRIMARY KEY, ZOUTCOME INTEGER, ZSHORTCUT INTEGER, ZDATE TIMESTAMP, ZSOURCE VARCHAR'
    if unified:
        run_cols += ', ZUNIFIEDTRIGGER INTEGER'
        db.execute('CREATE TABLE ZUNIFIEDTRIGGER (Z_PK INTEGER PRIMARY KEY, ZENABLEMENT INTEGER, '
                   'ZNOTIFICATIONLEVEL INTEGER, ZSHORTCUT INTEGER, ZUUID VARCHAR, ZDATA BLOB)')
    db.execute(f'CREATE TABLE ZSHORTCUTRUNEVENT ({run_cols})')
    db.execute('CREATE TABLE ZSHORTCUTACTIONS (Z_PK INTEGER PRIMARY KEY, ZSHORTCUT INTEGER, ZDATA BLOB)')
    actions = [{'WFWorkflowActionIdentifier': 'is.workflow.actions.example',
                'WFWorkflowActionParameters': {'Text': 'hello', 'Blob': b'abc'}},
               {'WFWorkflowActionIdentifier': 'is.workflow.actions.other'}]
    db.execute('INSERT INTO ZSHORTCUTACTIONS VALUES (1, 1, ?)', (plistlib.dumps(actions),))
    db.execute('INSERT INTO ZSHORTCUT VALUES (1, 100, 200, 300, ?, 2, 1, ?, NULL, ?, 0, 0, ?)',
               ('Test One', 'src', 'device', 'WF-1'))
    if unified:
        data = plistlib.dumps({'WFTriggerIdentifier': 'WFTimeOfDayTrigger', 'WFTriggerUUID': 'T-1',
                               'WFTriggerSerializedParameters': {'WFTimeComponents': {'hour': 1, 'minute': 2}}})
        db.execute('INSERT INTO ZUNIFIEDTRIGGER VALUES (1, 1, 0, 1, ?, ?)', ('U-1', data))
        db.execute('INSERT INTO ZUNIFIEDTRIGGER VALUES (2, 0, 0, 1, ?, ?)', ('U-2', b'not a plist'))
        db.execute('INSERT INTO ZSHORTCUTRUNEVENT VALUES (1, 1, 1, 300, ?, 1)', ('automation',))
    else:
        db.execute('INSERT INTO ZSHORTCUTRUNEVENT VALUES (1, 3, 1, 300, ?)', ('button',))
    db.commit()
    db.close()


class ShortcutsDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.directory.name)
        self.new = root / 'new' / BASE
        self.old = root / 'old' / BASE
        _build(self.new, unified=True)
        _build(self.old, unified=False)
        self.context = SimpleNamespace(get_files_found=lambda: [str(self.new), str(self.new) + '-wal', str(self.old)])

    def tearDown(self):
        self.directory.cleanup()

    def test_library(self):
        headers, rows, source = parser.shortcuts_library.__wrapped__(self.context)
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], datetime.datetime(2001, 1, 1, 0, 1, 40, tzinfo=datetime.timezone.utc))
        self.assertEqual(rows[0][3], 'Test One')
        self.assertEqual(len(source.splitlines()), 2)

    def test_actions(self):
        headers, rows, _ = parser.shortcuts_actions.__wrapped__(self.context)
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(len(rows), 4)
        first = rows[0]
        self.assertEqual(first[1:3], (1, 'is.workflow.actions.example'))
        self.assertEqual(json.loads(first[3]), {'Blob': '3 bytes', 'Text': 'hello'})
        self.assertEqual(rows[1][1:4], (2, 'is.workflow.actions.other', ''))

    def test_run_history(self):
        _, rows, _ = parser.shortcuts_run_history.__wrapped__(self.context)
        by_source = {r[2]: r for r in rows}
        self.assertEqual(by_source['automation'][4], 'U-1')
        self.assertEqual(by_source['button'][3], 3)
        self.assertEqual(by_source['button'][4], '')

    def test_automations(self):
        _, rows, _ = parser.shortcuts_automations.__wrapped__(self.context)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][1], 'WFTimeOfDayTrigger')
        self.assertEqual(json.loads(rows[0][2]), {'WFTimeComponents': {'hour': 1, 'minute': 2}})
        self.assertEqual(rows[1][1:3], ('', 'not decoded'))


if __name__ == '__main__':
    unittest.main()
