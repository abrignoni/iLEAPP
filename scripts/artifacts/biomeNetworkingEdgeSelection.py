__artifacts_v2__ = {
    "get_biomeNetworkingEdgeSelection": {
        "name": "Biome - Networking Edge Selection",
        "description": "Parses the public-facing network prefix (a truncated IP address), interface "
                       "type, radio technology, country and device time zone recorded by the "
                       "Device.Networking.EdgeSelection biome stream",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-28",
        "last_update_date": "2026-07-28",
        "requirements": "none",
        "category": "Biome",
        "notes": "Each record is a network-edge observation: the address is the public endpoint the "
                 "device saw for itself, so it places the device on a carrier or Wi-Fi network at "
                 "that moment. IMPORTANT: the address is TRUNCATED to the accompanying prefix "
                 "length, not the device's full public IP - every observed value has its host bits "
                 "zeroed (an IPv4 seen as 69.143.130.0 is the /24 network, an IPv6 as "
                 "2600:380:1871:6d00:: is the /56). Report it as a network, not as an endpoint "
                 "address. The stream is protobuf, which carries field numbers but no field names, "
                 "so the column names other than the timestamp are inferred from the observed "
                 "values; field 6 has no established meaning and is reported as Field 6. Tombstone "
                 "files hold deletion bookkeeping under a different schema and are skipped.",
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
from datetime import timezone

from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor


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
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.') or not os.path.isfile(file_found):
            continue
        if 'tombstone' in file_found:  # deletion bookkeeping, not edge observations
            continue

        for record in read_segb_file(file_found):
            if record.state != EntryState.Written:
                continue

            protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)

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

            data_list.append((timestamp, ip_address, ip_version, prefix_length, interface,
                              radio_technology, field_6, country, time_zone, filename))

    data_headers = (('SEGB Timestamp', 'datetime'), 'IP Address (Truncated)', 'IP Version',
                    'Prefix Length', 'Interface', 'Radio Technology', 'Field 6', 'Country',
                    'Time Zone', 'Filename')

    return data_headers, data_list, 'see Filename for more info'
