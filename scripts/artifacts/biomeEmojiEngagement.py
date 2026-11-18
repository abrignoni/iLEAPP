__artifacts_v2__ = {
    "get_biomeEmojiEngagement": {
        "name": "Biome - Emoji Engagement",
        "description": "Parses emoji records from the Emoji.Engagement biome stream: the emoji as "
                       "stored with its Unicode code points (so skin tone modifiers, variation "
                       "selectors and zero width joiner sequences stay visible), the input mode, "
                       "the locale and, for searches, the final search query.",
        "author": "@abrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names and Input Mode names are those of the BMEmojiEngagement class, "
                 "read from BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the "
                 "class was read. Locale is field 3 (localeIdentifier), a string. Before, this "
                 "artifact decoded those bytes as a nested message; on the tested images the "
                 "Context (decoded) column showed the last four characters of the locale in reverse "
                 "order. Positive Engagement is field 2 "
                 "(wasPositiveEngagement), Input Mode field 4 (inputMode: 0 Unknown, 1 "
                 "EmojiKeyboardPalette, 2 EmojiKeyboardPaletteRecents, 3 EmojiSearch, 4 "
                 "CandidateBar, 5 Handwriting, 6 Dictation, 7 CharacterPickerLightweight, 8 "
                 "CharacterPickerPopover, 9 CharacterPickerExtended, 10 DigitalFirstRow), "
                 "Replacement Context field 5, Result Position field 6, Search Queries Run field 7 "
                 "and Final Search Query field 8. Result Position is a signed 32-bit integer; it was "
                 "-1 on 11 of the 17 search records, and the meaning of -1 is not established. On the tested images Result Position and Final Search Query were "
                 "set on the 17 written records with Input Mode EmojiSearch and on no others, "
                 "Replacement Context on 2 and Search Queries Run on none. On the tested images every "
                 "record in the deleted SEGB state had an all-zero payload; deleted records are listed "
                 "with timestamp, filename and offset only."),
        "paths": ('*/streams/*/Emoji.Engagement/local/*',),
        "output_types": "standard",
        "artifact_icon": "smile",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 4 rows",
            "iphone11_ios17": "iOS 17.3 | 20 rows",
            "iphone12_ios18": "iOS 18.7 | 16 rows",
            "iphone14plus_ios18": "iOS 18.0 | 4 rows",
            "otto_ios17": "iOS 17.5.1 | 46 rows",
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

TYPESS = {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'int', 'name': ''},
          '3': {'type': 'bytes', 'name': ''}, '4': {'type': 'int', 'name': ''},
          '5': {'type': 'bytes', 'name': ''}, '6': {'type': 'int', 'name': ''},
          '7': {'type': 'int', 'name': ''}, '8': {'type': 'bytes', 'name': ''}}

# inputMode names, read from BiomeLibrary.framework BMEmojiEngagement on macOS 27.2.1 (26B131).
INPUT_MODES = {0: 'Unknown', 1: 'EmojiKeyboardPalette', 2: 'EmojiKeyboardPaletteRecents',
               3: 'EmojiSearch', 4: 'CandidateBar', 5: 'Handwriting', 6: 'Dictation',
               7: 'CharacterPickerLightweight', 8: 'CharacterPickerPopover',
               9: 'CharacterPickerExtended', 10: 'DigitalFirstRow'}


def _emoji(value):
    if not isinstance(value, bytes):
        return '' if value is None else str(value)
    try:
        return value.decode('utf-8')
    except UnicodeDecodeError:
        return value.decode('latin-1', 'replace')


def _code_points(text):
    return ' '.join(f'U+{ord(ch):04X}' for ch in text)


def _int32(value):
    """resultPosition is an int32; a negative value arrives as a 64-bit varint."""
    if not isinstance(value, int):
        return ''
    return value - (1 << 64) if value >= 1 << 63 else value


def _bool(value):
    return {1: 'True', 0: 'False'}.get(value, '') if isinstance(value, int) else ''


@artifact_processor
def get_biomeEmojiEngagement(context):

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
                    logfunc(f'Emoji Engagement: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                emoji = _emoji(protostuff.get('1'))
                mode = protostuff.get('4')
                data_list.append((ts, record.state.name, emoji, _code_points(emoji),
                                  _bool(protostuff.get('2')),
                                  INPUT_MODES.get(mode, '') if isinstance(mode, int) else '',
                                  '' if mode is None else mode,
                                  _emoji(protostuff.get('3')), _emoji(protostuff.get('5')),
                                  _int32(protostuff.get('6')),
                                  '' if protostuff.get('7') is None else protostuff.get('7'),
                                  _emoji(protostuff.get('8')),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name) + (None,) * 10 +
                                 (filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Emoji', 'Code Points',
                    'Positive Engagement', 'Input Mode', 'Input Mode (raw)', 'Locale',
                    'Replacement Context', 'Result Position', 'Search Queries Run',
                    'Final Search Query', 'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
