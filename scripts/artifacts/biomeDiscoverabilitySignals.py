__artifacts_v2__ = {
    "get_biomeDiscoverabilitySignals": {
        "name": "Biome - Discoverability Signals",
        "description": "Parses feature signals from the Discoverability.Signals biome stream. "
                       "Each record names a system condition that was reported, such as a Face "
                       "ID face covering being detected, a Wallet transaction occurring or a "
                       "photo being moved to the trash, together with the value or JSON payload "
                       "that accompanied it.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "Biome",
        "notes": "A high volume stream: the sample held tens of thousands of records across "
                 "thirty distinct signals, dominated by Face ID face covering detections. Some "
                 "records carry the signal name as a submessage rather than a string; those "
                 "are reported with an empty signal name and their raw content in the payload "
                 "column rather than being dropped.",
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


def _raw_repr(value):
    """Keep non-string content visible without pretending it is a name."""
    if value is None or (isinstance(value, dict) and not value):
        return ''
    return _to_str(value) if not isinstance(value, (dict, list)) else str(value)


@artifact_processor
def get_biomeDiscoverabilitySignals(context):

    data_list = []
    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
        else:
            continue

        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Discoverability Signals: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                signal = protostuff.get('1')
                context_msg = protostuff.get('3', {})
                if not isinstance(context_msg, dict):
                    context_msg = {}

                data_list.append((ts, record.state.name, _to_str(signal),
                                  _to_str(protostuff.get('2')),
                                  _to_str(protostuff.get('4')),
                                  _raw_repr(signal) if not isinstance(signal, bytes) else '',
                                  context_msg.get('13', ''), filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None,
                                  filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Signal', 'Value',
                    'Payload', 'Signal (raw)', 'Context ID (raw)', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
