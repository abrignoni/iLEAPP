import glob
import os
import sqlite3
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, kmlgen, is_platform_windows, open_sqlite_db_readonly


def get_routineDLocationsLocal(files_found, report_folder, seeker):
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) < version.parse("12"):
        logfunc("Unsupported version for RoutineD Locations Local.sqlite on iOS " + iOSversion)
    else:
        for file_found in files_found:
            file_found = str(file_found)
            
            if file_found.endswith('Local.sqlite'):
                break
                
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        if version.parse(iOSversion) >= version.parse("14"): # Tested 14.1
            cursor.execute('''
            select
            datetime(zrtlearnedlocationofinterestvisitmo.zentrydate + 978307200, 'unixepoch'),
            datetime(zrtlearnedlocationofinterestvisitmo.zexitdate + 978307200, 'unixepoch'),
            (zrtlearnedlocationofinterestvisitmo.zexitdate-zrtlearnedlocationofinterestvisitmo.zentrydate)/60.00,
            zrtlearnedlocationofinterestmo.zlocationlatitude,
            zrtlearnedlocationofinterestmo.zlocationlongitude,
            zrtlearnedlocationofinterestvisitmo.zconfidence,
            zrtlearnedlocationofinterestvisitmo.zlocationverticaluncertainty,
            zrtlearnedlocationofinterestvisitmo.zlocationhorizontaluncertainty,
            zrtlearnedlocationofinterestvisitmo.zdatapointcount,
            datetime(zrtlearnedlocationofinterestvisitmo.zcreationdate + 978307200, 'unixepoch'),
            datetime(zrtlearnedlocationofinterestvisitmo.zexpirationdate + 978307200, 'unixepoch'),
            zrtlearnedlocationofinterestvisitmo.zlocationlatitude,
            zrtlearnedlocationofinterestvisitmo.zlocationlongitude 
            from
            zrtlearnedlocationofinterestvisitmo,
            zrtlearnedlocationofinterestmo 
            where zrtlearnedlocationofinterestmo.z_pk = zrtlearnedlocationofinterestvisitmo.zlocationofinterest
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []    
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12]))
                
                description = 'Significant Locations - Location of Interest Entry (Historical)'
                report = ArtifactHtmlReport('Locations')
                report.start_artifact_report(report_folder, 'RoutineD Locations Entry', description)
                report.add_script()
                data_headers = ('Timestamp','Exit','Entry Time (Minutes)','Latitude', 'Longitude','Confidence','Location Vertical Uncertainty','Location Horizontal Uncertainty','Data Point Count','Place Creation Date','Expiration','Visit latitude', 'Visit Longitude' )     
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'RoutineD Locations Entry'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'RoutineD Locations Entry'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
                kmlactivity = 'RoutineD Locations Entry'
                kmlgen(report_folder, kmlactivity, data_list, data_headers)

            else:
                logfunc('No RoutineD Significant Locations Entry data available')
                
        else: # < ios 14
            cursor.execute('''
            select
            datetime(zrtlearnedlocationofinterestvisitmo.zentrydate + 978307200, 'unixepoch'),
            datetime(zrtlearnedlocationofinterestvisitmo.zexitdate + 978307200, 'unixepoch'),
            (zrtlearnedlocationofinterestvisitmo.zexitdate-zrtlearnedlocationofinterestvisitmo.zentrydate)/60.00,
            zrtlearnedlocationofinterestmo.zlocationlatitude,
            zrtlearnedlocationofinterestmo.zlocationlongitude,
            zrtlearnedlocationofinterestvisitmo.zconfidence,
            zrtlearnedlocationofinterestvisitmo.zlocationuncertainty,
            zrtlearnedlocationofinterestvisitmo.zdatapointcount,
            datetime(zrtlearnedlocationofinterestvisitmo.zcreationdate + 978307200, 'unixepoch'),
            datetime(zrtlearnedlocationofinterestvisitmo.zexpirationdate + 978307200, 'unixepoch'),
            zrtlearnedlocationofinterestvisitmo.zlocationlatitude,
            zrtlearnedlocationofinterestvisitmo.zlocationlongitude
            from
            zrtlearnedlocationofinterestvisitmo,
            zrtlearnedlocationofinterestmo 
            where zrtlearnedlocationofinterestmo.z_pk = zrtlearnedlocationofinterestvisitmo.zlocationofinterest
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]))
                
                description = 'Significant Locations - Location of Interest Entry (Historical)'
                report = ArtifactHtmlReport('Locations')
                report.start_artifact_report(report_folder, 'RoutineD Locations Entry', description)
                report.add_script()
                data_headers = ('Timestamp','Exit','Entry Time (Minutes)','Latitude', 'Longitude','Confidence','Location Uncertainty','Data Point Count','Place Creation Date','Expiration','Visit latitude', 'Visit Longitude' )
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'RoutineD Locations Entry'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'RoutineD Locations Entry'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
                kmlactivity = 'RoutineD Locations Entry'
                kmlgen(report_folder, kmlactivity, data_list, data_headers)

            else:
                logfunc('No RoutineD Significant Locations Entry data available')
            
        if version.parse(iOSversion) >= version.parse("12"):
            cursor.execute('''
            select
            datetime(zrtlearnedlocationofinteresttransitionmo.zstartdate + 978307200, 'unixepoch'),
            datetime(zrtlearnedlocationofinteresttransitionmo.zstopdate + 978307200, 'unixepoch'),
            datetime(zrtlearnedlocationofinteresttransitionmo.zcreationdate + 978307200, 'unixepoch'),
            datetime(zrtlearnedlocationofinteresttransitionmo.zexpirationdate + 978307200, 'unixepoch'),
            zrtlearnedlocationofinterestmo.zlocationlatitude,
            zrtlearnedlocationofinterestmo.zlocationlongitude
            from
            zrtlearnedlocationofinteresttransitionmo 
            left join
            zrtlearnedlocationofinterestmo 
            on zrtlearnedlocationofinterestmo.z_pk = zrtlearnedlocationofinteresttransitionmo.zlocationofinterest
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []    
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
                
                description = 'Significant Locations - Location of Interest Transition Start (Historical)'
                report = ArtifactHtmlReport('Locations')
                report.start_artifact_report(report_folder, 'RoutineD Transtition Start', description)
                report.add_script()
                data_headers = ('Timestamp','Stop','Creation Date', 'Expiration','Latitude','Longitude' )     
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'RoutineD Transtition Start'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'RoutineD Transtition Start'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
                tlactivity = 'RoutineD Transtition Start'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No RoutineD Significant Locations Transtition Start data available')

        if (version.parse(iOSversion) >= version.parse("12")):
            cursor.execute('''
            select
            datetime(zrtlearnedlocationofinteresttransitionmo.zstartdate + 978307200, 'unixepoch'),
            datetime(zrtlearnedlocationofinteresttransitionmo.zstopdate + 978307200, 'unixepoch'),
            datetime(zrtlearnedlocationofinteresttransitionmo.zcreationdate + 978307200, 'unixepoch'),
            datetime(zrtlearnedlocationofinteresttransitionmo.zexpirationdate + 978307200, 'unixepoch'),
            zrtlearnedlocationofinterestmo.zlocationlatitude,
            zrtlearnedlocationofinterestmo.zlocationlongitude
            from
            zrtlearnedlocationofinteresttransitionmo, zrtlearnedlocationofinterestmo 
            where zrtlearnedlocationofinterestmo.z_pk = zrtlearnedlocationofinteresttransitionmo.zlocationofinterest
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            data_list = []    
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
                
                description = 'Significant Locations - Location of Interest Transition Stop (Historical)'
                report = ArtifactHtmlReport('Locations')
                report.start_artifact_report(report_folder, 'RoutineD Transtition Stop', description)
                report.add_script()
                data_headers = ('Timestamp','Stop','Creation Date', 'Expiration','Latitude','Longitude' )     
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'RoutineD Transtition Stop'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'RoutineD Transtition Stop'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
                tlactivity = 'RoutineD Transtition Stop'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc('No RoutineD Significant Locations Transtition Stop data available')