import glob
import os
import pathlib
import plistlib
import sqlite3
import json
import textwrap
import scripts.artifacts.artGlobals
 
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist
from scripts.parse3 import ParseProto


def get_healthAll(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) >= version.parse("12"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "START DATE",
            DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH') AS "END DATE",
            METADATA_VALUES.NUMERICAL_VALUE AS "SPM (strides/min)",
            CASE WORKOUTS.ACTIVITY_TYPE 
                WHEN 63 THEN "HIGH INTENSITY INTERVAL TRAINING (HIIT)" 
                WHEN 37 THEN "INDOOR / OUTDOOR RUN" 
                WHEN 3000 THEN "OTHER" 
                WHEN 52 THEN "INDOOR / OUTDOOR WALK" 
                WHEN 20 THEN "FUNCTIONAL TRAINING" 
                WHEN 13 THEN "INDOOR CYCLE" 
                WHEN 16 THEN "ELLIPTICAL" 
                WHEN 35 THEN "ROWER"
                ELSE "UNKNOWN" || "-" || WORKOUTS.ACTIVITY_TYPE 
            END "WORKOUT TYPE", 
            WORKOUTS.DURATION / 60.00 AS "DURATION (IN MINUTES)", 
            WORKOUTS.TOTAL_ENERGY_BURNED AS "CALORIES BURNED", 
            WORKOUTS.TOTAL_DISTANCE AS "DISTANCE IN KILOMETERS",
            WORKOUTS.TOTAL_DISTANCE*0.621371 AS "DISTANCE IN MILES",  
            WORKOUTS.TOTAL_BASAL_ENERGY_BURNED AS "TOTAL BASEL ENERGY BURNED", 
            CASE WORKOUTS.GOAL_TYPE 
                WHEN 2 THEN "MINUTES" 
                WHEN 0 THEN "OPEN" 
            END "GOAL TYPE", 
            WORKOUTS.GOAL AS "GOAL", 
            WORKOUTS.TOTAL_FLIGHTS_CLIMBED AS "FLIGHTS CLIMBED", 
            WORKOUTS.TOTAL_W_STEPS AS "STEPS" 
        FROM
            SAMPLES 
            LEFT OUTER JOIN
                METADATA_VALUES 
                ON METADATA_VALUES.OBJECT_ID = SAMPLES.DATA_ID 
            LEFT OUTER JOIN
                METADATA_KEYS 
                ON METADATA_KEYS.ROWID = METADATA_VALUES.KEY_ID 
            LEFT OUTER JOIN
                WORKOUTS 
                ON WORKOUTS.DATA_ID = SAMPLES.DATA_ID 
        WHERE
            WORKOUTS.ACTIVITY_TYPE NOT NULL AND KEY IS "_HKPrivateWorkoutAverageCadence"
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))

            report = ArtifactHtmlReport('Health Workout Cadence')
            report.start_artifact_report(report_folder, 'Workout Cadence')
            report.add_script()
            data_headers = ('Start Date','End Date','Strides per Min.','Workout Type','Duration in Mins.','Calories Burned','Distance in KM','Distance in Miles','Total Base Energy','Goal Type','Goal','Flights Climbed','Steps' )   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Health Workout Cadence'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Health Workout Cadence'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Workout Cadence')
            
    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute(
        """
        SELECT
            DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "START DATE",
            DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH') AS "END DATE",
            QUANTITY AS "DISTANCE IN METERS",
            QUANTITY*3.28084 AS "DISTANCE IN FEET",
            (SAMPLES.END_DATE-SAMPLES.START_DATE) AS "TIME IN SECONDS",
            SAMPLES.DATA_ID AS "SAMPLES TABLE ID" 
        FROM
           SAMPLES 
           LEFT OUTER JOIN
              QUANTITY_SAMPLES 
              ON SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID 
           LEFT OUTER JOIN
              CORRELATIONS 
              ON SAMPLES.DATA_ID = CORRELATIONS.OBJECT 
        WHERE
           SAMPLES.DATA_TYPE = 8 
        """
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries == 0:
            logfunc('No data available in Distance')
        else:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5] ))

            description = ''
            report = ArtifactHtmlReport('Health Distance')
            report.start_artifact_report(report_folder, 'Distance', description)
            report.add_script()
            data_headers = ('Start Date','End Date','Distance in Meters','Distance in Feet','Time in Seconds','Samples Table ID' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Health Distance'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Health Distance'
            timeline(report_folder, tlactivity, data_list, data_headers)
    
    if version.parse(iOSversion) >= version.parse("12"):
        cursor = db.cursor()
        cursor.execute(
        """
        SELECT
            DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "START DATE",
            DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH') AS "END DATE",
            METADATA_VALUES.NUMERICAL_VALUE AS "ECG AVERAGE HEARTRATE",
            (SAMPLES.END_DATE-SAMPLES.START_DATE) AS "TIME IN SECONDS"
        FROM
            SAMPLES 
            LEFT OUTER JOIN
                METADATA_VALUES 
                ON METADATA_VALUES.OBJECT_ID = SAMPLES.DATA_ID 
            LEFT OUTER JOIN
                METADATA_KEYS 
                ON METADATA_KEYS.ROWID = METADATA_VALUES.KEY_ID 
            LEFT OUTER JOIN
                WORKOUTS 
                ON WORKOUTS.DATA_ID = SAMPLES.DATA_ID 
        WHERE
            KEY IS "_HKPrivateMetadataKeyElectrocardiogramHeartRate"
        """
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries == 0:
            logfunc('No data available in ECG Avg. Heart Rate')
        else:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3] ))

            description = ''
            report = ArtifactHtmlReport('Health ECG Avg Heart Rate')
            report.start_artifact_report(report_folder, 'ECG Avg. Heart Rate', description)
            report.add_script()
            data_headers = ('Start Date','End Date','ECG Avg. Heart Rate','Time in Seconds' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Health ECG Avg Heart Rate'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Health ECG Avg Heart Rate'
            timeline(report_folder, tlactivity, data_list, data_headers)

    if version.parse(iOSversion) >= version.parse("12"):    
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "START DATE",
            DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH') AS "END DATE",
            METADATA_VALUES.NUMERICAL_VALUE/100.00 AS "ELEVATION (METERS)",
            (METADATA_VALUES.NUMERICAL_VALUE/100.00)*3.28084 AS "ELEVATION (FEET)",
            CASE WORKOUTS.ACTIVITY_TYPE 
                WHEN 63 THEN "HIGH INTENSITY INTERVAL TRAINING (HIIT)" 
                WHEN 37 THEN "INDOOR / OUTDOOR RUN" 
                WHEN 3000 THEN "OTHER" 
                WHEN 52 THEN "INDOOR / OUTDOOR WALK" 
                WHEN 20 THEN "FUNCTIONAL TRAINING" 
                WHEN 13 THEN "INDOOR CYCLE" 
                WHEN 16 THEN "ELLIPTICAL" 
                WHEN 35 THEN "ROWER" 
                ELSE "UNKNOWN" || "-" || WORKOUTS.ACTIVITY_TYPE 
            END "WORKOUT TYPE", 
            WORKOUTS.DURATION / 60.00 AS "DURATION (IN MINUTES)", 
            WORKOUTS.TOTAL_ENERGY_BURNED AS "CALORIES BURNED", 
            WORKOUTS.TOTAL_DISTANCE AS "DISTANCE IN KILOMETERS",
            WORKOUTS.TOTAL_DISTANCE*0.621371 AS "DISTANCE IN MILES",  
            WORKOUTS.TOTAL_BASAL_ENERGY_BURNED AS "TOTAL BASEL ENERGY BURNED", 
                CASE WORKOUTS.GOAL_TYPE 
                    WHEN 2 THEN "MINUTES" 
                    WHEN 0 THEN "OPEN" 
                END "GOAL TYPE",
            WORKOUTS.GOAL AS "GOAL", 
            WORKOUTS.TOTAL_FLIGHTS_CLIMBED AS "FLIGHTS CLIMBED", 
            WORKOUTS.TOTAL_W_STEPS AS "STEPS" 
            FROM
            SAMPLES 
            LEFT OUTER JOIN
                METADATA_VALUES 
                ON METADATA_VALUES.OBJECT_ID = SAMPLES.DATA_ID 
            LEFT OUTER JOIN
                METADATA_KEYS 
                ON METADATA_KEYS.ROWID = METADATA_VALUES.KEY_ID 
            LEFT OUTER JOIN
                WORKOUTS 
                ON WORKOUTS.DATA_ID = SAMPLES.DATA_ID 
            WHERE
            WORKOUTS.ACTIVITY_TYPE NOT NULL AND (KEY IS "_HKPrivateWorkoutElevationAscendedQuantity" OR KEY IS "HKElevationAscended")
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))

            report = ArtifactHtmlReport('Health Workout Indoor Elevation')
            report.start_artifact_report(report_folder, 'Workout Indoor Elevation')
            report.add_script()
            data_headers = ('Start Date','End Date','Elevation in Meters','Elevation in Feet','Workout Type','Duration in Min.','Calories Burned','Distance in KM','Distance in Miles','Total Base Energy Burned','Goal Type','Goal','Flights Climbed','Steps' )   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Health Workout Indoor Elevation'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Health Workout Indoor Elevation'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No data available in Workout Indoor Elevation')
            
    if version.parse(iOSversion) >= version.parse("9"):  
        cursor = db.cursor()
        cursor.execute(
        """
        SELECT
            DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "START DATE",
            DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH') AS "END DATE",
            QUANTITY AS "FLIGHTS CLIMBED",
            (SAMPLES.END_DATE-SAMPLES.START_DATE) AS "TIME IN SECONDS",
            SAMPLES.DATA_ID AS "SAMPLES TABLE ID" 
        FROM
           SAMPLES 
           LEFT OUTER JOIN
              QUANTITY_SAMPLES 
              ON SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID 
        WHERE
           SAMPLES.DATA_TYPE = 12
        """
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []    
        if usageentries == 0:
                    logfunc('No data available in Flights Climbed')
        else:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4] ))
        
        description = ''
        report = ArtifactHtmlReport('Health Flights Climbed')
        report.start_artifact_report(report_folder, 'Flights Climbed', description)
        report.add_script()
        data_headers = ('Start Date','End Date','Flights Climbed','Time in Seconds','Samples Table ID' )     
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'Health Flights Climbed'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Health Flights Climbed'
        timeline(report_folder, tlactivity, data_list, data_headers)

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute(
        """
        SELECT
            DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "DATE",
            ORIGINAL_QUANTITY AS "HEART RATE", 
            UNIT_STRINGS.UNIT_STRING AS "UNITS",
            QUANTITY AS "QUANTITY",
            SAMPLES.DATA_ID AS "SAMPLES TABLE ID" 
        FROM
           SAMPLES 
           LEFT OUTER JOIN
              QUANTITY_SAMPLES 
              ON SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID 
           LEFT OUTER JOIN
              UNIT_STRINGS 
              ON QUANTITY_SAMPLES.ORIGINAL_UNIT = UNIT_STRINGS.ROWID 
        WHERE
           SAMPLES.DATA_TYPE = 5
        """
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        if usageentries == 0:
                logfunc('No data available in Heart Rate')
        else:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4] ))

            description = ''
            report = ArtifactHtmlReport('Health Heart Rate')
            report.start_artifact_report(report_folder, 'Heart Rate', description)
            report.add_script()
            data_headers = ('Date','Heart Rate','Units','Quantity','Samples Table ID' )     
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Health Heart Rate'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Health Heart Rate'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "START DATE",
            DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH') AS "END DATE",
            QUANTITY AS "STOOD UP",
            (SAMPLES.END_DATE-SAMPLES.START_DATE) AS "TIME IN SECONDS",
            SAMPLES.DATA_ID AS "SAMPLES TABLE ID" 
        FROM
            SAMPLES 
            LEFT OUTER JOIN
                QUANTITY_SAMPLES 
                ON SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID 
        WHERE
            SAMPLES.DATA_TYPE = 75
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4]))

            report = ArtifactHtmlReport('Health Stood Up')
            report.start_artifact_report(report_folder, 'Stood Up')
            report.add_script()
            data_headers = ('Start Date','End Date','Stood Up','TIme in Seconds','Table ID' )   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Health Stood Up'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Health Stood Up'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Stood Up')

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "START DATE",
            DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH') AS "END DATE",
            QUANTITY AS "STEPS",
            (SAMPLES.END_DATE-SAMPLES.START_DATE) AS "TIME IN SECONDS",
            SAMPLES.DATA_ID AS "SAMPLES TABLE ID" 
        FROM
            SAMPLES 
            LEFT OUTER JOIN
                QUANTITY_SAMPLES 
                ON SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID 
        WHERE
            SAMPLES.DATA_TYPE = 7     
            ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4]))

            report = ArtifactHtmlReport('Health Steps')
            report.start_artifact_report(report_folder, 'Steps')
            report.add_script()
            data_headers = ('Start Date','End Date','Steps','Time in Seconds','Samples Table ID' )   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Health Steps'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Health Steps'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Steps')

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "DATE",
            QUANTITY AS "WEIGHT (IN KG)",
            QUANTITY*2.20462 AS "WEIGHT (IN LBS)",
            SAMPLES.DATA_ID AS "SAMPLES TABLE ID" 
        FROM
            SAMPLES 
            LEFT OUTER JOIN QUANTITY_SAMPLES ON SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID 
        WHERE
            SAMPLES.DATA_TYPE = 3 
            AND "DATE" IS  NOT NULL
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3]))

            report = ArtifactHtmlReport('Health Weight')
            report.start_artifact_report(report_folder, 'Weight')
            report.add_script()
            data_headers = ('Date','Weight in KG','Weight in LBS','Samples Table ID' )   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Health Weight'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Health Weight'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Weight')

    if version.parse(iOSversion) >= version.parse("9"):
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "START DATE",
            DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH') AS "END DATE",
            CASE WORKOUTS.ACTIVITY_TYPE 
                WHEN 63 THEN "HIGH INTENSITY INTERVAL TRAINING (HIIT)" 
                WHEN 37 THEN "INDOOR / OUTDOOR RUN" 
                WHEN 3000 THEN "OTHER" 
                WHEN 52 THEN "INDOOR / OUTDOOR WALK" 
                WHEN 20 THEN "FUNCTIONAL TRAINING" 
                WHEN 13 THEN "INDOOR CYCLE" 
                WHEN 16 THEN "ELLIPTICAL" 
                WHEN 35 THEN "ROWER" 
                ELSE "UNKNOWN" || "-" || WORKOUTS.ACTIVITY_TYPE
            END "WORKOUT TYPE", 
            WORKOUTS.DURATION / 60.00 AS "DURATION (IN MINUTES)", 
            WORKOUTS.TOTAL_ENERGY_BURNED AS "CALORIES BURNED", 
            WORKOUTS.TOTAL_DISTANCE AS "DISTANCE IN KILOMETERS",
            WORKOUTS.TOTAL_DISTANCE*0.621371 AS "DISTANCE IN MILES",  
            WORKOUTS.TOTAL_BASAL_ENERGY_BURNED AS "TOTAL BASEL ENERGY BURNED", 
            CASE WORKOUTS.GOAL_TYPE 
                WHEN 2 THEN "MINUTES" 
                WHEN 0 THEN "OPEN" 
            END "GOAL TYPE",
            WORKOUTS.GOAL AS "GOAL", 
            WORKOUTS.TOTAL_FLIGHTS_CLIMBED AS "FLIGHTS CLIMBED", 
            WORKOUTS.TOTAL_W_STEPS AS "STEPS" 
        FROM
            SAMPLES 
            LEFT OUTER JOIN
                METADATA_VALUES 
                ON METADATA_VALUES.OBJECT_ID = SAMPLES.DATA_ID 
            LEFT OUTER JOIN
                METADATA_KEYS 
                ON METADATA_KEYS.ROWID = METADATA_VALUES.KEY_ID 
            LEFT OUTER JOIN
                WORKOUTS 
                ON WORKOUTS.DATA_ID = SAMPLES.DATA_ID 
        WHERE
            WORKOUTS.ACTIVITY_TYPE NOT NULL 
            AND (KEY IS NULL OR KEY IS "HKIndoorWorkout")
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))

            report = ArtifactHtmlReport('Health Workout General')
            report.start_artifact_report(report_folder, 'Workout General')
            report.add_script()
            data_headers = ('Start Date','End Date','Workout Type','Duration in Min.','Calories Burned','Distance in KM','Distance in Miles','Total Base Energy Burned','Goal Type','Goal','Flights Climbed','Steps' )   
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Health Workout General'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Health Workout General'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Workout General')
