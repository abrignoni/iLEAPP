import glob
import os
import sqlite3
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, tsv, is_platform_windows 


def get_routineDLocationsLocal(files_found, report_folder, seeker):
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) < version.parse("12"):
        logfunc("Unsupported version for RoutineD Locations Local.sqlite on iOS " + iOSversion)
    else:
        for file_found in files_found:
            file_found = str(file_found)
            
            if file_found.endswith('Local.sqlite'):
                break
                
        db = sqlite3.connect(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZENTRYDATE + 978307200, 'UNIXEPOCH') AS "ENTRY",
            DATETIME(ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZEXITDATE + 978307200, 'UNIXEPOCH') AS "EXIT",
            (ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZEXITDATE-ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZENTRYDATE)/60.00 AS "ENTRY TIME (MINUTES)",
            ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLATITUDE || ", " || ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLONGITUDE AS "COORDINATES",
            ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLATITUDE AS "LATITUDE",
            ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLONGITUDE AS "LONGITUDE",
            ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZCONFIDENCE AS "CONFIDENCE",
            ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZLOCATIONUNCERTAINTY AS "LOCATION UNCERTAINTY",
            ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZDATAPOINTCOUNT AS "DATA POINT COUNT",
            DATETIME(ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "PLACE CREATION DATE",
            DATETIME(ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZEXPIRATIONDATE + 978307200, 'UNIXEPOCH') AS "EXPIRATION",
            ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZLOCATIONLATITUDE AS "VISIT LATITUDE",
            ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZLOCATIONLONGITUDE AS "VISIT LONGITUDE",
            ZRTLEARNEDLOCATIONOFINTERESTVISITMO.Z_PK AS "ZRTLEARNEDLOCATIONOFINTERESTVISITMO TABLE ID" 
        FROM
            ZRTLEARNEDLOCATIONOFINTERESTVISITMO 
            LEFT JOIN
                ZRTLEARNEDLOCATIONOFINTERESTMO 
                ON ZRTLEARNEDLOCATIONOFINTERESTMO.Z_PK = ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZLOCATIONOFINTEREST
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))
            
            description = 'Significant Locations - Location of Interest Entry (Historical)'
            report = ArtifactHtmlReport('Locations')
            report.start_artifact_report(report_folder, 'RoutineD Locations Entry', description)
            report.add_script()
            data_headers = ('Entry','Exit','Entry Time (Minutes)','Coordinates','Latitude', 'Longitude','Confidence','Location Uncertainty','Data Point Count','Place Creation Date','Expiration','Visit latitude', 'Visit Longitude', 'Table ID' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'RoutineD Locations Entry'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'RoutineD Locations Entry'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No RoutineD Significant Locations Entry data available')
            
        
        cursor.execute('''
        SELECT
               DATETIME(ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZENTRYDATE + 978307200, 'UNIXEPOCH') AS "ENTRY",
               DATETIME(ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZEXITDATE + 978307200, 'UNIXEPOCH') AS "EXIT",
               (ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZEXITDATE-ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZENTRYDATE)/60.00 AS "EXIT TIME (MINUTES)",
               ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLATITUDE || ", " || ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLONGITUDE AS "COORDINATES",
               ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLATITUDE AS "LATITUDE",
               ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLONGITUDE AS "LONGITUDE",
               ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZCONFIDENCE AS "CONFIDENCE",
               ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZLOCATIONUNCERTAINTY AS "LOCATION UNCERTAINTY",
               ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZDATAPOINTCOUNT AS "DATA POINT COUNT",
               DATETIME(ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "PLACE CREATION DATE",
               DATETIME(ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZEXPIRATIONDATE + 978307200, 'UNIXEPOCH') AS "EXPIRATION",
               ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZLOCATIONLATITUDE AS "VISIT LATITUDE",
               ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZLOCATIONLONGITUDE AS "VISIT LONGITUDE",
               ZRTLEARNEDLOCATIONOFINTERESTVISITMO.Z_PK AS "ZRTLEARNEDLOCATIONOFINTERESTVISITMO TABLE ID" 
            FROM
               ZRTLEARNEDLOCATIONOFINTERESTVISITMO 
               LEFT JOIN
                  ZRTLEARNEDLOCATIONOFINTERESTMO 
                  ON ZRTLEARNEDLOCATIONOFINTERESTMO.Z_PK = ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZLOCATIONOFINTEREST
        ''')

        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))
            
            description = 'Significant Locations - Location of Interest Exit (Historical)'
            report = ArtifactHtmlReport('Locations')
            report.start_artifact_report(report_folder, 'RoutineD Locations Exit', description)
            report.add_script()
            data_headers = ('Entry','Exit','Entry Time (Minutes)','Coordinates','Latitude', 'Longitude','Confidence','Location Uncertainty','Data Point Count','Place Creation Date','Expiration','Visit latitude', 'Visit Longitude', 'Table ID' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'RoutineD Locations Exit'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'RoutineD Locations Exit'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No RoutineD Significant Locations Exit data available')
            
        if version.parse(iOSversion) >= version.parse("12"):
          cursor.execute('''
          SELECT
                  DATETIME(ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZENTRYDATE + 978307200, 'UNIXEPOCH') AS "ENTRY",
                  DATETIME(ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZEXITDATE + 978307200, 'UNIXEPOCH') AS "EXIT",
                  (ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZEXITDATE-ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZENTRYDATE)/60.00 AS "EXIT TIME (MINUTES)",
                  ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLATITUDE || ", " || ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLONGITUDE AS "COORDINATES",
                  ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLATITUDE AS "LATITUDE",
                  ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLONGITUDE AS "LONGITUDE",
                  ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZCONFIDENCE AS "CONFIDENCE",
                  ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZLOCATIONUNCERTAINTY AS "LOCATION UNCERTAINTY",
                  ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZDATAPOINTCOUNT AS "DATA POINT COUNT",
                  DATETIME(ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "PLACE CREATION DATE",
                  DATETIME(ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZEXPIRATIONDATE + 978307200, 'UNIXEPOCH') AS "EXPIRATION",
                  ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZLOCATIONLATITUDE AS "VISIT LATITUDE",
                  ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZLOCATIONLONGITUDE AS "VISIT LONGITUDE",
                  ZRTLEARNEDLOCATIONOFINTERESTVISITMO.Z_PK AS "ZRTLEARNEDLOCATIONOFINTERESTVISITMO TABLE ID" 
              FROM
                  ZRTLEARNEDLOCATIONOFINTERESTVISITMO 
                  LEFT JOIN
                    ZRTLEARNEDLOCATIONOFINTERESTMO 
                    ON ZRTLEARNEDLOCATIONOFINTERESTMO.Z_PK = ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZLOCATIONOFINTEREST       
          ''')

          all_rows = cursor.fetchall()
          usageentries = len(all_rows)
          data_list = []    
          if usageentries > 0:
              for row in all_rows:
                  data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
              
              description = 'Significant Locations - Location of Interest Transition Start (Historical)'
              report = ArtifactHtmlReport('Locations')
              report.start_artifact_report(report_folder, 'RoutineD Transtition Start', description)
              report.add_script()
              data_headers = ('Start','Stop','Transition Time (Minutes)','Coordinates','Creation Date', 'Expiration','Latitude','Longitude', 'Table ID' )     
              report.write_artifact_data_table(data_headers, data_list, file_found)
              report.end_artifact_report()
              
              tsvname = 'RoutineD Transtition Start'
              tsv(report_folder, data_headers, data_list, tsvname)
              
              tlactivity = 'RoutineD Transtition Start'
              timeline(report_folder, tlactivity, data_list, data_headers)

          else:
              logfunc('No RoutineD Significant Locations Transtition Start data available')

        if (version.parse(iOSversion) >= version.parse("11")) and (version.parse(iOSversion) < version.parse("12")):
          cursor.execute('''
          ELECT
               DATETIME(ZRTLEARNEDLOCATIONOFINTERESTTRANSITIONMO.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS "START",
               DATETIME(ZRTLEARNEDLOCATIONOFINTERESTTRANSITIONMO.ZSTOPDATE + 978307200, 'UNIXEPOCH') AS "STOP",
               (ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZEXITDATE-ZRTLEARNEDLOCATIONOFINTERESTVISITMO.ZENTRYDATE)/60.00 AS "TRANSITION TIME (MINUTES)",
               ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLATITUDE || ", " || ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLONGITUDE AS "COORDINATES",
               DATETIME(ZRTLEARNEDLOCATIONOFINTERESTTRANSITIONMO.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS "CREATION DATE",
               DATETIME(ZRTLEARNEDLOCATIONOFINTERESTTRANSITIONMO.ZEXPIRATIONDATE + 978307200, 'UNIXEPOCH') AS "EXPIRATION",
               ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLATITUDE AS "LATITUDE",
               ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLONGITUDE AS "LONGITUDE",
               ZRTLEARNEDLOCATIONOFINTERESTTRANSITIONMO.Z_PK AS "ZRTLEARNEDLOCATIONOFINTERESTTRANSITIONMO TABLE ID" 
            FROM
               ZRTLEARNEDLOCATIONOFINTERESTTRANSITIONMO 
               LEFT JOIN
                  ZRTLEARNEDLOCATIONOFINTERESTMO 
                  ON ZRTLEARNEDLOCATIONOFINTERESTMO.Z_PK = ZRTLEARNEDLOCATIONOFINTERESTTRANSITIONMO.ZLOCATIONOFINTEREST
          ''')

          all_rows = cursor.fetchall()
          usageentries = len(all_rows)
          data_list = []    
          if usageentries > 0:
              for row in all_rows:
                  data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
              
              description = 'Significant Locations - Location of Interest Transition Stop (Historical)'
              report = ArtifactHtmlReport('Locations')
              report.start_artifact_report(report_folder, 'RoutineD Transtition Stop', description)
              report.add_script()
              data_headers = ('Start','Stop','Transition Time (Minutes)','Coordinates','Creation Date', 'Expiration','Latitude','Longitude', 'Table ID' )     
              report.write_artifact_data_table(data_headers, data_list, file_found)
              report.end_artifact_report()
              
              tsvname = 'RoutineD Transtition Stop'
              tsv(report_folder, data_headers, data_list, tsvname)
              
              tlactivity = 'RoutineD Transtition Stop'
              timeline(report_folder, tlactivity, data_list, data_headers)

          else:
              logfunc('No RoutineD Significant Locations Transtition Stop data available')
            
            
        
