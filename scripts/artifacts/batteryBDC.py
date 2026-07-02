""" batteryBDC """
__artifacts_v2__ = {
    "battery_bdc": {
        "name": "Battery Data Collection (BDC)",
        "description": "Parses battery usage and temps from Battery Data Collection (BDC) logs",
        "author": "@stark4n6",
        "creation_date": "2026-03-18",
        "last_update_date": "2026-05-27",
        "requirements": "none",
        "category": "Battery",
        "notes": "",
        "paths": ('*/Battery/BDC/BDC_SBC_*.csv'),
        "output_types": "standard",
        "artifact_icon": "battery-charging"
    }
}

import csv
from scripts.ilapfuncs import artifact_processor, logfunc


def _col(row, index, default=''):
    return row[index] if len(row) > index else default


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
    return data_headers, data_list, 'See source path(s) below'
