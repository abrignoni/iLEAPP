__artifacts_v2__ = {
    "get_biomeFrontBoardDisplayElement": {
        "name": "Biome - FrontBoard Display Element",
        "description": "Parses display element records from the FrontBoard.DisplayElement "
                       "biome stream: which element (bundle id and identifier) was recorded "
                       "against which display, "
                       "with the time stored in the record read as Unix epoch seconds. This "
                       "is a high volume stream that may assist in reconstructing "
                       "app display activity; whether a record corresponds to on-screen "
                       "presentation is not established.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Records with an empty Bundle ID are reported with their Scene ID as stored; "
                 "what those scenes are is not established. Field names and the Element Type, "
                 "Change Type and Display Backlight Status names are those of the "
                 "BMFrontBoardDisplayElement class and its BMFrontBoardDisplayElementDisplay "
                 "class, read from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy "
                 "of the class was read. Scene ID is the field the framework names identifier. "
                 "Columns reported before as Display Type, Display Role "
                 "and Field 4, 5, 6, 7, 8 and 10 (raw) are now Display Name, Display Device Name, "
                 "Element Type, Layout Role, Level, Has Keyboard Focus, Is UI Application "
                 "Element and Change Type. Display Backlight Status is new. The integers for "
                 "the named fields stay in the (raw) columns; Layout Role and Level have no "
                 "names in the framework and are reported as stored. Has Keyboard Focus and Is "
                 "UI Application Element show True for 1 and False for 0. On the tested images "
                 "Element Type was SpringBoard (2) on all 42,978 written rows that carried it, "
                 "and 129 written rows carried none of these fields. 136 written records on "
                 "the tested images did not decode and are not reported. Transition Reasons is field 9.7 (transitionReasons) of the BMFrontBoardDisplayElementDisplay class in BiomeLibrary.framework, macOS 27.2.1 (26B131); no iOS copy was read. It was not reported before. The field repeats; its values are joined with a semicolon and a space, in stored order and shown as stored; their meaning is not decoded here. On the 21 iOS images tested (16 held written records of this stream) it was set on 39,060 of 43,107 written rows, with 80,689 values. By shape: 33,821 values start with com.apple.SpringBoard or com.apple.springboard, 30,115 start with a name prefixed SB, CS, BLS or _SB and hold no UUID, 16,368 hold a UUID, 371 start with SBSourceApplication and 14 are other. Each of those rows held at least one value without a UUID.",
        "paths": ('*/streams/*/FrontBoard.DisplayElement/local/*',),
        "output_types": "standard",
        "artifact_icon": "layers",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 7762 rows",
            "iphone11_ios17": "iOS 17.3 | 5234 rows",
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

# elementType names, read from BiomeLibrary.framework BMFrontBoardDisplayElement on macOS 27.2.1 (26B131).
ELEMENT_TYPE = {0: 'Unknown', 1: 'FrontBoard', 2: 'SpringBoard', 3: 'PineBoard', 4: 'Carousel'}
# changeType names, read from BiomeLibrary.framework BMFrontBoardDisplayElement on macOS 27.2.1 (26B131).
CHANGE_TYPE = {0: 'Unknown', 1: 'Added', 2: 'Modified', 3: 'Removed'}
# backlightStatus names, read from BiomeLibrary.framework BMFrontBoardDisplayElementDisplay on macOS 27.2.1 (26B131).
BACKLIGHT_STATUS = {0: 'Unknown', 1: 'Off', 2: 'On'}

TYPESS = {
    '2': {'type': 'str', 'name': ''},
    '3': {'type': 'str', 'name': ''},
    '4': {'type': 'int', 'name': ''},
    '5': {'type': 'int', 'name': ''},
    '6': {'type': 'int', 'name': ''},
    '7': {'type': 'int', 'name': ''},
    '8': {'type': 'int', 'name': ''},
    # only transitionReasons (9.7) is pinned; the other display fields keep their decoding
    '9': {'type': 'message', 'name': '', 'message_typedef': {'7': {'type': 'bytes', 'name': ''}}},
    '10': {'type': 'int', 'name': ''},
}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None:
        return ''
    return str(value)


def _bool(value):
    if value == 1:
        return 'True'
    if value == 0:
        return 'False'
    return ''


def _name(names, value):
    return names.get(value, '') if isinstance(value, int) else ''


def _transition_reasons(value):
    """transitionReasons (9.7) is repeated: one bytes value or a list, shown as stored."""
    values = value if isinstance(value, list) else [value]
    return '; '.join(item.decode('utf-8', errors='replace') for item in values if isinstance(item, bytes))


def _unix_double(value):
    if not isinstance(value, int) or value == 0:
        return None
    seconds = struct.unpack('<d', struct.pack('<q', value))[0] if value > 10 ** 15 else value
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


@artifact_processor
def get_biomeFrontBoardDisplayElement(context):

    data_headers = (('SEGB Timestamp', 'datetime'), ('Event Timestamp', 'datetime'),
                    'SEGB State', 'Bundle ID', 'Scene ID', 'Display Name', 'Display Device Name',
                    'Display Backlight Status', 'Display Backlight Status (raw)',
                    'Transition Reasons',
                    'Element Type', 'Element Type (raw)', 'Layout Role', 'Level',
                    'Has Keyboard Focus', 'Is UI Application Element', 'Change Type',
                    'Change Type (raw)', 'Filename', 'Offset')

    source_dirs = set()
    results = context.create_artifact_result(headers=data_headers)

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
                    logfunc(f'FrontBoard Display Element: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                display = protostuff.get('9', {})
                if not isinstance(display, dict):
                    display = {}

                results.add_row((ts, _unix_double(protostuff.get('1')), record.state.name,
                                  _to_str(protostuff.get('3', b'')),
                                  _to_str(protostuff.get('2', b'')),
                                  _to_str(display.get('2', b'')),
                                  _to_str(display.get('3', b'')),
                                  _name(BACKLIGHT_STATUS, display.get('6')),
                                  display.get('6', ''),
                                  _transition_reasons(display.get('7')),
                                  _name(ELEMENT_TYPE, protostuff.get('4')),
                                  protostuff.get('4', ''), protostuff.get('5', ''),
                                  protostuff.get('6', ''), _bool(protostuff.get('7')),
                                  _bool(protostuff.get('8')),
                                  _name(CHANGE_TYPE, protostuff.get('10')),
                                  protostuff.get('10', ''),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                results.add_row((ts, None, record.state.name, None, None, None, None, None, None,
                                  None, None, None, None, None, None, None, None, None, filename,
                                  record.data_start_offset))

    results.set_source_path('\n'.join(sorted(source_dirs)))
    return results
