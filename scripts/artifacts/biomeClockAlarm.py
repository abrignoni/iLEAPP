__artifacts_v2__ = {
    "get_biomeClockAlarm": {
        "name": "Biome - Clock Alarm",
        "description": "Parses alarm state changes from the Clock.Alarm biome stream, including "
                       "the alarm identifier.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names and Event Type and Last Event Type names are those of the "
                 "BMClockAlarm class, read from BiomeLibrary.framework on macOS 27.2.1 (26B131); "
                 "no iOS copy of the class was read. Event Type was reported before as State (raw), "
                 "Is Sleep Alarm as Field 1 (raw) and Last Event Type as Field 4 (raw). "
                 "The names depend on the integer shown in Data Version. The SEGB reader returns it "
                 "unnamed with each entry: it is the second integer of the entry header in SEGB "
                 "version 2 files and the last field of the record header in SEGB version 1 files. "
                 "It is read here as the Biome data version. BMClockAlarm reads data version 1 with Event Type 0 = Firing, "
                 "1 = Stopped, 2 = Snoozed, 3 = Created, 4 = Updated, 5 = Deleted and Last Event "
                 "Type 0 = Idle through 10 = TimedOut, and data version 2 with 0 = Unknown added "
                 "first, so every version 1 value moves up by one. "
                 "A value or version outside those lists keeps its integer with the name blank. All 48 written records on the tested images are data version 1. On those records Event Type was 0 (Firing) on 20, 1 (Stopped) on 17, 4 (Updated) on 7, 2 (Snoozed) on 2, 3 (Created) on 1 and 5 (Deleted) on 1, Last Event Type was 0 (Idle) on all 48, and Is Sleep Alarm was False on 44 and True on the 4 records of abe_ios16. "
                 "Deleted rows carry no fields. Published research on this stream: Mattia "
                 "Epifani, '84 Streams Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html"
                 " "
                 "On one tested iOS 16 image (abe_ios16) the stream is stored under Alarm, which BiomeLibrary.framework on macOS 27.2.1 (26B131) lists as its legacy name, and is read too. The tested iOS 15 image held no such folder. Its 4 written records held fields 1 to 4 and are data version 1."),
        "paths": ('*/streams/*/Clock.Alarm/local/*', '*/streams/*/Alarm/local/*'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 63 rows",
            "hc_ios18_7": "iOS 18.7.8 | 27 rows",
            "iphone11_ios17": "iOS 17.3 | 12 rows",
        },
    }
}


import os
import struct
from datetime import timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

# eventType and lastEventType names by record data version (the unnamed int the SEGB
# reader returns per entry), read from BiomeLibrary.framework BMClockAlarm on macOS 27.2.1 (26B131).
# Data version 2 adds 0 = Unknown, so every version 1 value moves up by one. Values the
# class renders only as its fallback get no name.
_EVENT_TYPES_V1 = ('Firing', 'Stopped', 'Snoozed', 'Created', 'Updated', 'Deleted')
_LAST_EVENT_TYPES_V1 = (
    'Idle', 'Fired', 'FiredAfterSnooze', 'FiredGoToBedReminder',
    'FiredGoToBedReminderAfterSnooze', 'Dismissed', 'DismissedGoToBedReminder', 'Snoozed',
    'SnoozedBedtime', 'ConfigurationChanged', 'TimedOut',
)
EVENT_TYPE_BY_VERSION = {
    1: dict(enumerate(_EVENT_TYPES_V1)),
    2: dict(enumerate(('Unknown',) + _EVENT_TYPES_V1)),
}
LAST_EVENT_TYPE_BY_VERSION = {
    1: dict(enumerate(_LAST_EVENT_TYPES_V1)),
    2: dict(enumerate(('Unknown',) + _LAST_EVENT_TYPES_V1)),
}

TYPESS = {
    '1': {'type': 'int', 'name': ''},
    '2': {'type': 'int', 'name': ''},
    '3': {'type': 'str', 'name': ''},
    '4': {'type': 'int', 'name': ''},
}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None:
        return ''
    return str(value)


def _bool_text(value):
    if value == 1 and not isinstance(value, bool):
        return 'True'
    if value == 0 and not isinstance(value, bool):
        return 'False'
    return ''


@artifact_processor
def get_biomeClockAlarm(context):

    data_list = []
    source_dirs = set()
    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in context.get_relative_path(file_found):
                continue
        else:
            continue

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Clock Alarm: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                version = getattr(record, '_unknown_value', None)
                event_type = protostuff.get('2', '')
                last_event_type = protostuff.get('4', '')
                data_list.append((ts, record.state.name, _to_str(protostuff.get('3', b'')),
                                  EVENT_TYPE_BY_VERSION.get(version, {}).get(event_type, ''),
                                  event_type,
                                  LAST_EVENT_TYPE_BY_VERSION.get(version, {}).get(
                                      last_event_type, ''),
                                  last_event_type,
                                  _bool_text(protostuff.get('1')), _to_str(version),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None, None,
                                  None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Alarm ID', 'Event Type',
                    'Event Type (raw)', 'Last Event Type', 'Last Event Type (raw)',
                    'Is Sleep Alarm', 'Data Version', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
