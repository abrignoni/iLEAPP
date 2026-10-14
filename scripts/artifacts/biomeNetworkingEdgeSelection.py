__artifacts_v2__ = {
    "get_biomeNetworkingEdgeSelection": {
        "name": "Biome - Networking Edge Selection",
        "description": 'Reports decoded Written records and structural Deleted records yielded by the '
                       'Device.Networking.EdgeSelection SEGB reader. Deleted rows do not establish a network event'
                       ' or user deletion.',
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-10-07",
        "requirements": "none",
        "category": "Biome",
        "notes": 'Reports successfully yielded Written and Deleted SEGB records. Written payload columns '
                 'retain the existing decoder and interpretations. Deleted rows contain only the SEGB '
                 'timestamp, structural SEGB State, Filename and Offset; all eight payload columns are '
                 'empty. Deleted is a structural reader state, not proof of a user deletion or a network '
                 'event. Offset is the shared reader data_start_offset within the source file. Unknown and '
                 'reader-excluded states are not recovered. Files under a tombstone folder and dot files '
                 'remain excluded. A Source File column appears only when contributing file paths have the '
                 'same basename and existing report source information cannot associate that basename and '
                 'offset with one source path. Historical Written-only sample counts below are not a recount'
                 ' of the expanded output. Original implementation/research attribution: @AlexisBrignoni, '
                 'Claude. Each written record is read here as a network-edge observation: the values are '
                 'consistent with a device-side public network prefix; this interpretation is inferred from '
                 'observed values and is unverified. IMPORTANT: the address is TRUNCATED to the accompanying'
                 " prefix length, not the device's full public IP - every observed value has its host bits "
                 'zeroed (an IPv4 seen as 69.143.130.0 is the /24 network, an IPv6 as 2600:380:1871:6d00:: '
                 'is the /56). Report it as a network, not as an endpoint address. The stream is protobuf, '
                 'which carries field numbers but no field names, so the eight Written payload column names '
                 'are inferred from the observed values; field 6 has no established meaning and is reported '
                 'as Field 6. Files under a tombstone folder are skipped.',
        "paths": ('*/streams/*/Device.Networking.EdgeSelection/local/*',),
        "output_types": "standard",
        "artifact_icon": "network",
        "sample_data": {
            "otto_ios17": "iOS 17.5.1 | 8 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows (stream present, all slots deleted)",
            "felix23_ios16": "iOS 16.5 | 0 rows (stream directory present but empty)",
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


def _text(value):
    """Return a protobuf field as text; non-scalar fields decode to dicts, so skip those."""
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    if isinstance(value, dict):  # empty/nested message = field not populated with a scalar
        return ''
    if value is None:
        return ''
    return str(value)


@artifact_processor
def get_biomeNetworkingEdgeSelection(context):
    # Field 6 is absent on some records and empty on others, so it is typed as bytes here and
    # normalized by _text(); the remaining fields are stable across the observed records.
    typess = {
        '1': {'type': 'bytes', 'name': ''},
        '2': {'type': 'int', 'name': ''},
        '3': {'type': 'int', 'name': ''},
        '4': {'type': 'bytes', 'name': ''},
        '5': {'type': 'bytes', 'name': ''},
        '7': {'type': 'bytes', 'name': ''},
        '8': {'type': 'bytes', 'name': ''},
    }

    data_list = []
    source_dirs = set()
    row_sources = []
    paths_by_basename = {}
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.') or not os.path.isfile(file_found):
            continue
        if 'tombstone' in context.get_relative_path(file_found):  # deletion bookkeeping, not edge observations
            continue

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            if record.state == EntryState.Deleted:
                timestamp = record.timestamp1.replace(tzinfo=timezone.utc)
                data_list.append((timestamp, record.state.name, None, None, None, None,
                                  None, None, None, None, filename, record.data_start_offset))
                row_sources.append(file_found)
                paths_by_basename.setdefault(filename, set()).add(file_found)
                continue
            if record.state != EntryState.Written:
                continue

            try:
                protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)
            except _DECODE_ERRORS as ex:
                logfunc(f'Biome Networking Edge Selection: could not decode record at offset '
                        f'{record.data_start_offset} in {filename}: {ex}')
                continue

            # The address is stored already truncated to the prefix length in field 3 (host bits
            # zeroed), so it identifies the network the device was on, not the device's endpoint.
            ip_address = _text(protostuff.get('1'))
            ip_version = _text(protostuff.get('2'))
            prefix_length = _text(protostuff.get('3'))
            interface = _text(protostuff.get('4'))
            radio_technology = _text(protostuff.get('5'))
            field_6 = _text(protostuff.get('6'))  # meaning unknown; reported verbatim
            country = _text(protostuff.get('7'))
            time_zone = _text(protostuff.get('8'))

            timestamp = record.timestamp1.replace(tzinfo=timezone.utc)

            data_list.append((timestamp, record.state.name, ip_address, ip_version, prefix_length,
                              interface, radio_technology, field_6, country, time_zone,
                              filename, record.data_start_offset))
            row_sources.append(file_found)
            paths_by_basename.setdefault(filename, set()).add(file_found)

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'IP Address (Truncated)', 'IP Version',
                    'Prefix Length', 'Interface', 'Radio Technology', 'Field 6', 'Country',
                    'Time Zone', 'Filename', 'Offset')

    if any(len(paths) > 1 for paths in paths_by_basename.values()):
        data_headers += ('Source File',)
        data_list = [row + (context.get_relative_path(path),)
                     for row, path in zip(data_list, row_sources)]

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
