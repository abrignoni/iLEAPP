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
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "Value follows the UIInterfaceOrientation enumeration; the raw value is "
                 "reported alongside the label.",
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
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "Modern counterpart of the _DKEvent.System.AirplaneMode stream parsed by "
                 "Biome - Airplane Mode DKEvent.",
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
        "last_update_date": "2026-07-25",
        "requirements": "none",
        "category": "Biome",
        "notes": "Modern counterpart of the _DKEvent.Carplay.IsConnected stream parsed by "
                 "Biome - Carplay.",
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
}


import os
from datetime import timezone

from scripts import blackboxprotobuf
from scripts.ccl_segb.ccl_segb import read_segb_file
from scripts.ccl_segb.ccl_segb_common import EntryState
from scripts.ilapfuncs import artifact_processor, logfunc

TYPESS = {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}

ON_OFF = {0: 'Off', 1: 'On'}
ENABLED = {0: 'Disabled', 1: 'Enabled'}
CONNECTED = {0: 'Not Connected', 1: 'Connected'}
INTERFACE_ORIENTATION = {0: 'Unknown', 1: 'Portrait', 2: 'Portrait Upside Down',
                         3: 'Landscape Left', 4: 'Landscape Right'}


def _records(context, label):
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
                    protostuff, _ = blackboxprotobuf.decode_message(record.data, TYPESS)
                except Exception as ex:
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
