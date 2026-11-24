__artifacts_v2__ = {
    "get_biomeDKKeybag": {
        "name": "Biome - Keybag",
        "description": "Parses records from the _DKEvent.Keybag.IsLocked biome stream: start and end "
                       "dates and the integer value stored with the record, without a Locked or "
                       "Unlocked label. Only records in the Written state are reported.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2025-04-29",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names come from CoreDuet's _DKPREvent class, read from CoreDuet.framework on "
                 "macOS 27.2.1 (26B131); no iOS copy of the class was read. Is Locked (as stored) is field 4.4 (the value's integerValue) of the _DKEvent.Keybag.IsLocked stream, and the header repeats that stream name. It does not say that 1 means locked. It was reported as Field 4.4 (as stored) in v2026.4.6; it is "
                 "reported as decoded, without Boolean conversion, and its meaning is not established. "
                 "Start Date and End Date are fields 2 and 3 (startDate and endDate) and were reported "
                 "before as Start Time and End Time. On the 21 iOS images tested (20 held written records of this stream), which include the sample_data keys, Is Locked (as stored) held 1 on 1,657 "
                 "and 0 on 1,532 of the 3,189 rows. Missing required fields retain the existing "
                 "skipped-record behavior, and Deleted-state records remain omitted. Original parser contribution: @JohnHyla. Time Zone Offset (seconds) is field 10 (timeZone), which CoreDuet's own conversion of synthetic records reads as seconds from GMT; it was not reported before. On the 21 iOS images tested (20 held written records of this stream), which include the sample_data keys, it was set on each of the 3,189 rows, with 8 distinct values, each a whole number of quarter hours within 14 hours of GMT. A Start Date or End Date whose stored value is not a number, is NaN or infinite, or is too large for a date is left empty, and the record keeps its row. The log names the file name and the record offset. The NSDate distantPast and distantFuture values, and a value within two days after distantPast, are also left empty, and the log does not name the file or offset for those. A synthetic test (admin/test/scripts/test_biome_dkevent_bad_dates.py) checks the first case with NaN, infinity and an out-of-range number in Start Date and with NaN in End Date. No record on the 4 corpus images run for this change (hill_iphone15pro_ios26, wilkerson_iphone16_ios26, dexter_ios18, iphone11_ios17) held such a value.",
        "paths": ('*/Biome/streams/restricted/_DKEvent.Keybag.IsLocked/local/*'),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "felix_ios17": "iOS 17.6.1 | 58 rows",
            "fsfull002_ios17": "iOS 17.1 | 6 rows",
            "hc_ios18_7": "iOS 18.7.8 | 138 rows",
            "iphone11_ios17": "iOS 17.3 | 82 rows",
            "iphone12_ios18": "iOS 18.7 | 115 rows",
            "iphone14plus_ios18": "iOS 18.0 | 28 rows",
            "otto_ios17": "iOS 17.5.1 | 62 rows",
            "dexter_ios18": "iOS 18.3.2 | 382 rows",
            "abe_ios16": "iOS 16.5 | 942 rows",
            "felix23_ios16": "iOS 16.5 | 8 rows",
            "magnet_ios16": "iOS 16.1.1 | 66 rows",
        }
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
from scripts.biome_stream_records import cocoa_date


@artifact_processor
def get_biomeDKKeybag(context):

    typess = {
        '1': {
            'type': 'message',
            'message_typedef': {
                '1': {'type': 'str', 'name': ''},
                '2': {
                    'type': 'message',
                    'message_typedef': {
                        '1': {'type': 'int', 'name': ''},
                        '2': {'type': 'int', 'name': ''}
                    },
                    'name': ''
                }
            },
            'name': ''
        },
        '2': {'type': 'double', 'name': ''},
        '3': {'type': 'double', 'name': ''},
        '4': {
            'type': 'message',
            'message_typedef': {
                '1': {
                    'type': 'message',
                    'message_typedef': {
                        '1': {'type': 'int', 'name': ''},
                        '2': {'type': 'int', 'name': ''}
                    },
                    'name': ''
                },
                '4': {'type': 'int', 'name': ''}
            },
            'name': ''
        },
        '5': {'type': 'bytes', 'name': ''},
        '8': {'type': 'double', 'name': ''},
        '10': {'type': 'int', 'name': ''}
    }

    data_list = []
    source_dirs = set()
    for file_found in context.get_files_found():
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
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)

                    time2 = (cocoa_date(protostuff['2'], 'Biome Keybag DKEvent', filename, record.data_start_offset))
                    time3 = (cocoa_date(protostuff['3'], 'Biome Keybag DKEvent', filename, record.data_start_offset))

                    tz_offset = protostuff.get('10') if type(protostuff.get('10')) is int else ''
                    data_list.append((ts, time2, time3, tz_offset, protostuff['4']['4'], filename))
                except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as ex:
                    logfunc(f"Skipping biomeDKKeybag record due to protobuf decode error: {ex} | "
                            f"File: {context.get_relative_path(file_found)} | "
                            f"Offset: {record.data_start_offset}")
                    continue

    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Date', 'datetime'), ('End Date', 'datetime'), 'Time Zone Offset (seconds)',
                    'Is Locked (as stored)', 'Filename')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
