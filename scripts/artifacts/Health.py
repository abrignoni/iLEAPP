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

    cursor.execute('''attach database "''' + healthdb + '''" as healthdb ''')

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

    query = ""
    data_headers = ()

    iOS_version = scripts.artifacts.artGlobals.versionf
    if version.parse(iOS_version) < version.parse("16"):
        query = '''
        SELECT 
        DATETIME(SAMPLES.START_DATE + 978307200, 'UNIXEPOCH') AS "START DATE",
        DATETIME(SAMPLES.END_DATE + 978307200, 'UNIXEPOCH') AS "END DATE",
        CASE
            WHEN CAST((strftime('%s', samples.end_date - samples.start_date, 'UNIXEPOCH')) % 86400 % 3600 / 60 AS TEXT) = 1
            THEN CAST((strftime('%s', samples.end_date - samples.start_date, 'UNIXEPOCH')) % 86400 % 3600 / 60 AS TEXT) || " minute and "
            WHEN CAST((strftime('%s', samples.end_date - samples.start_date, 'UNIXEPOCH')) % 86400 % 3600 / 60 AS TEXT) != 1
            THEN CAST((strftime('%s', samples.end_date - samples.start_date, 'UNIXEPOCH')) % 86400 % 3600 / 60 AS TEXT) || " minutes and "
            END || 
        CASE
            WHEN ((SUBSTR((datetime(samples.end_date + 978307200, 'UNIXEPOCH')),18,2)) - (SUBSTR((datetime(samples.start_date + 978307200, 'UNIXEPOCH')),18,2))) = 1
            THEN (((SUBSTR((datetime(samples.end_date + 978307200, 'UNIXEPOCH')),18,2)) - (SUBSTR((datetime(samples.start_date + 978307200, 'UNIXEPOCH')),18,2))) || " second")
            WHEN ((SUBSTR((datetime(samples.end_date + 978307200, 'UNIXEPOCH')),18,2)) - (SUBSTR((datetime(samples.start_date + 978307200, 'UNIXEPOCH')),18,2))) > 0
            THEN (((SUBSTR((datetime(samples.end_date + 978307200, 'UNIXEPOCH')),18,2)) - (SUBSTR((datetime(samples.start_date + 978307200, 'UNIXEPOCH')),18,2))) || " seconds")
            WHEN ((SUBSTR((datetime(samples.end_date + 978307200, 'UNIXEPOCH')),18,2)) - (SUBSTR((datetime(samples.start_date + 978307200, 'UNIXEPOCH')),18,2))) = 0
            THEN (((SUBSTR((datetime(samples.end_date + 978307200, 'UNIXEPOCH')),18,2)) - (SUBSTR((datetime(samples.start_date + 978307200, 'UNIXEPOCH')),18,2))) || " seconds")
            WHEN ((SUBSTR((datetime(samples.end_date + 978307200, 'UNIXEPOCH')),18,2)) - (SUBSTR((datetime(samples.start_date + 978307200, 'UNIXEPOCH')),18,2))) < 0
            THEN CASE 
                WHEN (((SUBSTR((datetime(samples.end_date + 978307200, 'UNIXEPOCH')),18,2)) - (SUBSTR((datetime(samples.start_date + 978307200, 'UNIXEPOCH')),18,2))) + 60) = 1
                THEN (((SUBSTR((datetime(samples.end_date + 978307200, 'UNIXEPOCH')),18,2)) - (SUBSTR((datetime(samples.start_date + 978307200, 'UNIXEPOCH')),18,2))) + 60) || " second"
                WHEN (((SUBSTR((datetime(samples.end_date + 978307200, 'UNIXEPOCH')),18,2)) - (SUBSTR((datetime(samples.start_date + 978307200, 'UNIXEPOCH')),18,2))) + 60) != 1
                THEN (((SUBSTR((datetime(samples.end_date + 978307200, 'UNIXEPOCH')),18,2)) - (SUBSTR((datetime(samples.start_date + 978307200, 'UNIXEPOCH')),18,2))) + 60) || " seconds"
                END
            END as "TOTAL TIME DURATION",
        CASE
            WHEN CAST((strftime('%s', workouts.duration, 'UNIXEPOCH')) % 86400 % 3600 / 60 AS TEXT) = 1
            THEN CAST((strftime('%s', workouts.duration, 'UNIXEPOCH')) % 86400 % 3600 / 60 AS TEXT) || " minute and "
            WHEN CAST((strftime('%s', workouts.duration, 'UNIXEPOCH')) % 86400 % 3600 / 60 AS TEXT) != 1
            THEN CAST((strftime('%s', workouts.duration, 'UNIXEPOCH')) % 86400 % 3600 / 60 AS TEXT) || " minutes and "
            END || 
            CASE
                WHEN CAST((strftime('%s', workouts.duration, 'UNIXEPOCH')) % 86400 % 3600 % 60 AS TEXT) = 1
                THEN CAST((strftime('%s', workouts.duration, 'UNIXEPOCH')) % 86400 % 3600 % 60 AS TEXT) || " second"
                WHEN CAST((strftime('%s', workouts.duration, 'UNIXEPOCH')) % 86400 % 3600 % 60 AS TEXT) != 1
                THEN CAST((strftime('%s', workouts.duration, 'UNIXEPOCH')) % 86400 % 3600 % 60 AS TEXT) || " seconds"
            END as "WORKOUT DURATION",
        CASE WORKOUTS.ACTIVITY_TYPE''' + activity_types + '''
        ELSE "Unknown" || "-" || WORKOUTS.ACTIVITY_TYPE
        END "WORKOUT TYPE",
        MAX(CASE 
            WHEN METADATA_KEYS.KEY = '_HKPrivateWorkoutWeatherLocationCoordinatesLatitude'
            THEN METADATA_VALUES.NUMERICAL_VALUE
            ELSE NULL
            END) as "LATITUDE",
        MAX(CASE 
            WHEN METADATA_KEYS.KEY = '_HKPrivateWorkoutWeatherLocationCoordinatesLongitude'
            THEN METADATA_VALUES.NUMERICAL_VALUE
            ELSE NULL
            END) as "LONGITUDE",
        WORKOUTS.TOTAL_DISTANCE AS "DISTANCE IN KILOMETERS",
        WORKOUTS.TOTAL_DISTANCE*0.621371 AS "DISTANCE IN MILES",
        WORKOUTS.TOTAL_ENERGY_BURNED AS "CALORIES BURNED",
        WORKOUTS.TOTAL_BASAL_ENERGY_BURNED AS "TOTAL BASEL ENERGY BURNED",
        CASE WORKOUTS.GOAL_TYPE ''' + goal_types + '''
        END "GOAL TYPE",
        WORKOUTS.GOAL AS "GOAL",
        WORKOUTS.TOTAL_FLIGHTS_CLIMBED AS "FLIGHTS CLIMBED",
        WORKOUTS.TOTAL_W_STEPS AS "STEPS",
        MAX(CASE 
            WHEN METADATA_KEYS.KEY = 'HKTimeZone'
            THEN METADATA_VALUES.STRING_VALUE
            ELSE NULL
            END) AS "TIME ZONE",
        SUBSTR(MAX(CASE 
            WHEN METADATA_KEYS.KEY = 'HKWeatherTemperature'
            THEN METADATA_VALUES.NUMERICAL_VALUE
            ELSE NULL
            END),1,5) || "°F" AS "TEMPERATURE",
        SUBSTR((MAX(CASE 
            WHEN METADATA_KEYS.KEY = 'HKWeatherHumidity'
            THEN METADATA_VALUES.NUMERICAL_VALUE
            ELSE NULL
            END)),
            (INSTR((MAX(CASE 
            WHEN METADATA_KEYS.KEY = 'HKWeatherHumidity'
            THEN METADATA_VALUES.NUMERICAL_VALUE
            ELSE NULL
            END)),'.')), -3) || "%" AS "HUMIDITY"
        FROM SAMPLES
        LEFT OUTER JOIN METADATA_VALUES ON SAMPLES.DATA_ID = METADATA_VALUES.OBJECT_ID 
        LEFT OUTER JOIN METADATA_KEYS ON METADATA_KEYS.ROWID = METADATA_VALUES.KEY_ID 
        LEFT OUTER JOIN WORKOUTS ON SAMPLES.DATA_ID = WORKOUTS.DATA_ID 
        LEFT OUTER JOIN QUANTITY_SAMPLES ON SAMPLES.DATA_ID = QUANTITY_SAMPLES.DATA_ID 
        LEFT OUTER JOIN OBJECTS ON SAMPLES.DATA_ID = OBJECTS.DATA_ID 
        LEFT OUTER JOIN DATA_PROVENANCES ON OBJECTS.PROVENANCE = DATA_PROVENANCES.ROWID 
        WHERE WORKOUTS.ACTIVITY_TYPE NOT NULL
        GROUP BY OBJECT_ID
        ORDER BY "START DATE" DESC
        '''
        
        data_headers = (
            'Start Timestamp', 'End Timestamp', 'Total Time Duration', 'Workout Duration', 'Workout Type', 'Latitude',  
            'Longitude', 'Distance (In KM)', 'Distance (In Miles)', 'Calories Burned', 'Total Basel Energy Burned', 
            'Goal Type', 'Goal', 'Flights Climbed', 'Steps', 'Time Zone', 'Temperature', 'Humidity')
    
    else:
        query = '''
        SELECT workout_activities.ROWID, workout_activities.owner_id,
        datetime('2001-01-01', workout_activities.start_date || ' seconds'),
        datetime('2001-01-01', workout_activities.end_date || ' seconds'),
        CASE workout_activities.activity_type''' + activity_types + '''
        ELSE "Unknown" || "-" || workout_activities.activity_type
        END,
        strftime('%H:%M:%S', workout_activities.duration, 'unixepoch'),
        printf('%.2f', workouts.total_distance),
        printf('%.2f', workouts.total_distance * 0.621371),
        CASE workouts.goal_type''' + goal_types + '''
        END,
        CAST(workouts.goal AS INT),
        healthdb.source_devices.hardware, healthdb.sources.name, data_provenances.source_version, 
        datetime('2001-01-01', objects.creation_date || ' seconds'), data_provenances.tz_name
        FROM workout_activities
        LEFT OUTER JOIN workouts ON workout_activities.owner_id = workouts.data_id
        LEFT JOIN objects ON workout_activities.owner_id = objects.data_id
        LEFT JOIN data_provenances ON objects.provenance = data_provenances.ROWID
        LEFT JOIN healthdb.sources ON data_provenances.source_id = healthdb.sources.ROWID
        LEFT JOIN healthdb.source_devices ON data_provenances.device_id = healthdb.source_devices.ROWID
        ORDER BY workout_activities.start_date
        '''
       
        statistics_query = '''
        SELECT workout_statistics.data_type, 
        printf('%.2f', workout_statistics.quantity)
        FROM workout_statistics
        WHERE workout_statistics.workout_activity_id = '''

        metadata_query = '''
        SELECT metadata_keys.key, metadata_values.numerical_value
        FROM metadata_values
        LEFT JOIN metadata_keys ON metadata_values.key_id = metadata_keys.ROWID
        WHERE metadata_values.object_id = '''

        data_headers = (
            'Start Timestamp (UTC)', 'End Timestamp (UTC)', 'Type', 'Duration', 'Distance (In KM)', 'Distance (In Miles)', 
            'Goal Type', 'Goal', 'Total Resting Energy (kcal)', 'Total Active Energy (kcal)', 'Average METs', 
            'Min. Heart Rate (BPM)', 'Max. Heart Rate (BPM)', 'Average Heart Rate (BPM)', 'Temperature (°C)', 'Temperature (°F)', 
            'Humidity (%)', 
            'Hardware', 'Source', 'Software Version', 'Date added to Health (UTC)', 
            'Timezone')

    cursor.execute(query)

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        if version.parse(iOS_version) < version.parse("16"):
            for row in all_rows:
                data_list.append(
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]))
        else:
            for row in all_rows:
                hardware = device_id.get(row[10], row[10])
                os_family = ''
                if 'Watch' in row[10]:
                    os_family = 'watchOS '
                elif 'iPhone' in row[10]:
                    os_family = 'iOS '
                software_version = f'{os_family}{row[12]}'
                resting_energy = None
                active_energy = None
                min_heart_rate = None
                max_heart_rate = None
                avg_heart_rate = None
                avg_mets = None
                temperature = None
                temp_celcius = None
                humidity = None
                
                cursor.execute(f'{statistics_query}{row[0]}')
                all_statistics = cursor.fetchall()
                if len(all_statistics) > 0:
                    for statistic in all_statistics:
                        if statistic[0] == 9:
                            resting_energy = statistic[1]
                        elif statistic[0] == 10:
                            active_energy = statistic[1]
                
                cursor.execute(f'{metadata_query}{row[1]}')
                all_metadata = cursor.fetchall()
                if len(all_metadata) > 0:
                    for metadata in all_metadata:
                        if metadata[0] == '_HKPrivateWorkoutMinHeartRate':
                            min_heart_rate = round(int(metadata[1] * 60))
                        elif metadata[0] == '_HKPrivateWorkoutMaxHeartRate':
                            max_heart_rate = round(int(metadata[1] * 60))
                        elif metadata[0] == '_HKPrivateWorkoutAverageHeartRate':
                            avg_heart_rate = round(int(metadata[1] * 60))
                        elif metadata[0] == 'HKAverageMETs':
                            avg_mets = round(metadata[1], 1)
                        elif metadata[0] == 'HKWeatherTemperature':
                            temperature = round(metadata[1], 2)
                            temp_celcius = round(((temperature - 32) * (5 / 9)), 2)
                        elif metadata[0] == 'HKWeatherHumidity':
                            humidity = metadata[1]

                data_list.append(
                    (row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], resting_energy, active_energy, 
                     avg_mets, min_heart_rate, max_heart_rate, avg_heart_rate, temp_celcius, temperature, humidity, 
                     hardware, row[11], software_version, row[13], row[14]))

        report = ArtifactHtmlReport('Health - Workouts')
        report.start_artifact_report(report_folder, 'Health - Workouts')
        report.add_script()
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
        
__artifacts__ = {
    "health": (
        "Health",
        ('*Health/healthdb_secure.sqlite*','*Health/healthdb.sqlite*'),
        get_Health)
}
