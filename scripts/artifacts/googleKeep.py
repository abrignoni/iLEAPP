__artifacts_v2__ = {
    "googleKeepNotes": {
        "name": "Google Keep - Notes",
        "description": "One row per note or list in KeepStore.sqlite (ZTOPLEVELNODE), the Core Data "
                       "store in the group.com.google.Keep app group. Text is the text of the list "
                       "items stored under a NOTE row; a LIST row gives its item count instead, and its"
                       " items are in Google Keep - List Items. Labels come from ZNODELABEL joined to "
                       "ZLABEL and Sharees from ZSHAREE.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Google Keep",
        "notes": "Times are Core Data timestamps (seconds since 2001-01-01 UTC) converted to UTC. A "
                 "value within one second of 1970-01-01 00:00:00 UTC is reported blank. Every note in "
                 "the known data held that value in ZTIMETRASHED and ZTIMEDELETED, so Time Trashed and "
                 "Time Deleted were blank on every row and a trashed or deleted note was not exercised."
                 " Type, Color and the Sharees role are reported as stored; what each role letter means"
                 " is not established. Archived and Pinned are ZISARCHIVED and ZISPINNED. Every NOTE "
                 "row in the known data had exactly one ZLISTITEM row under it, and ZTOPLEVELNODE.ZTEXT"
                 " was empty on every row, so ZTEXT is not reported. List items are joined to their "
                 "note by client id and account id, which all three store versions seen carry. The iOS "
                 "27 store also has a ZPARENT key on ZLISTITEM, and the two joins matched the same rows"
                 " there. Labels and sharees are joined by ZNODE. A label link with a ZTIMEDELETED is "
                 "left out of Labels; the known data held no such link. Account is "
                 "ZACCOUNT.ZACCOUNTNAME for the row's account id; Account held one value on every row "
                 "in the known data. Not reported, among other columns: ZQUILLTEXT, ZQUILLTHUMBNAIL, "
                 "ZTASKREFERENCE and ZERRORSTATUS (no rows in any store seen), ZREMINDERSMIGRATION "
                 "(migration counters), the ZACCOUNT sync flags, and the ZACCOUNT creation and "
                 "last-sync times. Rows already removed from the tables are not recovered. The store is"
                 " read when its container's metadata plist names group.com.google.Keep, or when no "
                 "identifier could be read from a metadata plist in that container. Built from a "
                 "private iPhone known-data image on iOS 27, which cannot be cited.",
        "paths": ('*/Containers/Shared/AppGroup/*/KeepStore.sqlite*',
                  '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "notebook",
        "sample_data": {
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows (KeepStore.sqlite present, every entity table empty)",
        },
    },
    "googleKeepListItems": {
        "name": "Google Keep - List Items",
        "description": "One row per list item in KeepStore.sqlite (ZLISTITEM), with the note or list it"
                       " belongs to. Parent Type is that parent's ZTYPE, so the body of a NOTE appears "
                       "here as well as on its row in Google Keep - Notes.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Google Keep",
        "notes": "Times are Core Data timestamps (seconds since 2001-01-01 UTC) converted to UTC. A "
                 "value within one second of 1970-01-01 00:00:00 UTC is reported blank. On the iOS 27 "
                 "known-data store every ZLISTITEM time column held such a value on every row, so Time "
                 "Created, Time Updated, Time Trashed and Time Deleted were blank on every row there; "
                 "on the iOS 16.1.1 store Time Created and Time Updated held times. Checked is ZCHECKED"
                 " and was set only on items of LIST rows. Parent Item ID is ZPARENTLISTITEMID; Parent "
                 "Item ID was empty on every row seen, so nested items were not exercised. Sort Value "
                 "is ZSORTVALUE as stored. Account is ZACCOUNT.ZACCOUNTNAME for the row's account id; "
                 "Account held one value on every row in the known data. The store is read when its "
                 "container's metadata plist names group.com.google.Keep, or when no identifier could "
                 "be read from a metadata plist in that container. Built from a private iPhone "
                 "known-data image on iOS 27, which cannot be cited.",
        "paths": ('*/Containers/Shared/AppGroup/*/KeepStore.sqlite*',
                  '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "list-check",
        "sample_data": {
            "magnet_ios16": "iOS 16.1.1 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows (KeepStore.sqlite present, every entity table empty)",
        },
    },
    "googleKeepAnnotations": {
        "name": "Google Keep - Annotations",
        "description": "One row per annotation in KeepStore.sqlite (ZANNOTATION), with the note it is "
                       "attached to: web link title, URL and description, and topic category.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Google Keep",
        "notes": "Time Deleted is ZTIMEDELETED converted from Core Data time to UTC, blank within one "
                 "second of 1970-01-01 00:00:00 UTC. In the known data some rows carried a Time Deleted"
                 " while their note was still in the store and was not trashed or deleted. Whether the "
                 "app still shows such an annotation was not checked. Topic Category is reported as "
                 "stored. Is Context Source is ZISCONTEXTSOURCE; its meaning is not established. Not "
                 "reported: ZSUGGESTTYPE (empty on every row seen) and ZWEBLINKIMAGEURL (a column only "
                 "in the iOS 16.1.1 store, which held no annotations). Account is ZACCOUNT.ZACCOUNTNAME"
                 " for the account id of the annotation's note; Account held one value on every row in "
                 "the known data. The store is read when its container's metadata plist names "
                 "group.com.google.Keep, or when no identifier could be read from a metadata plist in "
                 "that container. Built from a private iPhone known-data image on iOS 27, which cannot "
                 "be cited.",
        "paths": ('*/Containers/Shared/AppGroup/*/KeepStore.sqlite*',
                  '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist'),
        "output_types": "standard",
        "artifact_icon": "link",
        "sample_data": {
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows (KeepStore.sqlite present, every entity table empty)",
        },
    },
    "googleKeepMedia": {
        "name": "Google Keep - Media",
        "description": "One row per media item in KeepStore.sqlite (ZMEDIAITEM), joined to its blob "
                       "node (ZBLOBNODE) and note, with the file the item's ZLOCALPATH names in the app"
                       " group shown as media. Extracted Text is ZBLOBNODE.ZEXTRACTEDTEXT. A media file"
                       " in the app group that no item names gets a row of its own.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Google Keep",
        "notes": "ZLOCALPATH is resolved against the app group folder that holds the same "
                 "KeepStore.sqlite. In the known data the same relative path under that folder's "
                 "compressed/ subfolder held a smaller JPEG for every image, shown as Compressed Copy; "
                 "that the app made it from the original is not established. The four time columns are "
                 "ZBLOBNODE times. Items with no ZBLOBNODE are kept, with the time, blob, note and "
                 "Account columns blank. Several items named the same file, so a file can appear on "
                 "more than one row. Times are Core Data timestamps (seconds since 2001-01-01 UTC) "
                 "converted to UTC. A value within one second of 1970-01-01 00:00:00 UTC is reported "
                 "blank. Time Trashed and Time Deleted were blank on every row seen. Media Type, Blob "
                 "Type, Extraction Status and Data Transfer State are reported as stored; what the Data"
                 " Transfer State numbers mean is not established. Media Type held IMAGE_MEDIA and MIME"
                 " Type image/png on every row seen, and File Present was Yes on every row: the "
                 "unreferenced-file row, given for every Keep app group folder whether or not its store"
                 " could be read, was exercised only on a constructed folder. Not reported: ZLENGTH (0 "
                 "on every row seen) and ZSOURCEURI (NULL on every row seen). Account is "
                 "ZACCOUNT.ZACCOUNTNAME for the blob node's account id. The store is read when its "
                 "container's metadata plist names group.com.google.Keep, or when no identifier could "
                 "be read from a metadata plist in that container. Built from a private iPhone "
                 "known-data image on iOS 27, which cannot be cited.",
        "paths": ('*/Containers/Shared/AppGroup/*/KeepStore.sqlite*',
                  '*/Containers/Shared/AppGroup/*/.com.apple.mobile_container_manager.metadata.plist',
                  '*/Containers/Shared/AppGroup/*_MEDIA'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "iphone12_ios18": "iOS 18.7 | 0 rows (KeepStore.sqlite present, every entity table empty)",
        },
    },
}


import os
import plistlib
import re
import sqlite3

from scripts.ilapfuncs import (artifact_processor, check_in_media, convert_cocoa_core_data_ts_to_utc,
                               logfunc, open_sqlite_db_readonly)

_METADATA_NAME = '.com.apple.mobile_container_manager.metadata.plist'
_APP_GROUP = 'group.com.google.Keep'
_CONTAINER_RE = re.compile(r'^(.*/Containers/(?:Data/Application|Shared/AppGroup)/[^/]+)/')
# Core Data time of the Unix epoch. The store writes it, or a value a millisecond past it,
# into time columns that carry no event, so anything within a second of it is left blank.
_UNIX_EPOCH_IN_COCOA = -978307200


def _norm(path):
    return str(path).replace('\\', '/')


def _container_root(path):
    match = _CONTAINER_RE.match(_norm(path))
    return match.group(1) if match else ''


def _container_apps(files_found):
    '''Map each container folder to the bundle id its metadata plist records.'''
    apps = {}
    for found in files_found:
        found = _norm(found)
        if os.path.basename(found) != _METADATA_NAME:
            continue
        try:
            with open(found, 'rb') as handle:
                plist = plistlib.load(handle)
        except (plistlib.InvalidFileException, OSError, ValueError) as error:
            logfunc(f'Google Keep: could not read a container metadata plist: {error}')
            continue
        bundle_id = plist.get('MCMMetadataIdentifier') if isinstance(plist, dict) else None
        if bundle_id:
            apps[os.path.dirname(found)] = bundle_id
    return apps


def _keep_stores(files_found):
    '''KeepStore.sqlite files in containers that are, or may be, the Keep app group.'''
    apps = _container_apps(files_found)
    stores = []
    for found in files_found:
        found = str(found)
        if os.path.basename(found) != 'KeepStore.sqlite' or os.path.isdir(found):
            continue
        root = _container_root(found)
        bundle_id = apps.get(root)
        if bundle_id is None:
            logfunc(f'Google Keep: no container metadata plist beside {os.path.basename(found)}; '
                    'reading it as the Keep app group')
        elif bundle_id != _APP_GROUP:
            logfunc(f'Google Keep: skipping a KeepStore.sqlite in a container of {bundle_id}')
            continue
        stores.append((found, root))
    return sorted(stores)


def _when(value):
    '''Core Data time to UTC, blank for NULL and for the stored Unix-epoch placeholder.'''
    if value is None or value == '':
        return ''
    try:
        if abs(float(value) - _UNIX_EPOCH_IN_COCOA) < 1:
            return ''
    except (TypeError, ValueError):
        return ''
    return convert_cocoa_core_data_ts_to_utc(value)


def _yes_no(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _columns(cursor, table):
    try:
        cursor.execute(f"PRAGMA table_info('{table}')")
        return {row[1] for row in cursor.fetchall()}
    except sqlite3.Error:
        return set()


def _select(cursor, table, alias, wanted):
    '''Column expressions for a SELECT, NULL for columns this store generation lacks.'''
    have = _columns(cursor, table)
    return ', '.join(f'{alias}.{col}' if col in have else 'NULL' for col in wanted)


def _fetch(cursor, query, store):
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as error:
        logfunc(f'Google Keep: query failed on {os.path.basename(store)}: {error}')
        return []


def _has_tables(cursor, *tables):
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        present = {row[0] for row in cursor.fetchall()}
    except sqlite3.Error as error:
        logfunc(f'Google Keep: could not read the schema of a store: {error}')
        return False
    return all(table in present for table in tables)


# Notes and lists are joined to their children by client id and account id: the older
# store generation has no Z_PK foreign key columns for these relationships.
_NODE_JOIN = 'p.ZCLIENTID = {child}.ZPARENTID AND p.ZACCOUNTID = {child}.ZACCOUNTID'


def _accounts(cursor):
    if 'ZACCOUNTNAME' not in _columns(cursor, 'ZACCOUNT'):
        return {}
    rows = _fetch(cursor, 'SELECT ZACCOUNTID, ZACCOUNTNAME FROM ZACCOUNT', '')
    return {row[0]: row[1] or '' for row in rows if row[0]}


@artifact_processor
def googleKeepNotes(context):
    data_list = []
    sources = []
    for store, _root in _keep_stores(context.get_files_found()):
        db = open_sqlite_db_readonly(store)
        if db is None:
            continue
        cursor = db.cursor()
        if not _has_tables(cursor, 'ZTOPLEVELNODE'):
            logfunc(f'Google Keep: no ZTOPLEVELNODE table in {os.path.basename(store)}')
            db.close()
            continue
        sources.append(store)
        accounts = _accounts(cursor)
        cols = _select(cursor, 'ZTOPLEVELNODE', 'p', (
            'Z_PK', 'ZTIMECREATED', 'ZTIMEUPDATED', 'ZTIMEUSEREDITED', 'ZTIMETRASHED', 'ZTIMEDELETED',
            'ZTYPE', 'ZTITLE', 'ZISARCHIVED', 'ZISPINNED', 'ZCOLOR', 'ZLASTMODIFIEREMAIL', 'ZACCOUNTID',
            'ZSERVERID', 'ZCLIENTID'))
        nodes = _fetch(cursor, f'SELECT {cols} FROM ZTOPLEVELNODE p ORDER BY p.ZTIMECREATED', store)

        children = {}
        if _has_tables(cursor, 'ZLISTITEM'):
            item_sort = 'l.ZSORTVALUE DESC, ' if 'ZSORTVALUE' in _columns(cursor, 'ZLISTITEM') else ''
            for pk, text in _fetch(cursor, f'''
                    SELECT p.Z_PK, l.ZTEXT FROM ZLISTITEM l
                    JOIN ZTOPLEVELNODE p ON {_NODE_JOIN.format(child="l")}
                    ORDER BY {item_sort}l.Z_PK''', store):
                children.setdefault(pk, []).append(text or '')

        labels = {}
        if _has_tables(cursor, 'ZNODELABEL', 'ZLABEL'):
            for pk, name in _fetch(cursor, f'''
                    SELECT n.ZNODE, b.ZNAME FROM ZNODELABEL n
                    JOIN ZLABEL b ON b.ZLABELID = n.ZLABELID
                    WHERE n.ZTIMEDELETED IS NULL OR abs(n.ZTIMEDELETED - ({_UNIX_EPOCH_IN_COCOA})) < 1
                    ORDER BY b.ZNAME''', store):
                labels.setdefault(pk, []).append(name or '')

        sharees = {}
        if _has_tables(cursor, 'ZSHAREE'):
            for pk, email, role in _fetch(cursor, 'SELECT ZNODE, ZEMAIL, ZROLE FROM ZSHAREE ORDER BY Z_PK',
                                          store):
                sharees.setdefault(pk, []).append(f'{email or ""} ({role or ""})')
        db.close()

        for (pk, created, updated, edited, trashed, deleted, node_type, title, archived, pinned, color,
             modifier, account_id, server_id, client_id) in nodes:
            items = children.get(pk, [])
            is_list = node_type == 'LIST'
            data_list.append((
                _when(created), _when(updated), _when(edited), _when(trashed), _when(deleted),
                node_type or '', title or '',
                '' if is_list else '\n'.join(items),
                len(items) if is_list else '',
                ', '.join(labels.get(pk, [])), '\n'.join(sharees.get(pk, [])),
                _yes_no(archived), _yes_no(pinned), color or '', modifier or '',
                accounts.get(account_id, ''), server_id or '', client_id or ''))

    data_headers = (
        ('Time Created', 'datetime'), ('Time Updated', 'datetime'), ('Time User Edited', 'datetime'),
        ('Time Trashed', 'datetime'), ('Time Deleted', 'datetime'), 'Type', 'Title', 'Text',
        'List Item Count', 'Labels', 'Sharees (email, role as stored)', 'Archived', 'Pinned', 'Color',
        'Last Modifier Email', 'Account', 'Server ID', 'Client ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def googleKeepListItems(context):
    data_list = []
    sources = []
    for store, _root in _keep_stores(context.get_files_found()):
        db = open_sqlite_db_readonly(store)
        if db is None:
            continue
        cursor = db.cursor()
        if not _has_tables(cursor, 'ZLISTITEM', 'ZTOPLEVELNODE'):
            logfunc(f'Google Keep: no ZLISTITEM table in {os.path.basename(store)}')
            db.close()
            continue
        sources.append(store)
        accounts = _accounts(cursor)
        cols = _select(cursor, 'ZLISTITEM', 'l', (
            'ZTIMECREATED', 'ZTIMEUPDATED', 'ZTIMETRASHED', 'ZTIMEDELETED', 'ZTEXT', 'ZCHECKED',
            'ZSORTVALUE', 'ZPARENTLISTITEMID', 'ZACCOUNTID', 'ZSERVERID'))
        rows = _fetch(cursor, f'''
            SELECT {cols}, p.ZTYPE, p.ZTITLE, p.ZSERVERID FROM ZLISTITEM l
            LEFT JOIN ZTOPLEVELNODE p ON {_NODE_JOIN.format(child="l")}
            ORDER BY p.Z_PK, l.Z_PK''', store)
        db.close()
        for (created, updated, trashed, deleted, text, checked, sort_value, parent_item, account_id,
             server_id, parent_type, parent_title, parent_server_id) in rows:
            data_list.append((
                _when(created), _when(updated), _when(trashed), _when(deleted), text or '',
                _yes_no(checked), parent_type or '', parent_title or '', parent_item or '',
                sort_value if sort_value is not None else '', accounts.get(account_id, ''),
                server_id or '', parent_server_id or ''))

    data_headers = (
        ('Time Created', 'datetime'), ('Time Updated', 'datetime'), ('Time Trashed', 'datetime'),
        ('Time Deleted', 'datetime'), 'Text', 'Checked', 'Parent Type', 'Parent Title',
        'Parent Item ID', 'Sort Value', 'Account', 'Server ID', 'Parent Server ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def googleKeepAnnotations(context):
    data_list = []
    sources = []
    for store, _root in _keep_stores(context.get_files_found()):
        db = open_sqlite_db_readonly(store)
        if db is None:
            continue
        cursor = db.cursor()
        if not _has_tables(cursor, 'ZANNOTATION', 'ZTOPLEVELNODE'):
            logfunc(f'Google Keep: no ZANNOTATION table in {os.path.basename(store)}')
            db.close()
            continue
        sources.append(store)
        accounts = _accounts(cursor)
        cols = _select(cursor, 'ZANNOTATION', 'a', (
            'ZTIMEDELETED', 'ZWEBLINKTITLE', 'ZWEBLINKURL', 'ZWEBLINKDESCRIPTION', 'ZWEBLINKPROVENANCEURL',
            'ZTOPICCATEGORY', 'ZISCONTEXTSOURCE', 'ZANNOTATIONID'))
        rows = _fetch(cursor, f'''
            SELECT {cols}, p.ZTITLE, p.ZTYPE, p.ZACCOUNTID, p.ZSERVERID FROM ZANNOTATION a
            LEFT JOIN ZTOPLEVELNODE p ON p.Z_PK = a.ZNODE
            ORDER BY a.ZNODE, a.Z_PK''', store)
        db.close()
        for (deleted, link_title, url, description, provenance, topic, context_source, annotation_id,
             note_title, note_type, account_id, note_server_id) in rows:
            data_list.append((
                _when(deleted), note_title or '', note_type or '', link_title or '', url or '',
                description or '', provenance or '', topic or '',
                _yes_no(context_source), annotation_id or '', accounts.get(account_id, ''),
                note_server_id or ''))

    data_headers = (
        ('Time Deleted', 'datetime'), 'Note Title', 'Note Type', 'Web Link Title', 'Web Link URL',
        'Web Link Description', 'Web Link Provenance URL', 'Topic Category', 'Is Context Source',
        'Annotation ID', 'Account', 'Note Server ID')
    return data_headers, data_list, '\n'.join(sources)


def _media_index(files_found):
    '''Staged media files by their normalised path.'''
    return {_norm(f): str(f) for f in files_found if str(f).endswith('_MEDIA') and os.path.isfile(str(f))}


def _media_ref(index, path, name):
    found = index.get(_norm(path))
    if not found:
        return ''
    return check_in_media(found, name) or ''


@artifact_processor
def googleKeepMedia(context):
    files_found = context.get_files_found()
    index = _media_index(files_found)
    data_list = []
    sources = []
    named = set()
    stores = _keep_stores(files_found)
    # Media is listed for every Keep app group folder, whether or not its store could be read.
    roots = {root for _store, root in stores}
    roots.update(folder for folder, bundle_id in _container_apps(files_found).items()
                 if bundle_id == _APP_GROUP)
    for store, root in stores:
        db = open_sqlite_db_readonly(store)
        if db is None:
            continue
        cursor = db.cursor()
        if not _has_tables(cursor, 'ZMEDIAITEM'):
            logfunc(f'Google Keep: no ZMEDIAITEM table in {os.path.basename(store)}')
            db.close()
            continue
        sources.append(store)
        accounts = _accounts(cursor)
        media_cols = _select(cursor, 'ZMEDIAITEM', 'm', (
            'ZLOCALPATH', 'ZMEDIATYPE', 'ZMIMETYPE', 'ZWIDTH', 'ZHEIGHT', 'ZBYTESIZE', 'ZDATATRANSFERSTATE',
            'ZMEDIAID'))
        blob_cols = _select(cursor, 'ZBLOBNODE', 'b', (
            'ZTIMECREATED', 'ZTIMEUPDATED', 'ZTIMETRASHED', 'ZTIMEDELETED', 'ZBLOBTYPE', 'ZEXTRACTEDTEXT',
            'ZEXTRACTIONSTATUS', 'ZACCOUNTID', 'ZSERVERID'))
        have_blob = _has_tables(cursor, 'ZBLOBNODE')
        have_node = _has_tables(cursor, 'ZTOPLEVELNODE')
        joins = ''
        if have_blob:
            joins += ' LEFT JOIN ZBLOBNODE b ON b.Z_PK = m.ZBLOBNODE'
            if have_node:
                joins += f' LEFT JOIN ZTOPLEVELNODE p ON {_NODE_JOIN.format(child="b")}'
        else:
            blob_cols = ', '.join(['NULL'] * 9)
        node_cols = 'p.ZTITLE, p.ZTYPE' if have_blob and have_node else 'NULL, NULL'
        rows = _fetch(cursor, f'SELECT {blob_cols}, {media_cols}, {node_cols} FROM ZMEDIAITEM m{joins} '
                              'ORDER BY m.Z_PK', store)
        db.close()

        for (created, updated, trashed, deleted, blob_type, extracted, extraction, account_id, blob_server_id,
             local_path, media_type, mime, width, height, byte_size, transfer, media_id, note_title,
             note_type) in rows:
            media = compressed = ''
            if local_path:
                original = f'{root}/{local_path.lstrip("/")}'
                smaller = f'{root}/compressed/{local_path.lstrip("/")}'
                named.update((_norm(original), _norm(smaller)))
                media = _media_ref(index, original, os.path.basename(local_path))
                compressed = _media_ref(index, smaller, os.path.basename(local_path))
            data_list.append((
                _when(created), _when(updated), _when(trashed), _when(deleted), media, compressed,
                note_title or '', note_type or '', extracted or '', extraction or '', media_type or '',
                blob_type or '', mime or '', width if width is not None else '',
                height if height is not None else '', byte_size if byte_size is not None else '',
                transfer if transfer is not None else '',
                local_path or '', 'Yes' if media else 'No', media_id or '',
                accounts.get(account_id, ''), blob_server_id or ''))

    for root in sorted(roots):
        root_prefix = _norm(root) + '/'
        for path in sorted(index):
            if not path.startswith(root_prefix) or path in named:
                continue
            relative = path[len(root_prefix):]
            data_list.append((
                '', '', '', '', _media_ref(index, path, os.path.basename(path)), '', '', '',
                '', '', '', '', '', '', '', '', '', relative,
                'Yes (named by no media item)', '', '', ''))
            sources.append(index[path])

    data_headers = (
        ('Time Created', 'datetime'), ('Time Updated', 'datetime'), ('Time Trashed', 'datetime'),
        ('Time Deleted', 'datetime'), ('Media', 'media'), ('Compressed Copy', 'media'), 'Note Title',
        'Note Type', 'Extracted Text', 'Extraction Status', 'Media Type', 'Blob Type', 'MIME Type',
        'Width', 'Height', 'Byte Size', 'Data Transfer State', 'Local Path', 'File Present',
        'Media ID', 'Account', 'Blob Server ID')
    return data_headers, data_list, '\n'.join(sources)
