__artifacts_v2__ = {
    "mapsSync": {
        "name": "Maps Sync",
        "description": "Apple Maps MapsSync history rows, with each row's entity named from the store's own "
                       "Z_PRIMARYKEY table, the stored Z_ENT value, and the query text embedded in the row's "
                       "stored placeRequest payloads.",
        "author": '@AlexisBrignoni, @nwish, Codex, Claude',
        "creation_date": "2026-06-23",
        "last_update_date": "2026-11-16",
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
                 "numbers in the fixed list an earlier version of this module used (12, 14 and 16) each name "
                 "several "
                 "different entities, and 201 of the 248 tested rows carry a Z_ENT value outside that "
                 "list. Z_ENT (As Stored) is the direct SQLite value when ZHISTORYITEM has the column. A "
                 "store without the column reports SQL NULL and a blank Entity. All 22 stores tested have "
                 "the column. A blank Entity also results when the store has no Z_PRIMARYKEY table or "
                 "that table has no row for the stored Z_ENT. That output does not distinguish an absent "
                 "column from a stored NULL. Query (Sent) and Query (Raw) come from base64 'placeRequest=' "
                 "payloads embedded in the ZROUTEREQUESTSTORAGE and ZMAPITEMSTORAGE BLOBs: Query (Sent) is "
                 "field 8.1.3 of the decoded request and Query (Raw) is field 10000 under 8.1.7, the "
                 "position the Get Apple Maps search history artifact reads from GeoHistory.mapsdata. Both "
                 "are read as text, and distinct values from several payloads on one row are joined with "
                 "'; '. In the contributor's own test, Query (Raw) held the partial text typed before an "
                 "autocomplete suggestion was tapped and was absent when the search was submitted with "
                 "Enter; that is an observation from one device, not a sourced rule. Across the 248 rows "
                 "of the 22 stores tested (iOS 14.3 to 26.5.2), Query (Sent) held text on 123 rows and "
                 "Query (Raw) on 88, all of them HistoryPlaceItem or HistoryDirectionsItem rows; Location "
                 "Search (ZQUERY) held text on 22 rows, all HistorySearchItem, none of them with a Query "
                 "value. Sent and Raw are labels chosen here; Apple's names for these fields are not sourced. "
                 "Timestamp and Modified Time are ZCREATETIME and ZMODIFICATIONTIME, Core Data seconds "
                 "since 2001, shown in UTC. ZLOCATIONDISPLAY, ZLATITUDE1, ZLONGITUDE1, "
                 "ZROUTEREQUESTSTORAGE, ZMAPITEMSTORAGE and Z_ENT are each selected only when the store's "
                 "schema has the column, so the iOS 14 to 17 "
                 "stores tested, which have no ZLATITUDE1, still have their BLOBs decoded. "
                 "MapsSync_0.0.1_deviceLocalCache.db is not read here. On the 22 stores tested its "
                 "ZHISTORYITEM table has the same columns as the main store and held no rows.",
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
        "description": "Rows of the ZFAVORITEITEM table of Apple Maps MapsSync_0.0.1, with the name, coordinates, "
                       "decoded address and request query text where the row stores them.",
        "author": "@AlexisBrignoni, @nwish, Claude",
        "creation_date": "2026-11-13",
        "last_update_date": "2026-11-16",
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
                 "ZHIDDEN code meanings were not sourced. Query (Sent) and Query (Raw) are read from the "
                 "joined map item's ZMAPITEMSTORAGE the way the Maps Sync history reads them; across the 22 "
                 "stores in the Maps Sync sample_data, a wider set than the nine above, ZFAVORITEITEM held "
                 "20 rows; Query (Sent) and Query (Raw) held text on 4 of them and had no value on the "
                 "other 16, so a store can have no value in either column on every row. Sent and Raw are "
                 "labels chosen here; Apple's names for these fields are not sourced."
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

import base64
import re
import sqlite3
import struct

from google.protobuf.message import DecodeError

from scripts import blackboxprotobuf

from scripts.ilapfuncs import (artifact_processor, logfunc, open_sqlite_db_readonly,
                               does_column_exist_in_db)

_DECODE_ERRORS = (KeyError, TypeError, IndexError, ValueError, AttributeError, struct.error, DecodeError)

_PLACE_REQUEST_RE = re.compile(rb'placeRequest=([A-Za-z0-9+/=]+)')

# Fields 8.1.3 and 8.1.7.10000 are text. Without a type the decoder can read a short string as a
# nested message and drop it, so both are typed as bytes, as appleMapsSearchHistory.py does.
_PLACE_REQUEST_TYPEDEF = {
    '8': {'type': 'message', 'name': '', 'message_typedef': {
        '1': {'type': 'message', 'name': '', 'message_typedef': {
            '3': {'type': 'bytes', 'name': ''},
            '7': {'type': 'message', 'name': '', 'message_typedef': {
                '10000': {'type': 'bytes', 'name': ''}}}}}}}}


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


def _pb_get(message, path):
    """Follow a protobuf field path through decoded blackboxprotobuf output; repeated fields flatten."""
    current = [message]
    for step in path:
        nxt = []
        for item in current:
            if isinstance(item, dict) and step in item:
                value = item[step]
                nxt.extend(value if isinstance(value, list) else [value])
        current = nxt
    texts = []
    for item in current:
        if isinstance(item, bytes):
            texts.append(item.decode('utf-8', 'replace'))
        elif isinstance(item, str):
            texts.append(item)
    return '; '.join(dict.fromkeys(texts))


def _place_request_queries(*blobs):
    """Pull the query text out of base64 'placeRequest=' payloads embedded in MapsSync BLOBs.

    Returns (query_sent, query_raw): field 8.1.3 of each decoded request, and field 10000 under
    8.1.7, each the distinct values of every payload in the BLOBs joined with '; '. A field that
    no payload carries is returned as the empty string."""
    sent, raw = [], []
    for blob in blobs:
        if not blob:
            continue
        for match in _PLACE_REQUEST_RE.finditer(blob):
            try:
                payload = base64.b64decode(match.group(1) + b'=' * (-len(match.group(1)) % 4))
                message, _ = blackboxprotobuf.decode_message(payload, _PLACE_REQUEST_TYPEDEF)
            except _DECODE_ERRORS:
                continue
            sent.append(_pb_get(message, ('8', '1', '3')))
            raw.append(_pb_get(message, ('8', '1', '7', '10000')))
    return ('; '.join(dict.fromkeys(v for v in sent if v)),
            '; '.join(dict.fromkeys(v for v in raw if v)))


def _build_query(file_found):
    """Select the history columns this store's schema has, and NULL for the ones it lacks.

    Each column is checked on its own, so a store missing one of them (the iOS 14 to 17 stores
    tested have no ZLATITUDE1) still has its storage BLOBs read."""
    def has(table, column):
        return does_column_exist_in_db(file_found, table, column)

    mixin = has('ZHISTORYITEM', 'ZMAPITEM') and has('ZMIXINMAPITEM', 'Z_PK')
    if has('ZHISTORYITEM', 'ZLOCATIONDISPLAY'):
        display = 'ZHISTORYITEM.ZLOCATIONDISPLAY'
    elif mixin and has('ZMIXINMAPITEM', 'ZNAME'):
        display = 'ZMIXINMAPITEM.ZNAME'
    else:
        display = "''"
    lat1 = 'ZHISTORYITEM.ZLATITUDE1' if has('ZHISTORYITEM', 'ZLATITUDE1') else 'NULL'
    lon1 = 'ZHISTORYITEM.ZLONGITUDE1' if has('ZHISTORYITEM', 'ZLONGITUDE1') else 'NULL'
    route = 'ZHISTORYITEM.ZROUTEREQUESTSTORAGE' if has('ZHISTORYITEM', 'ZROUTEREQUESTSTORAGE') else 'NULL'
    mapitem = 'ZMIXINMAPITEM.ZMAPITEMSTORAGE' if mixin and has('ZMIXINMAPITEM', 'ZMAPITEMSTORAGE') else 'NULL'
    entity = 'ZHISTORYITEM.Z_ENT' if has('ZHISTORYITEM', 'Z_ENT') else 'NULL'
    join = 'LEFT JOIN ZMIXINMAPITEM ON ZMIXINMAPITEM.Z_PK = ZHISTORYITEM.ZMAPITEM' if mixin else ''
    return f'''
    SELECT
    datetime(ZHISTORYITEM.ZCREATETIME + 978307200, 'UNIXEPOCH'),
    datetime(ZHISTORYITEM.ZMODIFICATIONTIME + 978307200, 'UNIXEPOCH'),
    ZHISTORYITEM.Z_PK,
    NULL,
    ZHISTORYITEM.ZQUERY,
    {display},
    ZHISTORYITEM.ZLATITUDE,
    ZHISTORYITEM.ZLONGITUDE,
    {lat1},
    {lon1},
    {route},
    {mapitem},
    {entity}
    FROM ZHISTORYITEM
    {join}
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
        'Location Search', 'Location Display', 'Query (Sent)', 'Query (Raw)',
        'Latitude', 'Longitude', 'Latitude1', 'Longitude1',
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
            query_sent, query_raw = _place_request_queries(row[10], row[11])
            data_list.append((row[0], row[1], row[2], entities.get(row[12], ''), row[12], row[4], row[5],
                              query_sent, query_raw, row[6], row[7], row[8], row[9],
                              _parse_journey_blob(row[10]), _parse_mapitem_blob(row[11])))

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
        ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Address', 'Query (Sent)', 'Query (Raw)')
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
            query_sent, query_raw = _place_request_queries(blob)
            data_list.append((created, modified, pk, name, ztype, zsource, zhidden, lat, lon, address,
                              query_sent, query_raw))

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
