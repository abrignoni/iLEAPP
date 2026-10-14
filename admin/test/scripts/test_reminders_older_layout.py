"""Pin how the Reminders artifact finds a reminder's columns in the older store layout.

The models of the iOS 13.3.1, 14.3, 15.0.2 and 15.3.1 test images make a reminder a
REMCDReminder row of ZREMCDOBJECT, the table every subentity of REMCDObject shares, and a
property name that several of those entities define is kept in numbered columns. Which
number a reminder's column carries depends on which entities of the table define that name,
so it moves between releases. In the model of the iOS 15.0.2 test image REMCDHashtag
(entity 24) and REMCDReminder (28) both define creationDate, and the reminder's column is
ZCREATIONDATE1. The artifact read ZCREATIONDATE on every older-layout store, which there is
the hashtag's column, so the reminders built below came out with no Creation Date. It now
works each column out from the Core Data model the store caches in Z_MODELCACHE.

Every store and model below is built by the test; no row comes from a device. The entity
numbers are those of the iOS 14.3 and 15.0.2 test images, and the expected dates were
computed with datetime, not with SQLite.
"""
import os
import pathlib
import plistlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
import zlib
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import reminders as artifact  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

ATTRIBUTES = ('creationDate', 'lastModifiedDate', 'dueDate', 'completionDate', 'title', 'notes',
              'completed', 'flagged')


def model_cache(entities, style):
    """A Z_MODELCACHE blob: raw deflate of an NSKeyedArchiver archive of entity descriptions.

    entities is [(name, parent, {property: kind})] with kind 'attr', ('one', destination) or
    ('many', destination). A subentity lists its parent's properties as well as its own, as
    _NSPropertyDescriptionProxy objects (style 'proxy', which is how the models of the iOS
    13.3.1, 14.3, 15.0.2 and 15.3.1 test images store them) or as copies (style 'copy')."""
    uid = plistlib.UID
    objects, classes = ['$null'], {}

    def add(value):
        objects.append(value)
        return uid(len(objects) - 1)

    def cls(name):
        if name not in classes:
            classes[name] = add({'$classname': name, '$classes': [name, 'NSObject']})
        return classes[name]

    def description(prop, kind):
        if kind == 'attr':
            return add({'$class': cls('NSAttributeDescription'), 'NSPropertyName': add(prop),
                        'NSAttributeType': 700})
        return add({'$class': cls('NSRelationshipDescription'), 'NSPropertyName': add(prop),
                    'NSMaxCount': 1 if kind[0] == 'one' else 0,
                    '_NSDestinationEntityName': add(kind[1])})

    spec = {name: (parent, props) for name, parent, props in entities}
    slots = {name: add({}) for name in spec}
    own = {}

    def build(name):
        if name in own:
            return own[name]
        parent, props = spec[name]
        listed = {}
        if parent:
            for prop, (desc, kind) in build(parent).items():
                if style == 'proxy':
                    listed[prop] = (add({'$class': cls('_NSPropertyDescriptionProxy'),
                                         'NSUnderlyingProperty': desc,
                                         'NSEntityDescription': slots[name]}), kind)
                else:
                    listed[prop] = (description(prop, kind), kind)
        for prop, kind in props.items():
            listed[prop] = (description(prop, kind), kind)
        own[name] = listed
        return listed

    for name, (parent, _props) in spec.items():
        listed = build(name)
        table = add({'$class': cls('NSMutableDictionary'), 'NS.keys': [add(p) for p in listed],
                     'NS.objects': [desc for desc, _kind in listed.values()]})
        objects[slots[name].data] = {'$class': cls('NSEntityDescription'),
                                     'NSEntityName': add(name),
                                     'NSSuperentity': slots[parent] if parent else uid(0),
                                     'NSProperties': table}
    root = add({'$class': cls('NSManagedObjectModel'),
                'NSEntities': [slots[name] for name in spec]})
    archive = plistlib.dumps({'$version': 100000, '$archiver': 'NSKeyedArchiver',
                              '$top': {'root': root}, '$objects': objects},
                             fmt=plistlib.PlistFormat.FMT_BINARY)
    packer = zlib.compressobj(9, zlib.DEFLATED, -15)
    return packer.compress(archive) + packer.flush()


# The iOS 15.0.2 test image: REMCDHashtag (24) defines creationDate before REMCDReminder
# (28), and REMCDAlarmLocationTrigger (10) defines title before it.
IOS15_MODEL = [
    ('REMCDObject', None, {'markedForDeletion': 'attr', 'account': ('one', 'REMCDAccount')}),
    ('REMCDAccount', 'REMCDObject', {'name': 'attr'}),
    ('REMCDAlarmTrigger', 'REMCDObject', {}),
    ('REMCDAlarmLocationTrigger', 'REMCDAlarmTrigger', {'title': 'attr'}),
    ('REMCDHashtag', 'REMCDObject', {'name': 'attr', 'creationDate': 'attr'}),
    ('REMCDList', 'REMCDObject', {'name': 'attr', 'reminders': ('many', 'REMCDReminder')}),
    ('REMCDReminder', 'REMCDObject', {**{name: 'attr' for name in ATTRIBUTES},
                                      'list': ('one', 'REMCDList')})]
IOS15_NUMBERS = {'REMCDObject': 5, 'REMCDAccount': 6, 'REMCDAlarmTrigger': 8,
                 'REMCDAlarmLocationTrigger': 10, 'REMCDHashtag': 24, 'REMCDList': 25,
                 'REMCDReminder': 28}
IOS15_COLUMNS = ('Z_PK', 'Z_ENT', 'ZMARKEDFORDELETION', 'ZACCOUNT', 'ZNAME', 'ZTITLE',
                 'ZCREATIONDATE', 'ZNAME1', 'ZNAME2', 'ZCREATIONDATE1', 'ZLASTMODIFIEDDATE',
                 'ZDUEDATE', 'ZCOMPLETIONDATE', 'ZTITLE1', 'ZNOTES', 'ZCOMPLETED', 'ZFLAGGED',
                 'ZLIST')
IOS15_ROWS = (
    {'Z_PK': 1, 'Z_ENT': 6, 'ZNAME': 'iCloud'},
    {'Z_PK': 2, 'Z_ENT': 10, 'ZACCOUNT': 1, 'ZTITLE': 'Home'},
    {'Z_PK': 3, 'Z_ENT': 24, 'ZACCOUNT': 1, 'ZNAME1': 'groceries', 'ZCREATIONDATE': 700000000.0},
    {'Z_PK': 4, 'Z_ENT': 25, 'ZACCOUNT': 1, 'ZNAME2': 'Errands'},
    {'Z_PK': 5, 'Z_ENT': 28, 'ZACCOUNT': 1, 'ZLIST': 4, 'ZCREATIONDATE1': 650000000.0,
     'ZLASTMODIFIEDDATE': 650000100.0, 'ZDUEDATE': 650086400.0, 'ZTITLE1': 'Buy milk',
     'ZNOTES': 'two', 'ZCOMPLETED': 0, 'ZFLAGGED': 1, 'ZMARKEDFORDELETION': 0},
    {'Z_PK': 6, 'Z_ENT': 28, 'ZACCOUNT': 1, 'ZLIST': 4, 'ZCREATIONDATE1': 651000000.0,
     'ZLASTMODIFIEDDATE': 651500000.0, 'ZCOMPLETIONDATE': 651600000.0,
     'ZTITLE1': 'Call back', 'ZCOMPLETED': 1, 'ZFLAGGED': 0, 'ZMARKEDFORDELETION': 1})
IOS15_EXPECTED = (
    ('2021-08-07 03:33:20', '2021-08-07 03:35:00', '2021-08-08 03:33:20', None, 'Buy milk',
     'two', 0, 1, 0),
    ('2021-08-18 17:20:00', '2021-08-24 12:13:20', None, '2021-08-25 16:00:00', 'Call back',
     None, 1, 0, 1))

# The iOS 14.3 test image: REMCDReminder (24) defines lastModifiedDate before
# REMCDSmartListOrder (27), so the reminder keeps the unnumbered column, and it is the only
# entity of the table that defines creationDate.
IOS14_MODEL = [
    ('REMCDObject', None, {'markedForDeletion': 'attr'}),
    ('REMCDAccount', 'REMCDObject', {'name': 'attr'}),
    ('REMCDAlarmTrigger', 'REMCDObject', {}),
    ('REMCDAlarmLocationTrigger', 'REMCDAlarmTrigger', {'title': 'attr'}),
    ('REMCDList', 'REMCDObject', {'name': 'attr'}),
    ('REMCDReminder', 'REMCDObject', {name: 'attr' for name in ATTRIBUTES}),
    ('REMCDSmartListOrder', 'REMCDObject', {'lastModifiedDate': 'attr'})]
IOS14_NUMBERS = {'REMCDObject': 3, 'REMCDAccount': 4, 'REMCDAlarmTrigger': 6,
                 'REMCDAlarmLocationTrigger': 8, 'REMCDList': 22, 'REMCDReminder': 24,
                 'REMCDSmartListOrder': 27}
IOS14_COLUMNS = ('Z_PK', 'Z_ENT', 'ZMARKEDFORDELETION', 'ZNAME', 'ZTITLE', 'ZNAME1',
                 'ZCREATIONDATE', 'ZLASTMODIFIEDDATE', 'ZDUEDATE', 'ZCOMPLETIONDATE', 'ZTITLE1',
                 'ZNOTES', 'ZCOMPLETED', 'ZFLAGGED', 'ZLASTMODIFIEDDATE1')
IOS14_ROWS = (
    {'Z_PK': 1, 'Z_ENT': 27, 'ZLASTMODIFIEDDATE1': 610000000.0},
    {'Z_PK': 2, 'Z_ENT': 8, 'ZTITLE': 'Office'},
    {'Z_PK': 3, 'Z_ENT': 24, 'ZCREATIONDATE': 600000000.0, 'ZLASTMODIFIEDDATE': 600000100.0,
     'ZDUEDATE': 600086400.0, 'ZTITLE1': 'Pay rent', 'ZCOMPLETED': 0, 'ZFLAGGED': 0,
     'ZMARKEDFORDELETION': 0})
IOS14_EXPECTED = (
    ('2020-01-06 10:40:00', '2020-01-06 10:41:40', '2020-01-07 10:40:00', None, 'Pay rent',
     None, 0, 0, 0),)

NEWER_COLUMNS = ('Z_PK', 'Z_ENT', 'ZCREATIONDATE', 'ZLASTMODIFIEDDATE', 'ZDUEDATE',
                 'ZCOMPLETIONDATE', 'ZTITLE', 'ZNOTES', 'ZCOMPLETED', 'ZFLAGGED',
                 'ZMARKEDFORDELETION')


class RemindersOlderLayoutTest(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root, True)
        self.addCleanup(Context.clear)
        self.logged = []

    def store(self, name, numbers, cache, table, columns, rows):
        path = os.path.join(self.root, 'Container_v1', 'Stores', name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        db = sqlite3.connect(path)
        with db:
            db.execute('CREATE TABLE Z_PRIMARYKEY (Z_ENT INTEGER PRIMARY KEY, Z_NAME VARCHAR, '
                       'Z_SUPER INTEGER, Z_MAX INTEGER)')
            db.executemany('INSERT INTO Z_PRIMARYKEY VALUES (?, ?, 0, 0)',
                           [(number, entity) for entity, number in numbers.items()])
            if cache is not None:
                db.execute('CREATE TABLE Z_MODELCACHE (Z_CONTENT BLOB)')
                db.execute('INSERT INTO Z_MODELCACHE VALUES (?)', (cache,))
            db.execute(f'CREATE TABLE {table} ({", ".join(columns)})')
            db.executemany(f'INSERT INTO {table} VALUES ({", ".join("?" * len(columns))})',
                           [tuple(row.get(column) for column in columns) for row in rows])
        db.close()
        return path

    def ios15_store(self, name='Data-15.sqlite', style='proxy', model=None, numbers=None):
        return self.store(name, numbers or IOS15_NUMBERS,
                          model_cache(model or IOS15_MODEL, style), 'ZREMCDOBJECT',
                          IOS15_COLUMNS, IOS15_ROWS)

    def run_artifact(self, paths):
        Context.clear()
        Context.set_files_found(list(paths))
        with mock.patch.object(artifact, 'logfunc', self.logged.append, create=True):
            return artifact.reminders.__wrapped__(Context)

    def test_creation_date_is_read_from_the_column_the_model_names(self):
        path = self.ios15_store()
        _headers, rows, _source = self.run_artifact([path])
        self.assertEqual(rows, [expected + (path,) for expected in IOS15_EXPECTED])
        self.assertEqual(self.logged, [])

    def test_the_lower_numbered_entity_keeps_the_unnumbered_column(self):
        path = self.store('Data-14.sqlite', IOS14_NUMBERS, model_cache(IOS14_MODEL, 'proxy'),
                          'ZREMCDOBJECT', IOS14_COLUMNS, IOS14_ROWS)
        _headers, rows, _source = self.run_artifact([path])
        self.assertEqual(rows, [expected + (path,) for expected in IOS14_EXPECTED])
        self.assertEqual(self.logged, [])

    def test_inherited_properties_stored_as_copies(self):
        """An archive can list an inherited property as a copy rather than a proxy. The
        name decides it is inherited, so Marked for Deletion stays REMCDObject's column."""
        path = self.ios15_store(style='copy')
        _headers, rows, _source = self.run_artifact([path])
        self.assertEqual(rows, [expected + (path,) for expected in IOS15_EXPECTED])
        self.assertEqual(self.logged, [])

    def test_a_store_whose_model_cannot_be_read_is_logged_and_not_read(self):
        missing = self.store('Data-none.sqlite', IOS15_NUMBERS, None, 'ZREMCDOBJECT',
                             IOS15_COLUMNS, IOS15_ROWS)
        junk = self.store('Data-junk.sqlite', IOS15_NUMBERS, b'not deflate', 'ZREMCDOBJECT',
                          IOS15_COLUMNS, IOS15_ROWS)
        good = self.ios15_store()
        _headers, rows, _source = self.run_artifact([missing, junk, good])
        self.assertEqual(rows, [expected + (good,) for expected in IOS15_EXPECTED])
        self.assertEqual(self.logged, [
            f'Reminders: no readable Core Data model in {missing}; store not read',
            f'Reminders: no readable Core Data model in {junk}; store not read'])

    def test_a_store_the_model_does_not_fit_is_logged_and_not_read(self):
        no_entity = self.ios15_store('Data-noentity.sqlite',
                                     model=[e for e in IOS15_MODEL if e[0] != 'REMCDReminder'])
        no_number = self.ios15_store('Data-nonumber.sqlite', numbers={
            name: number for name, number in IOS15_NUMBERS.items() if name != 'REMCDReminder'})
        # A model that makes REMCDReminder a root entity puts reminders in ZREMCDREMINDER,
        # which this store does not have.
        own_table = self.ios15_store('Data-owntable.sqlite', model=[
            e if e[0] != 'REMCDReminder' else (e[0], None, e[2]) for e in IOS15_MODEL])
        _headers, rows, _source = self.run_artifact([no_entity, no_number, own_table])
        self.assertEqual(rows, [])
        self.assertEqual(self.logged, [
            f'Reminders: no REMCDReminder entity in the model of {no_entity}; store not read',
            f'Reminders: no entity number for REMCDReminder in {no_number}; store not read',
            f'Reminders: no ZREMCDREMINDER table for REMCDReminder in {own_table}; '
            'store not read'])

    def test_a_column_that_cannot_be_decided_is_reported_blank_and_logged(self):
        """Another entity of the table defines notes as a to-many relationship, which has no
        column, so which ZNOTES column is the reminder's cannot be decided."""
        model = IOS15_MODEL + [('REMCDTemplate', 'REMCDObject',
                                {'notes': ('many', 'REMCDReminder')})]
        path = self.ios15_store(model=model, numbers={**IOS15_NUMBERS, 'REMCDTemplate': 29})
        _headers, rows, _source = self.run_artifact([path])
        blank_notes = [expected[:5] + (None,) + expected[6:] for expected in IOS15_EXPECTED]
        self.assertEqual(rows, [expected + (path,) for expected in blank_notes])
        self.assertEqual(self.logged,
                         [f'Reminders: no column found for notes in {path}; reported blank'])

    def test_a_column_the_model_names_but_the_table_lacks_is_reported_blank_and_logged(self):
        columns = tuple(column for column in IOS15_COLUMNS if column != 'ZNOTES')
        path = self.store('Data-15.sqlite', IOS15_NUMBERS, model_cache(IOS15_MODEL, 'proxy'),
                          'ZREMCDOBJECT', columns, IOS15_ROWS)
        _headers, rows, _source = self.run_artifact([path])
        blank_notes = [expected[:5] + (None,) + expected[6:] for expected in IOS15_EXPECTED]
        self.assertEqual(rows, [expected + (path,) for expected in blank_notes])
        self.assertEqual(self.logged,
                         [f'Reminders: no column found for notes in {path}; reported blank'])

    def test_newer_layout_is_read_without_the_model(self):
        path = self.store('Data-16.sqlite', {'REMCDReminder': 32}, None, 'ZREMCDREMINDER',
                          NEWER_COLUMNS, [
                              {'Z_PK': 1, 'Z_ENT': 32, 'ZCREATIONDATE': 788000000.0,
                               'ZLASTMODIFIEDDATE': 788000500.0, 'ZDUEDATE': 788054400.0,
                               'ZTITLE': 'Pay rent', 'ZNOTES': 'By transfer', 'ZCOMPLETED': 0,
                               'ZFLAGGED': 1, 'ZMARKEDFORDELETION': 0}])
        _headers, rows, _source = self.run_artifact([path])
        self.assertEqual(rows, [('2025-12-21 08:53:20', '2025-12-21 09:01:40',
                                 '2025-12-22 00:00:00', None, 'Pay rent', 'By transfer', 0, 1,
                                 0, path)])
        self.assertEqual(self.logged, [])


if __name__ == '__main__':
    unittest.main()
