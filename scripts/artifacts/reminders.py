__artifacts_v2__ = {
    "reminders": {
        "name": "Reminders",
        "description": "iOS Reminders with creation, modification, due and completion timestamps",
        "author": "@any333",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-09-27",
        "requirements": "none",
        "category": "Reminders",
        "notes": ("Two store generations are read. On the iOS 16 and later test images reminders "
                  "are rows of a ZREMCDREMINDER table and each property is read from its "
                  "unnumbered column (ZCREATIONDATE, ZTITLE and so on), which on every tested "
                  "store of that generation is also the column the store's cached Core Data model "
                  "names. On the iOS 13.3.1, 14.3, 15.0.2 and 15.3.1 test images the stores' "
                  "models make a reminder a REMCDReminder row of ZREMCDOBJECT, a table it shares "
                  "with other entities such as accounts, lists and alarms, and the entity number "
                  "is read from each store's Z_PRIMARYKEY because it shifts between releases (23, "
                  "24, 28 and 28 on those images). A property name that several entities of such "
                  "a table define is kept in numbered columns (ZTITLE, ZTITLE1 and so on), so in "
                  "that generation the column of each property is worked out from the model the "
                  "store caches in Z_MODELCACHE, a raw deflate stream holding an NSKeyedArchiver "
                  "archive of the model: Z followed by the property name in capitals, with 1, 2 "
                  "and so on added when entities of the same table with lower numbers in "
                  "Z_PRIMARYKEY define a property of that name themselves, and a property an "
                  "entity inherits is read from the column of the entity that defines it. That "
                  "rule comes from measurement. On the 99 Reminders stores of the 22 registered "
                  "iOS images that carry them it names a column that exists for all 93,336 "
                  "attributes and to-one relationships their entities list, and in all 3,303 "
                  "cases on those stores where an entity defines a property name that another "
                  "entity of its table also defines, no row outside that entity and its "
                  "subentities has a value in its column of that name; its own rows have one in "
                  "349 of those cases, and reversing the entity order fails 349 of them. On those "
                  "stores ordering the entities by name gives the same columns as ordering them "
                  "by number, so the measurement does not tell those two orders apart. By that "
                  "rule a reminder's title is in ZTITLE1 on the iOS 13.3.1, 14.3, 15.0.2 and "
                  "15.3.1 test images, the column a guest post on Ciofeca Forensics read a "
                  "reminder's title from in the Reminders database of an iPhone from the "
                  "Cellebrite 2020 CTF, on iOS 13.6 according to that post (Reference: Ciofeca "
                  "Forensics, 'Cellebrite CTF 2020: Ruth Langmore', "
                  "https://www.ciofecaforensics.com/2020/11/02/cellebrite-ctf-ruth/), and on the "
                  "two iOS 15 images a reminder's creation date is in ZCREATIONDATE1, because "
                  "REMCDHashtag, entity 24, also defines creationDate and has the lower number. "
                  "None of the 20 older-generation stores on those images holds a reminder, with "
                  "or without its write-ahead log applied, so reading reminders of that "
                  "generation has been tested only on stores built by the unit tests and on a "
                  "copy of an iOS 15.0.2 store with one reminder row added, not on reminders from "
                  "a device. A store of that generation whose model cannot be read, or whose "
                  "model and Z_PRIMARYKEY do not lead to a REMCDReminder entity number and a "
                  "table the store has, is logged and not read, and a property whose column "
                  "cannot be decided or is missing is logged and reported blank; neither happened "
                  "on the tested stores. On the iOS 17 and later test images the store sits in "
                  "the Reminders app-group container (group.com.apple.reminders) rather than "
                  "Library/Reminders/Container_v1. Only reminders are reported; the accounts, "
                  "lists, alarms and other entities of the stores are not. Completed, Flagged and "
                  "Marked for Deletion are integer flags reported as stored; rows marked for "
                  "deletion are included. On the 64 reminders of the six test images that hold "
                  "any, Flagged held 0 on every row, Completed held 1 on 12 and Marked for "
                  "Deletion held 1 on 1."),
        "paths": ('*/Container_v1/Stores/*.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "hickman_ios13": "iOS 13.3.1 | 0 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "belkactf6": "iOS 16.3 | 14 rows (run against the decrypted filesystem copy)",
            "abe_ios16": "iOS 16.5 | 2 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 2 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 6 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 37 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        }
    }
}

import os
import plistlib
import zlib

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    does_table_exist_in_db, logfunc

# The newer layout: reminders have a table of their own, ZREMCDREMINDER, and each
# property is read from its unnumbered column.
_COLUMNS = '''
        DATETIME(ZCREATIONDATE + 978307200, 'UNIXEPOCH'),
        DATETIME(ZLASTMODIFIEDDATE + 978307200, 'UNIXEPOCH'),
        DATETIME(ZDUEDATE + 978307200, 'UNIXEPOCH'),
        DATETIME(ZCOMPLETIONDATE + 978307200, 'UNIXEPOCH'),
        ZTITLE,
        ZNOTES,
        ZCOMPLETED,
        ZFLAGGED,
        ZMARKEDFORDELETION
'''

_REMINDER = 'REMCDReminder'
# REMCDReminder properties read from the older layout, in column order, and whether each
# is a date.
_PROPERTIES = (('creationDate', True), ('lastModifiedDate', True), ('dueDate', True),
               ('completionDate', True), ('title', False), ('notes', False),
               ('completed', False), ('flagged', False), ('markedForDeletion', False))
_COLUMN_KINDS = ('attribute', 'to-one')


def _model(blob):
    """{entity: (superentity or None, {property: (owned, kind, destination)})} from a
    Z_MODELCACHE blob, or None when it cannot be read. kind is 'attribute', 'to-one',
    'to-many' or the class name of anything else. owned is False for a property its
    superentity also lists: a subentity lists its superentity's properties as well as its own,
    and archives differ in how they store an inherited one (a _NSPropertyDescriptionProxy of
    the superentity's description, or a copy of it), so the name is what decides."""
    try:
        archive = plistlib.loads(zlib.decompress(bytes(blob), -15))
    except (zlib.error, plistlib.InvalidFileException, ValueError, TypeError, OverflowError):
        return None
    objects = archive.get('$objects') if isinstance(archive, dict) else None
    if not isinstance(objects, list):
        return None

    def get(value):
        if isinstance(value, plistlib.UID):
            return objects[value.data] if value.data < len(objects) else None
        return value

    def class_name(item):
        meta = get(item.get('$class')) if isinstance(item, dict) else None
        return meta.get('$classname') if isinstance(meta, dict) else None

    def entity_name(value):
        value = get(value)
        return get(value.get('NSEntityName')) if isinstance(value, dict) else None

    def describe(item):
        kind = class_name(item)
        if kind == 'NSAttributeDescription':
            return 'attribute', None
        if kind == 'NSRelationshipDescription':
            destination = get(item.get('_NSDestinationEntityName')) or \
                entity_name(item.get('NSDestinationEntity'))
            return ('to-one' if get(item.get('NSMaxCount')) == 1 else 'to-many'), destination
        return kind, None

    model = {}
    for item in objects:
        if class_name(item) != 'NSEntityDescription':
            continue
        properties = {}
        table = get(item.get('NSProperties'))
        if isinstance(table, dict):
            for key, value in zip(table.get('NS.keys', []), table.get('NS.objects', [])):
                prop = get(value)
                if class_name(prop) == '_NSPropertyDescriptionProxy':
                    prop = get(prop.get('NSUnderlyingProperty'))
                properties[get(key)] = describe(prop)
        name = get(item.get('NSEntityName'))
        if isinstance(name, str):
            model[name] = (entity_name(item.get('NSSuperentity')), properties)
    return {name: (parent, {prop: (not (parent in model and prop in model[parent][1]), *kind)
                            for prop, kind in props.items()})
            for name, (parent, props) in model.items()} or None


def _root(model, entity):
    seen = set()
    while model.get(entity, (None,))[0] in model and entity not in seen:
        seen.add(entity)
        entity = model[entity][0]
    return entity


def _owner(model, entity, prop):
    """The entity that defines prop for entity: itself, or the ancestor it inherits it from."""
    seen = set()
    while entity in model and entity not in seen:
        seen.add(entity)
        owned = model[entity][1].get(prop, (False,))[0]
        if owned:
            return entity
        entity = model[entity][0]
    return None


def _column(model, order, entity, prop):
    """The column Core Data stores prop of entity in: Z and the property name in capitals,
    followed by 1, 2, ... when entities of the same table with lower entity numbers define a
    property of that name themselves. None when prop has no column of its own (to-many and
    other kinds), when an entity of the table defines that name as anything other than an
    attribute or a to-one relationship, or when an entity number is missing."""
    owner = _owner(model, entity, prop)
    if owner is None or model[owner][1][prop][1] not in _COLUMN_KINDS:
        return None
    root = _root(model, entity)
    owners = [name for name, (_parent, props) in model.items()
              if _root(model, name) == root and props.get(prop, (False,))[0]]
    if any(model[name][1][prop][1] not in _COLUMN_KINDS for name in owners):
        return None
    if any(name not in order for name in owners):
        return None
    owners.sort(key=lambda name: order[name])
    index = owners.index(owner)
    return f'Z{prop.upper()}{index if index else ""}'



def _quote(name):
    return '"' + str(name).replace('"', '""') + '"'


def _older_layout_query(file_found, relative):
    """(query, names of the properties that have no column) for the reminders of a store in
    the older layout, or (None, why the store cannot be read that way). The table and the
    column of each property are worked out from the model the store caches in Z_MODELCACHE,
    because in that layout reminders share ZREMCDOBJECT with other entities and a property
    name several of them define is kept in numbered columns (ZTITLE, ZTITLE1, ...)."""
    rows = list(get_sqlite_db_records(file_found, 'SELECT Z_CONTENT FROM Z_MODELCACHE')) \
        if does_table_exist_in_db(file_found, 'Z_MODELCACHE') else []
    model = _model(rows[0][0]) if rows and rows[0][0] else None
    if not model:
        return None, f'no readable Core Data model in {relative}'
    if _REMINDER not in model:
        return None, f'no {_REMINDER} entity in the model of {relative}'
    order = {row[0]: row[1] for row in get_sqlite_db_records(
        file_found, 'SELECT Z_NAME, Z_ENT FROM Z_PRIMARYKEY')} \
        if does_table_exist_in_db(file_found, 'Z_PRIMARYKEY') else {}
    if _REMINDER not in order:
        return None, f'no entity number for {_REMINDER} in {relative}'
    table = f'Z{_root(model, _REMINDER).upper()}'
    if not does_table_exist_in_db(file_found, table):
        return None, f'no {table} table for {_REMINDER} in {relative}'
    columns = {row[1] for row in get_sqlite_db_records(
        file_found, f'PRAGMA table_info({_quote(table)})')}
    select, unresolved = [], []
    for prop, is_date in _PROPERTIES:
        column = _column(model, order, _REMINDER, prop)
        if column not in columns:
            select.append('NULL')
            unresolved.append(prop)
        elif is_date:
            select.append(f"DATETIME({_quote(column)} + 978307200, 'UNIXEPOCH')")
        else:
            select.append(_quote(column))
    return (f'SELECT {", ".join(select)} FROM {_quote(table)} '
            f'WHERE Z_ENT = {int(order[_REMINDER])}', unresolved)


@artifact_processor
def reminders(context):
    data_headers = (
        ('Creation Date', 'datetime'),
        ('Last Modified', 'datetime'),
        ('Due Date', 'datetime'),
        ('Completion Date', 'datetime'),
        'Title',
        'Notes',
        'Completed',
        'Flagged',
        'Marked for Deletion',
        'File Location')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('.sqlite'):
            continue
        if os.path.basename(file_found).startswith('._'):
            continue    # AppleDouble sidecar, not a database

        rel_path = context.get_relative_path(file_found)
        if does_table_exist_in_db(file_found, 'ZREMCDREMINDER'):
            query = f'SELECT {_COLUMNS} FROM ZREMCDREMINDER'
        elif does_table_exist_in_db(file_found, 'ZREMCDOBJECT'):
            query, detail = _older_layout_query(file_found, rel_path)
            if query is None:
                logfunc(f'Reminders: {detail}; store not read')
                continue
            if detail:
                logfunc(f'Reminders: no column found for {", ".join(detail)} in {rel_path}; '
                        'reported blank')
        else:
            continue

        rows_seen = False
        for row in get_sqlite_db_records(file_found, query):
            data_list.append(tuple(row) + (rel_path,))
            rows_seen = True
        if rows_seen:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
