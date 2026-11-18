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
                 "every written record held fields 1, 2, 3 and 6. On iphone11_ios17 (iOS 17.3) all "
                 "3 records also held fields 4 and 5, fixed 64-bit values that were zero; the "
                 "macOS 27.2.1 class does not name them and they are not shown. SEGB Timestamp is "
                 "the SEGB record time; what it marks was not checked against another record. "
                 "Records the SEGB file marks deleted, and the stream's tombstone folder, are not "
                 "read. Each tested image that holds the stream has one file in its local folder, "
                 "so SEGB File held one value on every row. Fields: 1 idsHandle, 2 stateChange, 3 "
                 "activityState and 6 name, with State Change named by "
                 "BMFindMyLocationChangeStateChangeAsString and Activity State by "
                 "BMFindMyLocationChangeActivityStateAsString in the same framework, the stored "
                 "number kept beside each name. The names were read on macOS 27.2.1 and were not "
                 "checked against an iOS framework. Names are shown only when the extraction's iOS "
                 "version is 26 or later; on an earlier or unknown version only the stored number "
                 "is shown, because the names were not checked there. IDS Handle has the shape of "
                 "a telephone number or of an email address on the tested images; whose location a "
                 "record describes is not established here. IDS Handle held one value on every row "
                 "of hill_iphone15pro_ios26 (53) and iphone11_ios17 (3), and two values on "
                 "wilkerson_iphone16_ios26 (39). State Change held Update (1) on every row of the "
                 "two iOS 26 images and 0, 1 and 2 on one row each of iphone11_ios17. Activity "
                 "State held 0 on all 3 rows of iphone11_ios17. Name is empty on every row of the "
                 "three tested images.",
        "paths": ('*/streams/*/FindMy.LocationChange/local/*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 53 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 39 rows",
            "iphone11_ios17": "iOS 17.3 | 3 rows",
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
from scripts.ilapfuncs import artifact_processor, iOS, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)
# Field names and numbers from BMFindMyLocationChange protoFields (1 idsHandle, 2 stateChange,
# 3 activityState, 6 name; name and idsHandle are strings), and enum names from
# BMFindMyLocationChangeStateChangeAsString and BMFindMyLocationChangeActivityStateAsString, read
# from BiomeLibrary.framework on macOS 27.2.1 (26B131).
_TYPES = {'1': {'type': 'bytes'}, '6': {'type': 'bytes'}}
_STATE_CHANGE = {0: 'Unknown', 1: 'Update', 2: 'StartedSharing', 3: 'StoppedSharing'}
_ACTIVITY = {0: 'Unknown', 1: 'Stationary', 2: 'Walking', 3: 'Running', 4: 'Cycling',
             5: 'Automotive'}


def _names_checked():
    '''Whether the extraction's iOS version is 26 or later.

    The names were read from the macOS 27 framework and were not checked on earlier iOS
    versions, so there only the stored number is shown.
    '''
    try:
        return int(str(iOS.get_version()).split('.', maxsplit=1)[0]) >= 26
    except (TypeError, ValueError):
        return False


def _named(names, value):
    if not isinstance(value, int):
        return ''
    if not _names_checked():
        return str(value)
    return f'{names[value]} ({value})' if value in names else f'Unknown value ({value})'


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
                _named(_STATE_CHANGE, message.get('2')),
                _named(_ACTIVITY, message.get('3')),
                _text(message.get('6')),
                name,
                record.data_start_offset,
            ))
    data_headers = (('SEGB Timestamp', 'datetime'), 'IDS Handle', 'State Change', 'Activity State',
                    'Name', 'SEGB File', 'Offset')
    return data_headers, data_list, '\n'.join(sorted(source_dirs))
