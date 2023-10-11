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

# Updates: @SQLMcGee
# Date: 2023-03-25 Added column within Health - Workouts for Total Time Duration
# Total Time Duration reviewed side by side with Workout Duration can show variations which could be significant within an investigation/examination
# Additional details published within "Enriching Investigations with Apple Watch Data Through the healthdb_secure.sqlite Database" at https://dfir.pubpub.org/pub/xqvcn3hj/release/1
# Height / Weight parsing added 2023-04-04

# Updates: @KevinPagano3 | @stark4n6
# Date: 2023-10-06 - Added steps details

import sqlite3
import textwrap
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

from scripts.builds_ids import OS_build, device_id

def get_Health(files_found, report_folder, seeker, wrap_text, timezone_offset):

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
        
        else:
            continue
    
    db = open_sqlite_db_readonly(healthdb_secure)
    cursor = db.cursor()

    cursor.execute('''attach database "''' + healthdb + '''" as healthdb ''')

    iOS_version = scripts.artifacts.artGlobals.versionf

    # Workouts

    activity_types = '''
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
        WHEN 75 THEN "DISC SPORTS"
        WHEN 76 THEN "FITNESS GAMING"
        WHEN 77 THEN "DANCE"
        WHEN 78 THEN "SOCIAL DANCE"
        WHEN 79 THEN "PICKLEBALL"
        WHEN 80 THEN "COOLDOWN"
        WHEN 3000 THEN "OTHER"  
    '''

    goal_types = '''
        WHEN 0 THEN "Open"
        WHEN 1 THEN "Distance in meters"
        WHEN 2 THEN "Time in seconds"
        WHEN 3 THEN "Kilocalories"
        ELSE "Unknown" || "-" || workouts.goal_type
    '''

    distance_and_goals = '''
        round(workouts.total_distance, 2) AS 'Distance (in Km)',
        round(workouts.total_distance * 0.621371, 2) AS 'Distance (in Miles)',
        CASE workouts.goal_type''' + goal_types + '''
        END AS 'Goal Type',
        CAST(workouts.goal AS INT) AS 'Goal',
    '''

    metadata = '''
        MAX(
        CASE WHEN "metadata_keys"."key" = 'HKAverageMETs' THEN round(metadata_values.numerical_value, 1) ELSE NULL
        END) AS 'Average METs',
        MAX(
        CASE WHEN "metadata_keys"."key" = '_HKPrivateWorkoutMinHeartRate' THEN CAST(round(metadata_values.numerical_value * 60) AS INT) ELSE NULL
        END) AS 'Min. Heart Rate (BPM)',
        MAX(
        CASE WHEN "metadata_keys"."key" = '_HKPrivateWorkoutMaxHeartRate' THEN CAST(round(metadata_values.numerical_value * 60) AS INT) ELSE NULL
        END) AS 'Max. Heart Rate (BPM)',
        MAX(
        CASE WHEN "metadata_keys"."key" = '_HKPrivateWorkoutAverageHeartRate' THEN CAST(round(metadata_values.numerical_value * 60) AS INT) ELSE NULL
        END) AS 'Average Heart Rate (BPM)',
        MAX(
        CASE WHEN "metadata_keys"."key" = 'HKWeatherTemperature' THEN round(metadata_values.numerical_value, 2) ELSE NULL
        END) AS 'Temperature (°F)',
        MAX(
        CASE WHEN "metadata_keys"."key" = 'HKWeatherHumidity' THEN CAST(metadata_values.numerical_value AS INT) ELSE NULL
        END) AS 'Humidity (%)',
        MAX(
        CASE WHEN "metadata_keys"."key" = '_HKPrivateWorkoutWeatherLocationCoordinatesLatitude' THEN metadata_values.numerical_value ELSE NULL
        END) AS 'Latitude',
        MAX(
        CASE WHEN "metadata_keys"."key" = '_HKPrivateWorkoutWeatherLocationCoordinatesLongitude' THEN metadata_values.numerical_value ELSE NULL
        END) AS 'Longitude',
        MAX(
        CASE WHEN "metadata_keys"."key" = '_HKPrivateWorkoutMinGroundElevation' THEN round(metadata_values.numerical_value, 2) ELSE NULL
        END) AS 'Min. ground elevation (in Meters)',
        MAX(
        CASE WHEN "metadata_keys"."key" = '_HKPrivateWorkoutMaxGroundElevation' THEN round(metadata_values.numerical_value, 2) ELSE NULL
        END) AS 'Max ground elevation (in Meters)',
    '''

    source = '''
        healthdb.source_devices.hardware AS 'Hardware',
        healthdb.sources.name AS 'Source',
        data_provenances.source_version AS 'Software Version',
        data_provenances.tz_name AS 'Timezone',
        datetime('2001-01-01', objects.creation_date || ' seconds') AS 'Timestamp added to Health (UTC)'
    '''

    if version.parse(iOS_version) < version.parse("16"):
        query = '''
        SELECT datetime('2001-01-01', samples.start_date || ' seconds') AS 'Start timestamp (UTC)',
        datetime('2001-01-01', samples.end_date || ' seconds') AS 'End timestamp (UTC)',
        CASE workouts.activity_type''' + activity_types + '''
        ELSE "Unknown" || "-" || workouts.activity_type
        END AS 'Type',
        strftime('%H:%M:%S', samples.end_date - samples.start_date, 'unixepoch') AS 'Total Time Duration',
        strftime('%H:%M:%S', workouts.duration, 'unixepoch') AS 'Duration',
        ''' + distance_and_goals + '''
        round(workouts.total_energy_burned, 2) AS 'Total Active Energy (kcal)',
        round(workouts.total_basal_energy_burned, 2) AS 'Total Resting Energy (kcal)',
        ''' + metadata + source + '''
        FROM workouts
        LEFT OUTER JOIN samples ON samples.data_id = workouts.data_id
        LEFT OUTER JOIN metadata_values ON metadata_values.object_id = workouts.data_id
        LEFT OUTER JOIN metadata_keys ON metadata_keys.ROWID = metadata_values.key_id
        LEFT OUTER JOIN objects ON objects.data_id = workouts.data_id
        LEFT OUTER JOIN data_provenances ON data_provenances.ROWID = objects.provenance
        LEFT OUTER JOIN healthdb.source_devices ON healthdb.source_devices.ROWID = data_provenances.device_id
        LEFT OUTER JOIN healthdb.sources ON healthdb.sources.ROWID = data_provenances.source_id
        GROUP BY workouts.data_id
        ORDER BY samples.start_date
        '''   
    else:
        query = '''
        SELECT datetime('2001-01-01', workout_activities.start_date || ' seconds') AS 'Start Timestamp (UTC)',
        datetime('2001-01-01', workout_activities.end_date || ' seconds') AS 'End Timestamp (UTC)',
        CASE workout_activities.activity_type''' + activity_types + '''
        ELSE "Unknown" || "-" || workout_activities.activity_type
        END AS 'Type',
        strftime('%H:%M:%S', samples.end_date - samples.start_date, 'unixepoch') AS 'Total Time Duration',
        strftime('%H:%M:%S', workout_activities.duration, 'unixepoch') AS 'Duration',
        ''' + distance_and_goals + '''
        MAX(
        CASE WHEN workout_statistics.data_type = 10 THEN round(workout_statistics.quantity, 2) ELSE NULL
        END) AS 'Total Active Energy (kcal)',
        MAX(
        CASE WHEN workout_statistics.data_type = 9 THEN round(workout_statistics.quantity, 2)  ELSE NULL
        END) AS 'Total Resting Energy (kcal)',
        ''' + metadata + source + '''
        FROM workout_activities
        LEFT OUTER JOIN workouts ON workouts.data_id = workout_activities.owner_id
        LEFT OUTER JOIN workout_statistics ON workout_statistics.workout_activity_id = workout_activities.ROWID
        LEFT OUTER JOIN metadata_values ON metadata_values.object_id = workout_activities.owner_id
        LEFT OUTER JOIN metadata_keys ON metadata_keys.ROWID = metadata_values.key_id
        LEFT OUTER JOIN objects ON objects.data_id = workout_activities.owner_id
        LEFT OUTER JOIN data_provenances ON data_provenances.ROWID = objects.provenance
        LEFT OUTER JOIN healthdb.source_devices ON healthdb.source_devices.ROWID = data_provenances.device_id
        LEFT OUTER JOIN healthdb.sources ON healthdb.sources.ROWID = data_provenances.source_id
        LEFT OUTER JOIN samples ON samples.data_id = workouts.data_id
        GROUP BY workout_activities.ROWID
        ORDER BY workout_activities.start_date
        '''
       
    cursor.execute(query)

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)

    if usageentries > 0:
        celcius_temp = None
        data_list = []
        
        for row in all_rows:
            hardware = device_id.get(row[21], row[21])
            os_family = ''
            
            if 'Watch' in row[21]:
                os_family = 'watchOS '
            elif 'iPhone' in row[21]:
                os_family = 'iOS '
            
            software_version = f'{os_family}{row[23]}'
            
            if row[15]:
                celcius_temp = round(((row[15] - 32) * (5 / 9)), 2)  
            
            data_list.append(
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], 
                row[10], row[11], row[12], row[13], row[14], celcius_temp, row[15], row[16], row[17], row[18], 
                row[19], row[20], hardware, row[22], software_version, row[24], row[25])
                )

        report = ArtifactHtmlReport('Health - Workouts')
        report.start_artifact_report(report_folder, 'Health - Workouts')
        report.add_script()
        data_headers = (
            'Start Timestamp', 'End Timestamp', 'Type', 'Total Time Duration', 'Duration', 'Distance (in KM)', 'Distance (in Miles)', 
            'Goal Type', 'Goal', 'Total Active Energy (kcal)', 'Total Resting Energy (kcal)', 'Average METs', 
            'Min. Heart Rate (BPM)', 'Max. Heart Rate (BPM)', 'Average Heart Rate (BPM)', 'Temperature (°C)', 'Temperature (°F)', 
            'Humidity (%)', 'Latitude', 'Longitude', 'Min. ground elevation (in Meters)', 'Max. ground elevation (in Meters)',
            'Hardware', 'Source', 'Software Version', 'Timezone', 'Timestamp added to Health'
            )
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - Workouts'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - Workouts'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - Workouts')

    # Provenances

    cursor.execute('''
    SELECT data_provenances.ROWID AS 'Row ID', 
    data_provenances.origin_product_type AS 'Origin Product Type',
    data_provenances.origin_build AS 'Origin OS Build',
    data_provenances.local_product_type AS 'Local Product Type',
    data_provenances.local_build AS 'Local OS Build',
    data_provenances.source_id AS 'Source ID',
    healthdb.sources.name AS ' Source Name',
    data_provenances.source_version AS 'Source Version',
    data_provenances.device_id AS 'Device ID',
    CASE
    WHEN healthdb.source_devices.name = '__NONE__' THEN '' ELSE healthdb.source_devices.name
    END AS 'Device',
    data_provenances.tz_name AS 'Timezone'
    FROM data_provenances
    LEFT OUTER JOIN healthdb.sources ON healthdb.sources.ROWID = data_provenances.source_id
    LEFT OUTER JOIN healthdb.source_devices ON healthdb.source_devices.ROWID = data_provenances.device_id
    ORDER BY data_provenances.ROWID
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)

    if usageentries > 0:
        data_list = []
        
        for row in all_rows:
            origin_product_type = device_id.get(row[1], row[1])
            origin_build = OS_build.get(row[2], row[2])
            local_product_type = device_id.get(row[3], row[3])
            local_build = OS_build.get(row[4], row[4])

            data_list.append(
                (row[0], origin_product_type, origin_build, local_product_type, local_build, row[5], row[6], 
                 row[7], row[8], row[9], row[10])
                )

        report = ArtifactHtmlReport('Health - Provenances')
        report.start_artifact_report(report_folder, 'Health - Provenances')
        report.add_script()
        data_headers = (
            'Row ID', 'Origin Product Type', 'Origin OS Build', 'Local Product Type', 'Local OS Build', 
            'Source ID', 'Source Name', 'Source Version', 'Device ID', 'Device', 'Timezone'
            )
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - Provenances'
        tsv(report_folder, data_headers, data_list, tsvname)

    else:
        logfunc('No data available in Health - Provenances')

    # Headphone Audio Levels
     
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
    
    # Heart Rate
        
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
    
    # Resting Heart Rate
    
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

    # Achievements

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
        
    # Height

    cursor.execute('''
    select
    datetime(samples.start_date+978307200,'unixepoch') as "Height Value Timestamp",
    quantity_samples.quantity as "Height (in Meters)",
    CAST((quantity_samples.quantity * 100) as INT) as "Height (in Centimeters)",
    replace(quantity_samples.quantity * '3.281', substr((quantity_samples.quantity * '3.281'),2,8),"'" ||
    rtrim((substr((substr((quantity_samples.quantity * '3.281'),2,8) * '12'),1,2)), '.') || '"') as "Height (Feet and Inches)"
    FROM samples
    LEFT OUTER JOIN quantity_samples ON samples.data_id = quantity_samples.data_id
    WHERE samples.data_type = '2'
    ORDER BY samples.start_date DESC
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
        
            data_list.append((row[0], row[1], row[2], row[3]))

        report = ArtifactHtmlReport('Health - User Entered Data - Height')
        report.start_artifact_report(report_folder, 'Health - User Entered Data - Height')
        report.add_script()
        data_headers = (
            'Height Value Timestamp', 'Height (in Meters)', 'Height (in Centimeters)', 'Height (Feet and Inches)')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - User Entered Data - Height'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - User Entered Data - Height'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - User Entered Data - Height')

    # Weight

    cursor.execute('''
    select
    datetime(samples.start_date+978307200,'unixepoch') as "Weight Value Timestamp",
    substr(quantity_samples.quantity,1,5) as "Weight (in Kilograms)",
    CASE 
        WHEN SUBSTR(CAST(ROUND(((quantity_samples.quantity / 6.35029317) - CAST(quantity_samples.quantity / 6.35029317 AS INT)) * 14) AS VARCHAR), 1, INSTR(CAST(ROUND(((quantity_samples.quantity / 6.35029317) - CAST(quantity_samples.quantity / 6.35029317 AS INT)) * 14) AS VARCHAR), '.') - 1) = '14'
        THEN ((CAST(quantity_samples.quantity / 6.35029317 AS INT) + 1) || ' Stone 0 Pounds')
        ELSE ((CAST(quantity_samples.quantity / 6.35029317 AS INT) || ' Stone ' || SUBSTR(CAST(ROUND(((quantity_samples.quantity / 6.35029317) - CAST(quantity_samples.quantity / 6.35029317 AS INT)) * 14) AS VARCHAR), 1, INSTR(CAST(ROUND(((quantity_samples.quantity / 6.35029317) - CAST(quantity_samples.quantity / 6.35029317 AS INT)) * 14) AS VARCHAR), '.') - 1) || ' Pounds')) 
        END as "Weight (in Stones and Pounds)",
    substr((quantity_samples.quantity * '2.20462262'),1,6) as "Weight (Approximate in Pounds)"
    FROM samples
    LEFT OUTER JOIN quantity_samples ON samples.data_id = quantity_samples.data_id
    WHERE samples.data_type = '3'
    ORDER BY samples.start_date DESC
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
        
            data_list.append((row[0], row[1], row[2], row[3]))

        report = ArtifactHtmlReport('Health - User Entered Data - Weight')
        report.start_artifact_report(report_folder, 'Health - User Entered Data - Weight')
        report.add_script()
        data_headers = (
            'Weight Value Timestamp', 'Weight (in Kilograms)', 'Weight (in Stone)', 'Weight (Approximate in Pounds)')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - User Entered Data - Weight'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - User Entered Data - Weight'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - User Entered Data - Weight')
        
    # Steps
    
    cursor.execute('''
    select
    datetime(samples.start_date + 978307200, 'unixepoch') as "Start Date",
    datetime(samples.end_date + 978307200, 'unixepoch') as "End Date",
    quantity_samples.quantity as "Steps",
    (samples.end_date - samples.start_date) as "Duration (Seconds)",
    data_provenances.origin_product_type as "Device"
    from samples, quantity_samples, data_provenances, objects
    where samples.data_type = 7 
    and samples.data_id = quantity_samples.data_id
    and samples.data_id = objects.data_id
    and objects.provenance = data_provenances.rowid
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            hardware = device_id.get(row[4], row[4])
            data_list.append((row[0], row[1], row[2], row[3], hardware))

        report = ArtifactHtmlReport('Health - Steps')
        report.start_artifact_report(report_folder, 'Health - Steps')
        report.add_script()
        data_headers = (
            'Start Time','End Time','Steps','Duration (Seconds)','Device')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - Steps'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - Steps'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - Steps')
    
        
__artifacts__ = {
    "health": (
        "Health",
        ('*Health/healthdb_secure.sqlite*','*Health/healthdb.sqlite*'),
        get_Health)
}
