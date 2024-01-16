__artifacts_v2__ = {
    "Life360": {
        "name": "Life360",
        "description": "Parses Life360 app logs",
        "author": "@KevinPagano3",
        "version": "0.1",
        "date": "2024-01-15",
        "requirements": "none",
        "category": "Life360",
        "notes": "",
        "paths": ('*/com.life360.safetymap *.log'),
        "function": "get_life360"
    }
}

from datetime import *
import json
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, convert_ts_human_to_utc, convert_utc_human_to_timezone, kmlgen

def get_life360(files_found, report_folder, seeker, wrap_text, time_offset):

    data_list_geo = []
    data_list_dev = []
    
    for file_found in files_found:
        with open(file_found, encoding = 'utf-8', mode = 'r') as f:
            lines = f.readlines()
            
            for line in lines:
                if 'X-UserContext header set: ' in line:
                    log_split = line.split(' Life360[')
                    
                    timestamp = log_split[0]
                    
                    json_split = line.split('X-UserContext header set: ')
                    
                    json_str = json_split[1].strip()
                    json_load = json.loads(json_str)
                    
                    json_lat = json_load['geolocation'].get('lat','')
                    json_long = json_load['geolocation'].get('lon','')
                    json_speed = json_load['geolocation'].get('speed','')
                    json_heading = json_load['geolocation'].get('heading','')
                    json_alt = json_load['geolocation'].get('alt','')
                    json_accuracy = json_load['geolocation'].get('accuracy','')
                    json_vert_accuracy = json_load['geolocation'].get('vertical_accuracy','')
                    json_age = json_load['geolocation'].get('age','')
                    
                    json_timestamp = str(datetime.fromtimestamp(json_load['geolocation'].get('timestamp',''),tz=timezone.utc))[:-6]
                    time_create = convert_utc_human_to_timezone(convert_ts_human_to_utc(json_timestamp),time_offset)
                    
                    json_preciseLocation = json_load['flags'].get('preciseLocation','')
                    json_lmode = json_load['geolocation_meta'].get('lmode','').title()
                    json_userActivity = json_load['device'].get('userActivity','').replace('os_','').title()
                    
                    json_battery = json_load['device'].get('battery','')
                    json_charge = json_load['device'].get('charge','')
                    if json_charge == '0':
                        json_charge = ''
                    elif json_charge == '1':
                        json_charge = 'Yes'

                    data_list_geo.append((time_create,json_lat,json_long,json_alt,json_speed,json_heading,json_userActivity,json_lmode,json_preciseLocation,json_accuracy,json_vert_accuracy,json_age))
                    data_list_dev.append((time_create,json_battery,json_charge))
            
    if len(data_list_geo) > 0:
        report = ArtifactHtmlReport('Life360 - Locations')
        report.start_artifact_report(report_folder, 'Life360 - Locations')
        report.add_script()
        data_headers = ('Timestamp', 'Latitude', 'Longitude', 'Altitude', 'Speed (mps)', 'Heading', 'Activity Type', 'Location Mode', 'Location Precision','Accuracy (+/- m)','Vertical Accuracy (+/- m)','Age')

        report.write_artifact_data_table(data_headers, data_list_geo, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Life360 - Locations'
        tsv(report_folder, data_headers, data_list_geo, tsvname)
        
        tlactivity = 'Life360 - Locations'
        timeline(report_folder, tlactivity, data_list_geo, data_headers)
        
        kmlactivity = 'Life360 - Locations'
        kmlgen(report_folder, kmlactivity, data_list_geo, data_headers)
        
    else:
        logfunc('No Life360 - Locations data available')
        
    if len(data_list_dev) > 0:
        report = ArtifactHtmlReport('Life360 - Device Battery')
        report.start_artifact_report(report_folder, 'Life360 - Device Battery')
        report.add_script()
        data_headers = ('Timestamp', 'Device Battery (%)', 'Charging')

        report.write_artifact_data_table(data_headers, data_list_dev, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Life360 - Device Battery'
        tsv(report_folder, data_headers, data_list_dev, tsvname)
        
        tlactivity = 'Life360 - Device Battery'
        timeline(report_folder, tlactivity, data_list_dev, data_headers)
        
    else:
        logfunc('No Life360 - Device Battery data available')