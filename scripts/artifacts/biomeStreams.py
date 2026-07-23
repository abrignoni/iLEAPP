__artifacts_v2__ = {
    "biomeProactiveMail": {
        "name": "Biome - Proactive Harvesting Mail",
        "description": "Email metadata harvested by the system into the ProactiveHarvesting.Mail biome stream "
                       "(harvest time, the message date, subject, sender and recipient).",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "The message date comes from an embedded CFAbsoluteTime value; the harvest time is the SEGB "
                 "record timestamp.",
        "paths": ('*/Biome/streams/restricted/ProactiveHarvesting.Mail/local/*',
                  '*/biome/streams/restricted/ProactiveHarvesting.Mail/local/*'),
        "output_types": "standard",
        "artifact_icon": "mail",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 295 rows",
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
        "description": "Message content harvested by the system into the ProactiveHarvesting.Messages biome "
                       "stream (service and handle, message text, sender).",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/ProactiveHarvesting.Messages/local/*',
                  '*/biome/streams/restricted/ProactiveHarvesting.Messages/local/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 383 rows",
            "felix_ios17": "iOS 17.6.1 | 39 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 118 rows",
            "iphone11_ios17": "iOS 17.3 | 27 rows",
            "iphone12_ios18": "iOS 18.7 | 30 rows",
            "iphone14plus_ios18": "iOS 18.0 | 13 rows",
            "otto_ios17": "iOS 17.5.1 | 170 rows",
        },
    },
    "biomeMessagesRead": {
        "name": "Biome - Messages Read",
        "description": "Message read events from the Messages.Read biome stream (message identifier and the "
                       "time it was read).",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/Biome/streams/restricted/Messages.Read/local/*',
                  '*/biome/streams/restricted/Messages.Read/local/*'),
        "output_types": "standard",
        "artifact_icon": "check",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 280 rows",
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
        "description": "Per-app foreground start/end events from the ScreenTime.AppUsage biome stream.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "The SEGB record timestamp is used; an embedded timestamp field in this stream is unreliable.",
        "paths": ('*/Biome/streams/restricted/ScreenTime.AppUsage/local/*',
                  '*/biome/streams/restricted/ScreenTime.AppUsage/local/*'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 3678 rows",
            "felix_ios17": "iOS 17.6.1 | 361 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3723 rows",
            "iphone12_ios18": "iOS 18.7 | 1152 rows",
            "iphone14plus_ios18": "iOS 18.0 | 317 rows",
            "otto_ios17": "iOS 17.5.1 | 2783 rows",
        },
    },
    "biomeKeyboardTokens": {
        "name": "Biome - Keyboard Learned Tokens",
        "description": "Words and tokens the keyboard learned, from the Keyboard.TokenFrequency biome stream, "
                       "with their frequency.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-07-11",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Biome",
        "notes": "Some tokens are stored in a non-text form and appear blank.",
        "paths": ('*/Biome/streams/restricted/Keyboard.TokenFrequency/local/*',
                  '*/biome/streams/restricted/Keyboard.TokenFrequency/local/*'),
        "output_types": "standard",
        "artifact_icon": "keyboard",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 290 rows",
            "dexter_ios18": "iOS 18.3.2 | 167 rows",
            "felix23_ios16": "iOS 16.5 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | 11 rows",
            "hc_ios18_7": "iOS 18.7.8 | 143 rows",
            "iphone11_ios17": "iOS 17.3 | 379 rows",
            "iphone12_ios18": "iOS 18.7 | 180 rows",
            "iphone14plus_ios18": "iOS 18.0 | 58 rows",
            "otto_ios17": "iOS 17.5.1 | 187 rows",
        },
    },
}

import os
import struct
from datetime import timezone

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


def _header(message, name):
    """Looks up an email header (name/value pairs in field 10)."""
    headers = message.get('10', [])
    if isinstance(headers, dict):
        headers = [headers]
    for item in headers:
        if isinstance(item, dict) and _txt(item.get('1', '')).lower() == name:
            return _txt(item.get('2', ''))
    return ''


def _cf_double_to_utc(value):
    """The embedded date is a CFAbsoluteTime (seconds since 2001) stored as the
    raw bits of a little-endian double."""
    if not isinstance(value, int):
        return ''
    try:
        seconds = struct.unpack('<d', struct.pack('<q', value))[0]
    except (struct.error, OverflowError):
        return ''
    return convert_cocoa_core_data_ts_to_utc(seconds)


def _records(context):
    """Yields (segb_ts_utc, state_name, decoded_message_or_None, filename, offset)
    for each non-tombstone SEGB record across the matched stream files."""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename.startswith('.'):
            continue
        if not os.path.isfile(file_found) or 'tombstone' in file_found:
            continue
        for record in read_segb_file(file_found):
            ts = record.timestamp1.replace(tzinfo=timezone.utc)
            if record.state == EntryState.Written and record.data:
                try:
                    message, _ = blackboxprotobuf.decode_message(record.data)
                except _DECODE_ERRORS as ex:
                    logfunc(f'Skipping {filename} record at offset {record.data_start_offset} '
                            f'due to protobuf decode error: {ex}')
                    message = None
                yield ts, 'Written', message, filename, record.data_start_offset
            elif record.state == EntryState.Deleted:
                yield ts, 'Deleted', None, filename, record.data_start_offset


@artifact_processor
def biomeProactiveMail(context):
    data_headers = (('Harvest Time', 'datetime'), 'SEGB State', ('Message Date', 'datetime'), 'Subject',
                    'Sender', 'Recipient', 'Message ID', 'Filename', 'Offset')
    data_list = []
    for ts, state, message, filename, offset in _records(context):
        if message is None:
            data_list.append((ts, state, '', '', '', '', '', filename, offset))
            continue
        data_list.append((ts, state, _cf_double_to_utc(message.get('3')), _txt(message.get('11')),
                          _header(message, 'from'), _header(message, 'to'), _txt(message.get('2')),
                          filename, offset))
    return data_headers, data_list, 'see Filename for more info'


@artifact_processor
def biomeProactiveMessages(context):
    data_headers = (('Timestamp', 'datetime'), 'SEGB State', 'Service and Handle', 'Content', 'Sender',
                    'GUID', 'Filename', 'Offset')
    data_list = []
    for ts, state, message, filename, offset in _records(context):
        if message is None:
            data_list.append((ts, state, '', '', '', '', filename, offset))
            continue
        sender = message.get('11', {})
        sender = _txt(sender.get('1')) if isinstance(sender, dict) else ''
        data_list.append((ts, state, _txt(message.get('2')), _txt(message.get('10')), sender,
                          _txt(message.get('1')), filename, offset))
    return data_headers, data_list, 'see Filename for more info'


@artifact_processor
def biomeMessagesRead(context):
    data_headers = (('Read Timestamp', 'datetime'), 'SEGB State', 'Message ID', 'Filename', 'Offset')
    data_list = []
    for ts, state, message, filename, offset in _records(context):
        message_id = _txt(message.get('1')) if message else ''
        data_list.append((ts, state, message_id, filename, offset))
    return data_headers, data_list, 'see Filename for more info'


@artifact_processor
def biomeScreenTimeAppUsage(context):
    data_headers = (('Timestamp', 'datetime'), 'SEGB State', 'Bundle ID', 'Event', 'Filename', 'Offset')
    data_list = []
    for ts, state, message, filename, offset in _records(context):
        if message is None:
            data_list.append((ts, state, '', '', filename, offset))
            continue
        event = message.get('1')
        event = 'Start' if event == 1 else 'End' if event == 0 else _txt(event)
        data_list.append((ts, state, _txt(message.get('3')), event, filename, offset))
    return data_headers, data_list, 'see Filename for more info'


@artifact_processor
def biomeKeyboardTokens(context):
    data_headers = (('Timestamp', 'datetime'), 'SEGB State', 'Token', 'Frequency', 'Filename', 'Offset')
    data_list = []
    for ts, state, message, filename, offset in _records(context):
        if message is None:
            data_list.append((ts, state, '', '', filename, offset))
            continue
        token_field = message.get('1', {})
        token = _txt(token_field.get('1')) if isinstance(token_field, dict) else ''
        data_list.append((ts, state, token, _txt(message.get('3')), filename, offset))
    return data_headers, data_list, 'see Filename for more info'
