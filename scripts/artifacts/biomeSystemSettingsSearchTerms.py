__artifacts_v2__ = {
    "get_biomeSystemSettingsSearchTerms": {
        "name": "Biome - System Settings Search Terms",
        "description": "Parses searches typed in the Settings app from the "
                       "SystemSettings.SearchTerms biome stream, including result URIs and "
                       "labels recorded with the search.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
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


@artifact_processor
def get_biomeSystemSettingsSearchTerms(context):

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
            ts = record.timestamp1
            ts = ts.replace(tzinfo=timezone.utc)

            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data)
                except _DECODE_ERRORS as ex:
                    logfunc(f'System Settings Search Terms: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                search_term = _to_str(protostuff.get('1', b''))

                results = protostuff.get('2', [])
                if isinstance(results, dict):
                    results = [results]
                result_uris = []
                result_labels = []
                for result in results:
                    if not isinstance(result, dict):
                        continue
                    uri = _to_str(result.get('1', b''))
                    label = _to_str(result.get('2', b''))
                    if uri:
                        result_uris.append(uri)
                    if label:
                        result_labels.append(label)

                data_list.append((ts, record.state.name, search_term, '; '.join(result_uris),
                                  '; '.join(result_labels), filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, filename,
                                  record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Search Term',
                    'Result URI(s)', 'Result Label(s)', 'Filename', 'Offset')

    return data_headers, data_list, 'see Filename for more info'
