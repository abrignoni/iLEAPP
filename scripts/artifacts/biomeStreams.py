__artifacts_v2__ = {
    "biomeProactiveMail": {
        "name": "Biome - Proactive Harvesting Mail",
        "description": ("Email records from the ProactiveHarvesting.Mail biome stream: the SEGB "
                       "record timestamp, the stored message date and date received, subject, and the "
                       "From and To headers."),
        "author": "@AlexisBrignoni, Claude, Codex",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are those of the BMProactiveHarvestingMail class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read. "
                 "On the tested images (the sample_data keys) the field numbers and wire types of "
                 "the written records that decoded fit this class. Message Date is field 3 "
                 "(absoluteTimestamp) and Date Received is field 30 (dateReceived); the framework "
                 "decodes both as seconds since 2001-01-01 UTC. On the tested images the two were "
                 "equal on 73, within 60 seconds on 633 and more than 60 seconds apart on 32 of the "
                 "738 written records that held both. Sender and Recipient are the From and To "
                 "headers of field 10 (headers). Domain ID is field 2 (domainID), reported before "
                 "as Message ID, and Message Identifier is field 5 (messageIdentifier). Message "
                 "Identifier held a string of digits on each of the 766 written records that "
                 "decoded; what store it indexes was not established. 28 written records on "
                 "dexter_ios18 did not decode and are reported with their SEGB fields only. "
                 "The SEGB Record Timestamp column is the SEGB record's creation timestamp as read by "
                 "ccl_segb. Deleted rows carry no stored fields."),
        "paths": ('*/[Bb]iome/streams/restricted/ProactiveHarvesting.Mail/local/*',),
        "output_types": "standard",
        "artifact_icon": "mail",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 82 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 38 rows",
            "dexter_ios18": "iOS 18.3.2 | 295 rows",
            "falken_ios26": "iOS 26.2.1 | 941 rows",
            "felix_ios17": "iOS 17.6.1 | 25 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 275 rows",
            "iphone11_ios17": "iOS 17.3 | 299 rows",
            "iphone12_ios18": "iOS 18.7 | 60 rows",
            "iphone14plus_ios18": "iOS 18.0 | 62 rows",
            "otto_ios17": "iOS 17.5.1 | 193 rows",
        },
    },
    "biomeProactiveMessages": {
        "name": "Biome - Proactive Harvesting Messages",
        "description": ("Message records from the ProactiveHarvesting.Messages biome stream "
                       "(message date, domain id, message text, sender and the isFromMe flag)."),
        "author": "@AlexisBrignoni, Claude, Codex",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are those of the BMProactiveHarvestingMessages class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read. "
                 "On the tested images (the sample_data keys) the field numbers and wire types of "
                 "the written records that decoded fit this class. Message Date is field 3 "
                 "(absoluteTimestamp), which the framework decodes as seconds since 2001-01-01 "
                 "UTC; each of the 38 written records that decoded held a value in that range. "
                 "Domain ID is field 2 (domainID), reported before as Service and Handle. Sender "
                 "is the name of field 11 (fromHandle); the handle of field 11 held the same text "
                 "as the name on each of the 38 written records that decoded, so it is not a "
                 "separate column. Is From Me is field 22 (isFromMe); it is blank where the record "
                 "does not store it (27 of the 38). Unique ID is field 1 (uniqueID), reported "
                 "before as GUID. Deleted rows and the 5 written records on dexter_ios18 that did "
                 "not decode carry no Message Date. The SEGB Record Timestamp column is the SEGB "
                 "record's creation timestamp as read by ccl_segb."),
        "paths": ('*/[Bb]iome/streams/restricted/ProactiveHarvesting.Messages/local/*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 140 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 27 rows",
            "dexter_ios18": "iOS 18.3.2 | 383 rows",
            "falken_ios26": "iOS 26.2.1 | 297 rows",
            "felix_ios17": "iOS 17.6.1 | 39 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 124 rows",
            "iphone11_ios17": "iOS 17.3 | 27 rows",
            "iphone12_ios18": "iOS 18.7 | 30 rows",
            "iphone14plus_ios18": "iOS 18.0 | 13 rows",
            "otto_ios17": "iOS 17.5.1 | 170 rows",
        },
    },
    "biomeMessagesRead": {
        "name": "Biome - Messages Read",
        "description": ("Records from the Messages.Read biome stream (the IDS handle, the "
                       "marked-unread flag and the SEGB record timestamp; that the record timestamp "
                       "equals the time a message was read was not tested here)."),
        "author": "@AlexisBrignoni, Claude, Codex",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are those of the BMMessagesRead class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read. "
                 "On the tested images (the sample_data keys) the field numbers and wire types of "
                 "the written records that decoded fit this class. IDS Handle is field 1 (idsHandle), "
                 "reported before as Message ID. On the tested images it held a plus sign and "
                 "digits on 439 written rows, digits only on 123, an email-shaped string on 15 and "
                 "other short text on 5, and was blank on 112. Marked Unread is field 2 "
                 "(markedUnread): True on 440, False on 146 and blank on 108 of the 694 written "
                 "rows; the blank rows are on dexter_ios18, where the records did not decode or did "
                 "not store the field. What Marked Unread means for these records was not "
                 "established. Written records with no payload give no row. The SEGB Record "
                 "Timestamp column is the SEGB record's creation timestamp as read by ccl_segb. "
                 "Reference: Mattia "
                 "Epifani, '84 Streams Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html"),
        "paths": ('*/[Bb]iome/streams/restricted/Messages.Read/local/*',),
        "output_types": "standard",
        "artifact_icon": "check",
        "sample_data": {
            "adams_iphone12mini": "iOS 17.1.1 | 171 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 36 rows",
            "dexter_ios18": "iOS 18.3.2 | 280 rows",
            "falken_ios26": "iOS 26.2.1 | 260 rows",
            "felix_ios17": "iOS 17.6.1 | 53 rows",
            "fsfull002_ios17": "iOS 17.1 | 14 rows",
            "hc_ios18_7": "iOS 18.7.8 | 136 rows",
            "iphone11_ios17": "iOS 17.3 | 57 rows",
            "iphone12_ios18": "iOS 18.7 | 74 rows",
            "iphone14plus_ios18": "iOS 18.0 | 16 rows",
            "otto_ios17": "iOS 17.5.1 | 168 rows",
        },
    },
    "biomeScreenTimeAppUsage": {
        "name": "Biome - ScreenTime App Usage",
        "description": ("Per-app usage records from the ScreenTime.AppUsage biome stream: the bundle "
                       "id, the starting flag, the SEGB record timestamp and the stored absolute "
                       "timestamp."),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are those of the BMScreenTimeAppUsage class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read. "
                 "On the tested images (the sample_data keys) the field numbers and wire types of "
                 "the written records that decoded fit this class. Starting is field 1 (starting), "
                 "reported before as an undocumented event code. Absolute Timestamp is field 2 "
                 "(absoluteTimestamp), which the framework decodes as Unix seconds; on the tested "
                 "images it was within 2 seconds of the SEGB record timestamp on 4,759 of the 4,766 "
                 "written records that held it, and within 10 seconds on the other 7. 10 written "
                 "records on dexter_ios18 did not decode and are reported with their SEGB fields "
                 "only. Timestamp is the SEGB record's creation timestamp as read by ccl_segb."),
        "paths": ('*/[Bb]iome/streams/restricted/ScreenTime.AppUsage/local/*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "cookbook_ios1751": "iOS 17.5.1 | 835 rows",
            "dexter_ios18": "iOS 18.3.2 | 3678 rows",
            "falken_ios26": "iOS 26.2.1 | 1239 rows",
            "felix_ios17": "iOS 17.6.1 | 361 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3723 rows",
            "iphone12_ios18": "iOS 18.7 | 1152 rows",
            "iphone14plus_ios18": "iOS 18.0 | 317 rows",
            "otto_ios17": "iOS 17.5.1 | 2783 rows",
        },
    },
    "biomeKeyboardTokens": {
        "name": "Biome - Keyboard Learned Tokens",
        "description": ("Token entries from the Keyboard.TokenFrequency biome stream, one row per "
                       "token entry with its count, token type and locale. A deleted record gives one "
                       "row with no token."),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are those of the BMKeyboardTokenFrequency class, read from "
                 "BiomeLibrary.framework on macOS 27.2.1 (26B131); no iOS copy of the class was read. "
                 "On the tested images (the sample_data keys) the field numbers and wire types of "
                 "the written records that decoded fit this class. Field 1 is a repeated list of "
                 "token entries, each with the token text (1.1) and its count (1.2); one record "
                 "held up to 48 entries on the tested images, and the artifact writes one row per "
                 "entry, so several rows share a Timestamp and Offset. Before, a record with more "
                 "than one entry was printed as one decoded list, and the Frequency column held "
                 "field 3. Field 3 is tokenType, named in Token Type from the framework (0 Unknown, "
                 "1 Unigram, 2 Emoji, 3 NamedEntityGivenName, 4 NamedEntitySurname), with the "
                 "integer in Token Type (raw). Locale is field 2 (locale). On the tested images the "
                 "written rows per image equalled a separate count of field 1 entries in the "
                 "stored records (12 images, 4,074 entries). Timestamp is the SEGB record's "
                 "creation timestamp as read by ccl_segb. Reference: Mattia Epifani, '84 Streams "
                 "Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html"),
        "paths": ('*/[Bb]iome/streams/restricted/Keyboard.TokenFrequency/local/*',),
        "output_types": "standard",
        "artifact_icon": "keyboard",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 1147 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 414 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 90 rows",
            "dexter_ios18": "iOS 18.3.2 | 280 rows",
            "falken_ios26": "iOS 26.2.1 | 454 rows",
            "felix23_ios16": "iOS 16.5 | 12 rows",
            "felix_ios17": "iOS 17.6.1 | 20 rows",
            "hc_ios18_7": "iOS 18.7.8 | 179 rows",
            "iphone11_ios17": "iOS 17.3 | 861 rows",
            "iphone12_ios18": "iOS 18.7 | 896 rows",
            "iphone14plus_ios18": "iOS 18.0 | 390 rows",
            "otto_ios17": "iOS 17.5.1 | 223 rows",
        },
    },
}

import os
import struct
from datetime import datetime, timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError

from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, convert_cocoa_core_data_ts_to_utc, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)


def _txt(value):
    """Returns a protobuf field as text ('' when absent or non-text)."""
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value)


def _bool(value):
    """A framework bool field: 1 True, 0 False, anything else blank."""
    return {1: 'True', 0: 'False'}.get(value, '') if isinstance(value, int) else ''


def _unix_double_to_utc(value):
    """A double read as Unix seconds (the BiomeLibrary decoding of this field)."""
    seconds = _seconds(value)
    if not seconds or seconds < 0:
        return ''
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _header(message, name):
    """Looks up an email header (name/value pairs in field 10)."""
    headers = message.get('10', [])
    if isinstance(headers, dict):
        headers = [headers]
    for item in headers:
        if isinstance(item, dict) and _txt(item.get('1', '')).lower() == name:
            return _txt(item.get('2', ''))
    return ''


def _seconds(value):
    """A double field: a float under a pinned typedef, raw fixed64 bits otherwise."""
    if isinstance(value, float):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        try:
            return struct.unpack('<d', struct.pack('<q', value))[0]
        except (struct.error, OverflowError):
            return None
    return None


def _cf_double_to_utc(value):
    """A Cocoa-epoch double (seconds since 2001-01-01 UTC)."""
    seconds = _seconds(value)
    if not seconds:
        return ''
    return convert_cocoa_core_data_ts_to_utc(seconds)


def _stream_files(context):
    """Non-hidden, non-tombstone stream files from the artifact's matched paths."""
    for file_found in map(str, context.get_files_found()):
        if os.path.basename(file_found).startswith('.'):
            continue
        if not os.path.isfile(file_found) or 'tombstone' in context.get_relative_path(file_found):
            continue
        yield file_found


def _source_path(context):
    return '\n'.join(sorted({os.path.dirname(f) for f in _stream_files(context)}))


def _records(context, typedef=None):
    """Yields (segb_ts_utc, state_name, decoded_message_or_None, filename, offset)
    for each non-tombstone SEGB record across the matched stream files."""
    for file_found in _stream_files(context):
        filename = os.path.basename(file_found)
        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)
            if record.state == EntryState.Written and record.data:
                try:
                    message, _ = blackboxprotobuf.decode_message(record.data, typedef)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Skipping {filename} record at offset {record.data_start_offset} '
                            f'due to protobuf decode error: {ex}')
                    message = None
                yield ts, 'Written', message, filename, record.data_start_offset
            elif record.state == EntryState.Deleted:
                yield ts, 'Deleted', None, filename, record.data_start_offset


# Field types pinned from the BiomeLibrary classes so that a string whose bytes happen to
# parse as protobuf stays a string. Fields not listed decode schema-less.
_STR = {'type': 'bytes', 'name': ''}
_INT = {'type': 'int', 'name': ''}
_DBL = {'type': 'double', 'name': ''}
_HANDLE = {'type': 'message', 'name': '', 'message_typedef': {'1': _STR, '2': _STR}}
MAIL_TYPEDEF = {'1': _STR, '2': _STR, '3': _DBL, '4': _STR, '5': _STR, '10': _HANDLE,
                '11': _STR, '30': _DBL}
MESSAGES_TYPEDEF = {'1': _STR, '2': _STR, '3': _DBL, '10': _STR, '11': _HANDLE, '22': _INT}
READ_TYPEDEF = {'1': _STR, '2': _INT}
SCREENTIME_TYPEDEF = {'1': _INT, '2': _DBL, '3': _STR}


@artifact_processor
def biomeProactiveMail(context):
    data_headers = (('SEGB Record Timestamp', 'datetime'), ('Message Date', 'datetime'), 'SEGB State', 'Subject',
                    'Sender', 'Recipient', ('Date Received', 'datetime'), 'Domain ID', 'Message Identifier',
                    'Filename', 'Offset')
    data_list = []
    for ts, state, message, filename, offset in _records(context, MAIL_TYPEDEF):
        if message is None:
            data_list.append((ts, '', state, '', '', '', '', '', '', filename, offset))
            continue
        data_list.append((ts, _cf_double_to_utc(message.get('3')), state, _txt(message.get('11')),
                          _header(message, 'from'), _header(message, 'to'),
                          _cf_double_to_utc(message.get('30')), _txt(message.get('2')),
                          _txt(message.get('5')), filename, offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def biomeProactiveMessages(context):
    data_headers = (('SEGB Record Timestamp', 'datetime'), ('Message Date', 'datetime'), 'SEGB State',
                    'Domain ID', 'Content', 'Sender', 'Is From Me', 'Unique ID', 'Filename', 'Offset')
    data_list = []
    for ts, state, message, filename, offset in _records(context, MESSAGES_TYPEDEF):
        if message is None:
            data_list.append((ts, '', state, '', '', '', '', '', filename, offset))
            continue
        from_handle = message.get('11', {})
        if not isinstance(from_handle, dict):
            from_handle = {}
        data_list.append((ts, _cf_double_to_utc(message.get('3')), state, _txt(message.get('2')),
                          _txt(message.get('10')), _txt(from_handle.get('1')),
                          _bool(message.get('22')), _txt(message.get('1')), filename, offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def biomeMessagesRead(context):
    data_headers = (('SEGB Record Timestamp', 'datetime'), 'SEGB State', 'IDS Handle', 'Marked Unread',
                    'Filename', 'Offset')
    data_list = []
    for ts, state, message, filename, offset in _records(context, READ_TYPEDEF):
        handle = _txt(message.get('1')) if message else ''
        marked_unread = _bool(message.get('2')) if message else ''
        data_list.append((ts, state, handle, marked_unread, filename, offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def biomeScreenTimeAppUsage(context):
    data_headers = (('Timestamp', 'datetime'), ('Absolute Timestamp', 'datetime'), 'SEGB State', 'Bundle ID',
                    'Starting', 'Filename', 'Offset')
    data_list = []
    for ts, state, message, filename, offset in _records(context, SCREENTIME_TYPEDEF):
        if message is None:
            data_list.append((ts, '', state, '', '', filename, offset))
            continue
        data_list.append((ts, _unix_double_to_utc(message.get('2')), state, _txt(message.get('3')),
                          _bool(message.get('1')), filename, offset))
    return data_headers, data_list, _source_path(context)


def _keyboard_token(token_field):
    """Token text from field 1, keeping what is stored when the expected shape is absent.

    The expected shape is a submessage whose subfield 1 is the token text. The
    schema-less decoder can leave that submessage as bytes, and a record can
    store something else in field 1; neither is dropped.
    """
    if token_field is None:
        return ''
    if isinstance(token_field, bytes):
        try:
            inner, _ = blackboxprotobuf.decode_message(token_field)
        except _DECODE_ERRORS:
            inner = None
        if isinstance(inner, dict) and isinstance(inner.get('1'), bytes):
            return _txt(inner['1'])
        return _txt(token_field)
    if isinstance(token_field, dict):
        if isinstance(token_field.get('1'), (bytes, str)):
            return _txt(token_field['1'])
        return str(token_field) if token_field else ''
    if isinstance(token_field, list):
        return str(token_field)
    return _txt(token_field)


# tokenType names, read from BiomeLibrary.framework BMKeyboardTokenFrequency on macOS 27.2.1 (26B131).
TOKEN_TYPES = {0: 'Unknown', 1: 'Unigram', 2: 'Emoji', 3: 'NamedEntityGivenName', 4: 'NamedEntitySurname'}


# Field types from BMKeyboardTokenFrequency: 1 repeated (1 token string, 2 count int), 2 locale string,
# 3 tokenType enum. Pinned so a token whose text happens to parse as protobuf stays text.
KEYBOARD_TYPEDEF = {
    '1': {'type': 'message', 'name': '', 'message_typedef': {
        '1': {'type': 'bytes', 'name': ''},
        '2': {'type': 'int', 'name': ''},
    }},
    '2': {'type': 'bytes', 'name': ''},
    '3': {'type': 'int', 'name': ''},
}


def _token_entries(field):
    """Field 1 is repeated (token, count) pairs; one record can hold many."""
    if field is None:
        return [None]
    return field if isinstance(field, list) else [field]


def _token_count(entry):
    if isinstance(entry, bytes):
        try:
            entry, _ = blackboxprotobuf.decode_message(entry)
        except _DECODE_ERRORS:
            return ''
    count = entry.get('2') if isinstance(entry, dict) else None
    return count if isinstance(count, int) else ''


@artifact_processor
def biomeKeyboardTokens(context):
    data_headers = (('Timestamp', 'datetime'), 'SEGB State', 'Token', 'Count', 'Token Type',
                    'Token Type (raw)', 'Locale', 'Filename', 'Offset')
    data_list = []
    for ts, state, message, filename, offset in _records(context, KEYBOARD_TYPEDEF):
        if message is None:
            data_list.append((ts, state, '', '', '', '', '', filename, offset))
            continue
        token_type = message.get('3')
        type_name = TOKEN_TYPES.get(token_type, '') if isinstance(token_type, int) else ''
        locale = _txt(message.get('2'))
        for entry in _token_entries(message.get('1')):
            data_list.append((ts, state, _keyboard_token(entry), _token_count(entry), type_name,
                              _txt(token_type), locale, filename, offset))
    return data_headers, data_list, _source_path(context)
