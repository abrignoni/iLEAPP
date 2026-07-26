"""Biome _DKEvent.* streams that share the DuetKnowledge event wrapper schema.

Every record carries: the event stream name (field 1.1), a start and end
timestamp (fields 2 and 3, Cocoa epoch doubles), the event value (field 4.4),
an event GUID (field 5) and the device UTC offset in seconds (field 10).
Field 7 holds optional metadata entries, each pairing a numeric key with a
string or integer value (for example the audio route name, or the alarm
identifier).
"""
__artifacts_v2__ = {
    "get_biomeDKAudioInputRoute": {
        "name": "Biome - Audio Input Route DKEvent",
        "description": "Parses audio input route changes (built-in microphone, headset, "
                       "Bluetooth device) from the _DKEvent.Audio.InputRoute biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/streams/*/_DKEvent.Audio.InputRoute/local/*',),
        "output_types": "standard",
        "artifact_icon": "mic",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 260 rows",
            "iphone11_ios17": "iOS 17.3 | 360 rows",
        },
    },
    "get_biomeDKAudioOutputRoute": {
        "name": "Biome - Audio Output Route DKEvent",
        "description": "Parses audio output route changes (speaker, receiver, CarPlay, "
                       "Bluetooth device) from the _DKEvent.Audio.OutputRoute biome stream. "
                       "Bluetooth routes carry the device MAC address and name.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/streams/*/_DKEvent.Audio.OutputRoute/local/*',),
        "output_types": "standard",
        "artifact_icon": "volume-2",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 1475 rows",
            "iphone11_ios17": "iOS 17.3 | 546 rows",
        },
    },
    "get_biomeDKClockAlarm": {
        "name": "Biome - Clock Alarm DKEvent",
        "description": "Parses alarm state changes from the _DKEvent.Clock.Alarm biome stream. "
                       "Metadata carries the alarm identifier, which can be correlated with the "
                       "Clock app alarm list.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "Raw state values observed: 0, 1, 2 and 4. Apple's plist describes this stream "
                 "as capturing alarm states such as firing and snoozed; exact value semantics "
                 "are not confirmed, so the raw value is reported.",
        "paths": ('*/streams/*/_DKEvent.Clock.Alarm/local/*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 12 rows",
            "iphone11_ios17": "iOS 17.3 | 5 rows",
        },
    },
    "get_biomeDKDeviceIsLockedImputed": {
        "name": "Biome - Screen Lock Imputed DKEvent",
        "description": "Parses imputed screen lock state changes from the "
                       "_DKEvent.Device.IsLockedImputed biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "This is the imputed variant of the screen lock stream: iOS fills in lock "
                 "state transitions it did not observe directly.",
        "paths": ('*/streams/*/_DKEvent.Device.IsLockedImputed/local/*',),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 920 rows",
            "iphone11_ios17": "iOS 17.3 | 700 rows",
        },
    },
    "get_biomeDKDeviceLowPowerMode": {
        "name": "Biome - Low Power Mode DKEvent",
        "description": "Parses Low Power Mode transitions from the _DKEvent.Device.LowPowerMode "
                       "biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/streams/*/_DKEvent.Device.LowPowerMode/local/*',),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 21 rows",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
        },
    },
    "get_biomeDKDisplayOrientation": {
        "name": "Biome - Display Orientation DKEvent",
        "description": "Parses device orientation changes from the _DKEvent.Display.Orientation "
                       "biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "Value follows the UIDeviceOrientation enumeration; the raw value is reported "
                 "alongside the label.",
        "paths": ('*/streams/*/_DKEvent.Display.Orientation/local/*',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 94 rows",
            "iphone11_ios17": "iOS 17.3 | 85 rows",
        },
    },
    "get_biomeDKSiriUi": {
        "name": "Biome - Siri UI DKEvent",
        "description": "Parses Siri interface events from the _DKEvent.Siri.Ui biome stream. "
                       "Runs alongside the Siri.UI stream and carries the same activity in the "
                       "DuetKnowledge wrapper, with start and end timestamps that bound each "
                       "appearance of the Siri interface.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "Biome",
        "notes": "The event detail is carried in the metadata entries rather than the value "
                 "field, which was absent throughout the sample.",
        "paths": ('*/streams/*/_DKEvent.Siri.Ui/local/*',),
        "output_types": "standard",
        "artifact_icon": "mic",
    },
    "get_biomeDKSettingsDoNotDisturb": {
        "name": "Biome - Do Not Disturb DKEvent",
        "description": "Parses Do Not Disturb state changes from the "
                       "_DKEvent.Settings.DoNotDisturb biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/streams/*/_DKEvent.Settings.DoNotDisturb/local/*',),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 586 rows",
        },
    },
}


import os
import struct
from datetime import timedelta, timezone

from scripts import blackboxprotobuf
from google.protobuf.message import DecodeError
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc, webkit_timestampsconv

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

TYPESS = {
    '1': {
        'type': 'message',
        'message_typedef': {
            '1': {'type': 'str', 'name': ''},
            '2': {
                'type': 'message',
                'message_typedef': {
                    '1': {'type': 'int', 'name': ''},
                    '2': {'type': 'int', 'name': ''},
                },
                'name': '',
            },
        },
        'name': '',
    },
    '2': {'type': 'double', 'name': ''},
    '3': {'type': 'double', 'name': ''},
    '5': {'type': 'bytes', 'name': ''},
    '10': {'type': 'int', 'name': ''},
}

ON_OFF = {0: 'Off', 1: 'On'}
LOCKED = {0: 'Unlocked', 1: 'Locked'}
ORIENTATION = {0: 'Unknown', 1: 'Portrait', 2: 'Portrait Upside Down', 3: 'Landscape Left',
               4: 'Landscape Right', 5: 'Face Up', 6: 'Face Down'}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None:
        return ''
    return str(value)


def _cocoa(value):
    if not isinstance(value, (int, float)) or not value:
        return None
    try:
        return webkit_timestampsconv(value)
    except (OverflowError, OSError, ValueError):
        return None


def _metadata(protostuff):
    # Field 7 entries pair a numeric key (7.N.3) with a string (7.N.2.3) or int (7.N.2.4) value.
    entries = protostuff.get('7', [])
    if isinstance(entries, dict):
        entries = [entries]
    parts = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = entry.get('3', '')
        payload = entry.get('2', {})
        if not isinstance(payload, dict):
            continue
        if '3' in payload:
            value = _to_str(payload.get('3'))
        elif '4' in payload:
            value = _to_str(payload.get('4'))
        else:
            continue
        if value:
            parts.append(f'{key}={value}')
    return '; '.join(parts)


def _utc_offset(value):
    if not isinstance(value, int):
        return ''
    delta = timedelta(seconds=value)
    sign = '-' if delta.total_seconds() < 0 else '+'
    hours, remainder = divmod(abs(delta).seconds + abs(delta).days * 86400, 3600)
    minutes = remainder // 60
    return f'UTC{sign}{hours:02d}:{minutes:02d}'


def _parse(context, label, value_map):
    data_headers = (('SEGB Timestamp', 'datetime'), ('Start Timestamp', 'datetime'),
                    ('End Timestamp', 'datetime'), 'SEGB State', 'Value', 'Value (raw)',
                    'Metadata', 'Event', 'GUID', 'Device UTC Offset', 'Filename', 'Offset')
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
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except _DECODE_ERRORS as ex:
                    logfunc(f'{label}: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue

                event = _to_str(protostuff.get('1', {}).get('1', b'')) \
                    if isinstance(protostuff.get('1'), dict) else ''
                raw_value = protostuff.get('4', {}).get('4', '') \
                    if isinstance(protostuff.get('4'), dict) else ''
                value = value_map.get(raw_value, '') if value_map else ''

                data_list.append((ts, _cocoa(protostuff.get('2')), _cocoa(protostuff.get('3')),
                                  record.state.name, value, raw_value, _metadata(protostuff),
                                  event, _to_str(protostuff.get('5', b'')),
                                  _utc_offset(protostuff.get('10')), filename,
                                  record.data_start_offset))

            elif record.state == EntryState.Deleted:
                data_list.append((ts, None, None, record.state.name, None, None, None, None,
                                  None, None, filename, record.data_start_offset))

    return data_headers, data_list, 'see Filename for more info'


@artifact_processor
def get_biomeDKAudioInputRoute(context):
    return _parse(context, 'Audio Input Route DKEvent', None)


@artifact_processor
def get_biomeDKAudioOutputRoute(context):
    return _parse(context, 'Audio Output Route DKEvent', None)


@artifact_processor
def get_biomeDKClockAlarm(context):
    return _parse(context, 'Clock Alarm DKEvent', None)


@artifact_processor
def get_biomeDKDeviceIsLockedImputed(context):
    return _parse(context, 'Screen Lock Imputed DKEvent', LOCKED)


@artifact_processor
def get_biomeDKDeviceLowPowerMode(context):
    return _parse(context, 'Low Power Mode DKEvent', ON_OFF)


@artifact_processor
def get_biomeDKDisplayOrientation(context):
    return _parse(context, 'Display Orientation DKEvent', ORIENTATION)


@artifact_processor
def get_biomeDKSettingsDoNotDisturb(context):
    return _parse(context, 'Do Not Disturb DKEvent', ON_OFF)


@artifact_processor
def get_biomeDKSiriUi(context):
    return _parse(context, 'Siri UI DKEvent', None)
