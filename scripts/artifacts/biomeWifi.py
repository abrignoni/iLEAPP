__artifacts_v2__ = {
    "get_biomeWifi": {
        "name": "Biome - WiFi DKEvent",
        "description": "Parses DKEvent WiFi entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names come from CoreDuet's _DKPREvent class, read from CoreDuet.framework on macOS "
                  "27.2.1 (26B131); no iOS copy of the class was read. Start Date is field 2 (startDate) "
                  "and was reported before as Timestamp. End Date is field 3 (endDate) and was not reported before. Stream Name is field 1.1 and was reported before "
                  "as Event. Network Name is field 4.3 (the value's stringValue) of the _DKEvent.Wifi.Connection stream. It was reported as Device in v2026.4.6 and as Wi-Fi Connection Value (as stored) after that. In one known-data test on an iPhone running iOS 27.2.1, in which Wi-Fi and Airplane Mode were switched at logged times about two minutes apart, each record closed by a logged change described the interval before that change: the value held the name of the network the phone was joined to for an interval spent connected and was empty for an interval spent with Wi-Fi switched off or with Airplane Mode switched on, and End Date was the time of the change that closed the interval with its seconds dropped, as Start Date was for the change that opened it. The reading was not checked against known data on any other iOS version. On the 21 iOS images tested (19 held written records of this stream), which include the sample_data keys, Network Name was empty on 580 of "
                  "the 1,836 written rows. Identifier is field 5 and was reported before as GUID. Field 8 (creationDate) is not reported. Time Zone Offset (seconds) is field 10 (timeZone), which CoreDuet's own conversion of synthetic records reads as seconds from GMT; it was not reported before. On the 21 iOS images tested (19 held written records of this stream), which include the sample_data keys, it was set on each of the 1,836 written rows, with 7 distinct values, each a whole number of quarter hours within 14 hours of GMT."),
        "paths": ('*/Biome/streams/restricted/_DKEvent.Wifi.Connection/local/*'),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 398 rows",
            "felix_ios17": "iOS 17.6.1 | 609 rows",
            "fsfull002_ios17": "iOS 17.1 | 180 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1113 rows",
            "iphone11_ios17": "iOS 17.3 | 813 rows",
            "iphone14plus_ios18": "iOS 18.0 | 13 rows",
            "otto_ios17": "iOS 17.5.1 | 239 rows",
            "abe_ios16": "iOS 16.5 | 1191 rows",
            "felix23_ios16": "iOS 16.5 | 2232 rows",
            "magnet_ios16": "iOS 16.1.1 | 382 rows",
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
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)


@artifact_processor
def get_biomeWifi(context):

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
                '3': {'type': 'bytes', 'name': ''}
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
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome WiFi DKEvent: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                # an NSDate sentinel converts to ''; kept as None, as in the Deleted rows
                timestart = (webkit_timestampsconv(protostuff['2']) or None)
                timeend = (webkit_timestampsconv(protostuff['3']) or None) if '3' in protostuff else None

                event = protostuff['1']['1']
                guid = protostuff['5'].decode()
                device = protostuff['4'].get('3','')
                if device != '':
                    device = device.decode()

                tz_offset = protostuff.get('10') if type(protostuff.get('10')) is int else ''

                data_list.append((ts, timestart, timeend, tz_offset, record.state.name, event, device, guid, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, record.state.name, None, None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Date', 'datetime'), ('End Date', 'datetime'), 'Time Zone Offset (seconds)', 'SEGB State',
                    'Stream Name', 'Network Name',
                    'Identifier', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
