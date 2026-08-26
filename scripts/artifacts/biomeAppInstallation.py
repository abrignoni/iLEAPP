__artifacts_v2__ = {
    "get_biomeAppInstallation": {
        "name": "Biome - App Installation",
        "description": "Parses app installation events from the App.Installation biome stream: "
                       "the bundle identifier, a per-app UUID, its short and build "
                       "version, and the time the event was recorded. Complements the older "
                       "App.Install and _DKEvent.App.Install streams.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "The event type field takes values 0, 1, 2 and 3 in the tested sample; which of "
                 "install, update and removal each denotes is not confirmed, so the raw value is "
                 "reported. Two 16 byte values accompany each event and are surfaced as hex "
                 "digests; their role is not established. The version and 16 byte fields are read "
                 "with a pinned field type because some of those values are themselves valid "
                 "protobuf and an inferring decode reports them as empty.",
        "paths": ('*/streams/*/App.Installation/local/*',),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "hc_ios26": "iOS 26.5.2 | 232 rows",
        },
    }
}


import os
import struct
from datetime import datetime, timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

# The version strings and the two 16 byte values are sometimes themselves valid protobuf,
# and an inferring decode reads those as nested messages, which blanks the column. Only
# these four fields are pinned; everything else is still inferred, so the fixed64 fields
# keep arriving as integers for _unix_double().
_TYPEDEF = {
    '3': {'type': 'message', 'name': '', 'message_typedef': {
        '2': {'type': 'str', 'name': ''},
        '3': {'type': 'str', 'name': ''},
        '4': {'type': 'bytes', 'name': ''},
        '5': {'type': 'bytes', 'name': ''}}},
}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.hex()
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _hexed(value):
    return value.hex() if isinstance(value, bytes) else ''


def _unix_double(value):
    if not isinstance(value, int) or value == 0:
        return None
    seconds = struct.unpack('<d', struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF))[0]
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


@artifact_processor
def get_biomeAppInstallation(context):

    data_list = []
    source_dirs = set()
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

        source_dirs.add(os.path.dirname(file_found))
        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, _TYPEDEF)
                except _DECODE_ERRORS as ex:
                    logfunc(f'App Installation: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                app = protostuff.get('1', {})
                if not isinstance(app, dict):
                    app = {}
                detail = protostuff.get('3', {})
                if not isinstance(detail, dict):
                    detail = {}

                data_list.append((ts, _unix_double(protostuff.get('4')),
                                  _unix_double(detail.get('1')), record.state.name,
                                  _to_str(app.get('1')), _to_str(app.get('2')),
                                  _to_str(detail.get('3')), _to_str(detail.get('2')),
                                  protostuff.get('2', ''), _hexed(detail.get('4')),
                                  _hexed(detail.get('5')), filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, record.state.name, None, None, None, None,
                                  None, None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), ('Event Timestamp', 'datetime'),
                    ('App Timestamp', 'datetime'), 'SEGB State', 'Bundle ID', 'App UUID',
                    'Version', 'Build Version', 'Event Type (raw)', 'Digest 1', 'Digest 2',
                    'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
