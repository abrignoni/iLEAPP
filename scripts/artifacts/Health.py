# Module Description: Parses Apple Health details
# Author: @KevinPagano3
# Date: 2022-08-15
# Artifact version: 0.0.3
# Requirements: none

# Queries are a derivitive of research provided by Heather Mahalik and Jared Barnhart as part of their SANS DFIR Summit 2022 talk
# as well as research provided by Sarah Edwards as part of her APOLLO project.
# https://for585.com/dfirsummit22
# https://github.com/mac4n6/APOLLO

# Updates: @JohannPLW
# Date: 2023-03-02

import sqlite3
import textwrap
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

from scripts.builds_ids import OS_build, device_id

og_os_build = ''
local_os_build = ''

def get_Health(files_found, report_folder, seeker, wrap_text):

    healthdb_secure = ''
    healthdb = ''
    source_file_healthdb_secure = ''
    source_file_healthdb = ''
   
    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('healthdb_secure.sqlite'):
           healthdb_secure = str(file_found)
           source_file_healthdb_secure = file_found.replace(seeker.directory, '')

        if file_name.endswith('healthdb.sqlite'):
           healthdb = str(file_found)
           source_file_healthdb = file_found.replace(seeker.directory, '')
   
    db = open_sqlite_db_readonly(healthdb_secure)
    cursor = db.cursor()
    
    iOS_version = scripts.artifacts.artGlobals.versionf
    if version.parse(iOS_version) <= version.parse("16"):
        cursor.execute('''
        SELECT
        DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "START DATE",
        DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH') AS "END DATE",
        CASE WORKOUTS.ACTIVITY_TYPE
        WHEN 1 THEN "AMERICAN FOOTBALL"
        WHEN 2 THEN "ARCHERY"
        WHEN 3 THEN "AUSTRALIAN FOOTBALL"
        WHEN 4 THEN "BADMINTON"
        WHEN 5 THEN "BASEBALL"
        WHEN 6 THEN "BASKETBALL"
        WHEN 7 THEN "BOWLING"
        WHEN 8 THEN "BOXING"
        WHEN 9 THEN "CLIMBING"
        WHEN 10 THEN "CRICKET"
        WHEN 11 THEN "CROSS TRAINING"
        WHEN 12 THEN "CURLING"
        WHEN 13 THEN "CYCLING"
        WHEN 16 THEN "ELLIPTICAL"
        WHEN 17 THEN "EQUESTRIAN SPORTS"
        WHEN 18 THEN "FENCING"
        WHEN 19 THEN "FISHING"
        WHEN 20 THEN "FUNCTION STRENGTH TRAINING"
        WHEN 21 THEN "GOLF"
        WHEN 22 THEN "GYMNASTICS"
        WHEN 23 THEN "HANDBALL"
        WHEN 24 THEN "HIKING"
        WHEN 25 THEN "HOCKEY"
        WHEN 26 THEN "HUNTING"
        WHEN 27 THEN "LACROSS"
        WHEN 28 THEN "MARTIAL ARTS"
        WHEN 29 THEN "MIND AND BODY"
        WHEN 31 THEN "PADDLE SPORTS"
        WHEN 32 THEN "PLAY"
        WHEN 33 THEN "PREPARATION AND RECOVERY"
        WHEN 34 THEN "RACQUETBALL"
        WHEN 35 THEN "ROWING"
        WHEN 36 THEN "RUGBY"
        WHEN 37 THEN "RUNNING"
        WHEN 38 THEN "SAILING"
        WHEN 39 THEN "SKATING SPORTS"
        WHEN 40 THEN "SNOW SPORTS"
        WHEN 41 THEN "SOCCER"
        WHEN 42 THEN "SOFTBALL"
        WHEN 43 THEN "SQUASH"
        WHEN 44 THEN "STAIRSTEPPER"
        WHEN 45 THEN "SURFING SPORTS"
        WHEN 46 THEN "SWIMMING"
        WHEN 47 THEN "TABLE TENNIS"
        WHEN 48 THEN "TENNIS"
        WHEN 49 THEN "TRACK AND FIELD"
        WHEN 50 THEN "TRADITIONAL STRENGTH TRAINING"
        WHEN 51 THEN "VOLLEYBALL"
        WHEN 52 THEN "WALKING"
        WHEN 53 THEN "WATER FITNESS"
        WHEN 54 THEN "WATER POLO"
        WHEN 55 THEN "WATER SPORTS"
        WHEN 56 THEN "WRESTLING"
        WHEN 57 THEN "YOGA"
        WHEN 58 THEN "BARRE"
        WHEN 59 THEN "CORE TRAINING"
        WHEN 60 THEN "CROSS COUNTRY SKIING"
        WHEN 61 THEN "DOWNHILL SKIING"
        WHEN 62 THEN "FLEXIBILITY"
        WHEN 63 THEN "HIGH INTENSITY INTERVAL TRAINING (HIIT)"
        WHEN 64 THEN "JUMP ROPE"
        WHEN 65 THEN "KICKBOXING"
        WHEN 66 THEN "PILATES"
        WHEN 67 THEN "SNOWBOARDING"
        WHEN 68 THEN "STAIRS"
        WHEN 69 THEN "STEP TRAINING"
        WHEN 70 THEN "WHEELCHAIR WALK PACE"
        WHEN 71 THEN "WHEELCHAIR RUN PACE"
        WHEN 72 THEN "TAI CHI"
        WHEN 73 THEN "MIXED CARDIO"
        WHEN 74 THEN "HAND CYCLING"
        WHEN 3000 THEN "OTHER"  
        ELSE "UNKNOWN" || "-" || WORKOUTS.ACTIVITY_TYPE
        END "WORKOUT TYPE",
        strftime('%H:%M:%S',WORKOUTS.DURATION, 'unixepoch') AS "WORKOUT DURATION",
        WORKOUTS.DURATION / 60.00 AS "DURATION (IN MINUTES)",
        WORKOUTS.TOTAL_DISTANCE AS "DISTANCE IN KILOMETERS",
        WORKOUTS.TOTAL_DISTANCE*0.621371 AS "DISTANCE IN MILES",
        WORKOUTS.TOTAL_ENERGY_BURNED AS "CALORIES BURNED",
        WORKOUTS.TOTAL_BASAL_ENERGY_BURNED AS "TOTAL BASEL ENERGY BURNED",
        CASE WORKOUTS.GOAL_TYPE
        WHEN 2 THEN "MINUTES"
        WHEN 0 THEN "OPEN"
        END "GOAL TYPE",
        WORKOUTS.GOAL AS "GOAL",
        WORKOUTS.TOTAL_FLIGHTS_CLIMBED AS "FLIGHTS CLIMBED",
        WORKOUTS.TOTAL_W_STEPS AS "STEPS",
        metadata_values.string_value
        FROM SAMPLES
        LEFT OUTER JOIN METADATA_VALUES ON METADATA_VALUES.OBJECT_ID = SAMPLES.DATA_ID
        LEFT OUTER JOIN METADATA_KEYS ON METADATA_KEYS.ROWID = METADATA_VALUES.KEY_ID
        LEFT OUTER JOIN WORKOUTS ON WORKOUTS.DATA_ID = SAMPLES.DATA_ID
        WHERE WORKOUTS.ACTIVITY_TYPE NOT NULL AND (KEY IS NULL OR KEY IS "HKIndoorWorkout")
        ORDER BY "START DATE" DESC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append(
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))

            report = ArtifactHtmlReport('Health - Workouts')
            report.start_artifact_report(report_folder, 'Health - Workouts')
            report.add_script()
            data_headers = (
                'Start Timestamp', 'End Timestamp', 'Workout Type', 'Workout Duration', 'Duration (In Mintues)', 'Distance (In KM)', 'Distance (In Miles)', 'Calories Burned', 'Total Basel Energy Burned', 'Goal Type', 'Goal', 'Flights Climbed', 'Steps', 'String Value')
            report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
            report.end_artifact_report()

            tsvname = 'Health - Workouts'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Health - Workouts'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in Health - Workouts')
    else:
        logfunc("Health - Workouts: iOS 16 is not supported yet.")

    cursor.execute('''
    select
    ROWID,
    origin_product_type,
    origin_build,
    local_product_type,
    local_build,
    source_version,
    tz_name,
    source_id,
    device_id,
    sync_provenance
    from data_provenances
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        
        for row in all_rows:
        
            for key, value in OS_build.items():
                if str(row[2]) == key:
                    og_os_build = value
                    break
                else: og_os_build = row[2]
            
            for key2, value2 in OS_build.items():
                if str(row[4]) == key2:
                    local_os_build = value2
                    break
                else: local_os_build = row[4]
        
            data_list.append((row[0], row[1], og_os_build, row[3], local_os_build, row[5], row[6], row[7], row[8], row[9]))

        report = ArtifactHtmlReport('Health - Provenances')
        report.start_artifact_report(report_folder, 'Health - Provenances')
        report.add_script()
        data_headers = ('Row ID','Origin Product Type','Origin OS Build','Local Product Type','Local OS Build','Source Version','Timezone','Source ID','Device ID','Sync Provenance')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - Provenances'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - Provenances'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - Provenances')
    
    cursor.execute('''attach database "''' + healthdb + '''" as healthdb ''')
 
    cursor.execute('''
    Select
    datetime(samples.start_date+978307200,'unixepoch') as "Start Date",
    datetime(samples.end_date+978307200,'unixepoch') as "End Date",
    quantity_samples.quantity as "Decibels",
    metadata_values.string_value as "Bundle Name",
    healthdb.source_devices.name as "Device Name",
    healthdb.source_devices.manufacturer as "Device Manufacturer",
    healthdb.source_devices.model as "Device Model",
    healthdb.source_devices.localIdentifier as "Local Identifier",
    metadata_keys.key as "Key",
    samples.data_id as "Data ID"
    from samples
    left outer join quantity_samples on samples.data_id = quantity_samples.data_id
    left outer join metadata_values on metadata_values.object_id = samples.data_id
    left outer join metadata_keys on metadata_keys.ROWID = metadata_values.key_id
    left outer join objects on samples.data_id = objects.data_id
    left outer join data_provenances on objects.provenance = data_provenances.ROWID
    left outer join healthdb.source_devices on healthdb.source_devices.ROWID = data_provenances.device_id
    WHERE samples.data_type = 173 AND metadata_keys.key != "_HKPrivateMetadataKeyHeadphoneAudioDataIsTransient"
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            data_list.append(
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))

        report = ArtifactHtmlReport('Health - Headphone Audio Levels')
        report.start_artifact_report(report_folder, 'Health - Headphone Audio Levels')
        report.add_script()
        data_headers = (
            'Start Timestamp', 'End Timestamp', 'Decibels', 'Bundle Name', 'Device Name', 'Device Manufacturer', 'Device Model', 'Local Identifier', 'Key', 'Data ID')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - Headphone Audio Levels'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - Headphone Audio Levels'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - Headphone Audio Levels')
        
    cursor.execute('''
    SELECT datetime('2001-01-01', samples.start_date || ' seconds') AS 'Start Date (UTC)',
    datetime('2001-01-01', samples.end_date || ' seconds') AS 'End Date (UTC)',
    CAST(round(quantity_samples.quantity * 60) AS INT) AS 'Heart Rate',
    CASE metadata_values.numerical_value
    WHEN 1.0 THEN 'Background'
    WHEN 2.0 THEN 'Streaming'
    WHEN 3.0 THEN 'Sedentary'
    WHEN 4.0 THEN 'Walking'
    WHEN 5.0 THEN 'Breathe'
    WHEN 6.0 THEN 'Workout'
    WHEN 8.0 THEN 'Background'
    WHEN 9.0 THEN 'ECG'
    WHEN 10.0 THEN 'Blood Oxygen Saturation'
    ELSE metadata_values.numerical_value
    END AS 'Heart Rate Context',
    datetime('2001-01-01', objects.creation_date || ' seconds') AS 'Date added to Health (UTC)',
    CASE healthdb.source_devices.name
    WHEN '__NONE__' THEN ''
    ELSE healthdb.source_devices.name
    END AS 'Device', 
    healthdb.source_devices.manufacturer, healthdb.source_devices.hardware, healthdb.sources.name AS 'Source',
    data_provenances.source_version AS 'Software version', data_provenances.tz_name,
    quantity_sample_series.hfd_key, quantity_sample_series.count, healthdb.sources.source_options
    FROM samples
    LEFT JOIN quantity_samples on samples.data_id = quantity_samples.data_id
    LEFT JOIN metadata_values ON samples.data_id = metadata_values.object_id
    LEFT JOIN objects ON samples.data_id = objects.data_id
    LEFT JOIN data_provenances ON objects.provenance = data_provenances.ROWID
    LEFT JOIN healthdb.sources ON data_provenances.source_id = healthdb.sources.ROWID
    LEFT JOIN healthdb.source_devices ON data_provenances.device_id = healthdb.source_devices.ROWID
    LEFT JOIN quantity_sample_series ON samples.data_id = quantity_sample_series.data_id
    WHERE samples.data_type = 5 AND objects.type != 2
    ORDER BY samples.start_date DESC
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            hardware = device_id.get(row[7], row[7])
            os_family = ''
            if row[13] == 2:
                if 'Watch' in row[7]:
                    os_family = 'watchOS '
                elif 'iPhone' in row[7]:
                    os_family = 'iOS '
            software_version = f'{os_family}{row[9]}'
            if version.parse(iOS_version) >= version.parse("15"):
                if row[11] and row[12] > 0:
                    cursor.execute('''
                    SELECT datetime('2001-01-01', quantity_series_data.timestamp || ' seconds') AS 'Date (UTC)',
                    CAST(round(quantity_series_data.value *60) AS INT)
                    FROM quantity_series_data
                    WHERE quantity_series_data.series_identifier = ''' + str(row[11]) + '''
                    ORDER BY quantity_series_data.timestamp DESC
                    ''')
                    series_rows = cursor.fetchall()
                    if len(series_rows) > 0:
                        for series_data in series_rows:
                            data_list.append((
                                series_data[0],
                                series_data[1],
                                row[3],
                                row[4],
                                row[5],
                                row[6],
                                hardware,
                                row[8],
                                software_version,
                                row[10]
                            ))
                else:
                    data_list.append((
                        row[0],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        hardware,
                        row[8],
                        software_version,
                        row[10]
                    ))
            else:
                data_list.append((
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    hardware,
                    row[8],
                    software_version,
                    row[10]
                ))

        report = ArtifactHtmlReport('Health - Heart Rate')
        report.start_artifact_report(report_folder, 'Health - Heart Rate')
        report.add_script()

        if version.parse(iOS_version) >= version.parse("15"):
            data_headers = (
                'Date (UTC)',
                'Heart Rate (BPM)',
                'Heart Rate Context',
                'Date added to Health (UTC)',
                'Device',
                'Manufacturer',
                'Hardware',
                'Source',
                'Software Version',
                'Timezone'
            )
        else:
            data_headers = (
                'Start Date (UTC)',
                'End Date (UTC)',
                'Heart Rate (BPM)',
                'Heart Rate Context',
                'Date added to Health (UTC)',
                'Device',
                'Manufacturer',
                'Hardware',
                'Source',
                'Software Version',
                'Timezone'
            )

        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - Heart Rate'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - Heart Rate'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - Heart Rate')
    
    cursor.execute('''
    SELECT datetime('2001-01-01', samples.start_date || ' seconds') AS 'Start Date (UTC)',
    datetime('2001-01-01', samples.end_date || ' seconds') AS 'End Date (UTC)',
    CAST(quantity_samples.quantity AS INT) AS 'Resting Heart Rate',
    datetime('2001-01-01', objects.creation_date || ' seconds') AS 'Date added to Health (UTC)',
    healthdb.sources.product_type, healthdb.sources.name
    FROM samples
    LEFT JOIN quantity_samples ON samples.data_id = quantity_samples.data_id
    LEFT JOIN objects ON samples.data_id = objects.data_id
    LEFT JOIN data_provenances ON objects.provenance = data_provenances.ROWID
    LEFT JOIN healthdb.sources ON data_provenances.source_id = healthdb.sources.ROWID
    WHERE samples.data_type = 118 AND quantity_samples.quantity NOT NULL
    ORDER BY samples.start_date DESC
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            hardware = device_id.get(row[4], row[4])
            data_list.append(
                (row[0], row[1], row[2], row[3], hardware, row[5]))
        
        report = ArtifactHtmlReport('Health - Resting Heart Rate')
        report.start_artifact_report(report_folder, 'Health - Resting Heart Rate')
        report.add_script()
        data_headers = (
            'Start Date (UTC)', 'End Date (UTC)', 'Resting Heart Rate (BPM)', 'Date added to Health (UTC)', 'Hardware', 'Source')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - Resting Heart Rate'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - Resting Heart Rate'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - Resting Heart Rate')



    cursor.execute('''
    select
    datetime(created_date+978307200,'unixepoch') as "Created Timestamp",
    earned_date,
    template_unique_name,
    value_in_canonical_unit,
    value_canonical_unit,
    creator_device
    from ACHAchievementsPlugin_earned_instances
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
        
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

        report = ArtifactHtmlReport('Health - Achievements')
        report.start_artifact_report(report_folder, 'Health - Achievements')
        report.add_script()
        data_headers = (
            'Created Timestamp', 'Earned Date', 'Achievement', 'Value', 'Unit', 'Creator Device')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - Achievements'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - Achievements'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - Achievements')
        
__artifacts__ = {
    "health": (
        "Health",
        ('*Health/healthdb_secure.sqlite*','*Health/healthdb.sqlite*'),
        get_Health)
}