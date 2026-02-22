# Module Description: Parses Wifi details found in WiFiNetworkStoreModel database
# Author: @KevinPagano3
# Date: 2022-08-23
# Artifact version: 0.0.1
# Requirements: none

# Queries are derivitive of work provided by Heather Mahalik and Jared Barnhart as part of their SANS DFIR Summit 2022 talk
# https://for585.com/dfirsummit22

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_wifiNetworkStoreModel(files_found, report_folder, seeker, wrap_text, timezone_offset):
    file_found = str(files_found[0])
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('WiFiNetworkStoreModel.sqlite'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    DATETIME(ZGEOTAG.ZDATE+978307200,'unixepoch') AS "Last Connection Timestamp",
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

    all_rows = cursor.fetchall()
    data_list = []

    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

    db.close()

    data_headers = ('Last Connected Timestamp', 'PK', 'SSID', 'Latitude', 'Longitude', 'BSSID', '5 GHz Network', '2.4 GHz Network')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_wifiNetworkStoreModel": {
        "name": "Wifi Network Store Model",
        "description": "",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "date": "2022-08-23",
        "requirements": "none",
        "category": "Wifi Known Networks",
        "notes": "",
        "paths": ('*/root/Library/Application Support/WiFiNetworkStoreModel.sqlite*',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
