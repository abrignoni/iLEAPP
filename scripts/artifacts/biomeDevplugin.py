__artifacts_v2__ = {
    "get_biomeDevplugin": {
        "name": "Biome - Device Plugged In",
        "description": "Parses device plugged in entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Mattia Epifani quotes Ian Whiffin's article 'KnowledgeC Complete(ish)' under this stream: a record of this type is made whenever the device is charging, by cable or on a wireless charger, and isCharging may be a better name than plugged in. This module did not test it and does not label the value. Rows with SEGB State Deleted carry only the SEGB Timestamp, Filename and Offset; on the tested images there were 8,344 of them beside the 5,377 written rows, and the sample_data counts include both. Reference: "
                 "Mattia Epifani, '84 Streams Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html. "
                 "Field names come from CoreDuet's _DKPREvent class, read from CoreDuet.framework on "
                 "macOS 27.2.1 (26B131); no iOS copy of the class was read. Start Date, End Date and "
                 "Creation Date are fields 2, 3 and 8 (startDate, endDate and creationDate) and were "
                 "reported before as Time Start, Time End and Time Write. Stream Name is field 1.1 and "
                 "was reported before as Activity. Is Plugged In (as stored) is field 4.4 (the value's integerValue) of the _DKEvent.Device.IsPluggedIn stream, and the header repeats that stream name. It does not say that 1 means plugged in. It was reported as Status in v2026.4.6; it is shown as stored, and which value means which state is not established. On the 21 iOS images tested (20 held written records of this stream), which include the sample_data keys, it held "
                 "1 on 4,809 and 0 on 568 of the 5,377 written rows. Identifier is field 5 and was reported before as Action GUID. Adapter Is Wireless is the integer value of the metadata entry with index 38001, which CoreDuet's own conversion of synthetic records names adapterIsWireless; it is shown as stored and was not reported before. On the 21 iOS images tested (20 held written records of this stream), which include the sample_data keys, it held 0 on 3,547 and 1 on 11 of the 5,377 written rows and was empty on the 1,819 that held no such entry. Adapter Type (raw) is the integer value of the metadata entry with index 38000, which CoreDuet's own conversion of synthetic records names adapterType; it is shown as stored and was not reported before. On the 21 iOS images tested (20 held written records of this stream), which include the sample_data keys, it was set on the same 3,558 written rows as Adapter Is Wireless, with 12 distinct values, and each value equals one of the kIOPSFamilyCode constants in IOPM.h (IOKit, macOS 27.2 SDK), for example kIOPSFamilyCodeUSBHost (-536854528) and kIOPSFamilyCodeUSBCPD (-536854518). That the writer stores this family code was not read from its code, so no name is given. Time Zone Offset (seconds) is field 10 (timeZone), which CoreDuet's own conversion of synthetic records reads as seconds from GMT; it was not reported before. On the 21 iOS images tested (20 held written records of this stream), which include the sample_data keys, it was set on each of the 5,377 written rows, with 7 distinct values, each a whole number of quarter hours within 14 hours of GMT.",
        "paths": ('*/[Bb]iome/streams/restricted/_DKEvent.Device.IsPluggedIn/local/*',),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 1415 rows",
            "felix_ios17": "iOS 17.6.1 | 304 rows",
            "fsfull002_ios17": "iOS 17.1 | 153 rows",
            "hc_ios18_7": "iOS 18.7.8 | 639 rows",
            "iphone11_ios17": "iOS 17.3 | 476 rows",
            "iphone12_ios18": "iOS 18.7 | 455 rows",
            "iphone14plus_ios18": "iOS 18.0 | 18 rows",
            "otto_ios17": "iOS 17.5.1 | 746 rows",
            "abe_ios16": "iOS 16.5 | 3619 rows",
            "felix23_ios16": "iOS 16.5 | 170 rows",
            "magnet_ios16": "iOS 16.1.1 | 36 rows",
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
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

# _DKEvent metadata indexes that CoreDuet names _DKDeviceIsPluggedInMetadataKey-adapterIsWireless
# (read from _DKEvent fromPBCodable: on synthetic records, macOS 27.2.1, 26B131).
_ADAPTER_IS_WIRELESS_INDEX = 38001
# ... and _DKDeviceIsPluggedInMetadataKey-adapterType.
_ADAPTER_TYPE_INDEX = 38000


def _metadata_int(entries, index):
    """Integer value (field 7.N.2.4) of the metadata entry whose index (7.N.3) is index, or ''."""
    if isinstance(entries, dict):
        entries = [entries]
    for entry in entries or []:
        if isinstance(entry, dict) and entry.get('3') == index:
            value = entry.get('2')
            if isinstance(value, dict) and type(value.get('4')) is int:
                return value['4']
    return ''



def _cocoa_date(value, field, offset, filename):
    """Convert a Cocoa date; a value no datetime can hold (nan, inf, out of range) is left empty and logged."""
    try:
        # an NSDate sentinel converts to ''; kept as None, as in the Deleted rows
        return webkit_timestampsconv(value) or None
    except (ValueError, OverflowError) as ex:
        logfunc(f'Biome Device Plugged In: date in field {field} could not be converted at offset '
                f'{offset} in {filename}: {ex}')
        return None


@artifact_processor
def get_biomeDevplugin(context):

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
        '7': {
            'type': 'message',
            'message_typedef': {
                '1': {'type': 'bytes', 'name': ''},
                '2': {
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
                '3': {'type': 'int', 'name': ''}
            },
            'name': ''
        },
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
                    logfunc(f'Biome Device Plugged In: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                activity = (protostuff['1']['1'])
                timestart = _cocoa_date(protostuff['2'], 2, record.data_start_offset, filename)
                timeend = _cocoa_date(protostuff['3'], 3, record.data_start_offset, filename)
                timewrite = _cocoa_date(protostuff['8'], 8, record.data_start_offset, filename)
                
                con = (protostuff['4']['4'])
                wireless = _metadata_int(protostuff.get('7'), _ADAPTER_IS_WIRELESS_INDEX)
                adapter_type = _metadata_int(protostuff.get('7'), _ADAPTER_TYPE_INDEX)
                actionguid = (protostuff['5'])
                
                tz_offset = protostuff.get('10') if type(protostuff.get('10')) is int else ''
                data_list.append((ts, timestart, timeend, timewrite, tz_offset, record.state.name, activity, con, wireless, adapter_type, actionguid,
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, None, None, record.state.name, None, None, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Date', 'datetime'), ('End Date', 'datetime'),
                    ('Creation Date', 'datetime'), 'Time Zone Offset (seconds)', 'SEGB State', 'Stream Name', 'Is Plugged In (as stored)', 'Adapter Is Wireless',
                    'Adapter Type (raw)', 'Identifier', 'Filename',
                    'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
