"""Biome device state streams that record a single value per event.

These streams are the modern, flat counterparts to the older _DKEvent.* wrappers
and coexist with them on the same device. Each record is a state transition
stamped with the SEGB record timestamp.
"""
__artifacts_v2__ = {
    "get_biomeInterfaceOrientation": {
        "name": "Biome - Interface Orientation",
        "description": "Parses interface orientation changes from the "
                       "Device.Display.InterfaceOrientation biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-27",
        "requirements": "none",
        "category": "Biome",
        "notes": "Value follows the UIInterfaceOrientation enumeration (UIKit, defined in "
                 "UIApplication.h); the raw value is reported alongside the label. Read the "
                 "landscape labels carefully: Apple crosses the two landscape cases against "
                 "UIDeviceOrientation, so under UIInterfaceOrientation 3 is Landscape Right "
                 "and 4 is Landscape Left, the opposite of the values in the "
                 "_DKEvent.Display.Orientation stream parsed by Biome - Display Orientation "
                 "DKEvent. Header text: UIInterfaceOrientationLandscapeLeft = "
                 "UIDeviceOrientationLandscapeRight and UIInterfaceOrientationLandscapeRight = "
                 "UIDeviceOrientationLandscapeLeft. Only values 0, 1 and 2 have been observed "
                 "in sample data so far, and those three are identical in both enumerations, so "
                 "the choice of enumeration is not yet confirmed by data: the stream name says "
                 "interface orientation while the System Events plist describes it as capturing "
                 "device orientation. A value of 5 or 6 appearing here would indicate the "
                 "device enumeration instead, since UIInterfaceOrientation has no Face Up or "
                 "Face Down case. Enumeration source: Apple UIKit headers UIApplication.h and "
                 "UIDevice.h, mirrored at "
                 "https://github.com/silent0123/OSXDev/blob/master/uSav-Mac/usavMac/UIKit.framework/Headers/UIApplication.h "
                 "Stream reference: Mattia Epifani, '84 Streams Later, Part 2: Inside Apple "
                 "Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html",
        "paths": ('*/streams/*/Device.Display.InterfaceOrientation/local/*',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 308 rows",
            "iphone11_ios17": "iOS 17.3 | 110 rows",
        },
    },
    "get_biomeLowPowerMode": {
        "name": "Biome - Low Power Mode",
        "description": "Parses Low Power Mode transitions from the Device.Power.LowPowerMode "
                       "biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/streams/*/Device.Power.LowPowerMode/local/*',),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 76 rows",
            "iphone11_ios17": "iOS 17.3 | 16 rows",
        },
    },
    "get_biomeAirplaneModeWireless": {
        "name": "Biome - Airplane Mode",
        "description": "Parses Airplane Mode transitions from the Device.Wireless.AirplaneMode "
                       "biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "Appears to be the modern counterpart of the _DKEvent.System.AirplaneMode "
                 "stream parsed by Biome - Airplane Mode DKEvent.",
        "paths": ('*/streams/*/Device.Wireless.AirplaneMode/local/*',),
        "output_types": "standard",
        "artifact_icon": "airplay",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 98 rows",
            "iphone11_ios17": "iOS 17.3 | 23 rows",
        },
    },
    "get_biomeCellularDataEnabled": {
        "name": "Biome - Cellular Data Enabled",
        "description": "Parses cellular data enable and disable events from the "
                       "Device.Wireless.CellularDataEnabled biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "",
        "paths": ('*/streams/*/Device.Wireless.CellularDataEnabled/local/*',),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 200 rows",
            "iphone11_ios17": "iOS 17.3 | 19 rows",
        },
    },
    "get_biomeCarPlayConnected": {
        "name": "Biome - CarPlay Connected",
        "description": "Parses CarPlay connection state changes from the CarPlay.Connected "
                       "biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "Appears to be the modern counterpart of the _DKEvent.Carplay.IsConnected "
                 "stream parsed by Biome - Carplay.",
        "paths": ('*/streams/*/CarPlay.Connected/local/*',),
        "output_types": "standard",
        "artifact_icon": "truck",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 24 rows",
            "iphone11_ios17": "iOS 17.3 | 36 rows",
        },
    },
    "get_biomeBatteryTemperature": {
        "name": "Biome - Battery Temperature",
        "description": "Parses battery temperature samples from the "
                       "Device.Thermals.BatteryTemperature biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "The raw value is temperature in hundredths of a degree Celsius (observed "
                 "range 1900-3700, i.e. 19.00-37.00 C); both the converted and raw values are "
                 "reported. Field 2 is reported raw as its meaning is not confirmed.",
        "paths": ('*/streams/*/Device.Thermals.BatteryTemperature/local/*',),
        "output_types": "standard",
        "artifact_icon": "thermometer",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 817 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
        },
    },
    "get_biomeScreenLocked": {
        "name": "Biome - Screen Locked",
        "description": "Parses screen lock and unlock events from the Device.ScreenLocked "
                       "biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "Lock polarity validated against the _DKEvent.Device.IsLockedImputed stream "
                 "on the same device: 146 of 148 overlapping records agree, the exceptions "
                 "falling on interval boundaries. A small number of records carry a two byte "
                 "empty payload and are reported with no value.",
        "paths": ('*/streams/*/Device.ScreenLocked/local/*',),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 932 rows",
            "iphone11_ios17": "iOS 17.3 | 703 rows",
        },
    },
    "get_biomeKeybagLocked": {
        "name": "Biome - Keybag Locked",
        "description": "Parses keybag lock state changes from the Device.KeybagLocked biome "
                       "stream. The keybag holds the class keys that protect file data; the "
                       "stream records its locked state over time.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "Lock polarity validated against the _DKEvent.Keybag.IsLocked stream on the "
                 "same device: 124 of 128 overlapping records agree, the exceptions falling on "
                 "interval boundaries. Modern counterpart of that stream, parsed by "
                 "Biome - Keybag. Reference: Apple Platform Security, 'Keybags for Data "
                 "Protection', https://support.apple.com/guide/security/sec6483d5760/web",
        "paths": ('*/streams/*/Device.KeybagLocked/local/*',),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 308 rows",
            "iphone11_ios17": "iOS 17.3 | 292 rows",
        },
    },
    "get_biomeBatteryLevel": {
        "name": "Biome - Battery Level",
        "description": "Parses battery level samples from the Device.Power.BatteryLevel biome "
                       "stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Biome",
        "notes": "The level is a percentage stored as a double (observed range 1.0 to 100.0). "
                 "Appears to be the modern counterpart of the _DKEvent.Device.BatteryPercentage "
                 "stream parsed by Biome - Battery Percentage.",
        "paths": ('*/streams/*/Device.Power.BatteryLevel/local/*',),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 583 rows",
            "iphone11_ios17": "iOS 17.3 | 2945 rows",
        },
    },
    "get_biomeDevicePluggedIn": {
        "name": "Biome - Power Plugged In",
        "description": "Parses charger connect and disconnect events from the "
                       "Device.Power.PluggedIn biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-27",
        "requirements": "none",
        "category": "Biome",
        "notes": "Field 3 is populated only while plugged in and is reported raw as its "
                 "meaning is not confirmed. A record is written whenever the device is "
                 "charging, which includes wireless charging as well as a physical cable "
                 "connection (observation by Ian Whiffin). Modern counterpart of the "
                 "_DKEvent.Device.IsPluggedIn stream parsed by Biome - Device Plugged In. "
                 "Reference: Mattia Epifani, '84 Streams Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html",
        "paths": ('*/streams/*/Device.Power.PluggedIn/local/*',),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 771 rows",
            "iphone11_ios17": "iOS 17.3 | 514 rows",
        },
    },
    "get_biomeEnergyMode": {
        "name": "Biome - Energy Mode",
        "description": "Parses energy mode changes from the Device.Power.EnergyMode biome "
                       "stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "Both fields are reported raw: the sample data does not confirm which energy "
                 "mode each value denotes. Field 1 was observed as 1 or 2 and field 2 as 1, 3 "
                 "or 7.",
        "paths": ('*/streams/*/Device.Power.EnergyMode/local/*',),
        "output_types": "standard",
        "artifact_icon": "zap",
    },
    "get_biomeSilentMode": {
        "name": "Biome - Silent Mode",
        "description": "Parses ringer switch and silent mode changes from the "
                       "Device.SilentMode biome stream, including the reason the state was "
                       "recorded (a physical ringer switch event, or the session manager "
                       "reading the switch position at startup).",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "Reasons observed: RingerSwitchEvent and 'MXSessionManager startup HID ringer "
                 "switch state'. Field 2 is reported raw as its meaning is not confirmed.",
        "paths": ('*/streams/*/Device.SilentMode/local/*',),
        "output_types": "standard",
        "artifact_icon": "bell-off",
        "sample_data": {
            "hc_ios18_7": "iOS 18.7.8 | 73 rows",
            "iphone11_ios17": "iOS 17.3 | 35 rows",
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
from scripts.ilapfuncs import artifact_processor, logfunc

_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError,
                  IndexError)

TYPESS = {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}
BATTERY_TYPESS = {'1': {'type': 'double', 'name': ''}, '2': {'type': 'int', 'name': ''}}
SILENT_TYPESS = {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''},
                 '4': {'type': 'str', 'name': ''}}
PLUGGED_TYPESS = {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''},
                  '3': {'type': 'int', 'name': ''}}

ON_OFF = {0: 'Off', 1: 'On'}
ENABLED = {0: 'Disabled', 1: 'Enabled'}
CONNECTED = {0: 'Not Connected', 1: 'Connected'}
LOCKED = {0: 'Unlocked', 1: 'Locked'}
PLUGGED = {0: 'Not Plugged In', 1: 'Plugged In'}
SILENT = {0: 'Ringer On', 1: 'Silent'}
# UIInterfaceOrientation (UIKit, UIApplication.h). Apple deliberately crosses the two
# landscape cases against UIDeviceOrientation, because rotating the device left rotates
# the interface right:
#     UIInterfaceOrientationLandscapeLeft  = UIDeviceOrientationLandscapeRight  (4)
#     UIInterfaceOrientationLandscapeRight = UIDeviceOrientationLandscapeLeft   (3)
# Do not copy the 3/4 labels from ORIENTATION in biomeDKEventStreams.py; they are opposite.
INTERFACE_ORIENTATION = {0: 'Unknown', 1: 'Portrait', 2: 'Portrait Upside Down',
                         3: 'Landscape Right', 4: 'Landscape Left'}


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None:
        return ''
    return str(value)


def _records(context, label, typess=None):
    typess = TYPESS if typess is None else typess
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
            ts = record.timestamp1.replace(tzinfo=timezone.utc)
            if record.state == EntryState.Written:
                try:
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, typess)
                except _DECODE_ERRORS as ex:
                    logfunc(f'{label}: could not decode record at offset '
                            f'{record.data_start_offset} in {filename}: {ex}')
                    continue
                yield ts, record, protostuff, filename
            elif record.state == EntryState.Deleted:
                yield ts, record, None, filename


def _parse_state(context, label, value_map):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Value', 'Value (raw)',
                    'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, label):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, filename,
                              record.data_start_offset))
            continue
        raw = protostuff.get('1', '')
        data_list.append((ts, record.state.name, value_map.get(raw, ''), raw, filename,
                          record.data_start_offset))
    return data_headers, data_list, 'see Filename for more info'


@artifact_processor
def get_biomeInterfaceOrientation(context):
    return _parse_state(context, 'Interface Orientation', INTERFACE_ORIENTATION)


@artifact_processor
def get_biomeLowPowerMode(context):
    return _parse_state(context, 'Low Power Mode', ON_OFF)


@artifact_processor
def get_biomeAirplaneModeWireless(context):
    return _parse_state(context, 'Airplane Mode', ON_OFF)


@artifact_processor
def get_biomeCellularDataEnabled(context):
    return _parse_state(context, 'Cellular Data Enabled', ENABLED)


@artifact_processor
def get_biomeCarPlayConnected(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'CarPlay State',
                    'State (raw)', 'Field 2 (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, 'CarPlay Connected'):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, filename,
                              record.data_start_offset))
            continue
        raw = protostuff.get('1', '')
        data_list.append((ts, record.state.name, CONNECTED.get(raw, ''), raw,
                          protostuff.get('2', ''), filename, record.data_start_offset))
    return data_headers, data_list, 'see Filename for more info'


@artifact_processor
def get_biomeBatteryTemperature(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Temperature (C)',
                    'Temperature (raw)', 'Field 2 (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, 'Battery Temperature'):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, filename,
                              record.data_start_offset))
            continue
        raw = protostuff.get('1', '')
        celsius = round(raw / 100, 2) if isinstance(raw, int) else ''
        data_list.append((ts, record.state.name, celsius, raw, protostuff.get('2', ''),
                          filename, record.data_start_offset))
    return data_headers, data_list, 'see Filename for more info'


@artifact_processor
def get_biomeScreenLocked(context):
    return _parse_state(context, 'Screen Locked', LOCKED)


@artifact_processor
def get_biomeKeybagLocked(context):
    return _parse_state(context, 'Keybag Locked', LOCKED)


@artifact_processor
def get_biomeBatteryLevel(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Battery Level (%)',
                    'Field 2 (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, 'Battery Level', BATTERY_TYPESS):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, filename,
                              record.data_start_offset))
            continue
        level = protostuff.get('1', '')
        if isinstance(level, float):
            level = round(level, 2)
        data_list.append((ts, record.state.name, level, protostuff.get('2', ''), filename,
                          record.data_start_offset))
    return data_headers, data_list, 'see Filename for more info'


@artifact_processor
def get_biomeDevicePluggedIn(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Power State', 'State (raw)',
                    'Field 2 (raw)', 'Field 3 (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, 'Device Plugged In',
                                                     PLUGGED_TYPESS):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, None, filename,
                              record.data_start_offset))
            continue
        raw = protostuff.get('1', '')
        data_list.append((ts, record.state.name, PLUGGED.get(raw, ''), raw,
                          protostuff.get('2', ''), protostuff.get('3', ''), filename,
                          record.data_start_offset))
    return data_headers, data_list, 'see Filename for more info'


@artifact_processor
def get_biomeSilentMode(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Ringer State', 'State (raw)',
                    'Reason', 'Field 2 (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, 'Silent Mode', SILENT_TYPESS):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, None, filename,
                              record.data_start_offset))
            continue
        raw = protostuff.get('1', '')
        data_list.append((ts, record.state.name, SILENT.get(raw, ''), raw,
                          _to_str(protostuff.get('4', b'')), protostuff.get('2', ''), filename,
                          record.data_start_offset))
    return data_headers, data_list, 'see Filename for more info'


@artifact_processor
def get_biomeEnergyMode(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Field 1 (raw)',
                    'Field 2 (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, 'Energy Mode'):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, filename,
                              record.data_start_offset))
            continue
        data_list.append((ts, record.state.name, protostuff.get('1', ''),
                          protostuff.get('2', ''), filename, record.data_start_offset))
    return data_headers, data_list, 'see Filename for more info'
