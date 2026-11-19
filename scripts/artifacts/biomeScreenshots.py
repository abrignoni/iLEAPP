__artifacts_v2__ = {
    "get_biomeScreenshots": {
        "name": "Biome - Screenshots",
        "description": "Screenshot events from the Biome Screenshots.Screenshot stream.",
        "author": "@charpy",
        "creation_date": "2026-11-19",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Biome",
        "notes": ("The record layout is not known: on the one image tested (iOS 27.2, 24B119) all 6 records "
                  "were deleted and their data zeroed, so only the SEGB timestamp and state survive. That a "
                  "record marks a screenshot is taken from the stream name, not verified against the image "
                  "files. Written records, if any, are decoded without a type definition and shown as JSON in "
                  "Record Data so their fields can be identified. On the tested image SEGB State held Deleted "
                  "on all 6 rows, Record Data was empty on all 6 rows because no record was written, and "
                  "Filename held one value on all 6 rows because the stream held one SEGB file."),
        "paths": ('*/Biome/streams/restricted/Screenshots.Screenshot/local/*',),
        "output_types": "standard",
        "artifact_icon": "camera",
        "sample_data": {
            "gk_ios27_2": "iOS 27.2 | 6 rows",
        }
    }
}

import json
import os
import struct
from datetime import timezone
from google.protobuf.message import DecodeError
from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)


def _jsonable(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return str(value)


@artifact_processor
def get_biomeScreenshots(context):
    data_list = []
    source_dirs = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if (filename.startswith('.') or not os.path.isfile(file_found)
                or 'tombstone' in context.get_relative_path(file_found)):
            continue
        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)
            offset = record.data_start_offset
            if record.state == EntryState.Written:
                try:
                    proto, _ = blackboxprotobuf.decode_message(record.data)
                    data = json.dumps(proto, default=_jsonable, ensure_ascii=False)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome Screenshots: could not decode record at offset {offset} in '
                            f'{filename}: {ex}')
                    data = ''
                data_list.append((ts, record.state.name, data, filename, offset))
            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, filename, offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Record Data', 'Filename', 'Offset')
    return data_headers, data_list, '\n'.join(sorted(source_dirs))
