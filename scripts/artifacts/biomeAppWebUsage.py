__artifacts_v2__ = {
    "get_biomeAppWebUsage": {
        "name": "Biome - App Web Usage",
        "description": "Parses App Web Usage entries from Biome",
        "author": "r.schramp@nfi.nl",
        "version": "0.0.1",
        "date": "2026-05-29",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/App.WebUsage/local/*'),
        "output_types": "standard",
        "artifact_icon": "world"
    }
}


import os
from datetime import timezone
import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, webkit_timestampsconv


@artifact_processor
def get_biomeAppWebUsage(context):

    # Tested with:
    # MagnetCTF2026/00008110-0008196A2299401E_files_full.zip
    # 7b9530778c88472cc0a0361da361d953355cdc38428d3e1cebc48d2f4ce2291b  private/var/mobile/Library/Biome/streams/restricted/App.WebUsage/local/785879718693707
    #
    # Field mapping (based on observed protobuf decode):
    #   1  -> GUID / UUID string
    #   2  -> Timestamp (webkit/double, e.g. 7.858817e8)
    #   3  -> VARINT - function TBD (placeholder: pb_int_3)
    #   4  -> Full URL string
    #   5  -> Domain / host string
    #   6  -> Bundle ID string (e.g. com.apple.mobilesafari)
    #   8  -> VARINT - function TBD (placeholder: pb_int_8)

    typess = {
        '1': {'type': 'str',    'name': 'guid'},
        '2': {'type': 'double', 'name': 'timestamp'},
        '3': {'type': 'int',    'name': 'pb_int_3'}, # Values 1 and 3
        '4': {'type': 'str',    'name': 'url'},
        '5': {'type': 'str',    'name': 'domain'},
        '6': {'type': 'str',    'name': 'bundle_id'},
        '8': {'type': 'int',    'name': 'pb_int_8'},
    }

    data_list = []
    report_file = 'Unknown'

    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)

        if filename.startswith('.'):
            continue
        if os.path.isfile(file_found):
            if 'tombstone' in file_found:
                continue
            else:
                report_file = os.path.dirname(file_found)
        else:
            continue

        for record in read_segb_file(file_found):
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                protostuff, _types = blackboxprotobuf.decode_message(record.data, typess)

                guid               = protostuff.get('bundle_id', '')
                timestamp          = webkit_timestampsconv(protostuff['timestamp'])
                pb_int_3           = protostuff.get('pb_int_3', None)
                url                = protostuff.get('url', '')
                domain             = protostuff.get('domain', '')
                bundle_id          = protostuff.get('bundle_id', '')
                pb_int_8           = protostuff.get('pb_int_8', None)

                data_list.append((
                    ts,
                    timestamp,
                    record.state.name,
                    url,
                    domain,
                    bundle_id,
                    guid,
                    pb_int_3,
                    pb_int_8,
                    filename,
                    record.data_start_offset
                ))

            elif record.state == EntryState.Deleted:
                data_list.append((
                    ts,
                    None,               # timestart
                    record.state.name,
                    None,               # url
                    None,               # domain
                    None,               # bundle_id
                    None,               # guid
                    None,               # is_private_browsing
                    None,               # is_secure
                    filename,
                    record.data_start_offset
                ))

    data_headers = (
        ('SEGB Timestamp', 'datetime'),
        ('Timestamp',      'datetime'),
        'SEGB State',
        'URL',
        'Domain',
        'Bundle ID',
        'GUID',
        'pb_int_3',
        'pb_int_8',
        'Filename',
        'Offset'
    )

    return data_headers, data_list, report_file