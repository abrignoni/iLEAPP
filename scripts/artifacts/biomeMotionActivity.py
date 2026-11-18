__artifacts_v2__ = {
    "get_biomeMotionActivity": {
        "name": "Biome - Motion Activity",
        "description": "Motion activity records from the Motion.Activity biome stream: the "
                       "stationary, walking, running, automotive, cycling and unknown flags, "
                       "the start date and the confidence each record stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Biome",
        "notes": "One row per written record of the Motion.Activity stream. Field names and "
                 "numbers come from BMMotionActivity.protoFields in BiomeLibrary.framework, read "
                 "on macOS 27.2.1 (26B131): 1 stationary, 2 walking, 3 running, 4 automotive, 5 "
                 "cycling, 6 unknown, 7 startDate and 8 confidence. Confidence names come from "
                 "BMMotionActivityConfidenceAsString in the same framework (0 Unknown, 1 Low, 2 "
                 "Medium, 3 High), and the stored number is kept beside the name. That the iOS "
                 "writer of these files uses the same schema as the macOS framework was not "
                 "checked beyond the data: every written record on the tested images decoded to "
                 "those 8 fields. The six flags are shown as Yes or No. More than one flag was Yes "
                 "on 570 rows of hill_iphone15pro_ios26, 5,264 of wilkerson_iphone16_ios26 and "
                 "8,106 of iphone11_ios17, and none was Yes on 4,780, 3,826 and 4,607. Running "
                 "held No on every row of hill_iphone15pro_ios26 and Unknown held No on every row "
                 "of all three tested images. Start Date is startDate, a double. BMMotionActivity "
                 "in the same macOS framework reads it as seconds since 1970 UTC (checked with a "
                 "synthetic record); that the iOS writer does the same was not checked beyond the "
                 "data: read this way it is within one second of the SEGB Timestamp on 12,035 of "
                 "12,509, 20,132 of 21,032 and 32,371 of 32,933 rows, never more than 4 seconds "
                 "after it and at most 47 minutes before it. Rows span 28 days on each of the "
                 "three tested images. Records the SEGB file marks deleted are not listed, and "
                 "their payloads are not decoded: 16,380, 16,308 and 1,655 on the three images. "
                 "Files under the stream's tombstone folder are not read. Their written records do "
                 "not have the Motion.Activity layout: on the two iOS 26 images they hold six "
                 "fields numbered 1 to 6, on iphone11_ios17 five fields numbered 1 to 5, and "
                 "fields 1 and 5 are length-delimited. What they record is not established. The "
                 "Locationd Cache - Motion State History artifact covers the last 4 to 9 days on "
                 "the same images; this stream reaches back about 28 days. The two were not "
                 "compared row by row.",
        "paths": ('*/streams/*/Motion.Activity/local/*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 12509 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 21032 rows",
            "iphone11_ios17": "iOS 17.3 | 32933 rows",
        },
    }
}


import os
import struct
from datetime import datetime, timezone

from google.protobuf.message import DecodeError
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)
# Field numbers and names from BMMotionActivity.protoFields, and confidence names from
# BMMotionActivityConfidenceAsString, both read from BiomeLibrary.framework on macOS 27.2.1
# (26B131).
_FLAGS = (('1', 'stationary'), ('2', 'walking'), ('3', 'running'), ('4', 'automotive'),
          ('5', 'cycling'), ('6', 'unknown'))
_CONFIDENCE = {0: 'Unknown', 1: 'Low', 2: 'Medium', 3: 'High'}


def _start(value):
    '''startDate, a double carried as fixed64, read as Unix seconds in UTC, or None.'''
    if not isinstance(value, int):
        return None
    seconds = struct.unpack('<d', struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF))[0]
    if not seconds:
        return None
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def _flag(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _confidence(value):
    if not isinstance(value, int):
        return ''
    return f'{_CONFIDENCE[value]} ({value})' if value in _CONFIDENCE else f'Unknown value ({value})'


@artifact_processor
def get_biomeMotionActivity(context):
    data_list = []
    source_dirs = set()
    deleted = 0
    for file_found in sorted(str(found) for found in context.get_files_found()):
        filename = os.path.basename(file_found)
        if filename.startswith('.') or not os.path.isfile(file_found):
            continue
        if '/tombstone/' in context.get_relative_path(file_found).replace('\\', '/'):
            continue
        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            if record.state != EntryState.Written:
                deleted += 1
                continue
            try:
                message, _ = blackboxprotobuf.decode_message(record.data)
            except _DECODE_ERRORS as error:
                logfunc(f'Motion Activity: could not decode record at offset '
                        f'{record.data_start_offset} in {filename}: {error}')
                continue
            data_list.append((
                _start(message.get('7')),
                record.timestamp1.replace(tzinfo=timezone.utc),
                *(_flag(message.get(number)) for number, _ in _FLAGS),
                _confidence(message.get('8')),
                filename,
                record.data_start_offset,
            ))
    if deleted:
        logfunc(f'Motion Activity: {deleted} record(s) marked deleted are not listed')
    data_headers = (
        ('Start Date', 'datetime'), ('SEGB Timestamp', 'datetime'), 'Stationary', 'Walking',
        'Running', 'Automotive', 'Cycling', 'Unknown', 'Confidence', 'Filename', 'Offset')
    return data_headers, data_list, '\n'.join(sorted(source_dirs))
