__artifacts_v2__ = {
    "get_biomeEmojiEngagement": {
        "name": "Biome - Emoji Engagement",
        "description": "Parses emoji usage from the Emoji.Engagement biome stream. Each record "
                       "holds the emoji the user engaged with, along with the Unicode code "
                       "points so that skin tone modifiers, variation selectors and zero width "
                       "joiner sequences stay visible in the report.",
        "author": "@abrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "The context field decodes to a four character ASCII string that resembles a "
                 "trailing locale fragment (values seen: n_US and n-US, consistent with en_US "
                 "and en-US); it is reported both raw and decoded because that reading is not "
                 "confirmed. Field 2 was 1 on every record observed and field 4 varied from 1 "
                 "to 4; both are reported raw.",
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
          '4': {'type': 'int', 'name': ''}}


def _emoji(value):
    if not isinstance(value, bytes):
        return '' if value is None else str(value)
    try:
        return value.decode('utf-8')
    except UnicodeDecodeError:
        return value.decode('latin-1', 'replace')


def _code_points(text):
    return ' '.join(f'U+{ord(ch):04X}' for ch in text)


def _context_ascii(value):
    """The context integer spells four ASCII characters when read big endian."""
    if not isinstance(value, int):
        return ''
    try:
        decoded = struct.pack('>I', value & 0xFFFFFFFF).decode('ascii')
    except (struct.error, UnicodeDecodeError):
        return ''
    return decoded if decoded.isprintable() else ''


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
            if 'tombstone' in file_found:
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

                sub = protostuff.get('3', {})
                if not isinstance(sub, dict):
                    sub = {}
                context_raw = sub.get('12', '')

                data_list.append((ts, record.state.name, emoji, _code_points(emoji),
                                  _context_ascii(context_raw), context_raw,
                                  protostuff.get('2', ''), protostuff.get('4', ''),
                                  filename, record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, record.state.name, None, None, None, None, None, None,
                                  filename, record.data_start_offset))

    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Emoji', 'Code Points',
                    'Context (decoded)', 'Context (raw)', 'Field 2 (raw)', 'Field 4 (raw)',
                    'Filename', 'Offset')

    return data_headers, data_list, '\n'.join(sorted(source_dirs))
