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
