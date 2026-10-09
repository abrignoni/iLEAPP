""" batteryBDC """
__artifacts_v2__ = {
    "battery_bdc": {
        "name": "Battery Data Collection (BDC)",
        "description": "Parses battery usage and temps from Battery Data Collection (BDC) logs",
        "author": "@stark4n6, @AlexisBrignoni, Codex",
        "creation_date": "2026-03-18",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Battery",
        "notes": "Temperature scale: the stored Temperature value is centi-Celsius (Celsius x "
                 "100). Measured on 275 rows across BDC_SBC version 2.9 and 3.0 files from "
                 "two test images: dividing by 100 yields 21.7-37.2 C, consistent with an "
                 "operating device and rising while IsCharging is set, while a x1000 scale "
                 "would imply near-freezing temperatures. The reference below states Celsius "
                 "x 1000, which does not agree with this measurement. Each file's header row "
                 "is read: TimeStamp, CurrentCapacity, IsCharging, Temperature, Amperage, "
                 "Voltage and StateOfCharge are taken from the column carrying that exact "
                 "name, and from positions 1, 3, 4, 5, 6, 8 and 9 when the header does not "
                 "carry the name. Watts is read from position 19; the header name of that "
                 "column is not recorded here. On the abe_ios16 test file the seven names sit "
                 "at those positions. "
                 "Data rows too short to hold those columns are skipped with a diagnostic. "
                 "Reference: Kevin Pagano, 'BDC - More Battery Temps & Charging Stats for "
                 "iOS', "
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
        "description": "Battery identity fields (chemistry IDs, EEEE, YWW, design capacity, gas "
                       "gauge firmware) from BDC_Once logs, one row per file",
        "author": "@stark4n6, @ChrisJr404, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Battery",
        "notes": "One row per BDC_Once file. BatterySerialNumber is not reported by this "
                 "artifact. When the file is written is not sourced here. "
                 "GasGaugeFirmwareVersion is present in the files whose header carries it. "
                 "Columns are read by header name, so older narrower-schema files still parse.",
        "paths": ('*/Battery/BDC/BDC_Once_*.csv', '*/BatteryBDC/BDC_Once_*.csv'),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 2 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1 row"
        },
    },
    "battery_bdc_daily": {
        "name": "Battery Data Collection (BDC) - Daily",
        "description": "Daily battery health snapshots (capacity, cycle count) from BDC_Daily logs",
        "author": "@stark4n6, @ChrisJr404, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Battery",
        "notes": "NominalChargeCapacity and "
                 "DesignCapacity (from BDC_Once) are reported as stored; that their ratio is the "
                 "Maximum Capacity percentage shown in Settings is not sourced here. "
                 "TimeAtHighSoc is left as its raw hex token here; its encoding is not "
                 "established.",
        "paths": ('*/Battery/BDC/BDC_Daily_*.csv', '*/BatteryBDC/BDC_Daily_*.csv'),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | 53 rows",
            "iphone11_ios17": "iOS 17.3 | 601 rows",
            "hc_ios18_7": "iOS 18.7.8 | 288 rows"
        },
    },
    "battery_bdc_weekly": {
        "name": "Battery Data Collection (BDC) - Weekly",
        "description": "RaTableRaw0, TotalOperatingTime and gas gauge firmware version from "
                       "BDC_Weekly logs, reported as stored",
        "author": "@stark4n6, @ChrisJr404, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Battery",
        "notes": "Row cadence in tested files was one per seven days. RaTableRaw0 is left as its "
                 "raw hex token here; its encoding and meaning are not established.",
        "paths": ('*/Battery/BDC/BDC_Weekly_*.csv', '*/BatteryBDC/BDC_Weekly_*.csv'),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | 6 rows",
            "iphone11_ios17": "iOS 17.3 | 44 rows",
            "hc_ios18_7": "iOS 18.7.8 | 26 rows"
        },
    },
    "battery_bdc_obc": {
        "name": "Battery Data Collection (BDC) - OBC",
        "description": "External power and charging fields (FamilyCode, "
                       "ExternalConnected, ChargingOverride, NotChargingReason) from "
                       "BDC_OBC logs, one row per logged event",
        "author": "@stark4n6, @ChrisJr404, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Battery",
        "notes": "One row per logged event. FamilyCode is reported as stored and as a hex value; "
                 "its correspondence to IOKit adapter family codes is not sourced here. "
                 "NotChargingReason is reported as stored; the meaning of its values is not "
                 "established.",
        "paths": ('*/Battery/BDC/BDC_OBC_*.csv', '*/BatteryBDC/BDC_OBC_*.csv'),
        "output_types": "standard",
        "artifact_icon": "plug",
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | 11 rows",
            "iphone11_ios17": "iOS 17.3 | 228 rows",
            "hc_ios18_7": "iOS 18.7.8 | 315 rows"
        },
    },
    "battery_bdc_smartcharging": {
        "name": "Battery Data Collection (BDC) - SmartCharging",
        "description": "Charging state, charge limit and decision fields from "
                       "BDC_SmartCharging logs, reported as stored",
        "author": "@stark4n6, @ChrisJr404, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Battery",
        "notes": "One row per logged event. ChargeLimit and ChargingState are reported as "
                 "stored; their meaning is not sourced here. DecisionMaker was first seen in "
                 "tested files at schema "
                 "version 2.6, so columns are read by header name to stay aligned across versions.",
        "paths": ('*/Battery/BDC/BDC_SmartCharging_*.csv', '*/BatteryBDC/BDC_SmartCharging_*.csv'),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | 12 rows",
            "iphone11_ios17": "iOS 17.3 | 245 rows",
            "hc_ios18_7": "iOS 18.7.8 | 248 rows"
        },
    },
    "battery_bdc_cpmsrc": {
        "name": "Battery Data Collection (BDC) - CPMSRC",
        "description": "Impedance columns from BDC_CPMSRC logs, reported as stored; not "
                       "exercised on any tested image",
        "author": "@stark4n6, @ChrisJr404, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Battery",
        "notes": "Series resistance plus four RC branch columns, reported as stored. The CSV is "
                 "read as UTF-8. No tested image carries this file, so the cadence and column "
                 "meanings are not exercised. Parsing is header-driven; the source of the column "
                 "names is not recorded here.",
        "paths": ('*/Battery/BDC/BDC_CPMSRC_*.csv', '*/BatteryBDC/BDC_CPMSRC_*.csv'),
        "output_types": "standard",
        "artifact_icon": "activity",
    },
    "battery_bdc_timestamps": {
        "name": "Battery Data Collection (BDC) - Timestamps",
        "description": "System time and RTC tick pairs from BDC_Timestamps logs, reported as "
                       "stored",
        "author": "@stark4n6, @ChrisJr404, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Battery",
        "notes": "Each row pairs a system time with an RTC tick value as stored; what event "
                 "writes a row is not sourced here. The zone of the stored times is not "
                 "established here; they are passed as stored.",
        "paths": ('*/Battery/BDC/BDC_Timestamps_*.csv', '*/BatteryBDC/BDC_Timestamps_*.csv'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "iphone14plus_ios18": "iOS 18.0 | 2 rows",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 1 row"
        },
    },
}

import csv
import os
from scripts.ilapfuncs import artifact_processor, logfunc


# BDC_SBC header names with the zero-based position used when a header lacks the name.
_SBC_COLUMNS = (('timestamp', 0), ('currentcapacity', 2), ('ischarging', 3),
                ('temperature', 4), ('amperage', 5), ('voltage', 7), ('stateofcharge', 8))


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
            header = next(delimited, None)
            if header is None:
                continue
            normed = [h.strip().lower() for h in header]
            # Exact header name where the file carries it, else the fixed position.
            (i_ts, i_cap, i_chg, i_temp, i_amp, i_volt, i_soc) = [
                normed.index(name) if name in normed else position
                for name, position in _SBC_COLUMNS]
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
                if len(item) < 9:
                    logfunc(
                        f"Skipping BDC data row: expected at least 9 columns, "
                        f"found {len(item)}"
                    )
                    continue
                if len(item) <= max(i_ts, i_cap, i_chg, i_temp, i_amp, i_volt, i_soc):
                    logfunc(
                        f"Skipping BDC data row: named columns not present, "
                        f"found {len(item)} columns"
                    )
                    continue
                timestamp = item[i_ts]
                current_cap = item[i_cap]
                is_charging = int(item[i_chg])
                if is_charging == 0:
                    charging_status = 'No'
                elif is_charging == 1:
                    charging_status = 'Yes'
                else:
                    charging_status = is_charging
                temp = round(float(item[i_temp]) / 100 * 1.8 + 32, 3)
                temp2 = float(item[i_temp]) / 100
                amperage = item[i_amp]
                voltage = item[i_volt]
                soc = item[i_soc]
                watts = _col(item, 18)

                data_list.append((
                    timestamp, soc, current_cap, charging_status, temp, temp2,
                    amperage, voltage, watts, context.get_relative_path(file_found),
                ))

    data_headers = (
        'Timestamp (as stored, no zone recorded)',
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
        'Timestamp (as stored, no zone recorded)',
        'Chem ID',
        'Algo Chem ID',
        'EEEE (as stored)',
        'YWW (as stored)',
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
        'Timestamp (as stored, no zone recorded)',
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
        'Timestamp (as stored, no zone recorded)',
        'Ra Table Raw0',
        'Total Operating Time (as stored)',
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
        'Timestamp (as stored, no zone recorded)',
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
        'Timestamp (as stored, no zone recorded)',
        'Charging State',
        'Inflow State',
        'Charge Limit (as stored)',
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
        'Timestamp (as stored, no zone recorded)',
        'R0 + Rtrace (as stored)',
        'R1 (as stored)',
        'R2 (as stored)',
        'R3 (as stored)',
        'R4 (as stored)',
        'RC Freq1 (as stored)',
        'RC Freq2 (as stored)',
        'RC Freq3 (as stored)',
        'RC Freq4 (as stored)',
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
        'Reference System Time (as stored)',
        'Set System Time (as stored)',
        'Reference RTC Ticks',
        'Current RTC Ticks',
        'Source File',
    )
    return data_headers, data_list, _source_dirs(context)
