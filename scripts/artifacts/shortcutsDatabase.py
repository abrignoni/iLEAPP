__artifacts_v2__ = {
    "shortcuts_library": {
        "name": "Shortcuts - Library",
        "description": "Shortcuts saved in the Shortcuts app database (ZSHORTCUT in Shortcuts.sqlite), with their "
                       "dates, action and run counts and source.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Shortcuts",
        "notes": "Reads ZSHORTCUT in Shortcuts.sqlite, read-only with its -wal. Dates are Core Data timestamps "
                 "(seconds since 2001-01-01, UTC). Known data from an iOS 27.2 simulator (2026-11-16): one shortcut "
                 "was created, run twice, given a time-of-day automation and then deleted in the app. Modified "
                 "changed when the shortcut ran and again when the automation was saved, so it is not only an edit "
                 "time; whether an edit changes it was not tested. Last Run held the second run's date and Runs held "
                 "2, matching the two run events. After the delete the row stayed in ZSHORTCUT with ZTOMBSTONED 1, "
                 "and its actions, run events and automation stayed too. Modified did not change on the delete. The "
                 "database was read less than a minute after the delete; how long such a row is kept was not tested. "
                 "On belkactf6_tar Runs summed to the 5 run events and Last Run equalled the latest run date of both "
                 "shortcuts that had runs. Tombstoned held one value, 0, on every corpus row; it is kept because it "
                 "was 1 after the delete in the known data. Of the 15 corpus rows Source held "
                 "ShortcutSourceDefaultShortcut with a Gallery Identifier on 12, ShortcutSourceCloudLink on 2 and no "
                 "value on 1, and on hc_ios17_2 Source held the same value on all 4 rows. On fsfull002_ios17 and "
                 "hc_ios17_2, which recorded no run events, Runs held 0 and Last Run was empty on every row. On "
                 "hc_ios17_2 Created held one value on all 4 rows. Last Saved On Device held one value on every row "
                 "of belkactf6_tar and hc_ios17_2. On fsfull002_ios17 it held two values, one on 4 rows and another "
                 "on the 1 row with no Source. It is kept because it names a device; whether a shortcut synced from "
                 "another device carries that device's name was not tested. Source, Tombstoned and Runs are shown as "
                 "stored; their meaning beyond these observations is not established. Actions is the stored count "
                 "and the actions themselves are in Shortcuts - Actions. On iOS 13.3.1 (hickman_ios13) "
                 "Shortcuts.sqlite has no ZSHORTCUT, only the three voice-shortcut tables (ZVCVOICESHORTCUT*), so "
                 "nothing is read there. Those tables are not parsed on any version; their suggestion list table "
                 "held rows on 16 of the 18 corpus images. Also not read: ZSHORTCUTICON, ZSMARTPROMPTPERMISSION, the "
                 "folder join tables Z_4SHORTCUTS and Z_4PARENTS, ZCOLLECTION, ZLIBRARY, "
                 "ZPERSISTEDSERIALIZEDPARAMETERS and ZCLOUDKITSYNCTOKEN, and the tables that were empty on every "
                 "corpus image (ZACCESSRESOURCEPERMISSION, ZSHORTCUTBOOKMARK, ZSHORTCUTQUARANTINE, ZTRUSTEDDOMAIN, "
                 "ZAUTOSHORTCUTSPREFERENCES, ZFILESTATE, ZTRACKEDFILESYSTEMNODE).",
        "paths": ('*/mobile/Library/Shortcuts/Shortcuts.sqlite*',),
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6_tar": "iOS 16.3 | 6 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 5 rows",
            "hc_ios17_2": "iOS 17.2.1 | 4 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
        "output_types": "standard",
        "artifact_icon": "list",
    },
    "shortcuts_actions": {
        "name": "Shortcuts - Actions",
        "description": "The actions of each saved shortcut, one row per action in stored order, with the action "
                       "identifier and its parameters decoded from ZSHORTCUTACTIONS in Shortcuts.sqlite.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Shortcuts",
        "notes": "One row per entry of the property list in ZSHORTCUTACTIONS.ZDATA, per shortcut, in stored order. A "
                 "shortcut with no actions gives no row. Action Identifier is the entry's WFWorkflowActionIdentifier "
                 "and Action Parameters its WFWorkflowActionParameters as JSON, with any byte string replaced by its "
                 "length; no corpus row held one. On the corpus the parameter keys included Text and "
                 "WFSendMessageContent, all on ShortcutSourceDefaultShortcut shortcuts, each holding a nested "
                 "dictionary; what text those dictionaries hold was not reviewed. The rows of each shortcut equalled its stored "
                 "Actions count in Shortcuts - Library for every shortcut on belkactf6_tar, fsfull002_ios17 and "
                 "hc_ios17_2 (235 rows) and in the iOS 27.2 simulator known data (1 row). Identifiers are shown as "
                 "stored. Parameters are shown as decoded, with keys sorted. Neither is interpreted. A shortcut "
                 "whose ZDATA is missing or does not decode to a list gives one row with Action Identifier \"not "
                 "decoded\", and so does a single entry that is not a dictionary; no image exercised this.",
        "paths": ('*/mobile/Library/Shortcuts/Shortcuts.sqlite*',),
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6_tar": "iOS 16.3 | 67 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 84 rows",
            "hc_ios17_2": "iOS 17.2.1 | 84 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "list",
    },
    "shortcuts_run_history": {
        "name": "Shortcuts - Run History",
        "description": "Recorded runs of shortcuts (ZSHORTCUTRUNEVENT in Shortcuts.sqlite) with the run date, the "
                       "shortcut and the stored source and outcome values.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Shortcuts",
        "notes": "One row per ZSHORTCUTRUNEVENT row; Run Date is ZDATE (Core Data timestamp, UTC). In the iOS 27.2 "
                 "simulator known data the taps on the editor's play button were logged at 21:59:49.237Z and "
                 "22:00:24.068Z. Run Date held 21:59:52.04Z and 22:00:27.39Z, about 3 seconds after each logged tap "
                 "and earlier than the logged Done and Cancel taps, so Run Date is not the logged tap time. When the "
                 "rows were written was not measured. Both runs were stored with Source \"button\"; the one run closed "
                 "with Done was stored with Outcome 1 and the one closed with Cancel with Outcome 3. On "
                 "belkactf6_tar Source held one value, \"my-workflows\", on all 5 rows, and Outcome held one value, 1, "
                 "on all 5 rows. Source and Outcome are shown as stored and are not interpreted. Automation UUID is "
                 "read from ZUNIFIEDTRIGGER when the run points at one (table and column seen only in the iOS 27.2 "
                 "simulator). The automation in the known data did not run on the simulator, so Automation UUID was "
                 "empty on every tested row; the join is exercised only by a synthetic test. In the known data the "
                 "runs of the deleted shortcut were still in the table less than a minute after the delete (see "
                 "Shortcuts - Library). ZTRIGGER and ZTRIGGEREVENT were empty on all 17 corpus images that have them "
                 "and are not read.",
        "paths": ('*/mobile/Library/Shortcuts/Shortcuts.sqlite*',),
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6_tar": "iOS 16.3 | 5 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
        "output_types": "standard",
        "artifact_icon": "play",
    },
    "shortcuts_automations": {
        "name": "Shortcuts - Automations",
        "description": "Automations stored in ZUNIFIEDTRIGGER of Shortcuts.sqlite, with the trigger type and its "
                       "parameters decoded from the trigger's property list.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Shortcuts",
        "notes": "One row per ZUNIFIEDTRIGGER row. The table was present only in the iOS 27.2 simulator known data; "
                 "none of the 18 corpus images (iOS 13.3.1 to 26.5.2) has it, so on those this artifact reads "
                 "nothing. ZDATA is a property list: Trigger Identifier is its WFTriggerIdentifier and Trigger "
                 "Parameters its WFTriggerSerializedParameters as JSON. In the known data an automation set in the "
                 "app for 5:05 PM was stored as WFTimeOfDayTrigger with WFTimeComponents hour 17 and minute 5, the "
                 "local time as set, with no time zone, and with ZENABLEMENT 1 and ZNOTIFICATIONLEVEL 0. Enablement "
                 "and Notification Level are shown as stored and not interpreted. Other trigger types were not "
                 "created; their parameters are shown as decoded. ZTRIGGER was present on 17 corpus images and in "
                 "the simulator, was empty on all of them and is not read; whether earlier versions store "
                 "automations there was not established.",
        "paths": ('*/mobile/Library/Shortcuts/Shortcuts.sqlite*',),
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "belkactf6_tar": "iOS 16.3 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
        },
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "clock",
    },
}

import datetime
import json
import plistlib
import sqlite3
from xml.parsers.expat import ExpatError

from scripts.ilapfuncs import (artifact_processor, open_sqlite_db_readonly, does_table_exist_in_db,
                               does_column_exist_in_db, logfunc)

_COCOA = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
_PLIST_ERRORS = (plistlib.InvalidFileException, ExpatError, ValueError, TypeError, OverflowError)


def _cocoa(value):
    if value in (None, ''):
        return ''
    try:
        return _COCOA + datetime.timedelta(seconds=float(value))
    except (ValueError, OverflowError, TypeError):
        return ''


def _text(value):
    return '' if value is None else str(value)


def _databases(context):
    return [str(f) for f in context.get_files_found() if str(f).endswith('Shortcuts.sqlite')]


def _rows(path, sql):
    db = open_sqlite_db_readonly(path)
    if db is None:
        return []
    try:
        return db.execute(sql).fetchall()
    except sqlite3.Error as error:
        logfunc(f'Shortcuts: could not read {path}: {error}')
        return []
    finally:
        db.close()


def _column(path, table, column, fallback="NULL"):
    return column if does_column_exist_in_db(path, table, column) else fallback


@artifact_processor
def shortcuts_library(context):
    data_list = []
    sources = []
    for path in _databases(context):
        sources.append(path)
        if not does_table_exist_in_db(path, 'ZSHORTCUT'):
            continue
        columns = ', '.join(_column(path, 'ZSHORTCUT', name) for name in (
            'ZCREATIONDATE', 'ZMODIFICATIONDATE', 'ZLASTRUNEVENTDATE', 'ZNAME', 'ZACTIONCOUNT', 'ZRUNEVENTSCOUNT',
            'ZSOURCE', 'ZGALLERYIDENTIFIER', 'ZLASTSAVEDONDEVICENAME', 'ZTOMBSTONED', 'ZWORKFLOWID'))
        for row in _rows(path, f'SELECT {columns} FROM ZSHORTCUT ORDER BY Z_PK'):
            data_list.append((_cocoa(row[0]), _cocoa(row[1]), _cocoa(row[2]), _text(row[3]), row[4],
                              row[5], _text(row[6]), _text(row[7]), _text(row[8]), row[9], _text(row[10])))
    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'), ('Last Run', 'datetime'), 'Name',
        ('Actions', 'number'), ('Runs (as stored)', 'number'), 'Source (as stored)', 'Gallery Identifier',
        'Last Saved On Device', ('Tombstoned (as stored)', 'number'), 'Workflow ID',
    )
    return data_headers, data_list, '\n'.join(sources)


def _plain(value):
    """A JSON-safe copy of a decoded property list value; bytes are described, not dumped."""
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, bytes):
        return f'{len(value)} bytes'
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


@artifact_processor
def shortcuts_actions(context):
    data_list = []
    sources = []
    for path in _databases(context):
        sources.append(path)
        if not (does_table_exist_in_db(path, 'ZSHORTCUTACTIONS') and does_table_exist_in_db(path, 'ZSHORTCUT')):
            continue
        sql = f'''
            SELECT s.{_column(path, 'ZSHORTCUT', 'ZNAME')}, a.ZDATA, s.{_column(path, 'ZSHORTCUT', 'ZWORKFLOWID')}
            FROM ZSHORTCUTACTIONS a LEFT JOIN ZSHORTCUT s ON s.Z_PK = a.ZSHORTCUT ORDER BY a.ZSHORTCUT, a.Z_PK'''
        for name, blob, workflow in _rows(path, sql.replace('s.NULL', 'NULL')):
            try:
                actions = plistlib.loads(blob) if isinstance(blob, bytes) else None
            except _PLIST_ERRORS:
                actions = None
            if not isinstance(actions, list):
                data_list.append((_text(name), '', 'not decoded', '', _text(workflow)))
                continue
            for position, action in enumerate(actions, 1):
                if not isinstance(action, dict):
                    data_list.append((_text(name), position, 'not decoded', '', _text(workflow)))
                    continue
                parameters = action.get('WFWorkflowActionParameters')
                data_list.append((_text(name), position, _text(action.get('WFWorkflowActionIdentifier')),
                                  '' if parameters is None else json.dumps(_plain(parameters), sort_keys=True),
                                  _text(workflow)))
    data_headers = (
        'Shortcut Name', ('Position', 'number'), 'Action Identifier', 'Action Parameters', 'Workflow ID',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def shortcuts_run_history(context):
    data_list = []
    sources = []
    for path in _databases(context):
        sources.append(path)
        if not (does_table_exist_in_db(path, 'ZSHORTCUTRUNEVENT') and does_table_exist_in_db(path, 'ZSHORTCUT')):
            continue
        unified = does_column_exist_in_db(path, 'ZSHORTCUTRUNEVENT', 'ZUNIFIEDTRIGGER') and \
            does_table_exist_in_db(path, 'ZUNIFIEDTRIGGER')
        trigger_uuid = 'u.ZUUID' if unified else 'NULL'
        join = 'LEFT JOIN ZUNIFIEDTRIGGER u ON u.Z_PK = e.ZUNIFIEDTRIGGER' if unified else ''
        sql = f'''
            SELECT e.ZDATE, s.ZNAME, e.{_column(path, 'ZSHORTCUTRUNEVENT', 'ZSOURCE')},
                   e.{_column(path, 'ZSHORTCUTRUNEVENT', 'ZOUTCOME')}, {trigger_uuid}, s.ZWORKFLOWID
            FROM ZSHORTCUTRUNEVENT e LEFT JOIN ZSHORTCUT s ON s.Z_PK = e.ZSHORTCUT {join}
            ORDER BY e.ZDATE'''
        sql = sql.replace('e.NULL', 'NULL')
        for row in _rows(path, sql):
            data_list.append((_cocoa(row[0]), _text(row[1]), _text(row[2]), row[3], _text(row[4]), _text(row[5])))
    data_headers = (
        ('Run Date', 'datetime'), 'Shortcut Name', 'Source (as stored)', ('Outcome (as stored)', 'number'),
        'Automation UUID', 'Workflow ID',
    )
    return data_headers, data_list, '\n'.join(sources)


def _trigger(blob):
    """(identifier, parameters JSON) from a ZUNIFIEDTRIGGER.ZDATA property list."""
    if not isinstance(blob, bytes):
        return '', ''
    try:
        data = plistlib.loads(blob)
    except _PLIST_ERRORS:
        return '', 'not decoded'
    if not isinstance(data, dict):
        return '', 'not decoded'
    parameters = data.get('WFTriggerSerializedParameters')
    if isinstance(parameters, bytes):
        try:
            parameters = plistlib.loads(parameters)
        except _PLIST_ERRORS:
            parameters = f'{len(parameters)} bytes, not decoded'
    return _text(data.get('WFTriggerIdentifier')), json.dumps(parameters, sort_keys=True, default=str)


@artifact_processor
def shortcuts_automations(context):
    data_list = []
    sources = []
    for path in _databases(context):
        sources.append(path)
        if not (does_table_exist_in_db(path, 'ZUNIFIEDTRIGGER') and does_table_exist_in_db(path, 'ZSHORTCUT')):
            continue
        sql = '''
            SELECT s.ZNAME, u.ZDATA, u.ZENABLEMENT, u.ZNOTIFICATIONLEVEL, u.ZUUID, s.ZWORKFLOWID
            FROM ZUNIFIEDTRIGGER u LEFT JOIN ZSHORTCUT s ON s.Z_PK = u.ZSHORTCUT ORDER BY u.Z_PK'''
        for row in _rows(path, sql):
            identifier, parameters = _trigger(row[1])
            data_list.append((_text(row[0]), identifier, parameters, row[2], row[3], _text(row[4]), _text(row[5])))
    data_headers = (
        'Shortcut Name', 'Trigger Identifier', 'Trigger Parameters', ('Enablement (as stored)', 'number'),
        ('Notification Level (as stored)', 'number'), 'Automation UUID', 'Workflow ID',
    )
    return data_headers, data_list, '\n'.join(sources)
