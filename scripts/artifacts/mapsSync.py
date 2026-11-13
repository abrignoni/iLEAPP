__artifacts_v2__ = {
    "mapsSync": {
        "name": "Maps Sync",
        "description": "Apple Maps MapsSync history rows, with each row's entity named from the store's own "
                       "Z_PRIMARYKEY table and the stored Z_ENT value.",
        "author": '@AlexisBrignoni, Codex',
        "creation_date": "2026-06-23",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "Location",
        "notes": "Journey/Map Item addresses are decoded from protobuf BLOBs. Query courtesy of "
                 "CheekyForensicsMonkey "
                 "(https://cheeky4n6monkey.blogspot.com/2020/11/ios14-maps-history-blob-script.html). "
                 "Whether an entry was created on this device or synced from another device on the same "
                 "account is not established here, and an entry is not evidence that travel took place. "
                 "Original parser attribution: @abrignoni. Entity (Z_PRIMARYKEY Name) is the Z_NAME that "
                 "the same store's Z_PRIMARYKEY table gives for the row's Z_ENT, as stored; what each "
                 "entity records is not interpreted here. Entity numbers differ between stores: across "
                 "the 22 tested stores the Z_PRIMARYKEY table gives Z_ENT 16 five different names, the "
                 "numbers in the fixed list used before this change (12, 14 and 16) each name several "
                 "different entities, and 201 of the 248 tested rows carry a Z_ENT value outside that "
                 "list. Z_ENT (As Stored) is the direct SQLite value when the selected schema exposes the "
                 "column; fallback schemas without the column report SQL NULL, and their rows have a "
                 "blank Entity. A blank Entity also results when the store has no Z_PRIMARYKEY table or "
                 "that table has no row for the stored Z_ENT. That output does not distinguish an absent "
                 "column from a stored NULL.",
        "paths": ('*/MapsSync_0.0.1*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | com.apple.Maps | 50 rows",
            "felix_ios17": "iOS 17.6.1 | com.apple.Maps | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | com.apple.Maps | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | com.apple.Maps | 2 rows",
            "iphone11_ios17": "iOS 17.3 | com.apple.Maps | 48 rows",
            "iphone12_ios18": "iOS 18.7 | com.apple.Maps | 12 rows",
            "iphone14plus_ios18": "iOS 18.0 | com.apple.Maps | 0 rows",
            "otto_ios17": "iOS 17.5.1 | com.apple.Maps | 28 rows",
            "abe_ios16": "iOS 16.5 | com.apple.Maps | 36 rows",
            "felix23_ios16": "iOS 16.5 | com.apple.Maps | 1 row",
            "hickman_ios14": "iOS 14.3 | com.apple.Maps | 15 rows",
            "jess_ios15": "iOS 15.0.2 | com.apple.Maps | 5 rows",
            "magnet_ios16": "iOS 16.1.1 | com.apple.Maps | 2 rows",
            "adams_iphone12mini": "iOS 17.1.1 | com.apple.Maps | 2 rows",
            "belkactf6_tar": "iOS 16.3 | com.apple.Maps | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | com.apple.Maps | 2 rows",
            "falken_ios26": "iOS 26.2.1 | com.apple.Maps | 3 rows",
            "hc_ios17_2": "iOS 17.2.1 | com.apple.Maps | 4 rows",
            "hc_ios26": "iOS 26.5.2 | com.apple.Maps | 2 rows",
            "hexordia_ios1651": "iOS 16.5.1 | com.apple.Maps | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | com.apple.Maps | 27 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | com.apple.Maps | 5 rows",
        }
    },
    "mapsFavorites": {
        "name": "Maps Favorites",
        "description": "Rows of the ZFAVORITEITEM table of Apple Maps MapsSync_0.0.1, with the name, coordinates and "
                       "decoded address where the row stores them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-13",
        "last_update_date": "2026-11-13",
        "requirements": "none",
        "category": "Location",
        "notes": (
                 "Source is the ZFAVORITEITEM table of the Apple Maps store MapsSync_0.0.1 (in the Maps "
                 "folder of a shared app group container). Created and Modified are ZCREATETIME and "
                 "ZMODIFICATIONTIME, Core Data seconds since 2001, shown in UTC. Name is ZCUSTOMNAME as "
                 "stored and is blank when the row stores none; it was blank on 9 of the 12 rows tested. "
                 "Favorite Type, Source and Hidden are ZTYPE, ZSOURCE and ZHIDDEN, the stored integer codes, "
                 "reported as stored and not interpreted. Latitude and Longitude are ZFAVORITEITEM's own "
                 "values when stored, otherwise the ZMIXINMAPITEM row joined on ZMAPITEM; the fallback was "
                 "not reached by any tested row. Address is a best-effort decode of that map item's "
                 "ZMAPITEMSTORAGE protobuf, using the decoder the Maps Sync history uses (courtesy "
                 "CheekyForensicsMonkey), otherwise ZORIGINATINGADDRESSSTRING; that fallback was not reached "
                 "by any tested row, and a blank Address does not mean the map item holds none. 4 of the 12 "
                 "rows tested held no map item and so no coordinates or address. A row is a favorite entry "
                 "in the store; whether it was created on this device or synced from another device on the "
                 "account is not established, and it is not evidence that the device was at that place. Run "
                 "against nine iOS 15 to 18 images (keys in sample_data): 1 to 4 rows on six, 12 rows in "
                 "all, and 0 rows on three where the table exists and is empty. The ZTYPE, ZSOURCE and "
                 "ZHIDDEN code meanings were not sourced."
        ),
        "paths": ('*/MapsSync_0.0.1*',),
        "output_types": "all",
        "artifact_icon": "star",
        "sample_data": {
            'iphone12_ios18': 'iOS 18.7 | com.apple.Maps | 3 rows',
            'abe_ios16': 'iOS 16.5 | com.apple.Maps | 4 rows',
            'iphone11_ios17': 'iOS 17.3 | com.apple.Maps | 2 rows',
            'felix_ios17': 'iOS 17.6.1 | com.apple.Maps | 1 row',
            'otto_ios17': 'iOS 17.5.1 | com.apple.Maps | 1 row',
            'jess_ios15': 'iOS 15.0.2 | com.apple.Maps | 1 row',
            'magnet_ios16': 'iOS 16.1.1 | com.apple.Maps | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | com.apple.Maps | 0 rows',
            'hc_ios18_7': 'iOS 18.7.8 | com.apple.Maps | 0 rows',
        },
    },
    "mapsCollectionItems": {
        "name": "Maps Collection Items",
        "description": "Rows of the ZCOLLECTIONITEM table of Apple Maps MapsSync_0.0.1, with the name, category, "
                       "note, coordinates and address where the row stores them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-13",
        "last_update_date": "2026-11-13",
        "requirements": "none",
        "category": "Location",
        "notes": (
                 "Source is the ZCOLLECTIONITEM table of MapsSync_0.0.1, one output row per table row. All "
                 "15 rows tested are the CollectionPlaceItem entity and none is linked to a ZCOLLECTION row; "
                 "what puts a row in this table was not sourced. Created and Modified are ZCREATETIME and "
                 "ZMODIFICATIONTIME, Core Data seconds since 2001, shown in UTC. Name is ZCUSTOMNAME, "
                 "falling back to ZMAPITEMNAME; the fallback was not reached by any tested row. Category and "
                 "Note are ZMAPITEMCATEGORY and ZPLACEITEMNOTE as stored. These columns are present on the "
                 "three iOS 18.3 to 18.7 stores tested and absent on the six iOS 15 to 17 stores tested; on "
                 "a schema without them the code reports the fields blank, and no such store had rows. "
                 "Latitude and Longitude are the row's own values when stored, otherwise the ZMIXINMAPITEM "
                 "row joined on ZMAPITEM; the fallback was not reached by any tested row. Address is "
                 "ZMAPITEMADDRESS when the row stores one, otherwise a best-effort decode of the map item's "
                 "ZMAPITEMSTORAGE protobuf; the decode path was not reached by any tested row. A row is not "
                 "evidence that the device was at that place, and whether it was created on this device or "
                 "synced from another device on the account is not established. Run against nine iOS 15 to "
                 "18 images (keys in sample_data): 15 rows on iphone12_ios18 and 0 rows on eight others "
                 "where the table exists and is empty."
        ),
        "paths": ('*/MapsSync_0.0.1*',),
        "output_types": "all",
        "artifact_icon": "bookmark",
        "sample_data": {
            'iphone12_ios18': 'iOS 18.7 | com.apple.Maps | 15 rows',
            'abe_ios16': 'iOS 16.5 | com.apple.Maps | 0 rows',
            'iphone11_ios17': 'iOS 17.3 | com.apple.Maps | 0 rows',
            'felix_ios17': 'iOS 17.6.1 | com.apple.Maps | 0 rows',
            'otto_ios17': 'iOS 17.5.1 | com.apple.Maps | 0 rows',
            'jess_ios15': 'iOS 15.0.2 | com.apple.Maps | 0 rows',
            'magnet_ios16': 'iOS 16.1.1 | com.apple.Maps | 0 rows',
            'dexter_ios18': 'iOS 18.3.2 | com.apple.Maps | 0 rows',
            'hc_ios18_7': 'iOS 18.7.8 | com.apple.Maps | 0 rows',
        },
    }
}

import sqlite3
import struct

from scripts import blackboxprotobuf

from scripts.ilapfuncs import (artifact_processor, logfunc, open_sqlite_db_readonly,
                               does_column_exist_in_db)

_DECODE_ERRORS = (KeyError, TypeError, IndexError, ValueError, AttributeError, struct.error)


def get_recursively(search_dict, field):
    """Search all nested dicts/lists in search_dict for the given key, returning every value found."""
    fields_found = []
    for key, value in search_dict.items():
        if key == field:
            fields_found.append(value)
        elif isinstance(value, dict):
            fields_found.extend(get_recursively(value, field))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    fields_found.extend(get_recursively(item, field))
    return fields_found


def _journey_addresses(message, w, agg1):
    """Pull the destination address(es) for a 'create' journey leg out of the decoded protobuf."""
    msg2 = message['1'][1]['1'].get('2')
    if msg2 is not None:
        if isinstance(msg2, bytes):
            return agg1 + ' ' + msg2.decode('latin-1')
        directa = ''
        for address in message['1'][1]['1']['2']['6']:
            directa += ' ' + address.decode('latin-1')
    else:
        directa = ''
        try:
            for address in w['1']['101']['2']['11']:
                directa += ' ' + address.decode('latin-1')
        except (KeyError, TypeError, IndexError):
            directa = ''
            for address in w['1']['101']['2']:
                directa += ' ' + str(address)
    return directa if agg1 == '' else agg1 + ' <---> ' + directa


def _parse_journey_blob(blob):
    """Best-effort decode of ZROUTEREQUESTSTORAGE into a human-readable journey destination string."""
    if blob is None:
        return ''
    agg1 = ''
    try:
        message, _ = blackboxprotobuf.decode_message(blob)
        for x in message['1']:
            if isinstance(x, dict):
                check = x.get('2')
                if check is not None and x['2'].get('1', '') != '':
                    for y in x['2']['1']['4']:
                        z = y.get('8')
                        if isinstance(z, dict):
                            w = z.get('31')
                            if w is not None:
                                three = get_recursively(w, '3')
                                if three[1] == b'create':
                                    agg1 = _journey_addresses(message, w, agg1)
            else:
                agg1 = x['2']['8']['1'].decode() + ' -> ' + x['2']['8']['3'].decode()
    except _DECODE_ERRORS:
        pass
    return agg1


def _parse_mapitem_blob(blob):
    """Best-effort decode of ZMAPITEMSTORAGE into a human-readable address string."""
    if blob is None:
        return ''
    mapitem = ''
    try:
        message, _ = blackboxprotobuf.decode_message(blob)
        get101 = get_recursively(message, '101')
        if not isinstance(get101[0]['2'], bytes):
            for address in get101[0]['2']['11']:
                mapitem += ' ' + address.decode('latin-1')
        else:
            for address in get101[0]['2']:
                mapitem += ' ' + str(address)
    except _DECODE_ERRORS:
        pass
    return mapitem


def _build_query(file_found):
    """Pick the MapsSync query variant that matches the schema present in this database."""
    if (does_column_exist_in_db(file_found, 'ZHISTORYITEM', 'ZLOCATIONDISPLAY')
            and does_column_exist_in_db(file_found, 'ZHISTORYITEM', 'ZLATITUDE1')
            and does_column_exist_in_db(file_found, 'ZHISTORYITEM', 'ZROUTEREQUESTSTORAGE')
            and does_column_exist_in_db(file_found, 'ZMIXINMAPITEM', 'ZMAPITEMSTORAGE')):
        return '''
        SELECT
        datetime(ZHISTORYITEM.ZCREATETIME+978307200,'UNIXEPOCH'),
        datetime(ZHISTORYITEM.ZMODIFICATIONTIME+978307200,'UNIXEPOCH'),
        ZHISTORYITEM.z_pk,
        NULL,
        ZHISTORYITEM.ZQUERY,
        ZHISTORYITEM.ZLOCATIONDISPLAY,
        ZHISTORYITEM.ZLATITUDE,
        ZHISTORYITEM.ZLONGITUDE,
        ZHISTORYITEM.ZLATITUDE1,
        ZHISTORYITEM.ZLONGITUDE1,
        ZHISTORYITEM.ZROUTEREQUESTSTORAGE,
        ZMIXINMAPITEM.ZMAPITEMSTORAGE,
        ZHISTORYITEM.Z_ENT
        from ZHISTORYITEM
        left join ZMIXINMAPITEM on ZMIXINMAPITEM.Z_PK=ZHISTORYITEM.ZMAPITEM
        '''
    entity_column = ('ZHISTORYITEM.Z_ENT'
                     if does_column_exist_in_db(file_found, 'ZHISTORYITEM', 'Z_ENT') else 'NULL')
    if does_column_exist_in_db(file_found, 'ZMIXINMAPITEM', 'ZNAME'):
        logfunc("INFO: MapsSync modern schema columns not found. Trying iOS 15 schema.")
        return f'''
        SELECT
        datetime(ZHISTORYITEM.ZCREATETIME + 978307200, 'UNIXEPOCH'),
        datetime(ZHISTORYITEM.ZMODIFICATIONTIME + 978307200, 'UNIXEPOCH'),
        ZHISTORYITEM.Z_PK,
        NULL,
        ZHISTORYITEM.ZQUERY,
        ZMIXINMAPITEM.ZNAME,
        ZHISTORYITEM.ZLATITUDE,
        ZHISTORYITEM.ZLONGITUDE,
        NULL, NULL, NULL, NULL,
        {entity_column}
        FROM ZHISTORYITEM
        LEFT JOIN ZMIXINMAPITEM ON ZHISTORYITEM.ZMAPITEM = ZMIXINMAPITEM.Z_PK
        '''
    logfunc("INFO: MapsSync mixin map item columns not found. Trying basic history query.")
    return f'''
    SELECT
    datetime(ZHISTORYITEM.ZCREATETIME + 978307200, 'UNIXEPOCH'),
    datetime(ZHISTORYITEM.ZMODIFICATIONTIME + 978307200, 'UNIXEPOCH'),
    ZHISTORYITEM.Z_PK,
    NULL,
    ZHISTORYITEM.ZQUERY,
    '',
    ZHISTORYITEM.ZLATITUDE,
    ZHISTORYITEM.ZLONGITUDE,
    NULL, NULL, NULL, NULL,
    {entity_column}
    FROM ZHISTORYITEM
    '''


def _entity_names(cursor):
    """{Z_ENT: Z_NAME} from this store's own Z_PRIMARYKEY table; {} when it has none.

    Entity numbers differ between builds of the store, so they are never mapped by a fixed list."""
    try:
        cursor.execute('SELECT Z_ENT, Z_NAME FROM Z_PRIMARYKEY')
        return dict(cursor.fetchall())
    except sqlite3.Error:
        return {}


@artifact_processor
def mapsSync(context):
    data_headers = (
        ('Timestamp', 'datetime'), ('Modified Time', 'datetime'), 'Item Number', 'Entity (Z_PRIMARYKEY Name)',
        'Z_ENT (As Stored)',
        'Location Search', 'Location Display', 'Latitude', 'Longitude', 'Latitude1', 'Longitude1',
        'Journey Destination Address', 'Map Item Storage BLOB Address')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('MapsSync_0.0.1'):
            continue

        query = _build_query(file_found)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute(query)
            all_rows = cursor.fetchall()
            entities = _entity_names(cursor)
        except sqlite3.Error as ex:
            logfunc(f'Error processing MapsSync data: {ex}')
            db.close()
            continue
        db.close()

        for row in all_rows:
            data_list.append((row[0], row[1], row[2], entities.get(row[12], ''), row[12], row[4], row[5], row[6], row[7],
                              row[8], row[9], _parse_journey_blob(row[10]), _parse_mapitem_blob(row[11])))

        if all_rows:
            sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


def _col(file_found, table, column):
    """True when the column exists in the table of this MapsSync store."""
    return does_column_exist_in_db(file_found, table, column)


def _favorites_query(file_found):
    """ZFAVORITEITEM joined to ZMIXINMAPITEM, selecting only columns the schema exposes."""
    name = 'ZFAVORITEITEM.ZCUSTOMNAME' if _col(file_found, 'ZFAVORITEITEM', 'ZCUSTOMNAME') else 'NULL'
    orig = ('ZFAVORITEITEM.ZORIGINATINGADDRESSSTRING'
            if _col(file_found, 'ZFAVORITEITEM', 'ZORIGINATINGADDRESSSTRING') else 'NULL')
    ztype = 'ZFAVORITEITEM.ZTYPE' if _col(file_found, 'ZFAVORITEITEM', 'ZTYPE') else 'NULL'
    zsource = 'ZFAVORITEITEM.ZSOURCE' if _col(file_found, 'ZFAVORITEITEM', 'ZSOURCE') else 'NULL'
    zhidden = 'ZFAVORITEITEM.ZHIDDEN' if _col(file_found, 'ZFAVORITEITEM', 'ZHIDDEN') else 'NULL'
    has_mixin = _col(file_found, 'ZMIXINMAPITEM', 'ZMAPITEMSTORAGE')
    mlat = 'ZMIXINMAPITEM.ZLATITUDE' if has_mixin else 'NULL'
    mlon = 'ZMIXINMAPITEM.ZLONGITUDE' if has_mixin else 'NULL'
    blob = 'ZMIXINMAPITEM.ZMAPITEMSTORAGE' if has_mixin else 'NULL'
    join = ('LEFT JOIN ZMIXINMAPITEM ON ZMIXINMAPITEM.Z_PK = ZFAVORITEITEM.ZMAPITEM'
            if has_mixin else '')
    return f'''
    SELECT
        datetime(ZFAVORITEITEM.ZCREATETIME + 978307200, 'UNIXEPOCH'),
        datetime(ZFAVORITEITEM.ZMODIFICATIONTIME + 978307200, 'UNIXEPOCH'),
        ZFAVORITEITEM.Z_PK,
        {name},
        {ztype},
        {zsource},
        {zhidden},
        ZFAVORITEITEM.ZLATITUDE,
        ZFAVORITEITEM.ZLONGITUDE,
        {mlat},
        {mlon},
        {blob},
        {orig}
    FROM ZFAVORITEITEM
    {join}
    '''


@artifact_processor
def mapsFavorites(context):
    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'), 'Item Number', 'Name',
        'Favorite Type (As Stored)', 'Source (As Stored)', 'Hidden (As Stored)',
        ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Address')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('MapsSync_0.0.1'):
            continue
        if not _col(file_found, 'ZFAVORITEITEM', 'Z_PK'):
            continue
        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        cursor = db.cursor()
        try:
            cursor.execute(_favorites_query(file_found))
            all_rows = cursor.fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Error processing Maps Favorites: {ex}')
            db.close()
            continue
        db.close()

        for row in all_rows:
            (created, modified, pk, name, ztype, zsource, zhidden, flat, flon,
             mlat, mlon, blob, orig) = row
            lat = flat if flat is not None else mlat
            lon = flon if flon is not None else mlon
            address = _parse_mapitem_blob(blob).strip()
            if not address:
                address = (orig or '').strip()
            data_list.append((created, modified, pk, name, ztype, zsource, zhidden, lat, lon, address))

        if all_rows:
            sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


def _collection_items_query(file_found):
    """ZCOLLECTIONITEM, with the iOS 18 direct address columns when present, else a ZMIXINMAPITEM join."""
    name = 'ZCOLLECTIONITEM.ZCUSTOMNAME' if _col(file_found, 'ZCOLLECTIONITEM', 'ZCUSTOMNAME') else 'NULL'
    map_name = ('ZCOLLECTIONITEM.ZMAPITEMNAME'
                if _col(file_found, 'ZCOLLECTIONITEM', 'ZMAPITEMNAME') else 'NULL')
    direct_addr = ('ZCOLLECTIONITEM.ZMAPITEMADDRESS'
                   if _col(file_found, 'ZCOLLECTIONITEM', 'ZMAPITEMADDRESS') else 'NULL')
    category = ('ZCOLLECTIONITEM.ZMAPITEMCATEGORY'
                if _col(file_found, 'ZCOLLECTIONITEM', 'ZMAPITEMCATEGORY') else 'NULL')
    note = ('ZCOLLECTIONITEM.ZPLACEITEMNOTE'
            if _col(file_found, 'ZCOLLECTIONITEM', 'ZPLACEITEMNOTE') else 'NULL')
    has_mixin = _col(file_found, 'ZMIXINMAPITEM', 'ZMAPITEMSTORAGE')
    mlat = 'ZMIXINMAPITEM.ZLATITUDE' if has_mixin else 'NULL'
    mlon = 'ZMIXINMAPITEM.ZLONGITUDE' if has_mixin else 'NULL'
    blob = 'ZMIXINMAPITEM.ZMAPITEMSTORAGE' if has_mixin else 'NULL'
    join = ('LEFT JOIN ZMIXINMAPITEM ON ZMIXINMAPITEM.Z_PK = ZCOLLECTIONITEM.ZMAPITEM'
            if has_mixin else '')
    return f'''
    SELECT
        datetime(ZCOLLECTIONITEM.ZCREATETIME + 978307200, 'UNIXEPOCH'),
        datetime(ZCOLLECTIONITEM.ZMODIFICATIONTIME + 978307200, 'UNIXEPOCH'),
        ZCOLLECTIONITEM.Z_PK,
        {name},
        {map_name},
        {direct_addr},
        {category},
        {note},
        ZCOLLECTIONITEM.ZLATITUDE,
        ZCOLLECTIONITEM.ZLONGITUDE,
        {mlat},
        {mlon},
        {blob}
    FROM ZCOLLECTIONITEM
    {join}
    '''


@artifact_processor
def mapsCollectionItems(context):
    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'), 'Item Number', 'Name', 'Category',
        'Note', ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Address')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('MapsSync_0.0.1'):
            continue
        if not _col(file_found, 'ZCOLLECTIONITEM', 'Z_PK'):
            continue
        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        cursor = db.cursor()
        try:
            cursor.execute(_collection_items_query(file_found))
            all_rows = cursor.fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Error processing Maps Collection Items: {ex}')
            db.close()
            continue
        db.close()

        for row in all_rows:
            (created, modified, pk, custom_name, map_name, direct_addr, category,
             note, clat, clon, mlat, mlon, blob) = row
            name = custom_name or map_name
            lat = clat if clat is not None else mlat
            lon = clon if clon is not None else mlon
            address = (direct_addr or _parse_mapitem_blob(blob) or '').strip()
            data_list.append((created, modified, pk, name, category, note, lat, lon, address))

        if all_rows:
            sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
