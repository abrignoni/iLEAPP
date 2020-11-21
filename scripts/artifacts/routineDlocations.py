import glob
import os
import sqlite3
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, kmlgen, is_platform_windows, open_sqlite_db_readonly


def get_routineDlocations(files_found, report_folder, seeker):
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) < version.parse("10"):
        logfunc("Unsupported version for RoutineD Locations Cache.sqlite on iOS " + iOSversion)
    else:
        for file_found in files_found:
            file_found = str(file_found)
            
            if file_found.endswith('Cache.sqlite'):
                break
                
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(ztimestamp + 978307200, 'unixepoch'),
        zaltitude,
        zcourse,
        zspeed,
        zspeed*2.23694,
        zspeed*3.6,
        zhorizontalaccuracy,
        zverticalaccuracy,
        zlatitude,
        zlongitude 
        from
        zrtcllocationmo
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
            
            description = 'Granular location data (~ 1 week)'
            report = ArtifactHtmlReport('Locations')
            report.start_artifact_report(report_folder, 'RoutineD ZRTCLLOCATIONMO', description)
            report.add_script()
            data_headers = ('Timestamp','Altitude','Course','Speed (M/S)', 'Speed (MPH)','Speed (KMPH)','Horizontal Accuracy','Vertical Accuracy','Latitude','Longitude' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'RoutineD ZRTCLLOCATIONMO'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'RoutineD ZRTCLLOCATIONMO'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            kmlactivity = 'RoutineD ZRTCLLOCATIONMO'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)

        else:
            logfunc('No RoutineD ZRTCLLOCATIONMO data available')
            
        cursor.execute('''
        select
        datetime(zdate + 978307200, 'unixepoch'),
        zsource,
        zlatitude,
        zlongitude
        from
        zrthintmo 
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3]))
            
            description = 'Semi-granular location data (~ 1 week)'
            report = ArtifactHtmlReport('Locations')
            report.start_artifact_report(report_folder, 'RoutineD ZRTHINTMO', description)
            report.add_script()
            data_headers = ('Timestamp','Source','Latitude','Longitude' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'RoutineD ZRTHINTMO'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'RoutineD ZRTHINTMO'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            kmlactivity = 'RoutineD ZRTHINTMO'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)

        else:
            logfunc('No RoutineD ZRTHINTMO data available')
        
        
        cursor.execute('''
        select
        datetime(zentrydate + 978307200, 'unixepoch'),
        datetime(zexitdate + 978307200, 'unixepoch'),
        datetime(zdetectiondate + 978307200, 'unixepoch'),
        (zexitdate-zentrydate)/60.00,
        ztype,
        zlocationlatitude,
        zlocationlongitude,
        zlocationuncertainty
        from
        zrtvisitmo
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
            
            description = 'Visit locations'
            report = ArtifactHtmlReport('Locations')
            report.start_artifact_report(report_folder, 'RoutineD ZRTVISITMO', description)
            report.add_script()
            data_headers = ('Timestamp','Exit Timestamp','Detection Timestamp','Visit Time (Minutes)', 'Type','Latitude','Longitude','Uncertainty')     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'RoutineD ZRTVISITMO'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'RoutineD ZRTVISITMO'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            kmlactivity = 'RoutineD ZRTVISITMO'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)

        else:
            logfunc('No RoutineD ZRTVISITMO data available')
            
            
            
            