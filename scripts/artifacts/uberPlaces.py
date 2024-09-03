__artifacts_v2__ = {
    "uberPlaces": {
        "name": "Uber - Places",
        "description": "Parses Uber Places Database",
        "author": "Heather Charpentier",
        "version": "0.0.1",
        "date": "2024-04-10",
        "requirements": "none",
        "category": "Uber",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Documents/database.db*'),
        "function": "get_uberPlaces"
    }
}

import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone, kmlgen

def get_uberPlaces(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('database.db'):
            db = open_sqlite_db_readonly(file_found)
            #SQL QUERY TIME!
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime (timestamp_ms, 'unixepoch') as Timestamp, 
            json_extract(place.place_result, '$.payload.personalPreferencesPayload.preferredVehicles[0].lastUsedTimeMillis') as Last_Used,
            json_extract(place.place_result, '$.payload.personalPayload.id') as Uber_ID,
            json_extract(place.place_result, '$.payload.locationPayload.distanceMeters') as Distance_Meters,
            json_extract(place.place_result, '$.location.accessPoints[0].attachments.distance_to_target') as Distance_To_Target,
            json_extract(place.place_result, '$.location.coordinate.latitude') as Latitude,
            json_extract(place.place_result, '$.location.coordinate.longitude') as Longitude,
            json_extract(place.place_result, '$.location.name') as Name,
            json_extract(place.place_result, '$.location.fullAddress') as Related_Location,
            tag,
            json_extract(place.place_result, '$.location.accessPoints[0].usage') as Usage,
            json_extract(place.place_result, '$.location.accessPoints[0].attachments.tripCount') as Trip_Count,
            json_extract(place.place_result, '$.location.provider') as Provider
            FROM place
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    timestamp = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),timezone_offset)
                    if row[1] is None:
                        last_used = ''
                    else:
                        last_used = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]),timezone_offset)
                    data_list.append((timestamp,row[1],last_used,row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))
            db.close()
                    
        else:
            continue
        
    if data_list:
        description = 'Uber - Places'
        report = ArtifactHtmlReport('Uber - Places')
        report.start_artifact_report(report_folder, 'Uber - Places', description)
        report.add_script()
        data_headers = ('Timestamp','Last Used','Uber ID','Distance (Meters)','Distance To Target','Latitude','Longitude','Place Name','Place Address','Tag','Usage','Trip Count','Provider')
        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Uber - Places'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Uber - Places'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
        kmlactivity = 'Uber - Places Location Data'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)  
    
    else:
        logfunc('No Uber - Places data available')
