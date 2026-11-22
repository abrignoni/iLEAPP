__artifacts_v2__ = {
    "get_biomeDiscoverabilitySignals": {
        "name": "Biome - Discoverability Signals",
        "description": "Parses records from the Discoverability.Signals biome stream. "
                       "Written records carry a signal name in Content Identifier (the "
                       "names seen "
                       "include ones that refer to Face ID face coverings, Wallet transactions "
                       "and photos moved to the trash), together with the context, OS build "
                       "and user info stored with it. What causes a signal to be written is not "
                       "established.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names are those of the BMDiscoverabilitySignals class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was "
                 "read. The four fields are read with a fixed layout. Content Identifier, Context "
                 "and OS Build were reported before as Signal, Value and Context ID (raw), and "
                 "User Info as Payload. Field 3 is the OS build string. The old Context ID (raw) "
                 "column held a number taken from that string after the schema-less decoder "
                 "misread it as a submessage, and the old Signal (raw) column held signal names "
                 "misread the same way. User Info is stored as bytes and is reported as text. On "
                 "the tested images (9 images, 18,895 written rows) Content Identifier is filled "
                 "on 18,894 rows, 258 of which had an empty Signal before; OS Build is filled on "
                 "17,734 rows, where Context ID (raw) held digits on 12,901; Context is filled on "
                 "1,768 rows, 6 more than Value was. On wilkerson_iphone16_ios26, 64 written "
                 "records could not be decoded and are logged, not reported.",
        "paths": ('*/streams/*/Discoverability.Signals/local/*',),
        "output_types": "standard",
        "artifact_icon": "radio",
        "sample_data": {
            "dexter_ios18": "8951 rows",
            "hc_ios18_7": "319 rows",
            "hc_ios26": "26.5.2 | 142 rows",
            "iphone12_ios18": "168 rows",
            "iphone14plus_ios18": "31 rows",
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


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


# BMDiscoverabilitySignals fields, read from BiomeLibrary.framework on macOS 27.2.1 (26B131):
# 1 contentIdentifier, 2 context, 3 osBuild (strings), 4 userInfo (data). Pinned as bytes so
# short strings are never guessed to be submessages.
TYPESS = {
    '1': {'type': 'bytes', 'name': ''},
    '2': {'type': 'bytes', 'name': ''},
    '3': {'type': 'bytes', 'name': ''},
    '4': {'type': 'bytes', 'name': ''},
}


@artifact_processor
def get_biomeDiscoverabilitySignals(context):

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
                    logfunc(f'Discoverability Signals: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                data_list.append((ts, record.state.name, _to_str(protostuff.get('1')),
                                  _to_str(protostuff.get('2')),
                                  _to_str(protostuff.get('3')),
                                  _to_str(protostuff.get('4')),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None,
                                  filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Content Identifier',
                    'Context', 'OS Build', 'User Info', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
