__artifacts_v2__ = {
    "biomeLocationSemantic": {
        "name": "Biome - Location Semantic",
        "description": "Records of the Location.Semantic biome stream: the stored starting flag "
                       "(Start or End), the user-specific place type, the stored place type, and the "
                       "coordinates of the routined location of interest a record names.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "One row per written record of the Location.Semantic stream. Field names and "
                 "numbers come from BMLocationSemantic.protoFields in BiomeLibrary.framework, read "
                 "on macOS 27.2.1 (26B131): 1 starting, 2 userSpecificPlaceType, 3 placeType and 4 "
                 "loiIdentifier. That the iOS writer uses the same schema was not checked beyond "
                 "the data: every written record on the tested images holds fields 1 to 3, with or "
                 "without field 4. SEGB Timestamp is the SEGB record time. Starting shows Start "
                 "when field 1 is true and End otherwise. What starts or ends is not established. "
                 "The time was compared with the routined visits of the same place "
                 "(ZRTLEARNEDLOCATIONOFINTERESTVISITMO), a Start against visit entries and an End "
                 "against visit exits. It fell within 10 minutes of one on 3 of 24 records of "
                 "hill_iphone15pro_ios26, 29 of 73 of wilkerson_iphone16_ios26 and 29 of 39 of "
                 "iphone11_ios17. Do not read it as a visit time. User Place Type shows the "
                 "framework's name and the stored number (0 Unknown, 1 Home, 2 Work, 3 School, 4 "
                 "Gym); only 0 and 1 occur on the tested images. Every Home row names a location "
                 "of interest whose ZPLACETYPE is 1 (14, 19 and 25 rows). Place Type is the stored "
                 "number with no name. The 4-byte value in each record's SEGB header that follows "
                 "the checksum is 0 on every record. The reader does not name it. If it is the "
                 "data version, the records are version 0. The framework gives a stored number a "
                 "different name at data version 0 and at 1 (stored 2 is Address at 0 and "
                 "PointOfInterest at 1). The data does not settle which applies: Home rows hold 3 "
                 "on hill_iphone15pro_ios26 and 2 on the other two images. Location of Interest ID "
                 "is field 4 as stored. Latitude and Longitude come from the row of "
                 "ZRTLEARNEDLOCATIONOFINTERESTMO in routined Local.sqlite whose ZIDENTIFIER equals "
                 "that ID, and are the location of interest's stored coordinates, not a fix taken "
                 "at the record's time. Of the records that carry an ID, 24 of 24, 73 of 79 and 39 "
                 "of 40 found a row. hill_iphone15pro_ios26 holds 84 rows, "
                 "wilkerson_iphone16_ios26 137 and iphone11_ios17 125. Records the SEGB file marks "
                 "deleted are not listed or decoded (310, 813 and 1,018). Files under the stream's "
                 "tombstone folder are not read. Offset is the reader's record offset: the start "
                 "of the data in SEGB version 1 files and the start of the 8-byte entry header in "
                 "version 2 files.",
        "paths": ('*/streams/*/Location.Semantic/local/*',
                  '*/mobile/Library/Caches/com.apple.routined/Local.sqlite*'),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 84 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 137 rows",
            "iphone11_ios17": "iOS 17.3 | 125 rows",
        },
    }
}


import os
import struct
import uuid
from datetime import timezone

from google.protobuf.message import DecodeError
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import (artifact_processor, does_table_exist_in_db, get_sqlite_db_records,
                               is_sqlite_sidecar, logfunc)

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)
_TYPEDEF = {'4': {'type': 'bytes'}}
# userSpecificPlaceType names from BMLocationSemantic in BiomeLibrary.framework, macOS 27.2.1.
_USER_PLACE = {0: 'Unknown', 1: 'Home', 2: 'Work', 3: 'School', 4: 'Gym'}


def _places(files_found):
    '''({upper-case identifier: (latitude, longitude)}, paths read) from routined Local.sqlite.'''
    places, read = {}, []
    for found in files_found:
        if os.path.basename(found) != 'Local.sqlite' or is_sqlite_sidecar(found):
            continue
        if not does_table_exist_in_db(found, 'ZRTLEARNEDLOCATIONOFINTERESTMO'):
            continue
        read.append(found)
        for identifier, latitude, longitude in get_sqlite_db_records(
                found, 'SELECT ZIDENTIFIER, ZLOCATIONLATITUDE, ZLOCATIONLONGITUDE '
                       'FROM ZRTLEARNEDLOCATIONOFINTERESTMO'):
            if isinstance(identifier, bytes) and len(identifier) == 16:
                places[str(uuid.UUID(bytes=identifier)).upper()] = (latitude, longitude)
    return places, read


def _user_place(value):
    if not isinstance(value, int):
        return ''
    name = _USER_PLACE.get(value)
    return f'{name} ({value})' if name else f'Unknown value ({value})'


@artifact_processor
def biomeLocationSemantic(context):
    files_found = sorted(str(found) for found in context.get_files_found())
    places, place_paths = _places(files_found)
    data_list, source_dirs = [], set()
    deleted = 0
    for found in files_found:
        relative = context.get_relative_path(found).replace('\\', '/')
        if '/Location.Semantic/local/' not in relative or '/tombstone/' in relative:
            continue
        filename = os.path.basename(found)
        if filename.startswith('.') or not os.path.isfile(found):
            continue
        source_dirs.add(os.path.dirname(found))
        for record in read_segb_file(found):
            if record.state != EntryState.Written:
                deleted += 1
                continue
            try:
                message, _ = blackboxprotobuf.decode_message(record.data, _TYPEDEF)
            except _DECODE_ERRORS as error:
                logfunc(f'Location Semantic: could not decode record at offset '
                        f'{record.data_start_offset} in {filename}: {error}')
                continue
            raw_id = message.get('4')
            identifier = raw_id.decode('utf-8', 'replace') if isinstance(raw_id, bytes) else ''
            place = places.get(identifier.upper())
            data_list.append((
                record.timestamp1.replace(tzinfo=timezone.utc),
                'Start' if message.get('1') else 'End',
                _user_place(message.get('2')),
                message.get('3', ''),
                place[0] if place else '',
                place[1] if place else '',
                identifier,
                filename,
                record.data_start_offset,
            ))
    if deleted:
        logfunc(f'Location Semantic: {deleted} record(s) marked deleted are not listed')
    data_headers = (
        ('SEGB Timestamp', 'datetime'), 'Starting', 'User Place Type', 'Place Type (as stored)',
        ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Location of Interest ID',
        'Filename', 'Offset')
    sources = sorted(source_dirs) + (place_paths if data_list else [])
    return data_headers, data_list, '\n'.join(sources)
