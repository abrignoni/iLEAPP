__artifacts_v2__ = {
    "get_biomeScreenshots": {
        "name": "Biome - Screenshots",
        "description": "Screenshot events from the Biome Screenshots.Screenshot stream.",
        "author": "@charpy, @AlexisBrignoni, Codex",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Biome",
        "notes": ("The record layout is not known: on the one image tested (iOS 27.2, 24B119) all 6 records "
                  "were deleted and their data zeroed, so only the SEGB timestamp and state survive. That a "
                  "record marks a screenshot is inferred from the stream name. On this image each SEGB time "
                  "was within 4 to 11 seconds of a Photos.sqlite asset flagged ZISDETECTEDSCREENSHOT. The six "
                  "nearest matches involved four assets, so an individual image cannot be identified from this "
                  "comparison. Written records, if any, are decoded without a type definition and shown as JSON in "
                  "Record Data. Binary values and undecodable payloads are preserved as labeled hex. On the tested image SEGB State held Deleted "
                  "on all 6 rows, Record Data was empty on all 6 rows because no record was written, and "
                  "Source File held one value on all 6 rows because the stream held one SEGB file."),
        "paths": ('*/Biome/streams/restricted/Screenshots.Screenshot/local/*',),
        "output_types": "standard",
        "artifact_icon": "camera",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | 6 rows",
        }
    }
}

import json
import struct
from datetime import timezone

from google.protobuf.message import DecodeError
from scripts import blackboxprotobuf
from scripts.biome_stream_records import local_records
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc


def _json_bytes(value):
    try:
        return value.decode('utf-8')
    except UnicodeDecodeError:
        return {'hex': value.hex()}


@artifact_processor
def get_biomeScreenshots(context):
    data_list = []
    sources = set()
    for source, record in local_records(context, 'Screenshots.Screenshot'):
        sources.add(str(source))
        data = None
        if record.state == EntryState.Written:
            try:
                proto, _ = blackboxprotobuf.decode_message(record.data)
                data = json.dumps(proto, default=_json_bytes, ensure_ascii=False)
            except (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError) as error:
                logfunc(f'Biome Screenshots: could not decode offset {record.data_start_offset} in {source}: {error}')
                data = json.dumps({'raw_hex': record.data.hex()})
        data_list.append((record.timestamp1.replace(tzinfo=timezone.utc), record.state.name, data,
                          str(source), record.data_start_offset))
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Record Data', 'Source File', 'Offset')
    return data_headers, data_list, '\n'.join(sorted(sources))
