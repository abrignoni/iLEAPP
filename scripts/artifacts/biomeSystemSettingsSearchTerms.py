__artifacts_v2__ = {
    "get_biomeSystemSettingsSearchTerms": {
        "name": "Biome - System Settings Search Terms",
        "description": "Parses search terms from the SystemSettings.SearchTerms biome stream, "
                       "including the bundle ID with anchor and the title of "
                       "the results recorded as clicked on.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field names are those of the BMSystemSettingsSearchTerms class and its "
                 "searchResultsClickedOn entries, read from BiomeLibrary.framework on macOS 27.2.1 "
                 "(26B131); no iOS copy of the class was read. Bundle ID With Anchor(s) was "
                 "reported before as Result URI(s). The fields are read with a fixed layout. On "
                 "the tested images (7 images with written records, 17 written rows) that "
                 "changed 2 rows of falken_ios26, whose Result Label(s) the schema-less decoder "
                 "had shown as a decoded submessage instead of the stored text. Deleted rows are not "
                 "decoded, so Search Term, Bundle ID With Anchor(s) and Result Label(s) are empty "
                 "on them. All 12 rows of wilkerson_iphone16_ios26 are deleted.",
        "paths": ('*/streams/*/SystemSettings.SearchTerms/local/*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 14 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
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
    if value is None:
        return ''
    return str(value)


# BMSystemSettingsSearchTerms fields, read from BiomeLibrary.framework on macOS 27.2.1 (26B131):
# 1 searchTerm; 2 searchResultsClickedOn (repeated: 1 bundleIDwithAnchor, 2 searchResultTitle,
# 3 index). Pinned so short strings are never guessed to be submessages.
TYPESS = {
    '1': {'type': 'bytes', 'name': ''},
    '2': {'type': 'message', 'name': '', 'message_typedef': {
        '1': {'type': 'bytes', 'name': ''},
        '2': {'type': 'bytes', 'name': ''},
        '3': {'type': 'int', 'name': ''},
    }},
}


@artifact_processor
def get_biomeSystemSettingsSearchTerms(context):

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
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'System Settings Search Terms: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                search_term = _to_str(protostuff.get('1', b''))

                results = protostuff.get('2', [])
                if isinstance(results, dict):
                    results = [results]
                result_anchors = []
                result_labels = []
                for result in results:
                    if not isinstance(result, dict):
                        continue
                    anchor = _to_str(result.get('1', b''))
                    label = _to_str(result.get('2', b''))
                    if anchor:
                        result_anchors.append(anchor)
                    if label:
                        result_labels.append(label)

                data_list.append((ts, record.state.name, search_term, '; '.join(result_anchors),
                                  '; '.join(result_labels), filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Search Term',
                    'Bundle ID With Anchor(s)', 'Result Label(s)', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
