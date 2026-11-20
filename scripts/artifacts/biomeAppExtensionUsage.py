__artifacts_v2__ = {
    "get_biomeAppExtensionUsage": {
        "name": "Biome - App Extension Usage",
        "description": ("Runs of app extensions from the App.ExtensionUsage biome stream. Each row is "
                        "one run: a record with starting true, paired with a later record of the same "
                        "extension, parent and extension host with starting false, which is read here "
                        "as the end of the run. A record with no partner is listed on its own row."),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are those of the BMAppExtensionUsage class, read from "
                  "BiomeLibrary.framework on macOS 27.2.1 (26B131): starting, absoluteTimestamp, "
                  "bundleID, parentBundleID and extensionHostID. No iOS copy of the class was read. "
                  "The class has no stop or end field; reading a record with starting false as the end "
                  "of a run is an interpretation of the field name. Extension Bundle ID is the bundleID "
                  "field and Parent Bundle ID the parentBundleID field. Start Time and End Time are the "
                  "absoluteTimestamp of the two records, read as seconds since 2001-01-01 UTC; the macOS "
                  "class returns 2001-01-01 00:00:00 UTC for a planted value of 0. On the tested records "
                  "absoluteTimestamp held whole seconds and was between 0 and 1 second before the SEGB "
                  "record time. A record with no absoluteTimestamp uses the SEGB record time instead; that "
                  "did not occur on the tested records. Records are paired per Extension Bundle ID, Parent "
                  "Bundle ID and Extension Host ID in time order, and records with the same time are "
                  "ordered by file and then by offset. When runs with the same three identifiers overlap, "
                  "an end is paired with the earliest open start: the records do not say which start an "
                  "end belongs to, so the pairing of overlapping runs is an assumption. A start with no "
                  "later end keeps End Time blank, and an end with no earlier start keeps Start Time "
                  "blank; Paired says which. Paired held Yes on every row of the tested image; that "
                  "covers live records only. Filename and Offset name the SEGB file and record of the "
                  "start (of the end when there is no start); Filename separates the stream's files and "
                  "held one value on every row of the tested image. Extension Host ID is the "
                  "extensionHostID string, and a missing value shows as blank; on the tested records it "
                  "held reverse-DNS strings. Records the SEGB file marks deleted are not listed; on the "
                  "tested file their data was all zero bytes. The stream was absent from the tested "
                  "iOS 26.5.2 image. Field mapped from a private sample."),
        "paths": ('*/[Bb]iome/streams/restricted/App.ExtensionUsage/local/*',),
        "output_types": "standard",
        "artifact_icon": "package",
    }
}


import os
import struct
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from google.protobuf.message import DecodeError
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)
_COCOA_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)

# BMAppExtensionUsage field numbers and types, BiomeLibrary.framework on macOS 27.2.1 (26B131):
# 1 starting (bool), 2 absoluteTimestamp (double), 3 bundleID, 4 parentBundleID,
# 5 extensionHostID (strings).
TYPES = {
    '1': {'type': 'int', 'name': ''},
    '2': {'type': 'double', 'name': ''},
    '3': {'type': 'str', 'name': ''},
    '4': {'type': 'str', 'name': ''},
    '5': {'type': 'str', 'name': ''},
}


def _text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return '' if value is None else str(value)


def _cocoa(seconds):
    if not isinstance(seconds, float):
        return None
    try:
        return _COCOA_EPOCH + timedelta(seconds=seconds)
    except OverflowError:
        return None


@artifact_processor
def get_biomeAppExtensionUsage(context):
    events = []
    source_dirs = set()
    for file_found in sorted(map(str, context.get_files_found())):
        filename = os.path.basename(file_found)
        if filename.startswith('.') or not os.path.isfile(file_found):
            continue
        if 'tombstone' in context.get_relative_path(file_found):
            continue
        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            if record.state != EntryState.Written:
                continue
            try:
                fields, _ = blackboxprotobuf.decode_message(record.data, TYPES)
            except _DECODE_ERRORS as ex:
                logfunc(f'App Extension Usage: could not decode record at offset '
                        f'{record.data_start_offset} in {filename}: {ex}')
                continue
            when = _cocoa(fields.get('2'))
            if when is None:
                when = record.timestamp1.replace(tzinfo=timezone.utc)
                logfunc(f'App Extension Usage: record at offset {record.data_start_offset} in '
                        f'{filename} has no absoluteTimestamp; the SEGB record time is used')
            key = (_text(fields.get('3')), _text(fields.get('4')), _text(fields.get('5')))
            events.append((when, fields.get('1') == 1, key, filename, record.data_start_offset))

    data_list = []
    open_runs = defaultdict(deque)
    for when, starting, key, filename, offset in sorted(events, key=lambda e: (e[0], e[3], e[4])):
        if starting:
            open_runs[key].append((when, filename, offset))
        elif open_runs[key]:
            start, sfile, soff = open_runs[key].popleft()
            data_list.append(_row(start, when, key, 'Yes', sfile, soff))
        else:
            data_list.append(_row(None, when, key, 'No (end without start)', filename, offset))
    for key, starts in open_runs.items():
        for start, sfile, soff in starts:
            data_list.append(_row(start, None, key, 'No (start without end)', sfile, soff))
    data_list.sort(key=lambda r: (r[0] or r[1]))

    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'),
                    ('Duration (seconds)', 'number'), 'Extension Bundle ID', 'Parent Bundle ID',
                    'Extension Host ID', 'Paired', 'Filename', 'Offset')
    return data_headers, data_list, '\n'.join(sorted(source_dirs))


def _row(start, end, key, paired, filename, offset):
    duration = round((end - start).total_seconds(), 3) if start and end else None
    return (start, end, duration, key[0], key[1], key[2], paired, filename, offset)
