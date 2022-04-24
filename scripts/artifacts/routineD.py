import glob
import os
import pathlib
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, kmlgen, timeline, is_platform_windows, open_sqlite_db_readonly


def get_routineD(files_found, report_folder, seeker):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('Cache.sqlite'):
            
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT 
            DATETIME(ztimestamp+978307200,'UNIXEPOCH'), 
            zlatitude, zlongitude, zhorizontalaccuracy
            FROM zrtcllocationmo
            ORDER BY ztimestamp ASC
            ''')
        
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []    
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3],))
                
                    description = ''
                    report = ArtifactHtmlReport('RoutineD - Cache.sqlite Geolocation')
                    report.start_artifact_report(report_folder, 'RoutineD - Cache.sqlite Geolocation', description)
                    report.add_script()
                    data_headers = ('Timestamp','Latitude','Longitude','Horizontal Accuracy')     
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                tsvname = 'RoutineD - Cache.sqlite Geolocation'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'RoutineD - Cache.sqlite Geolocation'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
                kmlactivity = 'RoutineD - Cache.sqlite Geolocation'
                kmlgen(report_folder, kmlactivity, data_list, data_headers)    
            else:
                logfunc('No RoutineD - Cache.sqlite Geolocation data available')
        
        if file_found.endswith('Local.sqlite'):
            
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT DATETIME(ztimestamp+978307200,'UNIXEPOCH'), 
            zlatitude, zlongitude, zhorizontalaccuracy
            FROM zrtcllocationmo
            ORDER BY ztimestamp ASC
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []    
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3],))
                    
                    description = ''
                    report = ArtifactHtmlReport('RoutineD - Local.sqlite Geolocation')
                    report.start_artifact_report(report_folder, 'RoutineD - Local.sqlite Geolocation', description)
                    report.add_script()
                    data_headers = ('Timestamp','Latitude','Longitude','Horizontal Accuracy')     
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                tsvname = 'RoutineD - Local.sqlite Geolocation'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'RoutineD - Local.sqlite Geolocation'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
                kmlactivity = 'RoutineD - Local.sqlite Geolocation'
                kmlgen(report_folder, kmlactivity, data_list, data_headers)    
            else:
                logfunc('No RoutineD - Local.sqlite Geolocation data available')
                
        
        if file_found.endswith('Cloud.sqlite'):
            
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT DATETIME(ztimestamp+978307200,'UNIXEPOCH'), 
            zlatitude, zlongitude, zhorizontalaccuracy
            FROM zrtcllocationmo
            ORDER BY ztimestamp ASC
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []    
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3],))
                    
                    description = ''
                    report = ArtifactHtmlReport('RoutineD - Cloud.sqlite Geolocation')
                    report.start_artifact_report(report_folder, 'RoutineD - Cloud.sqlite Geolocation', description)
                    report.add_script()
                    data_headers = ('Timestamp','Latitude','Longitude','Horizontal Accuracy')     
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                tsvname = 'RoutineD - Cloud.sqlite Geolocation'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'RoutineD - Cloud.sqlite Geolocation'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
                kmlactivity = 'RoutineD - Cloud.sqlite Geolocation'
                kmlgen(report_folder, kmlactivity, data_list, data_headers)    
            else:
                logfunc('No RoutineD - Cloud.sqlite Geolocation data available')