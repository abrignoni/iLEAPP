__artifacts_v2__ = {
    "ConnectedDeviceInformation_DeviceHistory": {
        "name": "Connected Device Information - Connected Device and OS History",
        "description": "Connected Devices",
        "author": "@SQLMcGee",
        "version": "0.1",
        "date": "2025-01-30",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Queries from reserach conducted by Metadata Forensics, LLC\
        Apple product identification, common name, OS, and timeframe of use",
        "paths": ('*Health/healthdb_secure.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "smartphone"
    },
    "ConnectedDeviceInformation_ConsolidatedConnectedDeviceHistory": {
        "name": "Connected Device Information - Consolidated Connected Device History",
        "description": "Connected Devices",
        "author": "@SQLMcGee",
        "version": "0.1",
        "date": "2025-01-30",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Queries from reserach conducted by Metadata Forensics, LLC\
        Apple product grouped for starting and ending timeframe of use",
        "paths": ('*Health/healthdb_secure.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "smartphone"
    },
     "ConnectedDeviceInformation_CurrentDeviceInfo": {
        "name": "Connected Device Information - Current Device Information",
        "description": "Connected Devices",
        "author": "@SQLMcGee",
        "version": "0.1",
        "date": "2025-01-30",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Queries from reserach conducted by Metadata Forensics, LLC\
        Current Apple Device and OS Information",
        "paths": ('*Health/healthdb.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "smartphone"
    }
}

import scripts.artifacts.artGlobals

from packaging import version
from scripts.builds_ids import OS_build, device_id
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_ts_human_to_timezone_offset

@artifact_processor
def ConnectedDeviceInformation_DeviceHistory(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    healthdb_secure = ''

    for file_found in files_found:
        if file_found.endswith('healthdb_secure.sqlite'):
           healthdb_secure = file_found
        else:
            continue

    with open_sqlite_db_readonly(healthdb_secure) as db:
        cursor = db.cursor()

        cursor.execute('''
        SELECT
        MIN(datetime(objects.creation_date + 978307200, 'UNIXEPOCH')) AS "Start Date",
        MAX(datetime(objects.creation_date + 978307200, 'UNIXEPOCH')) AS "End Date",
        data_provenances.origin_product_type AS 'Product Origin (Common Name)',
        data_provenances.origin_product_type AS "Origin Product",
        source_id AS "Source ID",
        source_version AS "iOS / WatchOS Version"
        FROM objects
        LEFT OUTER JOIN data_provenances ON objects.provenance = data_provenances.ROWID
        WHERE 
        (
        data_provenances.origin_product_type LIKE 'iPhone17%' --iPhone 16
        )
        AND source_version IN ('18.0', '18.0.1', '18.1', '18.1.1', '18.2', '18.2.1', '18.3')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone15,4' -- iPhone 15
        OR data_provenances.origin_product_type LIKE 'iPhone15,5'
        OR data_provenances.origin_product_type LIKE 'iPhone16,1'
        OR data_provenances.origin_product_type LIKE 'iPhone16,2'
        )
        AND source_version IN ('17.0', '17.0.1', '17.0.2', '17.0.3', '17.1', '17.1.1', '17.1.2', '17.2', '17.2.1', '17.3', '17.3.1', '17.4', '17.4.1', '17.5', '17.5.1', '17.6', '17.6.1', '17.7', '17.7.1', '17.7.2', '17.7.3', '17.7.4', 
        '18.0', '18.0.1', '18.1', '18.1.1', '18.2', '18.2.1', '18.3')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone14,7' -- iPhone 14
        OR data_provenances.origin_product_type LIKE 'iPhone14,8'
        OR data_provenances.origin_product_type LIKE 'iPhone15,2'
        OR data_provenances.origin_product_type LIKE 'iPhone15,3'
        )
        AND source_version IN ('16.0', '16.0.1', '16.0.2', '16.0.3', '16.1', '16.1.1', '16.1.2', '16.2', '16.3', '16.3.1', '16.4', '16.4.1', '16.5', '16.5.1', '16.6', '16.6.1', '16.7', '16.7.1', '16.7.2', '16.7.3', '16.7.4', '16.7.5', '16.7.6', '16.7.7', '16.7.8', '16.7.9', '16.7.10',
        '17.0', '17.0.1', '17.0.2', '17.0.3', '17.1', '17.1.1', '17.1.2', '17.2', '17.2.1', '17.3', '17.3.1', '17.4', '17.4.1', '17.5', '17.5.1', '17.6', '17.6.1', '17.7', '17.7.1', '17.7.2', '17.7.3', '17.7.4', 
        '18.0', '18.0.1', '18.1', '18.1.1', '18.2', '18.2.1', '18.3')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone14,4' -- iPhone 13 and iPhone SE 3rd  Gen
        OR data_provenances.origin_product_type LIKE 'iPhone14,5'
        OR data_provenances.origin_product_type LIKE 'iPhone14,2'
        OR data_provenances.origin_product_type LIKE 'iPhone14,3'
        OR data_provenances.origin_product_type LIKE 'iPhone14,6'
        )
        AND source_version IN ('15.0', '15.0.1', '15.0.2', '15.0.3', '15.1', '15.1.1', '15.2', '15.2.1', '15.3', '15.3.1', '15.4', '15.4.1', '15.5', '15.6', '15.6.1', '15.7', '15.7.1', '15.7.2', '15.7.3', '15.7.4', '15.7.5', '15.7.6',  '15.7.7', '15.7.8', '15.7.9', '15.8', '15.8.1', '15.8.2', '15.8.3',
        '16.0', '16.0.1', '16.0.2', '16.0.3', '16.1', '16.1.1', '16.1.2', '16.2', '16.3', '16.3.1', '16.4', '16.4.1', '16.5', '16.5.1', '16.6', '16.6.1', '16.7', '16.7.1', '16.7.2', '16.7.3', '16.7.4', '16.7.5', '16.7.6', '16.7.7', '16.7.8', '16.7.9', '16.7.10',
        '17.0', '17.0.1', '17.0.2', '17.0.3', '17.1', '17.1.1', '17.1.2', '17.2', '17.2.1', '17.3', '17.3.1', '17.4', '17.4.1', '17.5', '17.5.1', '17.6', '17.6.1', '17.7', '17.7.1', '17.7.2', '17.7.3', '17.7.4', 
        '18.0', '18.0.1', '18.1', '18.1.1', '18.2', '18.2.1', '18.3')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone13%' -- iPhone 12
        )
        AND source_version IN ('14.0', '14.0.1', '14.1', '14.2', '14.2.1', '14.3', '14.4', '14.4.1', '14.4.2', '14.5', '14.5.1', '14.6', '14.7', '14.7.1', '14.8', '14.8.1', 
        '15.0', '15.0.1', '15.0.2', '15.0.3', '15.1', '15.1.1', '15.2', '15.2.1', '15.3', '15.3.1', '15.4', '15.4.1', '15.5', '15.6', '15.6.1', '15.7', '15.7.1', '15.7.2', '15.7.3', '15.7.4', '15.7.5', '15.7.6',  '15.7.7', '15.7.8', '15.7.9', '15.8', '15.8.1', '15.8.2', '15.8.3',
        '16.0', '16.0.1', '16.0.2', '16.0.3', '16.1', '16.1.1', '16.1.2', '16.2', '16.3', '16.3.1', '16.4', '16.4.1', '16.5', '16.5.1', '16.6', '16.6.1', '16.7', '16.7.1', '16.7.2', '16.7.3', '16.7.4', '16.7.5', '16.7.6', '16.7.7', '16.7.8', '16.7.9', '16.7.10',
        '17.0', '17.0.1', '17.0.2', '17.0.3', '17.1', '17.1.1', '17.1.2', '17.2', '17.2.1', '17.3', '17.3.1', '17.4', '17.4.1', '17.5', '17.5.1', '17.6', '17.6.1', '17.7', '17.7.1', '17.7.2', '17.7.3', '17.7.4', 
        '18.0', '18.0.1', '18.1', '18.1.1', '18.2', '18.2.1', '18.3')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone12%' -- iPhone 11 and iPhone SE 2nd Gen
        )
        AND source_version IN ('13.0', '13.1', '13.1.1', '13.1.2', '13.1.3', '13.2', '13.2.1', '13.2.2', '13.2.3', '13.3', '13.3.1', '13.4', '13.4.1', '13.5', '13.5.1', '13.6', '13.6.1', '13.7',
        '14.0', '14.0.1', '14.1', '14.2', '14.2.1', '14.3', '14.4', '14.4.1', '14.4.2', '14.5', '14.5.1', '14.6', '14.7', '14.7.1', '14.8', '14.8.1', 
        '15.0', '15.0.1', '15.0.2', '15.0.3', '15.1', '15.1.1', '15.2', '15.2.1', '15.3', '15.3.1', '15.4', '15.4.1', '15.5', '15.6', '15.6.1', '15.7', '15.7.1', '15.7.2', '15.7.3', '15.7.4', '15.7.5', '15.7.6',  '15.7.7', '15.7.8', '15.7.9', '15.8', '15.8.1', '15.8.2', '15.8.3',
        '16.0', '16.0.1', '16.0.2', '16.0.3', '16.1', '16.1.1', '16.1.2', '16.2', '16.3', '16.3.1', '16.4', '16.4.1', '16.5', '16.5.1', '16.6', '16.6.1', '16.7', '16.7.1', '16.7.2', '16.7.3', '16.7.4', '16.7.5', '16.7.6', '16.7.7', '16.7.8', '16.7.9', '16.7.10',
        '17.0', '17.0.1', '17.0.2', '17.0.3', '17.1', '17.1.1', '17.1.2', '17.2', '17.2.1', '17.3', '17.3.1', '17.4', '17.4.1', '17.5', '17.5.1', '17.6', '17.6.1', '17.7', '17.7.1', '17.7.2', '17.7.3', '17.7.4', 
        '18.0', '18.0.1', '18.1', '18.1.1', '18.2', '18.2.1', '18.3')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone11%' -- iPhone XS, iPhone XS Max, iPhone XR
        )
        AND source_version IN ('12.0', '12.0.1', '12.1', '12.1.1', '12.1.2', '12.1.3', '12.1.4', '12.2', '12.3', '12.3.1', '12.3.2', '12.3.3', '12.3.4', '12.4', '12.4.1', '12.4.2', '12.4.3', '12.4.4', '12.4.5', '12.4.6', '12.4.7', '12.4.8', '12.4.9', '12.5', '12.5.1', '12.5.2', '12.5.3', '12.5.4', '12.5.5', '12.5.6', '12.5.7',
        '13.0', '13.1', '13.1.1', '13.1.2', '13.1.3', '13.2', '13.2.1', '13.2.2', '13.2.3', '13.3', '13.3.1', '13.4', '13.4.1', '13.5', '13.5.1', '13.6', '13.6.1', '13.7',
        '14.0', '14.0.1', '14.1', '14.2', '14.2.1', '14.3', '14.4', '14.4.1', '14.4.2', '14.5', '14.5.1', '14.6', '14.7', '14.7.1', '14.8', '14.8.1', 
        '15.0', '15.0.1', '15.0.2', '15.0.3', '15.1', '15.1.1', '15.2', '15.2.1', '15.3', '15.3.1', '15.4', '15.4.1', '15.5', '15.6', '15.6.1', '15.7', '15.7.1', '15.7.2', '15.7.3', '15.7.4', '15.7.5', '15.7.6',  '15.7.7', '15.7.8', '15.7.9', '15.8', '15.8.1', '15.8.2', '15.8.3',
        '16.0', '16.0.1', '16.0.2', '16.0.3', '16.1', '16.1.1', '16.1.2', '16.2', '16.3', '16.3.1', '16.4', '16.4.1', '16.5', '16.5.1', '16.6', '16.6.1', '16.7', '16.7.1', '16.7.2', '16.7.3', '16.7.4', '16.7.5', '16.7.6', '16.7.7', '16.7.8', '16.7.9', '16.7.10',
        '17.0', '17.0.1', '17.0.2', '17.0.3', '17.1', '17.1.1', '17.1.2', '17.2', '17.2.1', '17.3', '17.3.1', '17.4', '17.4.1', '17.5', '17.5.1', '17.6', '17.6.1', '17.7', '17.7.1', '17.7.2', '17.7.3', '17.7.4', 
        '18.0', '18.0.1', '18.1', '18.1.1', '18.2', '18.2.1', '18.3')
        OR

        (
        data_provenances.origin_product_type LIKE 'iPhone10%' -- iPhone 8, 8 Plus, X
        )
        AND source_version IN ('11.0', '11.0.1', '11.0.2', '11.0.3', '11.1', '11.1.1', '11.1.2', '11.1.3', '11.2', '11.2.1', '11.2.2', '11.2.3', '11.2.4', '11.2.5', '11.2.6', '11.3', '11.3.1', '11.4', '11.4.1',
        '12.0', '12.0.1', '12.1', '12.1.1', '12.1.2', '12.1.3', '12.1.4', '12.2', '12.3', '12.3.1', '12.3.2', '12.3.3', '12.3.4', '12.4', '12.4.1', '12.4.2', '12.4.3', '12.4.4', '12.4.5', '12.4.6', '12.4.7', '12.4.8', '12.4.9', '12.5', '12.5.1', '12.5.2', '12.5.3', '12.5.4', '12.5.5', '12.5.6', '12.5.7',
        '13.0', '13.1', '13.1.1', '13.1.2', '13.1.3', '13.2', '13.2.1', '13.2.2', '13.2.3', '13.3', '13.3.1', '13.4', '13.4.1', '13.5', '13.5.1', '13.6', '13.6.1', '13.7',
        '14.0', '14.0.1', '14.1', '14.2', '14.2.1', '14.3', '14.4', '14.4.1', '14.4.2', '14.5', '14.5.1', '14.6', '14.7', '14.7.1', '14.8', '14.8.1', 
        '15.0', '15.0.1', '15.0.2', '15.0.3', '15.1', '15.1.1', '15.2', '15.2.1', '15.3', '15.3.1', '15.4', '15.4.1', '15.5', '15.6', '15.6.1', '15.7', '15.7.1', '15.7.2', '15.7.3', '15.7.4', '15.7.5', '15.7.6',  '15.7.7', '15.7.8', '15.7.9', '15.8', '15.8.1', '15.8.2', '15.8.3',
        '16.0', '16.0.1', '16.0.2', '16.0.3', '16.1', '16.1.1', '16.1.2', '16.2', '16.3', '16.3.1', '16.4', '16.4.1', '16.5', '16.5.1', '16.6', '16.6.1', '16.7', '16.7.1', '16.7.2', '16.7.3', '16.7.4', '16.7.5', '16.7.6', '16.7.7', '16.7.8', '16.7.9', '16.7.10')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone9%' -- iPhone 7, 7 Plus
        )
        AND source_version IN ('10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1', '10.2', '10.2.1', '10.3', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.4', '10.5', '10.6', '10.6.1',
        '11.0', '11.0.1', '11.0.2', '11.0.3', '11.1', '11.1.1', '11.1.2', '11.1.3', '11.2', '11.2.1', '11.2.2', '11.2.3', '11.2.4', '11.2.5', '11.2.6', '11.3', '11.3.1', '11.4', '11.4.1',
        '12.0', '12.0.1', '12.1', '12.1.1', '12.1.2', '12.1.3', '12.1.4', '12.2', '12.3', '12.3.1', '12.3.2', '12.3.3', '12.3.4', '12.4', '12.4.1', '12.4.2', '12.4.3', '12.4.4', '12.4.5', '12.4.6', '12.4.7', '12.4.8', '12.4.9', '12.5', '12.5.1', '12.5.2', '12.5.3', '12.5.4', '12.5.5', '12.5.6', '12.5.7',
        '13.0', '13.1', '13.1.1', '13.1.2', '13.1.3', '13.2', '13.2.1', '13.2.2', '13.2.3', '13.3', '13.3.1', '13.4', '13.4.1', '13.5', '13.5.1', '13.6', '13.6.1', '13.7',
        '14.0', '14.0.1', '14.1', '14.2', '14.2.1', '14.3', '14.4', '14.4.1', '14.4.2', '14.5', '14.5.1', '14.6', '14.7', '14.7.1', '14.8', '14.8.1', 
        '15.0', '15.0.1', '15.0.2', '15.0.3', '15.1', '15.1.1', '15.2', '15.2.1', '15.3', '15.3.1', '15.4', '15.4.1', '15.5', '15.6', '15.6.1', '15.7', '15.7.1', '15.7.2', '15.7.3', '15.7.4', '15.7.5', '15.7.6',  '15.7.7', '15.7.8', '15.7.9', '15.8', '15.8.1', '15.8.2', '15.8.3')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone7%' -- iPhone 6s, 6s Plus, SE 1st Gen
        OR data_provenances.origin_product_type LIKE 'iPhone8%'
        )
        AND source_version IN ('8.0', '8.0.1', '8.0.2', '8.1', '8.1.1', '8.1.2', '8.1.3', '8.2', '8.3', '8.4', '8.4.1', '8.4.2', '8.4.3', '8.4.4', '8.5', '8.5.1', '8.6', '8.7', '8.7.1', '8.8.1',
        '9.0', '9.0.1', '9.0.2', '9.1', '9.2', '9.2.1', '9.3', '9.3.1', '9.3.2', '9.3.3', '9.3.4', '9.3.5', '9.3.6', '9.4', '9.5', '9.5.1', '9.5.2', '9.6', '9.6.1', '9.6.2', '9.6.3',
        '10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1', '10.2', '10.2.1', '10.3', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.4', '10.5', '10.6', '10.6.1',
        '11.0', '11.0.1', '11.0.2', '11.0.3', '11.1', '11.1.1', '11.1.2', '11.1.3', '11.2', '11.2.1', '11.2.2', '11.2.3', '11.2.4', '11.2.5', '11.2.6', '11.3', '11.3.1', '11.4', '11.4.1',
        '12.0', '12.0.1', '12.1', '12.1.1', '12.1.2', '12.1.3', '12.1.4', '12.2', '12.3', '12.3.1', '12.3.2', '12.3.3', '12.3.4', '12.4', '12.4.1', '12.4.2', '12.4.3', '12.4.4', '12.4.5', '12.4.6', '12.4.7', '12.4.8', '12.4.9', '12.5', '12.5.1', '12.5.2', '12.5.3', '12.5.4', '12.5.5', '12.5.6', '12.5.7',
        '13.0', '13.1', '13.1.1', '13.1.2', '13.1.3', '13.2', '13.2.1', '13.2.2', '13.2.3', '13.3', '13.3.1', '13.4', '13.4.1', '13.5', '13.5.1', '13.6', '13.6.1', '13.7',
        '14.0', '14.0.1', '14.1', '14.2', '14.2.1', '14.3', '14.4', '14.4.1', '14.4.2', '14.5', '14.5.1', '14.6', '14.7', '14.7.1', '14.8', '14.8.1', 
        '15.0', '15.0.1', '15.0.2', '15.0.3', '15.1', '15.1.1', '15.2', '15.2.1', '15.3', '15.3.1', '15.4', '15.4.1', '15.5', '15.6', '15.6.1', '15.7', '15.7.1', '15.7.2', '15.7.3', '15.7.4', '15.7.5', '15.7.6',  '15.7.7', '15.7.8', '15.7.9', '15.8', '15.8.1', '15.8.2', '15.8.3')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone5%' -- iPhone 5, 5c, 5s
        OR data_provenances.origin_product_type LIKE 'iPhone6%'
        )
        AND source_version IN ('6.0', '6.0.1', '6.0.2', '6.1', '6.1.1', '6.1.2', '6.1.3', '6.1.4', '6.1.5', '6.1.6','6.2', '6.2.1', '6.2.5', '6.2.6', '6.2.7', '6.2.8', '6.2.9', '6.3', 
        '7.0', '7.0.1', '7.0.2', '7.0.3', '7.0.4', '7.0.5', '7.0.6', '7.1', '7.1.1', '7.1.2', '7.2', '7.3', '7.3.1', '7.3.2', '7.3.3', '7.4', '7.4.1', '7.5', '7.6', '7.6.1', '7.6.2',
        '8.0', '8.0.1', '8.0.2', '8.1', '8.1.1', '8.1.2', '8.1.3', '8.2', '8.3', '8.4', '8.4.1', '8.4.2', '8.4.3', '8.4.4', '8.5', '8.5.1', '8.6', '8.7', '8.7.1', '8.8.1',
        '9.0', '9.0.1', '9.0.2', '9.1', '9.2', '9.2.1', '9.3', '9.3.1', '9.3.2', '9.3.3', '9.3.4', '9.3.5', '9.3.6', '9.4', '9.5', '9.5.1', '9.5.2', '9.6', '9.6.1', '9.6.2', '9.6.3',
        '10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1', '10.2', '10.2.1', '10.3', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.4', '10.5', '10.6', '10.6.1',
        '11.0', '11.0.1', '11.0.2', '11.0.3', '11.1', '11.1.1', '11.1.2', '11.1.3', '11.2', '11.2.1', '11.2.2', '11.2.3', '11.2.4', '11.2.5', '11.2.6', '11.3', '11.3.1', '11.4', '11.4.1',
        '12.0', '12.0.1', '12.1', '12.1.1', '12.1.2', '12.1.3', '12.1.4', '12.2', '12.3', '12.3.1', '12.3.2', '12.3.3', '12.3.4', '12.4', '12.4.1', '12.4.2', '12.4.3', '12.4.4', '12.4.5', '12.4.6', '12.4.7', '12.4.8', '12.4.9', '12.5', '12.5.1', '12.5.2', '12.5.3', '12.5.4', '12.5.5', '12.5.6', '12.5.7')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone3%' -- iPhone 4, 4s
        OR data_provenances.origin_product_type LIKE 'iPhone4%'
        )
        AND source_version IN ('4.0', '4.0.1', '4.0.2', '4.1', '4.2', '4.2.1', '4.2.2', '4.2.3', '4.2.4', '4.2.5', '4.2.6', '4.2.7', '4.2.8', '4.2.9', '4.2.10', '4.3', '4.3.1', '4.3.2', '4.3.3', '4.3.4', '4.3.5',
        '5.0', '5.0.1', '5.1', '5.1.1', '5.1.2', '5.1.3', '5.2', '5.2.1', '5.3', '5.3.1', '5.3.2', '5.3.3', '5.3.4', '5.3.5', '5.3.6', '5.3.7', '5.3.8', '5.3.9',
        '6.0', '6.0.1', '6.0.2', '6.1', '6.1.1', '6.1.2', '6.1.3', '6.1.4', '6.1.5', '6.1.6','6.2', '6.2.1', '6.2.5', '6.2.6', '6.2.7', '6.2.8', '6.2.9', '6.3', 
        '7.0', '7.0.1', '7.0.2', '7.0.3', '7.0.4', '7.0.5', '7.0.6', '7.1', '7.1.1', '7.1.2', '7.2', '7.3', '7.3.1', '7.3.2', '7.3.3', '7.4', '7.4.1', '7.5', '7.6', '7.6.1', '7.6.2',
        '8.0', '8.0.1', '8.0.2', '8.1', '8.1.1', '8.1.2', '8.1.3', '8.2', '8.3', '8.4', '8.4.1', '8.4.2', '8.4.3', '8.4.4', '8.5', '8.5.1', '8.6', '8.7', '8.7.1', '8.8.1',
        '9.0', '9.0.1', '9.0.2', '9.1', '9.2', '9.2.1', '9.3', '9.3.1', '9.3.2', '9.3.3', '9.3.4', '9.3.5', '9.3.6', '9.4', '9.5', '9.5.1', '9.5.2', '9.6', '9.6.1', '9.6.2', '9.6.3',
        '10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1', '10.2', '10.2.1', '10.3', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.4', '10.5', '10.6', '10.6.1')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone2%' -- iPhone 3GS
        )
        AND source_version IN ('3.0', '3.0.1', '3.1', '3.1.1', '3.1.2', '3.1.3', '3.2', '3.2.1', '3.2.2', '3.2.3',
        '4.0', '4.0.1', '4.0.2', '4.1', '4.2', '4.2.1', '4.2.2', '4.2.3', '4.2.4', '4.2.5', '4.2.6', '4.2.7', '4.2.8', '4.2.9', '4.2.10', '4.3', '4.3.1', '4.3.2', '4.3.3', '4.3.4', '4.3.5',
        '5.0', '5.0.1', '5.1', '5.1.1', '5.1.2', '5.1.3', '5.2', '5.2.1', '5.3', '5.3.1', '5.3.2', '5.3.3', '5.3.4', '5.3.5', '5.3.6', '5.3.7', '5.3.8', '5.3.9',
        '6.0', '6.0.1', '6.0.2', '6.1', '6.1.1', '6.1.2', '6.1.3', '6.1.4', '6.1.5', '6.1.6','6.2', '6.2.1', '6.2.5', '6.2.6', '6.2.7', '6.2.8', '6.2.9', '6.3')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone1,2' -- iPhone 3G
        )
        AND source_version IN ('2.0', '2.0.1', '2.0.2', '2.1', '2.1.1', '2.2', '2.2.1', '2.2.2',
        '3.0', '3.0.1', '3.1', '3.1.1', '3.1.2', '3.1.3', '3.2', '3.2.1', '3.2.2', '3.2.3',
        '4.0', '4.0.1', '4.0.2', '4.1', '4.2', '4.2.1', '4.2.2', '4.2.3', '4.2.4', '4.2.5', '4.2.6', '4.2.7', '4.2.8', '4.2.9', '4.2.10', '4.3', '4.3.1', '4.3.2', '4.3.3', '4.3.4', '4.3.5')
        OR
        (
        data_provenances.origin_product_type LIKE 'iPhone1,1' -- iPhone
        )
        AND source_version IN ('1.0', '1.0.1', '1.0.2', '1.1', '1.1.1', '1.1.2', '1.1.3', '1.1.4', '1.1.5',
        '2.0', '2.0.1', '2.0.2', '2.1', '2.1.1', '2.2', '2.2.1', '2.2.2',
        '3.0', '3.0.1', '3.1', '3.1.1', '3.1.2', '3.1.3', '3.2', '3.2.1', '3.2.2', '3.2.3')
        OR 
        (
        data_provenances.origin_product_type LIKE 'Watch7,8' -- Watch Series 10
        OR data_provenances.origin_product_type LIKE 'Watch7,9'
        OR data_provenances.origin_product_type LIKE 'Watch7,10'
        OR data_provenances.origin_product_type LIKE 'Watch7,11'
        )
        AND source_version IN ('11.0', '11.0.1', '11.0.2', '11.0.3', '11.1', '11.1.1', '11.1.2', '11.1.3', '11.2', '11.2.1', '11.2.2', '11.2.3', '11.2.4', '11.2.5', '11.2.6', '11.3', '11.3.1', '11.4', '11.4.1'
        )
        OR 
        (
        data_provenances.origin_product_type LIKE 'Watch7,1' -- Watch Series 9 and Ultra 2
        OR data_provenances.origin_product_type LIKE 'Watch7,2'
        OR data_provenances.origin_product_type LIKE 'Watch7,3'
        OR data_provenances.origin_product_type LIKE 'Watch7,4'
        OR data_provenances.origin_product_type LIKE 'Watch7,5'
        )
        AND source_version IN ('10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1', '10.2', '10.2.1', '10.3', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.4', '10.5', '10.6', '10.6.1',
        '11.0', '11.0.1', '11.0.2', '11.0.3', '11.1', '11.1.1', '11.1.2', '11.1.3', '11.2', '11.2.1', '11.2.2', '11.2.3', '11.2.4', '11.2.5', '11.2.6', '11.3', '11.3.1', '11.4', '11.4.1'
        )
        OR 
        (
        data_provenances.origin_product_type LIKE 'Watch6,10' -- Watch Series SE 2nd Gen, 8, Ultra 1st Gen
        OR data_provenances.origin_product_type LIKE 'Watch6,11'
        OR data_provenances.origin_product_type LIKE 'Watch6,12'
        OR data_provenances.origin_product_type LIKE 'Watch6,13'
        OR data_provenances.origin_product_type LIKE 'Watch6,14'
        OR data_provenances.origin_product_type LIKE 'Watch6,15'
        OR data_provenances.origin_product_type LIKE 'Watch6,16'
        OR data_provenances.origin_product_type LIKE 'Watch6,17'
        OR data_provenances.origin_product_type LIKE 'Watch6,18'
        )
        AND source_version IN ('9.0', '9.0.1', '9.0.2', '9.1', '9.2', '9.2.1', '9.3', '9.3.1', '9.3.2', '9.3.3', '9.3.4', '9.3.5', '9.3.6', '9.4', '9.5', '9.5.1', '9.5.2', '9.6', '9.6.1', '9.6.2', '9.6.3',
        '10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1', '10.2', '10.2.1', '10.3', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.4', '10.5', '10.6', '10.6.1',
        '11.0', '11.0.1', '11.0.2', '11.0.3', '11.1', '11.1.1', '11.1.2', '11.1.3', '11.2', '11.2.1', '11.2.2', '11.2.3', '11.2.4', '11.2.5', '11.2.6', '11.3', '11.3.1', '11.4', '11.4.1'
        )
        OR 
        (
        data_provenances.origin_product_type LIKE 'Watch6,6' -- Watch Series 7
        OR data_provenances.origin_product_type LIKE 'Watch6,7'
        OR data_provenances.origin_product_type LIKE 'Watch6,8'
        OR data_provenances.origin_product_type LIKE 'Watch6,9'
        )
        AND source_version IN ('8.0', '8.0.1', '8.0.2', '8.1', '8.1.1', '8.1.2', '8.1.3', '8.2', '8.3', '8.4', '8.4.1', '8.4.2', '8.4.3', '8.4.4', '8.5', '8.5.1', '8.6', '8.7', '8.7.1', '8.8.1',
        '9.0', '9.0.1', '9.0.2', '9.1', '9.2', '9.2.1', '9.3', '9.3.1', '9.3.2', '9.3.3', '9.3.4', '9.3.5', '9.3.6', '9.4', '9.5', '9.5.1', '9.5.2', '9.6', '9.6.1', '9.6.2', '9.6.3',
        '10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1', '10.2', '10.2.1', '10.3', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.4', '10.5', '10.6', '10.6.1',
        '11.0', '11.0.1', '11.0.2', '11.0.3', '11.1', '11.1.1', '11.1.2', '11.1.3', '11.2', '11.2.1', '11.2.2', '11.2.3', '11.2.4', '11.2.5', '11.2.6', '11.3', '11.3.1', '11.4', '11.4.1'
        )
        OR 
        (
        data_provenances.origin_product_type LIKE 'Watch6,1' -- Watch Series 6
        OR data_provenances.origin_product_type LIKE 'Watch6,2'
        OR data_provenances.origin_product_type LIKE 'Watch6,3'
        OR data_provenances.origin_product_type LIKE 'Watch6,4'
        )
        AND source_version IN ('7.0', '7.0.1', '7.0.2', '7.0.3', '7.0.4', '7.0.5', '7.0.6', '7.1', '7.1.1', '7.1.2', '7.2', '7.3', '7.3.1', '7.3.2', '7.3.3', '7.4', '7.4.1', '7.5', '7.6', '7.6.1', '7.6.2',
        '8.0', '8.0.1', '8.0.2', '8.1', '8.1.1', '8.1.2', '8.1.3', '8.2', '8.3', '8.4', '8.4.1', '8.4.2', '8.4.3', '8.4.4', '8.5', '8.5.1', '8.6', '8.7', '8.7.1', '8.8.1',
        '9.0', '9.0.1', '9.0.2', '9.1', '9.2', '9.2.1', '9.3', '9.3.1', '9.3.2', '9.3.3', '9.3.4', '9.3.5', '9.3.6', '9.4', '9.5', '9.5.1', '9.5.2', '9.6', '9.6.1', '9.6.2', '9.6.3',
        '10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1', '10.2', '10.2.1', '10.3', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.4', '10.5', '10.6', '10.6.1',
        '11.0', '11.0.1', '11.0.2', '11.0.3', '11.1', '11.1.1', '11.1.2', '11.1.3', '11.2', '11.2.1', '11.2.2', '11.2.3', '11.2.4', '11.2.5', '11.2.6', '11.3', '11.3.1', '11.4', '11.4.1'
        )
        OR 
        (
        data_provenances.origin_product_type LIKE 'Watch5,9' -- Watch Series SE
        OR data_provenances.origin_product_type LIKE 'Watch5,10'
        OR data_provenances.origin_product_type LIKE 'Watch5,11'
        OR data_provenances.origin_product_type LIKE 'Watch5,12'
        )
        AND source_version IN ('7.0', '7.0.1', '7.0.2', '7.0.3', '7.0.4', '7.0.5', '7.0.6', '7.1', '7.1.1', '7.1.2', '7.2', '7.3', '7.3.1', '7.3.2', '7.3.3', '7.4', '7.4.1', '7.5', '7.6', '7.6.1', '7.6.2',
        '8.0', '8.0.1', '8.0.2', '8.1', '8.1.1', '8.1.2', '8.1.3', '8.2', '8.3', '8.4', '8.4.1', '8.4.2', '8.4.3', '8.4.4', '8.5', '8.5.1', '8.6', '8.7', '8.7.1', '8.8.1',
        '9.0', '9.0.1', '9.0.2', '9.1', '9.2', '9.2.1', '9.3', '9.3.1', '9.3.2', '9.3.3', '9.3.4', '9.3.5', '9.3.6', '9.4', '9.5', '9.5.1', '9.5.2', '9.6', '9.6.1', '9.6.2', '9.6.3',
        '10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1', '10.2', '10.2.1', '10.3', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.4', '10.5', '10.6', '10.6.1'
        )
        OR 
        (
        data_provenances.origin_product_type LIKE 'Watch5,9' -- Watch Series SE 1st Gen
        OR data_provenances.origin_product_type LIKE 'Watch5,10'
        OR data_provenances.origin_product_type LIKE 'Watch5,11'
        OR data_provenances.origin_product_type LIKE 'Watch5,12'
        )
        AND source_version IN ('7.0', '7.0.1', '7.0.2', '7.0.3', '7.0.4', '7.0.5', '7.0.6', '7.1', '7.1.1', '7.1.2', '7.2', '7.3', '7.3.1', '7.3.2', '7.3.3', '7.4', '7.4.1', '7.5', '7.6', '7.6.1', '7.6.2',
        '8.0', '8.0.1', '8.0.2', '8.1', '8.1.1', '8.1.2', '8.1.3', '8.2', '8.3', '8.4', '8.4.1', '8.4.2', '8.4.3', '8.4.4', '8.5', '8.5.1', '8.6', '8.7', '8.7.1', '8.8.1',
        '9.0', '9.0.1', '9.0.2', '9.1', '9.2', '9.2.1', '9.3', '9.3.1', '9.3.2', '9.3.3', '9.3.4', '9.3.5', '9.3.6', '9.4', '9.5', '9.5.1', '9.5.2', '9.6', '9.6.1', '9.6.2', '9.6.3',
        '10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1', '10.2', '10.2.1', '10.3', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.4', '10.5', '10.6', '10.6.1'
        )
        OR 
        (
        data_provenances.origin_product_type LIKE 'Watch5,1' -- Watch Series 5
        OR data_provenances.origin_product_type LIKE 'Watch5,2'
        OR data_provenances.origin_product_type LIKE 'Watch5,3'
        OR data_provenances.origin_product_type LIKE 'Watch5,4'
        )
        AND source_version IN ('6.0', '6.0.1', '6.0.2', '6.1', '6.1.1', '6.1.2', '6.1.3', '6.1.4', '6.1.5', '6.1.6','6.2', '6.2.1', '6.2.5', '6.2.6', '6.2.7', '6.2.8', '6.2.9', '6.3', 
        '7.0', '7.0.1', '7.0.2', '7.0.3', '7.0.4', '7.0.5', '7.0.6', '7.1', '7.1.1', '7.1.2', '7.2', '7.3', '7.3.1', '7.3.2', '7.3.3', '7.4', '7.4.1', '7.5', '7.6', '7.6.1', '7.6.2',
        '8.0', '8.0.1', '8.0.2', '8.1', '8.1.1', '8.1.2', '8.1.3', '8.2', '8.3', '8.4', '8.4.1', '8.4.2', '8.4.3', '8.4.4', '8.5', '8.5.1', '8.6', '8.7', '8.7.1', '8.8.1',
        '9.0', '9.0.1', '9.0.2', '9.1', '9.2', '9.2.1', '9.3', '9.3.1', '9.3.2', '9.3.3', '9.3.4', '9.3.5', '9.3.6', '9.4', '9.5', '9.5.1', '9.5.2', '9.6', '9.6.1', '9.6.2', '9.6.3',
        '10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1', '10.2', '10.2.1', '10.3', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.4', '10.5', '10.6', '10.6.1'
        )
        OR 
        (
        data_provenances.origin_product_type LIKE 'Watch4%' -- Watch Series 4
        )
        AND source_version IN ('5.0', '5.0.1', '5.1', '5.1.1', '5.1.2', '5.1.3', '5.2', '5.2.1', '5.3', '5.3.1', '5.3.2', '5.3.3', '5.3.4', '5.3.5', '5.3.6', '5.3.7', '5.3.8', '5.3.9',
        '6.0', '6.0.1', '6.0.2', '6.1', '6.1.1', '6.1.2', '6.1.3', '6.1.4', '6.1.5', '6.1.6','6.2', '6.2.1', '6.2.5', '6.2.6', '6.2.7', '6.2.8', '6.2.9', '6.3', 
        '7.0', '7.0.1', '7.0.2', '7.0.3', '7.0.4', '7.0.5', '7.0.6', '7.1', '7.1.1', '7.1.2', '7.2', '7.3', '7.3.1', '7.3.2', '7.3.3', '7.4', '7.4.1', '7.5', '7.6', '7.6.1', '7.6.2',
        '8.0', '8.0.1', '8.0.2', '8.1', '8.1.1', '8.1.2', '8.1.3', '8.2', '8.3', '8.4', '8.4.1', '8.4.2', '8.4.3', '8.4.4', '8.5', '8.5.1', '8.6', '8.7', '8.7.1', '8.8.1',
        '9.0', '9.0.1', '9.0.2', '9.1', '9.2', '9.2.1', '9.3', '9.3.1', '9.3.2', '9.3.3', '9.3.4', '9.3.5', '9.3.6', '9.4', '9.5', '9.5.1', '9.5.2', '9.6', '9.6.1', '9.6.2', '9.6.3',
        '10.0', '10.0.1', '10.0.2', '10.0.3', '10.1', '10.1.1', '10.2', '10.2.1', '10.3', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '10.4', '10.5', '10.6', '10.6.1'
        )
        OR 
        (
        data_provenances.origin_product_type LIKE 'Watch3%' -- Watch Series 3
        )
        AND source_version IN ('4.0', '4.0.1', '4.0.2', '4.1', '4.2', '4.2.1', '4.2.2', '4.2.3', '4.2.4', '4.2.5', '4.2.6', '4.2.7', '4.2.8', '4.2.9', '4.2.10', '4.3', '4.3.1', '4.3.2', '4.3.3', '4.3.4', '4.3.5',
        '5.0', '5.0.1', '5.1', '5.1.1', '5.1.2', '5.1.3', '5.2', '5.2.1', '5.3', '5.3.1', '5.3.2', '5.3.3', '5.3.4', '5.3.5', '5.3.6', '5.3.7', '5.3.8', '5.3.9',
        '6.0', '6.0.1', '6.0.2', '6.1', '6.1.1', '6.1.2', '6.1.3', '6.1.4', '6.1.5', '6.1.6','6.2', '6.2.1', '6.2.5', '6.2.6', '6.2.7', '6.2.8', '6.2.9', '6.3', 
        '7.0', '7.0.1', '7.0.2', '7.0.3', '7.0.4', '7.0.5', '7.0.6', '7.1', '7.1.1', '7.1.2', '7.2', '7.3', '7.3.1', '7.3.2', '7.3.3', '7.4', '7.4.1', '7.5', '7.6', '7.6.1', '7.6.2',
        '8.0', '8.0.1', '8.0.2', '8.1', '8.1.1', '8.1.2', '8.1.3', '8.2', '8.3', '8.4', '8.4.1', '8.4.2', '8.4.3', '8.4.4', '8.5', '8.5.1', '8.6', '8.7', '8.7.1', '8.8.1'
        )
        OR 
        (
        data_provenances.origin_product_type LIKE 'Watch2%' -- Watch Series 1, 2
        )
        AND source_version IN ('3.0', '3.0.1', '3.1', '3.1.1', '3.1.2', '3.1.3', '3.2', '3.2.1', '3.2.2', '3.2.3',
        '4.0', '4.0.1', '4.0.2', '4.1', '4.2', '4.2.1', '4.2.2', '4.2.3', '4.2.4', '4.2.5', '4.2.6', '4.2.7', '4.2.8', '4.2.9', '4.2.10', '4.3', '4.3.1', '4.3.2', '4.3.3', '4.3.4', '4.3.5',
        '5.0', '5.0.1', '5.1', '5.1.1', '5.1.2', '5.1.3', '5.2', '5.2.1', '5.3', '5.3.1', '5.3.2', '5.3.3', '5.3.4', '5.3.5', '5.3.6', '5.3.7', '5.3.8', '5.3.9',
        '6.0', '6.0.1', '6.0.2', '6.1', '6.1.1', '6.1.2', '6.1.3', '6.1.4', '6.1.5', '6.1.6','6.2', '6.2.1', '6.2.5', '6.2.6', '6.2.7', '6.2.8', '6.2.9', '6.3'
        )
        OR 
        (
        data_provenances.origin_product_type LIKE 'Watch1%' -- Watch Origin 1st Gen
        )
        AND source_version IN ('1.0', '1.0.1', '1.0.2', '1.1', '1.1.1', '1.1.2', '1.1.3', '1.1.4', '1.1.5',
        '2.0', '2.0.1', '2.0.2', '2.1', '2.1.1', '2.2', '2.2.1', '2.2.2',
        '3.0', '3.0.1', '3.1', '3.1.1', '3.1.2', '3.1.3', '3.2', '3.2.1', '3.2.2', '3.2.3',
        '4.0', '4.0.1', '4.0.2', '4.1', '4.2', '4.2.1', '4.2.2', '4.2.3', '4.2.4', '4.2.5', '4.2.6', '4.2.7', '4.2.8', '4.2.9', '4.2.10', '4.3', '4.3.1', '4.3.2', '4.3.3', '4.3.4', '4.3.5'
        )
        AND data_provenances.origin_product_type != "iPhone0,0" 
        AND objects.creation_date > 0
        GROUP BY origin_product_type, source_version
        HAVING MIN(datetime(objects.creation_date + 978307200, 'UNIXEPOCH')) != MAX(datetime(objects.creation_date + 978307200, 'UNIXEPOCH'))
        ORDER BY creation_date;
        ''')
    
        all_rows = cursor.fetchall()

        for row in all_rows:
            origin_product_type = device_id.get(row[2], row[2])
            start_timestamp = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            end_timestamp = convert_ts_human_to_timezone_offset(row[1], timezone_offset)
            data_list.append(
                (start_timestamp, end_timestamp, origin_product_type, row[3], row[4], row[5]))
        
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Product Origin (Common Name)', 'Product Origin', 'Source ID', 'iOS / WatchOS Version')
    return data_headers, data_list, healthdb_secure

@artifact_processor
def ConnectedDeviceInformation_ConsolidatedConnectedDeviceHistory(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    healthdb_secure = ''

    for file_found in files_found:
        if file_found.endswith('healthdb_secure.sqlite'):
           healthdb_secure = file_found
        else:
            continue

    with open_sqlite_db_readonly(healthdb_secure) as db:
        cursor = db.cursor()

        cursor.execute('''
        SELECT
        MIN(datetime(objects.creation_date + 978307200, 'UNIXEPOCH')) AS "Start Date",
        MAX(datetime(objects.creation_date + 978307200, 'UNIXEPOCH')) AS "End Date",
        data_provenances.origin_product_type AS 'Product Origin (Common Name)',
        data_provenances.origin_product_type AS "Origin Product"
        FROM objects
        LEFT OUTER JOIN data_provenances ON objects.provenance = data_provenances.ROWID
        WHERE data_provenances.origin_product_type != "UnknownDevice" and data_provenances.origin_product_type != "iPhone0,0" AND objects.creation_date > 1
        GROUP BY data_provenances.origin_product_type
        ORDER BY creation_date;
        ''')
    
        all_rows = cursor.fetchall()

        for row in all_rows:
            origin_product_type = device_id.get(row[2], row[2])
            start_timestamp = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            end_timestamp = convert_ts_human_to_timezone_offset(row[1], timezone_offset)
            data_list.append(
                (start_timestamp, end_timestamp, origin_product_type, row[3]))
        
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Product Origin (Common Name)', 'Product Origin')
    return data_headers, data_list, healthdb_secure

@artifact_processor
def ConnectedDeviceInformation_CurrentDeviceInfo(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []
    healthdb = ''

    for file_found in files_found:
        if file_found.endswith('healthdb.sqlite'):
            healthdb = file_found
            break
    else:
        return ('No healthdb.sqlite file found.', [], '')

    try:
        with open_sqlite_db_readonly(healthdb) as db:
            cursor = db.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='device_context';")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("Note: The 'device_context' table was not found in this database - only in newer OS versions.")
                return ('device_context table missing', [], healthdb)

            cursor.execute('''
            Select 
            (datetime(device_context.date_modified + 978307200, 'UNIXEPOCH')) AS "Date Modified",
            device_context.product_type_name AS 'Product Origin (Common Name)',
            device_context.product_type_name AS "Origin Product",
            device_context.currentOS_name || " " || device_context.currentOS_version As "OS Version"
            From device_context;
            ''')

            all_rows = cursor.fetchall()

            for row in all_rows:
                product_type_name = device_id.get(row[1], row[1])
                mod_timestamp = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
                data_list.append(
                    (mod_timestamp, product_type_name, row[2], row[3]))

    except Exception as e:
        # Catch any unexpected errors
        print(f"An unexpected error occurred: {e}")
        return ('An unexpected error occurred.', [], healthdb)

    data_headers = (
        ('Modified Time', 'datetime'), 'Device Origin (Common Name)', 'Device Origin', 'OS Version')
    return data_headers, data_list, healthdb
