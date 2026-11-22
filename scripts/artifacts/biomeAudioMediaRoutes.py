"""Biome audio and media route streams.

Both streams record the route in use when audio or media plays. Bluetooth and
CarPlay routes carry an accessory identifier and name, which may associate an
accessory with the device at the recorded time.
"""
__artifacts_v2__ = {
    "get_biomeAudioRoute": {
        "name": "Biome - Audio Route",
        "description": "Parses audio route changes from the Audio.Route biome stream: the "
                       "route identifier, its port type and port name, whether the route is "
                       "external, the route change reason and whether the route is an input "
                       "or an output.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names and the Route Change Reason and Type names are those of the "
                 "BMAudioRoute class, read from BiomeLibrary.framework on macOS 27.2.1 "
                 "(26B131); no iOS copy of the class was read. Columns reported before as "
                 "Route Name, Field 1 (raw), Field 5 (raw) and Field 6 (raw) are now "
                 "Identifier, External, Route Change Reason and Type; the integers for Route "
                 "Change Reason and Type stay in the (raw) columns, and External shows True "
                 "for 1 and False for 0. On the tested images Type was Input (1) on 350 and "
                 "Output (2) on 917 of the 1,267 written rows. On the tested images Input was on "
                 "341 rows whose port type names a microphone, and Output on 813 rows whose "
                 "port type names a speaker or receiver, which fits the framework names. On the "
                 "tested images External was True on 113 and False on 1,154 of the 1,267 "
                 "written rows, and it was uniform False on some images.",
        "paths": ('*/streams/*/Audio.Route/local/*',),
        "output_types": "standard",
        "artifact_icon": "headphones",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 3833 rows",
            "iphone11_ios17": "iOS 17.3 | 2261 rows",
        },
    },
    "get_biomeMediaRoute": {
        "name": "Biome - Media Route",
        "description": "Parses records from the Media.Route biome stream. Rows carry a group "
                       "leader output device ID and, where stored, a route identifier; route "
                       "type and subtype are reported raw.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "A BMMediaRoute class exists in BiomeLibrary.framework on macOS 27.2.1 "
                 "(26B131) but is not bound to a stream there. Its field layout fits the 461 "
                 "written records on the tested images, and Group Leader Output Device ID "
                 "(reported before as Route Name) is its name for field 2. Labels are not "
                 "established from an iOS source. On the tested images Group Leader Output "
                 "Device ID and Route Identifier were identical on each of the 434 written rows "
                 "where both are set.",
        "paths": ('*/streams/*/Media.Route/local/*',),
        "output_types": "standard",
        "artifact_icon": "speaker",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 2061 rows",
            "iphone11_ios17": "iOS 17.3 | 225 rows",
        },
    },
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

# routeChangeReason names, read from BiomeLibrary.framework BMAudioRoute on macOS 27.2.1 (26B131).
ROUTE_CHANGE_REASON = {0: 'Unknown', 1: 'NewDeviceAvailable', 2: 'OldDeviceUnavailable',
                       3: 'CategoryChange', 4: 'Override', 5: 'WakeFromSleep',
                       6: 'NoSuitableRouteForCategory', 7: 'RouteConfigurationChange'}
# type names, read from BiomeLibrary.framework BMAudioRoute on macOS 27.2.1 (26B131).
ROUTE_TYPE = {0: 'Unknown', 1: 'Input', 2: 'Output'}

AUDIO_TYPESS = {
    '1': {'type': 'int', 'name': ''},
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'str', 'name': ''},
    '4': {'type': 'str', 'name': ''},
    '5': {'type': 'int', 'name': ''},
    '6': {'type': 'int', 'name': ''},
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


def _bool(value):
    if value == 1:
        return 'True'
    if value == 0:
        return 'False'
    return ''


def _name(names, value):
    return names.get(value, '') if isinstance(value, int) else ''


def _stream_files(context):
    """Non-hidden, non-tombstone stream files from the artifact's matched paths."""
    for file_found in sorted(map(str, context.get_files_found())):
        if os.path.basename(file_found).startswith('.'):
            continue
        if not os.path.isfile(file_found) or 'tombstone' in context.get_relative_path(file_found):
            continue
        yield file_found


def _source_path(context):
    return '\n'.join(sorted({os.path.dirname(f) for f in _stream_files(context)}))


def _iter_records(context, label, typess=None):
    for file_found in _stream_files(context):
        filename = os.path.basename(file_found)

        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)
            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess) \
                        if typess else blackboxprotobuf.decode_message(record.data)
                except _DECODE_ERRORS as ex:
                    logfunc(f'{label}: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue
                yield ts, record, protostuff, filename
            elif record.state == EntryState.Deleted:
                yield ts, record, None, filename


@artifact_processor
def get_biomeAudioRoute(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Identifier', 'Port Type',
                    'Port Name', 'External', 'Route Change Reason', 'Route Change Reason (raw)',
                    'Type', 'Type (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _iter_records(context, 'Audio Route', AUDIO_TYPESS):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, None, None, None,
                              None, None, filename, record.data_start_offset))
            continue
        data_list.append((ts, record.state.name, _to_str(protostuff.get('2', b'')),
                          _to_str(protostuff.get('3', b'')), _to_str(protostuff.get('4', b'')),
                          _bool(protostuff.get('1')),
                          _name(ROUTE_CHANGE_REASON, protostuff.get('5')),
                          protostuff.get('5', ''), _name(ROUTE_TYPE, protostuff.get('6')),
                          protostuff.get('6', ''), filename, record.data_start_offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def get_biomeMediaRoute(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State',
                    'Group Leader Output Device ID', 'Route Identifier', 'Route Type (raw)', 'Route Subtype (raw)',
                    'Field 1 (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _iter_records(context, 'Media Route'):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, None, None, filename,
                              record.data_start_offset))
            continue
        detail = protostuff.get('4', {})
        if not isinstance(detail, dict):
            detail = {}
        data_list.append((ts, record.state.name, _to_str(protostuff.get('2', b'')),
                          _to_str(detail.get('1', b'')), detail.get('2', ''),
                          detail.get('3', ''), protostuff.get('1', ''), filename,
                          record.data_start_offset))
    return data_headers, data_list, _source_path(context)
