import glob
import os
import sqlite3
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows 


def get_routineDlocations(files_found, report_folder, seeker):
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) < version.parse("10"):
        logfunc("Unsupported version for RoutineD Locations Cache.sqlite on iOS " + iOSversion)
    else:
        for file_found in files_found:
            file_found = str(file_found)
            
            if file_found.endswith('Cache.sqlite'):
                break
                
        db = sqlite3.connect(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(ZTIMESTAMP + 978307200, 'UNIXEPOCH') AS "TIMESTAMP",
            ZLATITUDE || ", " || ZLONGITUDE AS "COORDINATES",
            ZALTITUDE AS "ALTITUDE",
            ZCOURSE AS "COURSE",
            ZSPEED AS "SPEED (M/S)",
            ZSPEED*2.23694 AS "SPEED (MPH)",
            ZSPEED*3.6 AS "SPEED (KMPH)",
            ZHORIZONTALACCURACY AS "HORIZONTAL ACCURACY",
            ZVERTICALACCURACY AS "VERTICAL ACCURACY",
            ZLATITUDE AS "LATITUDE",
            ZLONGITUDE AS "LONGITUDE",
            ZRTCLLOCATIONMO.Z_PK AS "ZRTCLLOCATIONMO TABLE ID" 
            FROM
            ZRTCLLOCATIONMO
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]))
            
            description = 'Granular location data (~ 1 week)'
            report = ArtifactHtmlReport('Locations')
            report.start_artifact_report(report_folder, 'RoutineD ZRTCLLOCATIONMO', description)
            report.add_script()
            data_headers = ('Timestamp','Coordinates','Altitude','Course','Speed (M/S)', 'Speed (MPH)','Speed (KMPH)','Horizontal Accuracy','Vertical Accuracy','Latitude','Longitude','Table ID' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'RoutineD ZRTCLLOCATIONMO'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'RoutineD ZRTCLLOCATIONMO'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No RoutineD ZRTCLLOCATIONMO data available')
            
        
        cursor.execute('''
        SELECT
            DATETIME(ZDATE + 978307200, 'UNIXEPOCH') AS "TIMESTAMP",
            ZLATITUDE || ", " || ZLONGITUDE AS "COORDINATES",
            ZSOURCE AS "SOURCE",
            ZLATITUDE AS "LATITUDE",
            ZLONGITUDE AS "LONGITUDE",
            ZRTHINTMO.Z_PK AS "ZRTHINTMO TABLE ID" 
        FROM
            ZRTHINTMO 
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
            
            description = 'Semi-granular location data (~ 1 week)'
            report = ArtifactHtmlReport('Locations')
            report.start_artifact_report(report_folder, 'RoutineD ZRTHINTMO', description)
            report.add_script()
            data_headers = ('Timestamp','Coordinates','Source','Latitude','Longitude','Table ID' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'RoutineD ZRTHINTMO'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'RoutineD ZRTHINTMO'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No RoutineD ZRTHINTMO data available')
            
        cursor.execute('''
        SELECT
                DATETIME(ZENTRYDATE + 978307200, 'UNIXEPOCH') AS "ENTRY TIMESTAMP",
                DATETIME(ZEXITDATE + 978307200, 'UNIXEPOCH') AS "EXIT TIMESTAMP",
                ZLOCATIONLATITUDE || ", " ||   ZLOCATIONLONGITUDE AS "COORDINATES",
                DATETIME(ZDETECTIONDATE + 978307200, 'UNIXEPOCH') AS "DETECTION TIMESTAMP",
                (ZEXITDATE-ZENTRYDATE)/60.00 AS "VISIT TIME (MINUTES)",
                ZTYPE AS "TYPE",
                ZLOCATIONLATITUDE AS "LATITUDE",
                ZLOCATIONLONGITUDE AS "LONGITUDE",
                ZLOCATIONUNCERTAINTY AS "UNCERTAINTY",
                ZDATAPOINTCOUNT AS "DATA POINT COUNT",
                Z_PK AS "ZRTVISITMO TABLE ID" 
            FROM
                ZRTVISITMO
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
            
            description = 'Visit locations'
            report = ArtifactHtmlReport('Locations')
            report.start_artifact_report(report_folder, 'RoutineD ZRTVISITMO', description)
            report.add_script()
            data_headers = ('Entry Timestamp','Exit Timestamp','Coordinates','Detection Timestamp','Visit Time (Minutes)', 'Type','Latitude','Longitude','Uncertainty','Data Point Count', 'Table ID' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'RoutineD ZRTVISITMO'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'RoutineD ZRTVISITMO'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No RoutineD ZRTVISITMO data available')
            
            
            
