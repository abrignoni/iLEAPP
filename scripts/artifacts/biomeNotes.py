__artifacts_v2__ = {
    "get_biomeNotes": {
        "name": "Biome - Notes",
        "description": "Parses notes entries from biomes",
        "author": "@JohnHyla",
        "creation_date": "2024-10-17",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Unique ID is field 1 (uniqueID), Domain ID field 2 (domainID), Timestamp field "
                 "3 (absoluteTimestamp, which the framework decodes as seconds since 2001-01-01 "
                 "UTC) and Note field 5 (content) of the BMProactiveHarvestingNotes class, read "
                 "from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class "
                 "was read. Unique ID and Domain ID were reported before as Identifier 1 and "
                 "Identifier 2. The stream is read from ProactiveHarvesting.Notes and from "
                 "NotesContent, the legacy name the framework lists for it; the first was not read "
                 "before. Across the 21 staged iOS images, 12 held local stream files with records: "
                 "10 written records on 2 images and 178 deleted records. Timestamp was 0 on 6 of "
                 "the 10 written records and is blank there, since 0 would read as 2001-01-01. On "
                 "the other 4 it fell 90 seconds to about 19 days before the SEGB Timestamp. Field "
                 "4 (title) was not present on the 10 written records.",
        "paths": ('*/Biome/streams/restricted/NotesContent/local/*',
                  '*/[Bb]iome/streams/restricted/ProactiveHarvesting.Notes/local/*'),
        "html_columns" : ['Note'],
        "output_types": "standard",
        "function": "get_biomeNotes",
        "artifact_icon": "notes",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 34 rows",
            "hc_ios18_7": "iOS 18.7.8 | 16 rows",
            "iphone12_ios18": "iOS 18.7 | 55 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    }
}


import os
import struct
from datetime import timezone
from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import webkit_timestampsconv, artifact_processor, logfunc
from scripts.html_safe import safe_source

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

# Field types of BMProactiveHarvestingNotes, read from BiomeLibrary.framework on macOS 27.2.1
# (26B131), so that a string whose bytes parse as protobuf stays a string.
TYPESS = {
    '1': {'type': 'bytes', 'name': ''},
    '2': {'type': 'bytes', 'name': ''},
    '3': {'type': 'double', 'name': ''},
    '5': {'type': 'bytes', 'name': ''},
}


def _text(value):
    return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else ''


@artifact_processor
def get_biomeNotes(context):

    data_headers = (('SEGB Timestamp', 'datetime'), ('Timestamp', 'datetime'), 'SEGB State', 'Record Num', 'Unique ID',
                    'Domain ID', 'Note', 'Filename', 'Offset')

    data_list = []
    data_list_html = []
    record_counter = 0
    source_dirs = set()
    for file_found in context.get_files_found():
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
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Biome Notes: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue
                record_counter += 1
                # 0 and the NSDate sentinels hold no date; kept as None, as in the Deleted rows
                stored_time = protostuff.get('3')
                time = (webkit_timestampsconv(stored_time) or None) if stored_time else None
                identifier1 = _text(protostuff.get('1'))
                identifier2 = _text(protostuff.get('2'))
                message = _text(protostuff.get('5'))
                messagehtml = safe_source(message)
                data_list.append((ts, time, record.state.name, record_counter, identifier1, identifier2, message, filename, record.data_start_offset))
                data_list_html.append((ts, time, record.state.name, record_counter, identifier1, identifier2, messagehtml, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, record.state.name, None, None, None, None, filename,
                                       record.data_start_offset))
                data_list_html.append((ts, None, record.state.name, None, None, None, None, filename,
                                            record.data_start_offset))

    return data_headers, (data_list, data_list_html), '\n'.join(sorted(source_dirs))
