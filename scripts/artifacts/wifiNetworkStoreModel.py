# Module Description: Parses Wifi details found in WiFiNetworkStoreModel database
# Author: @KevinPagano3
# Date: 2022-08-23
# Artifact version: 0.0.1
# Requirements: none

# Queries are derivitive of work provided by Heather Mahalik and Jared Barnhart as part of their SANS DFIR Summit 2022 talk
# https://for585.com/dfirsummit22

import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_wifiNetworkStoreModel(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
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
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

        report = ArtifactHtmlReport('Wifi Network Store Model - Networks')
        report.start_artifact_report(report_folder, 'Wifi Network Store Model - Networks')
        report.add_script()
        data_headers = ('Last Connected Timestamp', 'PK', 'SSID', 'Latitude', 'Longitude', 'BSSID', '5 GHz Network', '2.4 GHz Network')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Wifi Network Store Model - Networks'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Wifi Network Store Model - Networks'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Wifi Network Store Model - Networks data available')

    db.close()
    return

__artifacts__ = {
    "wifiNetworkStoreModel": (
        "Wifi Known Networks",
        ('*/root/Library/Application Support/WiFiNetworkStoreModel.sqlite*'),
        get_wifiNetworkStoreModel)
}