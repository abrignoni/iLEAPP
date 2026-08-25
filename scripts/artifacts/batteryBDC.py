""" batteryBDC """
__artifacts_v2__ = {
    "battery_bdc": {
        "name": "Battery Data Collection (BDC)",
        "description": "Parses battery usage and temps from Battery Data Collection (BDC) logs",
        "author": "@stark4n6",
        "creation_date": "2026-03-18",
        "last_update_date": "2026-08-21",
        "requirements": "none",
        "category": "Battery",
        "notes": "Temperature scale: the stored Temperature value is centi-Celsius (Celsius x "
                 "100). Validated against 275 rows across BDC_SBC version 2.9 and 3.0 files "
                 "from two test images: dividing by 100 yields 21.7-37.2 C, consistent with "
                 "an operating device and rising while IsCharging is set, while a x1000 scale "
                 "would imply near-freezing temperatures. The reference below states Celsius "
                 "x 1000, which this testing indicates is a typo. The CSV header row in the "
                 "files matches the column positions parsed here. "
                 "Reference: Kevin Pagano, 'BDC - More Battery Temps & Charging Stats', "
                 "https://www.stark4n6.com/2026/03/bdc-more-battery-temps-charging-stats.html",
        "paths": ('*/Battery/BDC/BDC_SBC_*.csv', '*/BatteryBDC/BDC_SBC_*.csv'),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "dexter_ios18": "iOS 18.3.2 | 2942 rows",
            "felix_ios17": "iOS 17.6.1 | 1479 rows",
            "fsfull002_ios17": "iOS 17.1 | 1744 rows",
            "hc_ios18_7": "iOS 18.7.8 | 3069 rows",
            "iphone11_ios17": "iOS 17.3 | 7599 rows",
            "iphone12_ios18": "iOS 18.7 | 688 rows",
            "iphone14plus_ios18": "iOS 18.0 | 393 rows",
            "otto_ios17": "iOS 17.5.1 | 3121 rows",
            "abe_ios16": "iOS 16.5 | 5221 rows",
            "felix23_ios16": "iOS 16.5 | 2154 rows",
            "jess_ios15": "iOS 15.0.2 | 550 rows",
            "magnet_ios16": "iOS 16.1.1 | 807 rows",
        }
    },
    "battery_bdc_once": {
        "name": "Battery Data Collection (BDC) - Once",
        "description": "Static battery identity written once per battery pack from BDC_Once logs",
        "author": "@stark4n6, @ChrisJr404",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "none",
        "category": "Battery",
        "notes": "One row per battery pack (first boot with a new pack, or after a data reset). "
                 "A new BatterySerialNumber and a fresh BDC_Once file signal a battery "
                 "replacement. GasGaugeFirmwareVersion appears from schema version 1.7. "
                 "Columns are read by header name, so older narrower-schema files still parse.",
        "paths": ('*/Battery/BDC/BDC_Once_*.csv', '*/BatteryBDC/BDC_Once_*.csv'),
        "output_types": "standard",
        "artifact_icon": "battery",
    },
    "battery_bdc_daily": {
        "name": "Battery Data Collection (BDC) - Daily",
        "description": "Daily battery health snapshots (capacity, cycle count) from BDC_Daily logs",
        "author": "@stark4n6, @ChrisJr404",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "none",
        "category": "Battery",
        "notes": "Roughly two rows per day. NominalChargeCapacity over DesignCapacity (from "
                 "BDC_Once) gives the user-visible Maximum Capacity percentage. TimeAtHighSoc "
                 "is a little-endian uint32 blob left as its raw hex token here.",
        "paths": ('*/Battery/BDC/BDC_Daily_*.csv', '*/BatteryBDC/BDC_Daily_*.csv'),
        "output_types": "standard",
        "artifact_icon": "battery",
    },
    "battery_bdc_weekly": {
        "name": "Battery Data Collection (BDC) - Weekly",
        "description": "Weekly gauge resistance table and operating time from BDC_Weekly logs",
        "author": "@stark4n6, @ChrisJr404",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "none",
        "category": "Battery",
        "notes": "One row every seven days. RaTableRaw0 is the raw Impedance Track Ra table "
                 "(big-endian uint16 words) left as its raw hex token here; rising values "
                 "over months indicate cell aging.",
        "paths": ('*/Battery/BDC/BDC_Weekly_*.csv', '*/BatteryBDC/BDC_Weekly_*.csv'),
        "output_types": "standard",
        "artifact_icon": "battery",
    },
    "battery_bdc_obc": {
        "name": "Battery Data Collection (BDC) - OBC",
        "description": "On-charger and external power transition events from BDC_OBC logs",
        "author": "@stark4n6, @ChrisJr404",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "none",
        "category": "Battery",
        "notes": "Event driven, one row per attach/detach/charge-state change. FamilyCode is a "
                 "signed 32-bit IOPS adapter family code; the hex column recovers the "
                 "0xE0004xxx form used by IOKit. NotChargingReason is a bitmask (0 means "
                 "charging normally).",
        "paths": ('*/Battery/BDC/BDC_OBC_*.csv', '*/BatteryBDC/BDC_OBC_*.csv'),
        "output_types": "standard",
        "artifact_icon": "plug",
    },
    "battery_bdc_smartcharging": {
        "name": "Battery Data Collection (BDC) - SmartCharging",
        "description": "Optimized Battery Charging policy decisions from BDC_SmartCharging logs",
        "author": "@stark4n6, @ChrisJr404",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "none",
        "category": "Battery",
        "notes": "Event driven. ChargeLimit drops to 80 when the 80 percent hold is engaged, and "
                 "ChargingState 0 marks a paused/held charge. DecisionMaker was added in schema "
                 "version 2.6, so columns are read by header name to stay aligned across versions.",
        "paths": ('*/Battery/BDC/BDC_SmartCharging_*.csv', '*/BatteryBDC/BDC_SmartCharging_*.csv'),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
    },
    "battery_bdc_cpmsrc": {
        "name": "Battery Data Collection (BDC) - CPMSRC",
        "description": "Battery RC equivalent-circuit impedance model from BDC_CPMSRC logs",
        "author": "@stark4n6, @ChrisJr404",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "none",
        "category": "Battery",
        "notes": "Daily cadence. Series resistance plus four RC branches (fast to slow time "
                 "constants). Header units read as mojibake when the file is decoded as "
                 "Latin-1, so the CSV is read as UTF-8. Not present in the local test images, "
                 "so parsing is header-driven off the documented column names.",
        "paths": ('*/Battery/BDC/BDC_CPMSRC_*.csv', '*/BatteryBDC/BDC_CPMSRC_*.csv'),
        "output_types": "standard",
        "artifact_icon": "activity",
    },
    "battery_bdc_timestamps": {
        "name": "Battery Data Collection (BDC) - Timestamps",
        "description": "RTC-to-wall-clock set events for time reconstruction from BDC_Timestamps logs",
        "author": "@stark4n6, @ChrisJr404",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "none",
        "category": "Battery",
        "notes": "Each row records a system-clock set event against the monotonic RTC tick "
                 "counter, which is forensically useful for spotting power-loss events, battery "
                 "pulls and clock changes. Times are UTC.",
        "paths": ('*/Battery/BDC/BDC_Timestamps_*.csv', '*/BatteryBDC/BDC_Timestamps_*.csv'),
        "output_types": "standard",
        "artifact_icon": "clock",
    },
}

import csv
import os
from scripts.ilapfuncs import artifact_processor, logfunc


def _col(row, index, default=''):
    return row[index] if len(row) > index else default


def _header_index(header, key):
    """Index of the column whose (normalized) name equals or starts with key, else None."""
    key = key.strip().lower()
    normed = [h.strip().lower() for h in header]
    if key in normed:
        return normed.index(key)
    for i, name in enumerate(normed):
        if name.startswith(key):
            return i
    return None


def _resolve(header, keys):
    return [_header_index(header, k) for k in keys]


def _values(row, indices):
    return [row[i] if (i is not None and i < len(row)) else '' for i in indices]


def _source_dirs(context):
    """Newline-joined directories of the files this artifact matched."""
    return '\n'.join(sorted({os.path.dirname(str(f)) for f in context.get_files_found()}))


def _iter_bdc_files(context):
    """Yield (relative_source, header, remaining_rows) for each BDC CSV, header row skipped."""
    for file_found in context.get_files_found():
        file_found = str(file_found)
        with open(file_found, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')
            header = next(reader, None)
            if header is None:
                continue
            source = context.get_relative_path(file_found)
            yield source, header, reader


def _simple_stream(context, keys):
    """Resolve keys by header name for every file and flatten rows, appending the source path."""
    data_list = []
    for source, header, reader in _iter_bdc_files(context):
        indices = _resolve(header, keys)
        for row in reader:
            data_list.append((*_values(row, indices), source))
    return data_list


@artifact_processor
def battery_bdc(context):
    """
    Processes battery data from Battery Data Collection (BDC) logs
    """

    data_list = []
    files_found = context.get_files_found()

    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, 'r', encoding='utf-8') as f:
            delimited = csv.reader(f, delimiter=',')
            next(delimited, None)
            try:
                first_row = next(delimited)
            except StopIteration:
                continue
            if len(first_row) < 9:
                logfunc(
                    f"Skipping {file_found}: expected at least 9 columns, "
                    f"found {len(first_row)}"
                )
                continue

            for item in (first_row, *delimited):
                timestamp = item[0]
                current_cap = item[2]
                is_charging = int(item[3])
                if is_charging == 0:
                    charging_status = 'No'
                elif is_charging == 1:
                    charging_status = 'Yes'
                else:
                    charging_status = is_charging
                temp = round(float(item[4]) / 100 * 1.8 + 32, 3)
                temp2 = float(item[4]) / 100
                amperage = item[5]
                voltage = item[7]
                soc = item[8]
                watts = _col(item, 18)

                data_list.append((
                    timestamp, soc, current_cap, charging_status, temp, temp2,
                    amperage, voltage, watts, context.get_relative_path(file_found),
                ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'UI Displayed Capacity (%)',
        'Raw Battery Capacity (%)',
        'Is Charging',
        'Temperature (F)',
        'Temperature (C)',
        'Amperage (mA)',
        'Voltage (mV)',
        'Watts',
        'Source File',
    )
    return data_headers, data_list, _source_dirs(context)


@artifact_processor
def battery_bdc_once(context):
    """Static per-battery identity from BDC_Once logs"""
    keys = ['TimeStamp', 'ChemID', 'AlgoChemID', 'EEEE', 'YWW',
            'DesignCapacity', 'GasGaugeFirmwareVersion']
    data_list = _simple_stream(context, keys)
    data_headers = (
        ('Timestamp', 'datetime'),
        'Chem ID',
        'Algo Chem ID',
        'EEEE (Factory Code)',
        'YWW (Mfr Date Code)',
        'Design Capacity (mAh)',
        'Gas Gauge Firmware Version',
        'Source File',
    )
    return data_headers, data_list, _source_dirs(context)


@artifact_processor
def battery_bdc_daily(context):
    """Daily battery health snapshots from BDC_Daily logs"""
    keys = ['TimeStamp', 'WeightedRa', 'Qmax0', 'CycleCount', 'NominalChargeCapacity',
            'TimeAtHighSoc', 'ChargingVoltage', 'BHServiceFlags', 'BHCalibrationFlags']
    data_list = _simple_stream(context, keys)
    data_headers = (
        ('Timestamp', 'datetime'),
        'Weighted Ra',
        'Qmax0 (mAh)',
        'Cycle Count',
        'Nominal Charge Capacity (mAh)',
        'Time At High SoC',
        'Charging Voltage (mV)',
        'BH Service Flags',
        'BH Calibration Flags',
        'Source File',
    )
    return data_headers, data_list, _source_dirs(context)


@artifact_processor
def battery_bdc_weekly(context):
    """Weekly gauge resistance table from BDC_Weekly logs"""
    keys = ['TimeStamp', 'RaTableRaw0', 'TotalOperatingTime', 'GasGaugeFirmwareVersion']
    data_list = _simple_stream(context, keys)
    data_headers = (
        ('Timestamp', 'datetime'),
        'Ra Table Raw0',
        'Total Operating Time (hrs)',
        'Gas Gauge Firmware Version',
        'Source File',
    )
    return data_headers, data_list, _source_dirs(context)


@artifact_processor
def battery_bdc_obc(context):
    """On-charger / external power events from BDC_OBC logs"""
    keys = ['TimeStamp', 'FamilyCode', 'ExternalConnected', 'AppleRawExternalConnected',
            'ChargingOverride', 'NotChargingReason', 'VacVoltageLimit']
    data_list = []
    for source, header, reader in _iter_bdc_files(context):
        indices = _resolve(header, keys)
        for row in reader:
            vals = _values(row, indices)
            family = vals[1]
            family_hex = ''
            try:
                fc = int(family)
                if fc < 0:
                    fc += 2 ** 32
                family_hex = f'0x{fc:08X}'
            except (ValueError, TypeError):
                family_hex = ''
            data_list.append((
                vals[0], vals[1], family_hex, vals[2], vals[3], vals[4], vals[5], vals[6],
                source,
            ))
    data_headers = (
        ('Timestamp', 'datetime'),
        'Family Code',
        'Family Code (Hex)',
        'External Connected',
        'Apple Raw External Connected',
        'Charging Override',
        'Not Charging Reason',
        'Vac Voltage Limit (mV)',
        'Source File',
    )
    return data_headers, data_list, _source_dirs(context)


@artifact_processor
def battery_bdc_smartcharging(context):
    """Optimized Battery Charging policy decisions from BDC_SmartCharging logs"""
    keys = ['TimeStamp', 'ChargingState', 'InflowState', 'ChargeLimit', 'CheckPoint',
            'DecisionMaker', 'ModeOfOperation']
    data_list = _simple_stream(context, keys)
    data_headers = (
        ('Timestamp', 'datetime'),
        'Charging State',
        'Inflow State',
        'Charge Limit (%)',
        'Check Point',
        'Decision Maker',
        'Mode Of Operation',
        'Source File',
    )
    return data_headers, data_list, _source_dirs(context)


@artifact_processor
def battery_bdc_cpmsrc(context):
    """Battery RC equivalent-circuit impedance model from BDC_CPMSRC logs"""
    keys = ['TimeStamp', 'ImpedanceR0PlusRtrace', 'ImpedanceR1', 'ImpedanceR2',
            'ImpedanceR3', 'ImpedanceR4', 'ImpedanceRCFreq1', 'ImpedanceRCFreq2',
            'ImpedanceRCFreq3', 'ImpedanceRCFreq4']
    data_list = _simple_stream(context, keys)
    data_headers = (
        ('Timestamp', 'datetime'),
        'R0 + Rtrace (mOhm)',
        'R1 (mOhm)',
        'R2 (mOhm)',
        'R3 (mOhm)',
        'R4 (mOhm)',
        'RC Freq1 (Hz)',
        'RC Freq2 (Hz)',
        'RC Freq3 (Hz)',
        'RC Freq4 (Hz)',
        'Source File',
    )
    return data_headers, data_list, _source_dirs(context)


@artifact_processor
def battery_bdc_timestamps(context):
    """RTC-to-wall-clock set events from BDC_Timestamps logs"""
    keys = ['reference_system_time', 'set_system_time',
            'reference_rtc_ticks', 'current_rtc_ticks']
    data_list = _simple_stream(context, keys)
    data_headers = (
        ('Reference System Time', 'datetime'),
        ('Set System Time', 'datetime'),
        'Reference RTC Ticks',
        'Current RTC Ticks',
        'Source File',
    )
    return data_headers, data_list, _source_dirs(context)
