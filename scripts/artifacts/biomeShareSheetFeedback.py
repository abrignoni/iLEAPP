__artifacts_v2__ = {
    "get_biomeShareSheetFeedback": {
        "name": "Biome - Share Sheet Feedback",
        "description": "Parses share sheet records from the ShareSheet.Feedback biome stream: the "
                       "source bundle id, the target and transport bundle ids (on the tested images 28 "
                       "of 59 written records held a UIKit activity identifier there, such as copy to "
                       "pasteboard or save to camera roll), the supported bundle ids, the engagement "
                       "type, the selected index and the number of visible suggestions value.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names and Engagement Type names are those of the BMShareSheetFeedback "
                 "class, read from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy "
                 "of the class was read. Source Bundle ID is field 15 (sourceBundleID), Target "
                 "Bundle ID field 2 (targetBundleID), Transport Bundle ID field 16 "
                 "(transportBundleID), Supported Bundle IDs field 11 (supportedBundleIDs), "
                 "Location UUIDs field 5 (locationUUIDs), Extension Context UUID field 3 "
                 "(extensionContextUUID), Reason Type and Reason fields 13 and 14, Visible "
                 "Suggestions field 17 (numberOfVisibleSuggestions, a double; it held a fractional "
                 "value on all 58 records where set), Engagement Type "
                 "field 20 (0 Unknown, 1 EngagementWithSuggestion, 2 "
                 "EngagementWithNonSuggestion, 3 Abandonment, 4 SPICall; on 17 of the 59 written "
                 "records on the tested images, all on four images, field 20 held a large integer outside that list, so "
                 "Engagement Type is blank there and the value is in Engagement Type (raw)) and "
                 "Index Selected field "
                 "21, a signed 32-bit integer; it was -1 on 51 of 59 written records, and the "
                 "meaning of -1 is not established. Extension Context UUID held a 12-character "
                 "hexadecimal string on every tested written record. Before, fields 16, 2, 11, 5 and 3 were "
                 "labelled Chosen Activity, Activity Type, Offered Candidates, Event UUID and "
                 "Session ID, and fields 17 and 20 were raw. Whether a listed bundle ID shows that "
                 "the app was installed is not established. On the tested images Target Bundle ID and "
                 "Transport Bundle ID held the same text on 58 of 59 written records, Reason Type and "
                 "Reason were set on 7 and Location UUIDs on 15. Field 4 (attachments) holds an "
                 "NSKeyedArchiver plist that is not parsed."),
        "paths": ('*/streams/*/ShareSheet.Feedback/local/*',),
        "output_types": "standard",
        "artifact_icon": "share-2",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | 17 rows",
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

TYPESS = {
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'str', 'name': ''},
    '4': {'type': 'bytes', 'name': ''},
    '5': {'type': 'str', 'name': ''},
    '11': {'type': 'str', 'name': ''},
    '13': {'type': 'str', 'name': ''},
    '14': {'type': 'str', 'name': ''},
    '15': {'type': 'str', 'name': ''},
    '16': {'type': 'str', 'name': ''},
    '17': {'type': 'double', 'name': ''},
    '20': {'type': 'int', 'name': ''},
    '21': {'type': 'int', 'name': ''},
}

# engagementType names, read from BiomeLibrary.framework BMShareSheetFeedback on
# macOS 27.2.1 (26B131).
ENGAGEMENT_TYPES = {0: 'Unknown', 1: 'EngagementWithSuggestion', 2: 'EngagementWithNonSuggestion',
                    3: 'Abandonment', 4: 'SPICall'}


def _int32(value):
    """An int32 field; a negative value arrives as a 64-bit varint."""
    if not isinstance(value, int):
        return ''
    return value - (1 << 64) if value >= 1 << 63 else value


def _list(value):
    """A repeated string field: several values join with a comma."""
    if isinstance(value, list):
        return ', '.join(_to_str(v) for v in value)
    return _to_str(value)


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
def get_biomeShareSheetFeedback(context):

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
                    logfunc(f'Share Sheet Feedback: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                candidates = _to_str(protostuff.get('11', b'')).replace(',', ', ')
                engagement = protostuff.get('20')
                visible = protostuff.get('17')

                data_list.append((ts, record.state.name,
                                  _to_str(protostuff.get('15', b'')),
                                  _to_str(protostuff.get('2', b'')),
                                  _to_str(protostuff.get('16', b'')),
                                  candidates,
                                  ENGAGEMENT_TYPES.get(engagement, '')
                                  if isinstance(engagement, int) else '',
                                  '' if engagement is None else engagement,
                                  _int32(protostuff.get('21')),
                                  visible if isinstance(visible, float) else '',
                                  _to_str(protostuff.get('13', b'')),
                                  _to_str(protostuff.get('14', b'')),
                                  _list(protostuff.get('5', b'')),
                                  _to_str(protostuff.get('3', b'')),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name) + (None,) * 12 +
                                 (filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Source Bundle ID',
                    'Target Bundle ID', 'Transport Bundle ID', 'Supported Bundle IDs',
                    'Engagement Type', 'Engagement Type (raw)', 'Index Selected',
                    'Visible Suggestions', 'Reason Type', 'Reason', 'Location UUIDs',
                    'Extension Context UUID', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
