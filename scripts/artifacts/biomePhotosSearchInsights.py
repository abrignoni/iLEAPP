__artifacts_v2__ = {
    "get_biomePhotosSearchInsights": {
        "name": "Biome - Photos Search Insights",
        "description": "Parses Photos search terms from the "
                       "AeroML.Insights.PhotosSearchInsights biome stream, along with two "
                       "strings read as a language and a region. The search term is the "
                       "class's queryRaw field. The UI Surface names include Spotlight as well as "
                       "the Photos app.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names (Search Term aside) and UI Surface and Library Size Bucket value "
                 "names are those of the "
                 "BMAeroMLPhotosSearchInsights class, read from BiomeLibrary.framework on macOS "
                 "27.2.1 (26B131); no iOS copy of the class was read. The class reads only data "
                 "version 0 (the unnamed integer the SEGB reader returns with each entry); a record of another "
                 "version, or a value outside the class's lists, keeps its integer in the (raw) "
                 "column with the name blank. Version was reported before as Schema Version, Was "
                 "There Any Results Shown as Field 1 (raw), UI Surface as Field 5 (raw), Library "
                 "Processing Progress as Field 25 (raw) and Library Size Bucket as Field 26 (raw). "
                 "Search Term is the class's queryRaw field. Was There Any Results Shown reads True "
                 "for 1, False for 0 and is blank otherwise. Fields 1, 5, 25 and 26 were constant "
                 "across the private sample the fields were mapped from. No record of this stream was on the tested images, so these "
                 "columns were not exercised on them.",
        "paths": ('*/streams/*/AeroML.Insights.PhotosSearchInsights/local/*',),
        "output_types": "standard",
        "artifact_icon": "search",
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

# uiSurface and librarySizeBucket names, read from BiomeLibrary.framework
# BMAeroMLPhotosSearchInsights on macOS 27.2.1 (26B131). The class reads only data
# version 0 (the unnamed int the SEGB reader returns per entry); other versions get no name, and so
# do values the class renders only as its fallback.
UI_SURFACE_BY_VERSION = {
    0: dict(enumerate(('Unknown', 'Spotlight', 'PhotosAppGlobalSearch',
                       'PhotosAppScopedSearch', 'StoryTellingBackground'))),
}
LIBRARY_SIZE_BUCKET_BY_VERSION = {
    0: dict(enumerate(('Unknown', '500OrLess', '500To2K', '2KTo5K', '5KTo10K', '10KTo20K',
                       '20KTo30K', '30KTo40K', '40KTo50K', '50KTo100K', 'MoreThan100K'))),
}

TYPESS = {
    '1': {'type': 'int', 'name': ''},
    '3': {'type': 'int', 'name': ''},
    '4': {'type': 'int', 'name': ''},
    '5': {'type': 'int', 'name': ''},
    '9': {'type': 'str', 'name': ''},
    '22': {'type': 'str', 'name': ''},
    '23': {'type': 'str', 'name': ''},
    '24': {'type': 'str', 'name': ''},
    '25': {'type': 'int', 'name': ''},
    '26': {'type': 'int', 'name': ''},
}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _bool_text(value):
    if value == 1 and not isinstance(value, bool):
        return 'True'
    if value == 0 and not isinstance(value, bool):
        return 'False'
    return ''


@artifact_processor
def get_biomePhotosSearchInsights(context):

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
                    logfunc(f'Photos Search Insights: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                version = getattr(record, '_unknown_value', None)
                ui_surface = protostuff.get('5', '')
                size_bucket = protostuff.get('26', '')
                data_list.append((ts, record.state.name,
                                  _to_str(protostuff.get('9', b'')),
                                  _to_str(protostuff.get('22', b'')),
                                  _to_str(protostuff.get('23', b'')),
                                  _to_str(protostuff.get('24', b'')),
                                  _bool_text(protostuff.get('1')),
                                  UI_SURFACE_BY_VERSION.get(version, {}).get(ui_surface, ''),
                                  ui_surface, protostuff.get('25', ''),
                                  LIBRARY_SIZE_BUCKET_BY_VERSION.get(version, {}).get(
                                      size_bucket, ''),
                                  size_bucket, filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None, None,
                                  None, None, None, None, filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Search Term', 'Language',
                    'Region', 'Version', 'Was There Any Results Shown', 'UI Surface',
                    'UI Surface (raw)', 'Library Processing Progress', 'Library Size Bucket',
                    'Library Size Bucket (raw)', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
