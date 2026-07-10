__artifacts_v2__ = {
    "mapsSync": {
        "name": "Maps Sync",
        "description": "Apple Maps history — searches, displayed locations and navigation journeys "
                       "from MapsSync_0.0.1",
        "author": "",
        "creation_date": "2026-06-23",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Location",
        "notes": "Journey/Map Item addresses are decoded from protobuf BLOBs. Query courtesy of "
                 "CheekyForensicsMonkey "
                 "(https://cheeky4n6monkey.blogspot.com/2020/11/ios14-maps-history-blob-script.html). "
                 "Disclaimer: Entries should be corroborated. Locations and searches from other linked "
                 "devices might show up here. Travel should be confirmed. Medium confidence.",
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
        }
    }
}

import sqlite3
import struct

import blackboxprotobuf

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
        CASE
        when ZHISTORYITEM.z_ent = 14 then 'coordinates of search'
        when ZHISTORYITEM.z_ent = 16 then 'location search'
        when ZHISTORYITEM.z_ent = 12 then 'navigation journey'
        end,
        ZHISTORYITEM.ZQUERY,
        ZHISTORYITEM.ZLOCATIONDISPLAY,
        ZHISTORYITEM.ZLATITUDE,
        ZHISTORYITEM.ZLONGITUDE,
        ZHISTORYITEM.ZLATITUDE1,
        ZHISTORYITEM.ZLONGITUDE1,
        ZHISTORYITEM.ZROUTEREQUESTSTORAGE,
        ZMIXINMAPITEM.ZMAPITEMSTORAGE
        from ZHISTORYITEM
        left join ZMIXINMAPITEM on ZMIXINMAPITEM.Z_PK=ZHISTORYITEM.ZMAPITEM
        '''
    if does_column_exist_in_db(file_found, 'ZMIXINMAPITEM', 'ZNAME'):
        logfunc("INFO: MapsSync modern schema columns not found. Trying iOS 15 schema.")
        return '''
        SELECT
        datetime(ZHISTORYITEM.ZCREATETIME + 978307200, 'UNIXEPOCH'),
        datetime(ZHISTORYITEM.ZMODIFICATIONTIME + 978307200, 'UNIXEPOCH'),
        ZHISTORYITEM.Z_PK,
        'Unknown',
        ZHISTORYITEM.ZQUERY,
        ZMIXINMAPITEM.ZNAME,
        ZHISTORYITEM.ZLATITUDE,
        ZHISTORYITEM.ZLONGITUDE,
        NULL, NULL, NULL, NULL
        FROM ZHISTORYITEM
        LEFT JOIN ZMIXINMAPITEM ON ZHISTORYITEM.ZMAPITEM = ZMIXINMAPITEM.Z_PK
        '''
    logfunc("INFO: MapsSync mixin map item columns not found. Trying basic history query.")
    return '''
    SELECT
    datetime(ZHISTORYITEM.ZCREATETIME + 978307200, 'UNIXEPOCH'),
    datetime(ZHISTORYITEM.ZMODIFICATIONTIME + 978307200, 'UNIXEPOCH'),
    ZHISTORYITEM.Z_PK,
    'Unknown',
    ZHISTORYITEM.ZQUERY,
    '',
    ZHISTORYITEM.ZLATITUDE,
    ZHISTORYITEM.ZLONGITUDE,
    NULL, NULL, NULL, NULL
    FROM ZHISTORYITEM
    '''


@artifact_processor
def mapsSync(context):
    data_headers = (
        ('Timestamp', 'datetime'), ('Modified Time', 'datetime'), 'Item Number', 'Type',
        'Location Search', 'Location City', 'Latitude', 'Longitude', 'Latitude1', 'Longitude1',
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
        except sqlite3.Error as ex:
            logfunc(f'Error processing MapsSync data: {ex}')
            db.close()
            continue
        db.close()

        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                              row[8], row[9], _parse_journey_blob(row[10]), _parse_mapitem_blob(row[11])))

        if all_rows:
            sources.append(context.get_relative_path(file_found))

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
