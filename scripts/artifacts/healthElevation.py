import glob
import os
import pathlib
import plistlib
import sqlite3
import scripts.artifacts.artGlobals #use to get iOS version -> iOSversion = scripts.artifacts.artGlobals.versionf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows 
from scripts.ccl import ccl_bplist

def get_healthElevation(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
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
        
        tsvname = 'Health Elevation'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Health Elevation'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in table')

    db.close()
    return      
    
    
