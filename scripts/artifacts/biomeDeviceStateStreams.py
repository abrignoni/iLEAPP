"""Biome device state streams that record a single value per event.

These streams are the modern, flat counterparts to the older _DKEvent.* wrappers
and coexist with them on the same device. Each record is a state transition
stamped with the SEGB record timestamp.
"""
__artifacts_v2__ = {
    "get_biomeInterfaceOrientation": {
        "name": "Biome - Interface Orientation",
        "description": "Parses interface orientation records from the "
                       "Device.Display.InterfaceOrientation biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Category is field 1 (category) of the BMDeviceInterfaceOrientation class, "
                 "read from BiomeLibrary.framework on macOS 27.2.1 (26B131), where the field's values are 0 Unknown, "
                 "1 Portrait and 2 Landscape; the iOS writer's schema was checked only against "
                 "the data. Only values 0, 1 and 2 were seen on the written records of the nine tested "
                 "images (records in the deleted SEGB state carry no value). Before, this artifact "
                 "labelled the values with UIKit's UIInterfaceOrientation, which named 2 Portrait "
                 "Upside Down and left 0 blank. The framework enumeration has one Landscape value, "
                 "so Category does not give the landscape side; see "
                 "Biome - Display Orientation DKEvent for the _DKEvent.Display.Orientation stream. "
                 "Stream reference: Mattia Epifani, '84 Streams Later, Part 2: Inside Apple "
                 "Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html"),
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
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "The Value column labels the stored value 0 as Off and 1 as On, as given in the "
                 "reference below. The raw value is reported alongside the label. Reference: "
                 "Mattia Epifani, '84 Streams Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html",
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
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "The Value column labels the stored value 0 as Off and 1 as "
                 "On, as given in the reference below. The raw value is "
                 "reported alongside the label. See also the "
                 "_DKEvent.System.AirplaneMode stream parsed by Biome - "
                 "Airplane Mode DKEvent. Reference: Mattia Epifani, '84 "
                 "Streams Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html",
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
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "The Value column labels the stored value 0 as Disabled and 1 as Enabled, as "
                 "given in the reference below. The raw value is reported alongside the label. "
                 "Reference: Mattia Epifani, '84 Streams Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html",
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
        "description": "Parses CarPlay connection records from the CarPlay.Connected "
                       "biome stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("The CarPlay State column labels the stored value 0 as Not "
                 "Connected and 1 as Connected; the BMCarPlayConnected class, read from BiomeLibrary.framework on macOS 27.2.1 (26B131), "
                 "names field 1 starting. Reason is field 2 (reason), named from the "
                 "same class: 0 Unknown, 1 USB, 2 WiFi; the iOS writer's schema was checked only "
                 "against the data. On hc_ios18_7 Reason held USB on all 24 rows; WiFi appeared on three tested images: abe_ios16 (4 rows), dexter_ios18 (4) and wilkerson_iphone16_ios26 (7). The raw values are reported alongside the labels. See "
                 "also the _DKEvent.Carplay.IsConnected stream parsed by Biome "
                 "- Carplay. Reference: Mattia Epifani, '84 Streams Later, "
                 "Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html"
                 " "
                 "On one tested iOS 16 image (abe_ios16) the stream is stored under CarPlay, which BiomeLibrary.framework on macOS 27.2.1 (26B131) lists as its legacy name, and is read too. The tested iOS 15 image held no such folder. Its 56 written records held fields 1 and 2."),
        "paths": ('*/streams/*/CarPlay.Connected/local/*', '*/streams/*/CarPlay/local/*'),
        "output_types": "standard",
        "artifact_icon": "truck",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | 122 rows",
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
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("The framework names field 1 temperature, an integer, and gives no unit. The "
                 "values fit hundredths of a degree Celsius, and Temperature (C) divides by 100 on "
                 "that reading. Observed range 600 to 4500 on the nine tested images (6.00 to "
                 "45.00 C on that reading); every written value was a multiple of 100. Both the "
                 "converted and raw values are reported. Plugged In is field 2, which the "
                 "BMDeviceBatteryTemperature class, read from BiomeLibrary.framework on macOS 27.2.1 (26B131), names "
                 "pluggedIn, a bool; the iOS writer's schema was checked only against the data."),
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
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Lock polarity compared with the _DKEvent.Device.IsLockedImputed stream "
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
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Biome",
        "notes": "Lock polarity compared with the _DKEvent.Keybag.IsLocked stream on the "
                 "same device: 124 of 128 overlapping records agree, the exceptions falling on "
                 "interval boundaries. See also that stream, parsed by "
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
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("The level is stored as a double; on the tested images it ranged from 1.0 to "
                 "100.0, which fits a percentage, and the BMDeviceBatteryLevel class, "
                 "read from BiomeLibrary.framework on macOS 27.2.1 (26B131), names it batteryPercentage. Fully Charged is "
                 "field 2 (fullyCharged), a bool in the same class; the iOS writer's schema was "
                 "checked only against the data. See also the _DKEvent.Device.BatteryPercentage "
                 "stream parsed by Biome - Battery Percentage."),
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
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Field names are those of the BMDevicePluggedIn class, read from BiomeLibrary.framework on macOS 27.2.1 (26B131): "
                 "1 starting, 2 wireless (a bool, reported in Wireless) and 3 adapterType, a "
                 "64-bit integer that the class prints as a number, with no enumeration found, "
                 "reported in Adapter Type "
                 "(raw); the iOS writer's schema was checked only against the data. On the nine "
                 "tested images every written record held fields 1, 2 and 3, plugged in or not; "
                 "deleted records carry no value. Ian Whiffin observed that records are written "
                 "for wireless charging as well as a cable connection; on the tested images "
                 "Wireless was True on one image. See also the "
                 "_DKEvent.Device.IsPluggedIn stream parsed by Biome - Device Plugged In. "
                 "Reference: Mattia Epifani, '84 Streams Later, Part 2: Inside Apple Biome', "
                 "https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html"),
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
        "description": "Parses energy mode records from the Device.Power.EnergyMode biome "
                       "stream.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Mode is field 1 (mode) and Reason is field 2 (reason) of the BMEnergyMode class, "
                 "read from BiomeLibrary.framework on macOS 27.2.1 (26B131). Mode values are 0 Unknown, 1 LowPower, "
                 "2 Normal, 3 HighPower. Reason values are 0 Unknown, 1 Settings, 2 "
                 "SiriShortcuts, 3 SpringBoardAlert, 4 ReenableBulletin, 5 ControlCenter, 6 "
                 "LostMode, 7 SystemDisable, 8 Workouts, 9 StandbyMode. The iOS writer's schema "
                 "was checked only against the data: on five tested images Mode held 1 or 2 and "
                 "Reason held 1, 3, 5, 6 or 7. The raw values are reported beside the names."),
        "paths": ('*/streams/*/Device.Power.EnergyMode/local/*',),
        "output_types": "standard",
        "artifact_icon": "zap",
        "sample_data": {
            "abe_ios16": "13 rows",
            "fsfull002_ios17": "2 rows, all deleted state",
            "hc_ios18_7": "11 rows, all deleted state",
            "iphone12_ios18": "13 rows",
            "magnet_ios16": "5 rows",
            "otto_ios17": "7 rows",
        },
    },
    "get_biomeSilentMode": {
        "name": "Biome - Silent Mode",
        "description": "Parses ringer and silent mode records from the "
                       "Device.SilentMode biome stream, including the reason string stored "
                       "with the record, reported as stored.",
        "author": "@abrignoni, @mattiaepi (Mattia Epifani)",
        "creation_date": "2026-07-25",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Biome",
        "notes": ("Ringer State labels the stored value 0 as Ringer On and 1 as Silent; the "
                 "BMDeviceSilentMode class names field 1 starting. Reasons observed include "
                 "RingerSwitchEvent and 'MXSessionManager startup HID ringer switch state'. Client "
                 "Type is field 2 (clientType) of the BMDeviceSilentMode "
                 "class, read from BiomeLibrary.framework on macOS 27.2.1 (26B131): 0 Unknown, 1 Springboard, 2 "
                 "ControlCenter, 3 FocusFilter, 4 Accessibility, 5 Gesture, 6 Shortcuts, 7 "
                 "Settings, 8 CarKitDaemon, 9 WidgetKitControl; the raw value is reported beside "
                 "the name, and the iOS writer's schema was checked only against the data. The "
                 "class also defines field 3 (untilTime); no tested written record held it, and "
                 "this artifact does not report it. On hc_ios18_7 Client Type (raw) equalled State "
                 "(raw) on all 10 written rows (the other 63 rows are deleted records with no "
                 "value); the two differed on other tested images, so they are kept apart."),
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
# Enum names read from BiomeLibrary.framework on macOS 27.2.1 (26B131), by building one-field
# records and reading each event's own description.
# BMDeviceInterfaceOrientation field 1 (category).
INTERFACE_ORIENTATION = {0: 'Unknown', 1: 'Portrait', 2: 'Landscape'}
# BMCarPlayConnected field 2 (reason).
CARPLAY_REASON = {0: 'Unknown', 1: 'USB', 2: 'WiFi'}
# BMDeviceSilentMode field 2 (clientType).
SILENT_CLIENT = {0: 'Unknown', 1: 'Springboard', 2: 'ControlCenter', 3: 'FocusFilter',
                 4: 'Accessibility', 5: 'Gesture', 6: 'Shortcuts', 7: 'Settings',
                 8: 'CarKitDaemon', 9: 'WidgetKitControl'}
# BMEnergyMode field 1 (mode) and field 2 (reason).
ENERGY_MODE = {0: 'Unknown', 1: 'LowPower', 2: 'Normal', 3: 'HighPower'}
ENERGY_REASON = {0: 'Unknown', 1: 'Settings', 2: 'SiriShortcuts', 3: 'SpringBoardAlert',
                 4: 'ReenableBulletin', 5: 'ControlCenter', 6: 'LostMode', 7: 'SystemDisable',
                 8: 'Workouts', 9: 'StandbyMode'}


def _bool(value):
    """A framework bool field: 1 True, 0 False, anything else blank."""
    return {1: 'True', 0: 'False'}.get(value, '') if isinstance(value, int) else ''


def _to_str(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', 'replace')
    if value is None:
        return ''
    return str(value)


def _stream_files(context):
    """Non-hidden, non-tombstone stream files from the artifact's matched paths."""
    for file_found in sorted(map(str, context.get_files_found())):
        if os.path.basename(file_found).startswith('.'):
            continue
        if not os.path.isfile(file_found) or 'tombstone' in context.get_relative_path(file_found):
            continue
        yield file_found


def _source_path(context):
    return '\n'.join(sorted({os.path.dirname(f) for f in _stream_files(context)}))


def _records(context, label, typess=None):
    typess = TYPESS if typess is None else typess
    for file_found in _stream_files(context):
        filename = os.path.basename(file_found)

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


def _parse_state(context, label, value_map, value_header='Value'):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', value_header,
                    f'{value_header} (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, label):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, filename,
                              record.data_start_offset))
            continue
        raw = protostuff.get('1', '')
        data_list.append((ts, record.state.name, value_map.get(raw, ''), raw, filename,
                          record.data_start_offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def get_biomeInterfaceOrientation(context):
    return _parse_state(context, 'Interface Orientation', INTERFACE_ORIENTATION, 'Category')


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
                    'State (raw)', 'Reason', 'Reason (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, 'CarPlay Connected'):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, None, filename,
                              record.data_start_offset))
            continue
        raw = protostuff.get('1', '')
        reason = protostuff.get('2', '')
        data_list.append((ts, record.state.name, CONNECTED.get(raw, ''), raw,
                          CARPLAY_REASON.get(reason, ''), reason, filename,
                          record.data_start_offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def get_biomeBatteryTemperature(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Temperature (C)',
                    'Temperature (raw)', 'Plugged In', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, 'Battery Temperature'):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, filename,
                              record.data_start_offset))
            continue
        raw = protostuff.get('1', '')
        celsius = round(raw / 100, 2) if isinstance(raw, int) else ''
        data_list.append((ts, record.state.name, celsius, raw, _bool(protostuff.get('2')),
                          filename, record.data_start_offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def get_biomeScreenLocked(context):
    return _parse_state(context, 'Screen Locked', LOCKED)


@artifact_processor
def get_biomeKeybagLocked(context):
    return _parse_state(context, 'Keybag Locked', LOCKED)


@artifact_processor
def get_biomeBatteryLevel(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Battery Level (%)',
                    'Fully Charged', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, 'Battery Level', BATTERY_TYPESS):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, filename,
                              record.data_start_offset))
            continue
        level = protostuff.get('1', '')
        if isinstance(level, float):
            level = round(level, 2)
        data_list.append((ts, record.state.name, level, _bool(protostuff.get('2')), filename,
                          record.data_start_offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def get_biomeDevicePluggedIn(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Power State', 'State (raw)',
                    'Wireless', 'Adapter Type (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, 'Device Plugged In',
                                                     PLUGGED_TYPESS):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, None, filename,
                              record.data_start_offset))
            continue
        raw = protostuff.get('1', '')
        data_list.append((ts, record.state.name, PLUGGED.get(raw, ''), raw,
                          _bool(protostuff.get('2')), protostuff.get('3', ''), filename,
                          record.data_start_offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def get_biomeSilentMode(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Ringer State', 'State (raw)',
                    'Reason', 'Client Type', 'Client Type (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, 'Silent Mode', SILENT_TYPESS):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, None, None, filename,
                              record.data_start_offset))
            continue
        raw = protostuff.get('1', '')
        client = protostuff.get('2', '')
        data_list.append((ts, record.state.name, SILENT.get(raw, ''), raw,
                          _to_str(protostuff.get('4', b'')), SILENT_CLIENT.get(client, ''), client,
                          filename, record.data_start_offset))
    return data_headers, data_list, _source_path(context)


@artifact_processor
def get_biomeEnergyMode(context):
    data_headers = (('SEGB Timestamp', 'datetime'), 'SEGB State', 'Mode', 'Mode (raw)', 'Reason',
                    'Reason (raw)', 'Filename', 'Offset')
    data_list = []
    for ts, record, protostuff, filename in _records(context, 'Energy Mode'):
        if protostuff is None:
            data_list.append((ts, record.state.name, None, None, None, None, filename,
                              record.data_start_offset))
            continue
        mode = protostuff.get('1', '')
        reason = protostuff.get('2', '')
        data_list.append((ts, record.state.name, ENERGY_MODE.get(mode, ''), mode,
                          ENERGY_REASON.get(reason, ''), reason, filename,
                          record.data_start_offset))
    return data_headers, data_list, _source_path(context)
