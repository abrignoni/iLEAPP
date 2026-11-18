__artifacts_v2__ = {
    "get_biomePhotosDelete": {
        "name": "Biome - Photos Delete",
        "description": "Deletion records from the Photos.Delete biome stream, with the asset "
                       "identifier each names and the state of that asset in Photos.sqlite.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and numbers come from the BMPhotosDelete, BMPhotosShare and "
                 "BMPhotosEngagement classes' protoFields in BiomeLibrary.framework, read on macOS "
                 "27.2.1 (26B131): 1 identifier, 2 subset and 3 type. Type names come from the "
                 "matching TypeAsString function in the same framework, and the stored number is "
                 "kept beside the name. That the iOS writer uses the same schema was not checked "
                 "beyond the data: every written record decoded to those fields. No record of this "
                 "stream held a subset on the tested images, and the artifact does not report one. "
                 "Asset Identifier is the identifier as stored; Photos Library State compares it "
                 "with ZASSET.ZUUID in Photos.sqlite and says In library, Trashed (ZTRASHEDSTATE "
                 "not 0) or Not in Photos.sqlite, and Filename and Trashed Date are that asset's "
                 "ZFILENAME and ZTRASHEDDATE (seconds since 2001, UTC). Photos Library State is "
                 "empty when the record has no identifier or no Photos.sqlite was found. Records "
                 "the SEGB file marks deleted, and the stream's tombstone folder, are not read. "
                 "Each tested image has one file in the stream's local folder outside tombstone, "
                 "so SEGB File held one value on every row. SEGB Timestamp is the SEGB record "
                 "time. On the 7 rows whose state is Trashed it is between 68 seconds before and 1 "
                 "second after ZTRASHEDDATE on 6 rows (hill_iphone15pro_ios26) and 309 seconds "
                 "before it on 1 row (wilkerson_iphone16_ios26). What event the SEGB time marks "
                 "was not established beyond that. On hill_iphone15pro_ios26 6 of 7 records name a "
                 "trashed asset and 1 names an asset not in Photos.sqlite. On "
                 "wilkerson_iphone16_ios26 13 of 14 name an asset not in Photos.sqlite. Those "
                 "identifiers were not found elsewhere in Photos.sqlite or in the Photos.Share and "
                 "Photos.Engagement streams; the rest of the image was not searched. Filename and "
                 "Trashed Date are empty on those rows. Type held Other (3) on all 7 rows of "
                 "hill_iphone15pro_ios26; what the type names mean was not established.",
        "paths": ('*/streams/*/Photos.Delete/local/*',
                  '*/mobile/Media/PhotoData/Photos.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "trash",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 7 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 14 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows, no stream file",
        },
    },
    "get_biomePhotosShare": {
        "name": "Biome - Photos Share",
        "description": "Share records from the Photos.Share biome stream, with the asset "
                       "identifier, the subset and share type each stores and the state of "
                       "that asset in Photos.sqlite.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and numbers come from the BMPhotosDelete, BMPhotosShare and "
                 "BMPhotosEngagement classes' protoFields in BiomeLibrary.framework, read on macOS "
                 "27.2.1 (26B131): 1 identifier, 2 subset and 3 type. Type names come from the "
                 "matching TypeAsString function in the same framework, and the stored number is "
                 "kept beside the name. That the iOS writer uses the same schema was not checked "
                 "beyond the data: every written record decoded to those fields. Asset Identifier "
                 "is the identifier as stored; Photos Library State compares it with ZASSET.ZUUID "
                 "in Photos.sqlite and says In library, Trashed (ZTRASHEDSTATE not 0) or Not in "
                 "Photos.sqlite, and Filename and Trashed Date are that asset's ZFILENAME and "
                 "ZTRASHEDDATE (seconds since 2001, UTC). Photos Library State is empty when the "
                 "record has no identifier or no Photos.sqlite was found. Records the SEGB file "
                 "marks deleted, and the stream's tombstone folder, are not read. Each tested "
                 "image has one file in the stream's local folder outside tombstone, so SEGB File "
                 "held one value on every row. Subset is the subset as stored. It held a "
                 "reverse-DNS style identifier on wilkerson_iphone16_ios26 and a camel-case name "
                 "on hill_iphone15pro_ios26; what it identifies was not established. On "
                 "wilkerson_iphone16_ios26 Type held Extension (1) and Subset held one value on "
                 "all 3 rows. One of those rows has no identifier, so Photos Library State is "
                 "empty there. SEGB Timestamp is the SEGB record time; what it marks for a share "
                 "was not checked against another record. Trashed Date is empty on every row of "
                 "both tested images: 3 of the 4 rows name an asset in the library and 1 has no "
                 "identifier.",
        "paths": ('*/streams/*/Photos.Share/local/*',
                  '*/mobile/Media/PhotoData/Photos.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "share",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 1 row",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows, no stream file",
        },
    },
    "get_biomePhotosEngagement": {
        "name": "Biome - Photos Engagement",
        "description": "Engagement records from the Photos.Engagement biome stream, with the "
                       "asset identifier and engagement type each stores and the state of that "
                       "asset in Photos.sqlite.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and numbers come from the BMPhotosDelete, BMPhotosShare and "
                 "BMPhotosEngagement classes' protoFields in BiomeLibrary.framework, read on macOS "
                 "27.2.1 (26B131): 1 identifier, 2 subset and 3 type. Type names come from the "
                 "matching TypeAsString function in the same framework, and the stored number is "
                 "kept beside the name. That the iOS writer uses the same schema was not checked "
                 "beyond the data: every written record decoded to those fields. No record of this "
                 "stream held a subset on the tested images, and the artifact does not report one. "
                 "Asset Identifier is the identifier as stored; Photos Library State compares it "
                 "with ZASSET.ZUUID in Photos.sqlite and says In library, Trashed (ZTRASHEDSTATE "
                 "not 0) or Not in Photos.sqlite, and Filename and Trashed Date are that asset's "
                 "ZFILENAME and ZTRASHEDDATE (seconds since 2001, UTC). Photos Library State is "
                 "empty when the record has no identifier or no Photos.sqlite was found. Records "
                 "the SEGB file marks deleted, and the stream's tombstone folder, are not read. "
                 "Each tested image has one file in the stream's local folder outside tombstone, "
                 "so SEGB File held one value on every row; the 6 written records in the tombstone "
                 "file of hill_iphone15pro_ios26 use a different record layout. SEGB Timestamp is "
                 "the SEGB record time; what it marks for an engagement was not checked against "
                 "another record. Every record on the tested images (108 on "
                 "hill_iphone15pro_ios26, 378 on wilkerson_iphone16_ios26) names an asset that is "
                 "in the library, so Photos Library State held In library on every row and Trashed "
                 "Date is empty on every row. Type held Unknown (0), the framework's own name for "
                 "0, on 30 of 108 and 58 of 378 rows. What the engagement type names mean was not "
                 "established.",
        "paths": ('*/streams/*/Photos.Engagement/local/*',
                  '*/mobile/Media/PhotoData/Photos.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 108 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 378 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows, no stream file",
        },
    },
}


import os
import struct
from datetime import timezone

from google.protobuf.message import DecodeError
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import (artifact_processor, convert_cocoa_core_data_ts_to_utc,
                               does_column_exist_in_db, does_table_exist_in_db,
                               get_sqlite_db_records, is_sqlite_sidecar, logfunc)

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)
# Field names and numbers from BMPhotosDelete, BMPhotosShare and BMPhotosEngagement
# protoFields (1 identifier, 2 subset, 3 type), and type names from BMPhotosDeleteTypeAsString,
# BMPhotosShareTypeAsString and BMPhotosEngagementTypeAsString, all read from
# BiomeLibrary.framework on macOS 27.2.1 (26B131).
_TYPES = {
    'Photos.Delete': {0: 'Unknown', 1: 'Recent', 2: 'Old', 3: 'Other'},
    'Photos.Share': {0: 'Unknown', 1: 'Extension', 2: 'UseAsWallpaper', 3: 'CreateWatchFace',
                     4: 'AirPlay', 5: 'AirDrop', 6: 'SaveToFiles', 7: 'AssignToContact',
                     8: 'AddToAlbum', 9: 'AddToSharedAlbum', 10: 'Hide', 11: 'Recent'},
    'Photos.Engagement': {0: 'Unknown', 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Zoom',
                          5: 'Eyecatchiness', 6: 'Other', 7: 'Recent'},
}


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return '' if value is None or isinstance(value, (dict, list)) else str(value)


def _type(stream, value):
    if not isinstance(value, int):
        return ''
    names = _TYPES[stream]
    return f'{names[value]} ({value})' if value in names else f'Unknown value ({value})'


def _library(files_found):
    '''({asset UUID: (filename, trashed state, trashed date)}, Photos.sqlite path or '').'''
    for found in files_found:
        if os.path.basename(found) != 'Photos.sqlite' or is_sqlite_sidecar(found):
            continue
        if not does_table_exist_in_db(found, 'ZASSET'):
            continue
        trashed = does_column_exist_in_db(found, 'ZASSET', 'ZTRASHEDSTATE')
        query = ('SELECT ZUUID, ZFILENAME, ' +
                 ('ZTRASHEDSTATE, ZTRASHEDDATE' if trashed else 'NULL, NULL') + ' FROM ZASSET')
        assets = {}
        for record in get_sqlite_db_records(found, query):
            if record[0]:
                assets[str(record[0]).upper()] = (record[1], record[2], record[3])
        return assets, found
    return None, ''


def _rows(context, stream):
    files_found = sorted(str(found) for found in context.get_files_found())
    assets, library_path = _library(files_found)
    data_list, sources = [], set()
    marker = f'/{stream}/local/'
    for found in files_found:
        relative = context.get_relative_path(found).replace('\\', '/')
        if marker not in relative or '/tombstone/' in relative or not os.path.isfile(found):
            continue
        if os.path.basename(found).startswith('.'):
            continue
        sources.add(os.path.dirname(found))
        for record in read_segb_file(found):
            if record.state != EntryState.Written:
                continue
            try:
                message, _ = blackboxprotobuf.decode_message(record.data)
            except _DECODE_ERRORS as error:
                logfunc(f'{stream}: could not decode record at offset {record.data_start_offset} '
                        f'in {os.path.basename(found)}: {error}')
                continue
            identifier = _text(message.get('1'))
            asset = assets.get(identifier.upper()) if assets is not None and identifier else None
            if assets is None or not identifier:
                state = ''
            elif asset is None:
                state = 'Not in Photos.sqlite'
            else:
                state = 'Trashed' if asset[1] else 'In library'
            trashed_date = convert_cocoa_core_data_ts_to_utc(asset[2]) if asset and asset[2] else ''
            row = (record.timestamp1.replace(tzinfo=timezone.utc), trashed_date, identifier,
                   _type(stream, message.get('3')))
            if stream == 'Photos.Share':
                row += (_text(message.get('2')),)
            data_list.append(row + (
                state,
                _text(asset[0]) if asset else '',
                os.path.basename(found),
                record.data_start_offset,
            ))
    if library_path and data_list:
        sources.add(library_path)
    headers = ((('SEGB Timestamp', 'datetime'), ('Trashed Date', 'datetime'), 'Asset Identifier',
                'Type') +
               (('Subset',) if stream == 'Photos.Share' else ()) +
               ('Photos Library State', 'Filename', 'SEGB File', 'Offset'))
    return headers, data_list, '\n'.join(sorted(sources))


@artifact_processor
def get_biomePhotosDelete(context):
    return _rows(context, 'Photos.Delete')


@artifact_processor
def get_biomePhotosShare(context):
    return _rows(context, 'Photos.Share')


@artifact_processor
def get_biomePhotosEngagement(context):
    return _rows(context, 'Photos.Engagement')
