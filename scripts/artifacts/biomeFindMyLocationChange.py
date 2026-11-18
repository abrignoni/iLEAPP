__artifacts_v2__ = {
    "get_biomeFindMyLocationChange": {
        "name": "Biome - Find My Location Change",
        "description": "Records from the FindMy.LocationChange biome stream: the IDS handle, the "
                       "state change, the activity state and the name each record stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and numbers come from the protoFields of BMFindMyLocationChange in "
                 "BiomeLibrary.framework, read on macOS 27.2.1 (26B131). That the iOS writer uses "
                 "the same schema was checked only against the data: on the two iOS 26 images "
                 "every written record held fields 1, 2, 3 and 6. On iphone11_ios17 (iOS 17.3) all 3 written records and on otto_ios17 all 695 written records also held fields 4 and 5, fixed 64-bit values that were zero; the "
                 "macOS 27.2.1 class does not name them and they are not shown. SEGB Timestamp is "
                 "the SEGB record time; what it marks was not checked against another record. "
                 "Records the SEGB file marks deleted are skipped. Files in the stream's tombstone folder are not parsed. Each tested image that holds the stream has one file in its local folder, "
                 "so SEGB File held one value on every row. Fields: 1 idsHandle, 2 stateChange, 3 "
                 "activityState and 6 name, with State Change and Activity State named from the same framework, decoded per data version, the stored number kept beside each name. The version is read from an integer in the SEGB record header that the SEGB reader leaves unnamed (the last field of the header in SEGB v1, the second in SEGB v2); that it is the data version was checked only against the data: the values seen on the records shown (0 and 1) are the versions the framework decodes. Data version 0 numbers State Change from 0 (Update, StartedSharing, StoppedSharing) and version 1 inserts 0 Unknown; Activity State is the same in both. On the tested images the iOS 17 records are version 0 and the iOS 26 ones version 1. A number the version's table does not name, or a version with no table, shows the number only. The names were read on macOS 27.2.1 and were not checked against an iOS framework. IDS Handle has the shape of "
                 "a telephone number or of an email address on the tested images; whose location a "
                 "record describes is not established here. IDS Handle held one value on every row "
                 "of hill_iphone15pro_ios26 (53) and iphone11_ios17 (3), and two values on "
                 "wilkerson_iphone16_ios26 (39). State Change held Update (1) on every row of the two iOS 26 images (version 1), Update (0) on all 695 rows of otto_ios17, and Update (0), StartedSharing (1) and StoppedSharing (2) on one row each of iphone11_ios17. The records of both iOS 17 images are version 0. Activity State held Unknown (0) on all 3 rows of iphone11_ios17. Name is empty on every row of hill_iphone15pro_ios26, wilkerson_iphone16_ios26 and iphone11_ios17, and set on 196 of the 695 rows of otto_ios17, where IDS Handle held one value.",
        "paths": ('*/streams/*/FindMy.LocationChange/local/*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 53 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 39 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
            "otto_ios17": "iOS 17.5.1 | 695 rows",
        },
    }
}


import os
import struct
from datetime import timezone

from google.protobuf.message import DecodeError
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)
# Field names and numbers from BMFindMyLocationChange protoFields (1 idsHandle, 2 stateChange,
# 3 activityState, 6 name; name and idsHandle are strings), read from BiomeLibrary.framework on
# macOS 27.2.1 (26B131). Enum names are read the same way, per record data version: one-field
# records were decoded with eventWithData:dataVersion: and each name taken from the event's
# description. Data version 0 numbers stateChange from 0 (Update); version 1 inserts 0 Unknown.
# activityState is the same in both versions.
_TYPES = {'1': {'type': 'bytes'}, '6': {'type': 'bytes'}}
_STATE_CHANGE = {0: {0: 'Update', 1: 'StartedSharing', 2: 'StoppedSharing'},
                 1: {0: 'Unknown', 1: 'Update', 2: 'StartedSharing', 3: 'StoppedSharing'}}
_ACTIVITY_NAMES = {0: 'Unknown', 1: 'Stationary', 2: 'Walking', 3: 'Running', 4: 'Cycling',
                   5: 'Automotive'}
_ACTIVITY = {0: _ACTIVITY_NAMES, 1: _ACTIVITY_NAMES}


def _named(names_by_version, value, version):
    '''Name and stored number from the table of the record's data version, else the number.'''
    if not isinstance(value, int):
        return ''
    names = names_by_version.get(version, {})
    return f'{names[value]} ({value})' if value in names else str(value)


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return '' if value is None or isinstance(value, (dict, list)) else str(value)


@artifact_processor
def get_biomeFindMyLocationChange(context):
    data_list, source_dirs = [], set()
    for found in sorted(str(path) for path in context.get_files_found()):
        name = os.path.basename(found)
        if name.startswith('.') or not os.path.isfile(found):
            continue
        if '/tombstone/' in context.get_relative_path(found).replace('\\', '/'):
            continue
        source_dirs.add(os.path.dirname(found))
        for record in read_segb_file(found):
            if record.state != EntryState.Written:
                continue
            try:
                message, _ = blackboxprotobuf.decode_message(record.data, _TYPES)
            except _DECODE_ERRORS as error:
                logfunc(f'Find My Location Change: could not decode record at offset '
                        f'{record.data_start_offset} in {name}: {error}')
                continue
            data_list.append((
                record.timestamp1.replace(tzinfo=timezone.utc),
                _text(message.get('1')),
                _named(_STATE_CHANGE, message.get('2'), getattr(record, '_unknown_value', None)),
                _named(_ACTIVITY, message.get('3'), getattr(record, '_unknown_value', None)),
                _text(message.get('6')),
                name,
                record.data_start_offset,
            ))
    data_headers = (('SEGB Timestamp', 'datetime'), 'IDS Handle', 'State Change', 'Activity State',
                    'Name', 'SEGB File', 'Offset')
    return data_headers, data_list, '\n'.join(sorted(source_dirs))
