import glob
import os
import pathlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, open_sqlite_db_readonly


def get_ooklaSpeedtestData(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('speedtest.sqlite'):
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        datetime(("ZDATE")+strftime('%s', '2001-01-01 00:00:00'), 'unixepoch') as 'Date',
        "ZEXTERNALIP" as 'External IP Address',
        "ZINTERNALIP" as 'Internal IP Address',
        "ZCARRIERNAME" as 'Carrier Name',
        "ZISP" as 'ISP',
        "ZWIFISSID" as 'Wifi SSID',
        "ZWANTYPE" as 'WAN Type',
        CASE "ZDEVICEMODEL" 
            WHEN "iPad3,1"
                THEN "iPad 3rd Gen (Wi-Fi Only)"
            WHEN "iPad3,2"
                THEN "iPad 3rd Gen (Wi-Fi/Cellular Verizon/GPS)"
            WHEN "iPad3,3"
                THEN "iPad 3rd Gen (Wi-Fi/Cellular AT&T/GPS)"
            WHEN "iPad3,4"
                THEN "iPad 4th Gen (Wi-Fi Only)"
            WHEN "iPad3,5"
                THEN "iPad 4th Gen (Wi-Fi/AT&T/GPS)"
            WHEN "iPad3,6"
                THEN "iPad 4th Gen (Wi-Fi/Verizon & Sprint/GPS)"
            WHEN "iPad6,11"
                THEN "iPad 9.7 5th Gen (Wi-Fi Only)"
            WHEN "iPad6,12"
                THEN "iPad 9.7 5th Gen (Wi-Fi/Cellular)"
            WHEN "iPad7,5"
                THEN "iPad 9.7 6th Gen (Wi-Fi Only)"
            WHEN "iPad7,6"
                THEN "iPad 9.7 6th Gen (Wi-Fi/Cellular)"
            WHEN "iPad7,11"
                THEN "iPad 10.2 7th Gen (Wi-Fi Only)"
            WHEN "iPad7,12"
                THEN "iPad 10.2 7th Gen (Wi-Fi/Cellular Global)"
            WHEN "iPad11,3"
                THEN "iPad Air 3rd Gen (Wi-Fi Only)"
            WHEN "iPad11,4"
                THEN "iPad Air 3rd Gen (Wi-Fi+Cell)"
            WHEN "iPad2,5"
                THEN "iPad mini Wi-Fi Only/1st Gen"
            WHEN "iPad2,6"
                THEN "iPad mini Wi-Fi/AT&T/GPS - 1st Gen"
            WHEN "iPad2,7"
                THEN "iPad mini Wi-Fi/VZ & Sprint/GPS - 1st Gen"
            WHEN "iPad4,4"
                THEN "iPad mini 2 (Retina/2nd Gen Wi-Fi Only)"
            WHEN "iPad4,5"
                THEN "iPad mini 2 (Retina/2nd Gen Wi-Fi/Cellular)"
            WHEN "iPad4,7"
                THEN "iPad mini 3 (Wi-Fi Only)"
            WHEN "iPad4,8"
                THEN "iPad mini 3 (Wi-Fi/Cellular)"
            WHEN "iPad5,1"
                THEN "iPad mini 4 (Wi-Fi Only)"
            WHEN "iPad5,2"
                THEN "iPad mini 4 (Wi-Fi/Cellular)"
            WHEN "iPad11,1"
                THEN "iPad mini 5th Gen (Wi-Fi Only)"
            WHEN "iPad11,2"
                THEN "iPad mini 5th Gen (Wi-Fi+Cell)"
            WHEN "iPad6,7" 
                THEN "iPad Pro 12.9 (Wi-Fi Only)"
            WHEN "iPad6,8" 
                THEN "iPad Pro 12.9 (Wi-Fi/Cellular)"
            WHEN "iPad6,3" 
                THEN "iPad Pro 9.7 (Wi-Fi Only)"
            WHEN "iPad6,4" 
                THEN "iPad Pro 9.7 (Wi-Fi/Cellular)"
            WHEN "iPad7,3" 
                THEN "iPad Pro 10.5 (Wi-Fi Only)"
            WHEN "iPad7,4" 
                THEN "iPad Pro 10.5 (Wi-Fi/Cellular)"
            WHEN "iPad7,1" 
                THEN "iPad Pro 12.9 (Wi-Fi Only - 2nd Gen)"
            WHEN "iPad7,2" 
                THEN "iPad Pro 12.9 (Wi-Fi/Cell - 2nd Gen)"
            WHEN "iPad8,9" 
                THEN "iPad Pro 11 (Wi-Fi Only - 2nd Gen)"
            WHEN "iPad8,10" 
                THEN "iPad Pro 11 (Wi-Fi/Cell - 2nd Gen)"
            WHEN "iPad8,11" 
                THEN "iPad Pro 12.9 (Wi-Fi Only - 4th Gen)"
            WHEN "iPad8,12" 
                THEN "iPad Pro 12.9 (Wi-Fi/Cell - 4th Gen)"
            WHEN "iPhone8,4" 
                THEN "iPhone SE (United States/A1662)"
            WHEN "iPhone9,1" 
                THEN "iPhone 7 (Verizon/Sprint/China/A1660)"
            WHEN "iPhone9,3" 
                THEN "iPhone 7 (AT&T/T-Mobile/A1778)"
            WHEN "iPhone9,2" 
                THEN "iPhone 7 Plus (Verizon/Sprint/China/A1661)"
            WHEN "iPhone9,4" 
                THEN "iPhone 7 Plus (AT&T/T-Mobile/A1784)"
            WHEN "iPhone10,1" 
                THEN "iPhone 8 (Verizon/Sprint/China/A1863)"
            WHEN "iPhone10,4" 
                THEN "iPhone 8 (AT&T/T-Mobile/Global/A1905)"
            WHEN "iPhone10,2" 
                THEN "iPhone 8 Plus (Verizon/Sprint/China/A1864)"
            WHEN "iPhone10,5" 
                THEN "iPhone 8 Plus (AT&T/T-Mobile/Global/A1897)"
            WHEN "iPhone10,3" 
                THEN "iPhone X (Verizon/Sprint/China/A1865)"
            WHEN "iPhone10,6" 
                THEN "iPhone X (AT&T/T-Mobile/Global/A1901)"
            WHEN "iPhone11,2" 
                THEN "iPhone Xs (A1920/A2097/A2098/A2100)"
            WHEN "iPhone11,6" 
                THEN "iPhone Xs Max (A1921/A2101/A2101/A2104)"
            WHEN "iPhone11,8" 
                THEN "iPhone XR (A1984/A2105/A2106/A2108)"
            WHEN "iPhone12,1" 
                THEN "iPhone 11 (A2111/A2221/A2223)"
            WHEN "iPhone12,3" 
                THEN "iPhone 11 Pro (A2160/A2215/A2217)"
            WHEN "iPhone12,5" 
                THEN "iPhone 11 Pro Max (A2161/A2218/A2220)"
                    ELSE "ZDEVICEMODEL"
            END 'Device Model',
        "ZLATITUDE" as 'Latitude',
        "ZLONGITUDE" as 'Longitude',
        "ZHORIZONTALACCURACY" as 'Accuracy in Meters'
        FROM ZSPEEDTESTRESULT
        
        ORDER BY "ZDATE" DESC	
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []    
    if usageentries > 0:
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
        
            description = ''
            report = ArtifactHtmlReport('Applications')
            report.start_artifact_report(report_folder, 'Ookla Speedtest', description)
            report.add_script()
            data_headers = ('Timestamp','External IP Address','Internal IP Address','Carrier Name','ISP','Wifi SSID','WAN Type','Device Model','Latitude','Longitude','Accuracy in Meters' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Ookla Speedtest Data'
            tsv(report_folder, data_headers, data_list, tsvname)
        
            tlactivity = 'Ookla Speedtest Data'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            kmlactivity = 'Ookla Speedtest Data'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)
        else:
            logfunc('No Ookla Speedtest Application data available')
        
        db.close()
        return 

__artifacts__ = {
    "ooklaSpeedtestData": (
        "Applications",
        ('**/speedtest.sqlite*'),
        get_ooklaSpeedtestData)
}