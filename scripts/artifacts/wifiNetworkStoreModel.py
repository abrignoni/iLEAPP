# Module Description: Parses Wifi details found in WiFiNetworkStoreModel database
# Author: @KevinPagano3
# Date: 2022-08-23
# Artifact version: 0.0.1
# Requirements: none

# Queries are derivitive of work provided by Heather Mahalik and Jared Barnhart as part of their SANS DFIR Summit 2022 talk
# https://for585.com/dfirsummit22
__artifacts_v2__ = {
     "get_wifiNetworkStoreModel": {
        "name": "Wifi Known Networkss",
        "description": "Parses Wifi details found in WiFiNetworkStoreModel database",
        "author": "@KevinPagano",
        "creation_date": "2022-08-23",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Network",
        "notes": "",
        "paths": ('*/root/Library/Application Support/WiFiNetworkStoreModel.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "wifi"
    }
}


from scripts.ilapfuncs import (
    open_sqlite_db_readonly,
    artifact_processor,
    convert_cocoa_core_data_ts_to_utc
    )


@artifact_processor
def get_wifiNetworkStoreModel(context):
    files_found = context.get_files_found()
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('WiFiNetworkStoreModel.sqlite'):
            break
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    ZGEOTAG.ZDATE AS "Last Connection Timestamp",
    ZNETWORK.Z_PK,
    ZNETWORK.ZSSID,
    ZGEOTAG.ZLATITUDE,
    ZGEOTAG.ZLONGITUDE,
    ZGEOTAG.ZBSSID,
    CASE ZGEOTAG.ZHIGHERBANDNETWORK
    WHEN 1 then 'Yes'
    ELSE ''
    END AS "5 GHz Network",
    CASE ZGEOTAG.ZLOWERBANDNETWORK
    WHEN 1 then 'Yes'
    ELSE ''
    END AS "2.4 GHz Network"
    FROM ZNETWORK
    LEFT JOIN ZGEOTAG ON ZGEOTAG.Z_PK = ZNETWORK.Z_PK
    ORDER BY "Last Connection Timestamp" DESC
    ''')
    data_headers = (
        ('Last Connection Timestamp', 'datetime'),
        'Record ID',
        'SSID',
        'Latitude',
        'Longitude',
        'BSSID',
        '5 GHz Network',
        '2.4 GHz Network'
        )

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        last_conn_time = convert_cocoa_core_data_ts_to_utc(row[0])
        data_list.append((
            last_conn_time,
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7]
            ))
    return data_headers, data_list, files_found[0]
