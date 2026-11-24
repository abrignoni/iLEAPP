__artifacts_v2__ = {
    "get_biomeAirpMode": {
        "name": "Biome - Airplane Mode DKEvent",
        "description": "Parses airplane mode entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2020-04-30",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names come from CoreDuet's _DKPREvent class, read from CoreDuet.framework on macOS "
                  "27.2.1 (26B131); no iOS copy of the class was read. Start Date and End Date are fields 2 "
                  "and 3 (startDate and endDate) and were reported before as Timestamp and Timestamp2. "
                  "Stream Name is field 1.1 (the name of the record's stream) and was reported before as "
                  "Event. Identifier is field 5 (identifier) and was reported before as GUID. Airplane Mode (raw) is field 4.4 (the value's integerValue) of the _DKEvent.System.AirplaneMode stream. Airplane Mode reads On for 1 and Off for 0 and is left empty for any other value. That reading comes from one known-data test on an iPhone running iOS 27.2.1, in which Airplane Mode was switched on and off at logged times about two minutes apart. The End Date of each record closed by a logged change fell within a second of that change (that test's records held End Date in whole seconds), and the value was 1 on the records whose interval Airplane Mode spent on and 0 on those it spent off. In that test a record described the interval that ended at the change, not the state the change set. The reading was not checked against known data on any other iOS version. The value was not reported in v2026.4.6 and was reported as Airplane Mode (as stored) in v2026.4.7. On the 21 iOS images tested (15 held written records of this stream), which include the sample_data keys, it held 0 on 72 and 1 on 49 of the 121 written rows. Field 8 (creationDate) is not reported. Time Zone Offset (seconds) is field 10 (timeZone), which CoreDuet's own conversion of synthetic records reads as seconds from GMT; it was not reported before. On the 21 iOS images tested (15 held written records of this stream), which include the sample_data keys, it was set on each of the 121 written rows, with 7 distinct values, each a whole number of quarter hours within 14 hours of GMT. A Start Date or End Date whose stored value is not a number, is NaN or infinite, or is too large for a date is left empty, and the record keeps its row. The log names the file name and the record offset. The NSDate distantPast and distantFuture values, and a value within two days after distantPast, are also left empty, and the log does not name the file or offset for those. A synthetic test (admin/test/scripts/test_biome_dkevent_bad_dates.py) checks the first case with NaN, infinity and an out-of-range number in Start Date and with NaN in End Date. No record on the 4 corpus images run for this change (hill_iphone15pro_ios26, wilkerson_iphone16_ios26, dexter_ios18, iphone11_ios17) held such a value. A written record with no field 1, 1.1, 2, 3 or 5 is skipped. So is one whose field 1 is not a message, or whose field 5 is not bytes or is not valid UTF-8. The log names the file name and the record offset, and the other records are still reported. A record with no field 4, 4.4 or 10 keeps its row with those columns empty. A synthetic test (admin/test/scripts/test_biome_dkevent_missing_fields.py) checks the skip with fields 1, 2, 3 and 5 removed in turn and with an integer in place of field 1 and of field 5. No record on the 4 corpus images run for this change (hill_iphone15pro_ios26, wilkerson_iphone16_ios26, dexter_ios18, iphone11_ios17) was skipped this way."),
        "paths": ('*/Biome/streams/restricted/_DKEvent.System.AirplaneMode/local/*'),
        "output_types": "standard",
        "artifact_icon": "plane",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 35 rows",
            "felix_ios17": "iOS 17.6.1 | 14 rows",
            "fsfull002_ios17": "iOS 17.1 | 13 rows",
            "hc_ios18_7": "iOS 18.7.8 | 48 rows",
            "iphone11_ios17": "iOS 17.3 | 12 rows",
            "iphone12_ios18": "iOS 18.7 | 27 rows",
            "otto_ios17": "iOS 17.5.1 | 23 rows",
            "abe_ios16": "iOS 16.5 | 114 rows",
            "felix23_ios16": "iOS 16.5 | 27 rows",
            "magnet_ios16": "iOS 16.1.1 | 8 rows",
        }
    }
}

import os
import struct
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from datetime import timezone
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.biome_stream_records import cocoa_date

# Labels from a known-data test on iOS 27.2.1; see the notes.
ON_OFF = {0: 'Off', 1: 'On'}

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)
# A decoded record that raises one of these while its fields are read is skipped and logged.
_FIELD_ERRORS = (KeyError, TypeError, AttributeError, ValueError, IndexError)

@artifact_processor
def get_biomeAirpMode(context):

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
                '3': {'type': 'bytes', 'name': ''},
                '4': {'type': 'int', 'name': ''}
            },
            'name': ''
        },
        '5': {'type': 'bytes', 'name': ''},
        '8': {'type': 'fixed64', 'name': ''},
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
            offset = record.data_start_offset
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome Airplane Mode DKEvent: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue
                try:
                    # an NSDate sentinel converts to ''; kept as None, as in the Deleted rows
                    timestart = (cocoa_date(protostuff['2'], 'Biome Airplane Mode DKEvent', filename, record.data_start_offset) or None)
                    timeend = (cocoa_date(protostuff['3'], 'Biome Airplane Mode DKEvent', filename, record.data_start_offset) or None)
                    event = protostuff['1']['1']
                    guid = protostuff['5'].decode()
                    value = protostuff['4'].get('4', '') if isinstance(protostuff.get('4'), dict) else ''
                    state = ON_OFF.get(value, '') if type(value) is int else ''
                    tz_offset = protostuff.get('10') if type(protostuff.get('10')) is int else ''

                    data_list.append((ts, timestart, timeend, tz_offset, record.state.name, event, state, value, guid, filename, offset))
                except _FIELD_ERRORS as ex:
                    logfunc(f'Biome Airplane Mode DKEvent: record at offset {record.data_start_offset} in {filename} could not be '
                            f'read ({type(ex).__name__}: {ex}); skipped')
                    continue

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, record.state.name, None, None, None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Date', 'datetime'), ('End Date', 'datetime'),
                    'Time Zone Offset (seconds)', 'SEGB State', 'Stream Name', 'Airplane Mode', 'Airplane Mode (raw)', 'Identifier', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))


