"""Biome audio and media route streams.

Both streams record the route in use when audio or media plays. Bluetooth and
CarPlay routes carry an accessory identifier and name, which may associate an
accessory with the device at the recorded time.
"""
__artifacts_v2__ = {
    "get_biomeAudioRoute": {
        "name": "Biome - Audio Route",
        "description": "Parses audio route changes from the Audio.Route biome stream: the "
                       "route name, its port type and the port name (for example Built-In "
                       "Microphone / MicrophoneBuiltIn / iPhone Microphone).",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field 6 distinguishes input from output routes in observed data (1 with "
                 "microphone routes, 2 with speaker and receiver routes) but is reported raw "
                 "as the mapping is not confirmed.",
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
        "description": "Parses media output route changes from the Media.Route biome stream. "
                       "Bluetooth and AirPlay routes carry the accessory identifier and name.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
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


def _stream_files(context):
    """Non-hidden, non-tombstone stream files from the artifact's matched paths."""
    for file_found in sorted(map(str, context.get_files_found())):
        if os.path.basename(file_found).startswith('.'):
            continue
        if not os.path.isfile(file_found) or 'tombstone' in file_found:
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
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Route Name', 'Port Type',
                    'Port Name', 'Field 1 (raw)', 'Field 5 (raw)', 'Field 6 (raw)', 'Filename',
                    'Offset')
    data_list = []
    for ts, record, protostuff, filename in _iter_records(context, 'Audio Route', AUDIO_TYPESS):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, None, None, None,
                              filename, record.data_start_offset))
            continue
        data_list.append((ts, record.state.name, _to_str(protostuff.get('2', b'')),
                          _to_str(protostuff.get('3', b'')), _to_str(protostuff.get('4', b'')),
                          protostuff.get('1', ''), protostuff.get('5', ''),
                          protostuff.get('6', ''), filename, record.data_start_offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def get_biomeMediaRoute(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Route Name',
                    'Route Identifier', 'Route Type (raw)', 'Route Subtype (raw)',
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
