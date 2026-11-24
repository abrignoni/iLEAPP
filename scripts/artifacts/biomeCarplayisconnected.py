__artifacts_v2__ = {
    "get_biomeCarplayisconnected": {
        "name": "Biome - Carplay",
        "description": "Parses carplay is connected entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names come from CoreDuet's _DKPREvent class, read from CoreDuet.framework on macOS "
                  "27.2.1 (26B131); no iOS copy of the class was read. Start Date, End Date and Creation "
                  "Date are fields 2, 3 and 8 (startDate, endDate and creationDate) and were reported "
                  "before as Time Start, Time End and Time Write. Stream Name is field 1.1 and was reported "
                  "before as Activity. Is Connected (as stored) is field 4.4 (the value's integerValue) of the _DKEvent.Carplay.IsConnected stream, and the header repeats that stream name. It does not say that 1 means connected. It was reported as Status in v2026.4.6; it is shown as stored and its meaning is not established. On the 21 iOS images tested (12 held written records of this stream), which include the sample_data keys, it held 0 on 89 and 1 on 68 of the 157 written rows. Identifier is field 5 and was reported before as Action GUID. Time Zone Offset (seconds) is field 10 (timeZone), which CoreDuet's own conversion of synthetic records reads as seconds from GMT; it was not reported before. On the 21 iOS images tested (12 held written records of this stream), which include the sample_data keys, it was set on each of the 157 written rows, with 6 distinct values, each a whole number of quarter hours within 14 hours of GMT. A Start Date, End Date or Creation Date whose stored value is not a number, is NaN or infinite, or is too large for a date is left empty, and the record keeps its row. The log names the file name and the record offset. The NSDate distantPast and distantFuture values, and a value within two days after distantPast, are also left empty, and the log does not name the file or offset for those. A synthetic test (admin/test/scripts/test_biome_dkevent_bad_dates.py) checks the first case with NaN, infinity and an out-of-range number in Start Date and with NaN in End Date and Creation Date. No record on the 4 corpus images run for this change (hill_iphone15pro_ios26, wilkerson_iphone16_ios26, dexter_ios18, iphone11_ios17) held such a value. A written record with no field 1, 1.1, 2, 3, 4, 4.4, 5 or 8 is skipped. So is one whose field 1 or 4 is not a message. The log names the file name and the record offset, and the other records are still reported. A record with no field 10 keeps its row with that column empty. A synthetic test (admin/test/scripts/test_biome_dkevent_missing_fields.py) checks the skip with fields 1, 2, 3, 4, 5 and 8 removed in turn and with an integer in place of field 1 and of field 4. No record on the 4 corpus images run for this change (hill_iphone15pro_ios26, wilkerson_iphone16_ios26, dexter_ios18, iphone11_ios17) was skipped this way."),
        "paths": ('*/Biome/streams/restricted/_DKEvent.Carplay.IsConnected/local/*'),
        "output_types": "standard",
        "artifact_icon": "car",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 116 rows",
            "felix_ios17": "iOS 17.6.1 | 2 rows",
            "fsfull002_ios17": "iOS 17.1 | 6 rows",
            "hc_ios18_7": "iOS 18.7.8 | 36 rows",
            "iphone11_ios17": "iOS 17.3 | 34 rows",
            "iphone12_ios18": "iOS 18.7 | 2 rows",
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "otto_ios17": "iOS 17.5.1 | 8 rows",
            "abe_ios16": "iOS 16.5 | 116 rows",
            "felix23_ios16": "iOS 16.5 | 2 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
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

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)
# A decoded record that raises one of these while its fields are read is skipped and logged.
_FIELD_ERRORS = (KeyError, TypeError, AttributeError, ValueError, IndexError)


@artifact_processor
def get_biomeCarplayisconnected(context):

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
        '5': {'type': 'str', 'name': ''},
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
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome Carplay: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue
                try:
                    activity = (protostuff['1']['1'])

                    # an NSDate sentinel converts to ''; kept as None, as in the Deleted rows
                    timestart = (cocoa_date(protostuff['2'], 'Biome CarPlay Connected', filename, record.data_start_offset) or None)
                    timeend = (cocoa_date(protostuff['3'], 'Biome CarPlay Connected', filename, record.data_start_offset) or None)
                    timewrite = (cocoa_date(protostuff['8'], 'Biome CarPlay Connected', filename, record.data_start_offset) or None)

                    actionguid = (protostuff['5'])
                    status = (protostuff['4']['4'])

                    tz_offset = protostuff.get('10') if type(protostuff.get('10')) is int else ''
                    data_list.append((ts, timestart, timeend, timewrite, tz_offset, record.state.name, activity, status, actionguid,
                                      filename,  record.data_start_offset))
                except _FIELD_ERRORS as ex:
                    logfunc(f'Biome CarPlay Connected: record at offset {record.data_start_offset} in {filename} could not be '
                            f'read ({type(ex).__name__}: {ex}); skipped')
                    continue

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, None, record.state.name, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Date', 'datetime'), ('End Date', 'datetime'),
                    ('Creation Date', 'datetime'), 'Time Zone Offset (seconds)', 'SEGB State', 'Stream Name', 'Is Connected (as stored)', 'Identifier', 'Filename',
                    'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
