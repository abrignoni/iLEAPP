__artifacts_v2__ = {
    "get_biomeWidgetsViewed": {
        "name": "Biome - Widgets Viewed",
        "description": "Records from the Widgets.Viewed biome stream: the start and end dates, "
                       "the widget extension and bundle identifiers, and the page, stack, view and "
                       "budget values each record stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "One row per written record of the Widgets.Viewed stream. Field names and numbers "
                 "come from BMWidgetsViewed protoFields in BiomeLibrary.framework, read on macOS "
                 "27.2.1 (26B131): 1 budgetID, 2 bundleID, 3 endDate, 4 extensionBundleID, 5 "
                 "inStack, 6 pageID, 7 startDate, 8 timeUntilExpiration and 9 viewID. That the iOS "
                 "writer uses the same schema was checked only against the data: every written "
                 "record decoded to those fields. Start Date and End Date are startDate and "
                 "endDate read as seconds since 1970 UTC; no source for that epoch was found. Read "
                 "that way End Date is never before Start Date, Duration (seconds) is End Date "
                 "minus Start Date and ran from under a second to 92 seconds on "
                 "hill_iphone15pro_ios26 and to 300 seconds on wilkerson_iphone16_ios26, and the "
                 "SEGB Timestamp falls after End Date on every row, by up to 12 hours on "
                 "hill_iphone15pro_ios26 and 24 hours on wilkerson_iphone16_ios26, so the SEGB "
                 "time is not the viewing time. What a start and end mark on screen is not "
                 "established. The widget is named by Extension Bundle ID (6 values on "
                 "hill_iphone15pro_ios26, 7 on wilkerson_iphone16_ios26); Bundle ID is empty on "
                 "every row of both images, which store no bundleID. In Stack held No on every row "
                 "of wilkerson_iphone16_ios26. Page ID, View ID, Budget ID and Time Until "
                 "Expiration are reported as stored; Time Until Expiration held a value below "
                 "minus one billion on 11 rows of hill_iphone15pro_ios26 and 68 of "
                 "wilkerson_iphone16_ios26, and what it means is not established. Only records in "
                 "the written state are reported, and the stream's tombstone folder is not read. "
                 "hill_iphone15pro_ios26 has one stream file, so SEGB File held one value on every "
                 "row there. iphone11_ios17 holds no stream file.",
        "paths": ('*/streams/*/Widgets.Viewed/local/*',),
        "output_types": "standard",
        "artifact_icon": "layout-dashboard",
        "sample_data": {
            "hill_iphone15pro_ios26": "iOS 26.3.1 | 199 rows",
            "wilkerson_iphone16_ios26": "iOS 26.5.2 | 2300 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows, no stream file",
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
# Field names and numbers from BMWidgetsViewed protoFields, read from BiomeLibrary.framework on
# macOS 27.2.1 (26B131): 1 budgetID, 2 bundleID, 3 endDate, 4 extensionBundleID, 5 inStack,
# 6 pageID, 7 startDate, 8 timeUntilExpiration, 9 viewID. The string fields are decoded as bytes.
_TYPES = {key: {'type': 'bytes'} for key in ('1', '2', '4', '9')}


def _double(value):
    if isinstance(value, float):
        return value
    if not isinstance(value, int):
        return None
    return struct.unpack('<d', struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF))[0]


def _unix(value):
    seconds = _double(value)
    if not seconds:
        return ''
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return '' if value is None or isinstance(value, (dict, list)) else str(value)


def _flag(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


@artifact_processor
def get_biomeWidgetsViewed(context):
    data_list, read = [], set()
    for found in sorted(str(path) for path in context.get_files_found()):
        name = os.path.basename(found)
        if name.startswith('.') or not os.path.isfile(found):
            continue
        if '/tombstone/' in context.get_relative_path(found).replace('\\', '/'):
            continue
        read.add(found)
        for record in read_segb_file(found):
            if record.state != EntryState.Written:
                continue
            try:
                message, _ = blackboxprotobuf.decode_message(record.data, _TYPES)
            except _DECODE_ERRORS as error:
                logfunc(f'Widgets Viewed: could not decode record at offset '
                        f'{record.data_start_offset} in {name}: {error}')
                continue
            start, end = _double(message.get('7')), _double(message.get('3'))
            expiration = _double(message.get('8'))
            data_list.append((
                _unix(message.get('7')),
                _unix(message.get('3')),
                record.timestamp1.replace(tzinfo=timezone.utc),
                round(end - start, 3) if start is not None and end is not None else '',
                _text(message.get('4')),
                _text(message.get('2')),
                _flag(message.get('5')),
                '' if message.get('6') is None else message.get('6'),
                _text(message.get('9')),
                _text(message.get('1')),
                '' if expiration is None else expiration,
                name,
                record.data_start_offset,
            ))
    data_headers = (
        ('Start Date', 'datetime'), ('End Date', 'datetime'), ('SEGB Timestamp', 'datetime'),
        'Duration (seconds)', 'Extension Bundle ID', 'Bundle ID', 'In Stack',
        'Page ID (as stored)', 'View ID', 'Budget ID', 'Time Until Expiration (as stored)',
        'SEGB File', 'Offset')
    return data_headers, data_list, '\n'.join(sorted(read))
