"""
This module contains artifacts for Apple Health data
See artifacts description for more details.
"""

__artifacts_v2__ = {
    "health_workouts": {
        "name": "Health - Workouts",
        "description": "Added column within Health - Workouts for Total Time "
                       "Duration. Total Time Duration reviewed side by side "
                       "with Workout Duration can show variations which could "
                       "be significant within an investigation/examination. "
                       "Additional details published within 'Enriching "
                       "Investigations with Apple Watch Data Through the "
                       "healthdb_secure.sqlite Database' at "
                       "https://dfir.pubpub.org/pub/xqvcn3hj/release/1",
        "author": "@KevinPagano3 - @Johann-PLW - @SQLMcGee",
        "creation_date": "2022-08-15",
        "last_update_date": "2025-10-09",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "health_provenances": {
        "name": "Health - Provenances",
        "description": "Devices and Apps collecting Health data."
                       "Queries are a derivitive of research provided by Heather Mahalik "
                       "and Jared Barnhart as part of their SANS DFIR Summit 2022 talk "
                       "as well as research provided by Sarah Edwards as part of "
                       "her APOLLO project. https://for585.com/dfirsummit22 - "
                       "https://github.com/mac4n6/APOLLO",
        "author": "@KevinPagano3 - @Johann-PLW",
        "creation_date": "2022-08-15",
        "last_update_date": "2025-10-09",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "smartphone"
    },
    "health_headphone_audio_levels": {
        "name": "Health - Headphone Audio Levels",
        "description": "Headphone audio levels"
                       "Queries are a derivitive of research provided by Heather Mahalik "
                       "and Jared Barnhart as part of their SANS DFIR Summit 2022 talk "
                       "as well as research provided by Sarah Edwards as part of "
                       "her APOLLO project. https://for585.com/dfirsummit22 - "
                       "https://github.com/mac4n6/APOLLO",
        "author": "@KevinPagano3",
        "creation_date": "2022-08-24",
        "last_update_date": "2025-10-09",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "standard",
        "artifact_icon": "headphones"
    },
    "health_heart_rate": {
        "name": "Health - Heart Rate",
        "description": "Heart Rate"
                       "Queries are a derivitive of research provided by Heather Mahalik "
                       "and Jared Barnhart as part of their SANS DFIR Summit 2022 talk "
                       "as well as research provided by Sarah Edwards as part of "
                       "her APOLLO project. https://for585.com/dfirsummit22 - "
                       "https://github.com/mac4n6/APOLLO",
        "author": "@KevinPagano3 - @Johann-PLW",
        "creation_date": "2023-03-06",
        "last_update_date": "2025-10-09",
        "requirements": "none",
        "category": "Health",
        "notes": "Update: @Johann-PLW - Splitting Heart Rate and Resting Heart Rate "
                 "and adding Heart Rate Context and Provenance",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "health_resting_heart_rate": {
        "name": "Health - Resting Heart Rate",
        "description": "Resting Heart Rate"
                       "Queries are a derivitive of research provided by Heather Mahalik "
                       "and Jared Barnhart as part of their SANS DFIR Summit 2022 talk "
                       "as well as research provided by Sarah Edwards as part of "
                       "her APOLLO project. https://for585.com/dfirsummit22 - "
                       "https://github.com/mac4n6/APOLLO",
        "author": "@KevinPagano3 - @Johann-PLW",
        "creation_date": "2023-03-06",
        "last_update_date": "2025-10-09",
        "requirements": "none",
        "category": "Health",
        "notes": "Update: @Johann-PLW - Splitting Heart Rate and Resting Heart Rate "
                 "and adding Heart Rate Context and Provenance",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "health_achievements": {
        "name": "Health - Achievements",
        "description": "Health achievements"
                       "Queries are a derivitive of research provided by Heather Mahalik "
                       "and Jared Barnhart as part of their SANS DFIR Summit 2022 talk "
                       "as well as research provided by Sarah Edwards as part of "
                       "her APOLLO project. https://for585.com/dfirsummit22 - "
                       "https://github.com/mac4n6/APOLLO",
        "author": "@KevinPagano3",
        "creation_date": "2022-08-24",
        "last_update_date": "2025-10-13",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "star"
    },
    "health_steps": {
        "name": "Health - Steps",
        "description": "Health - Steps",
        "author": "@KevinPagano3",
        "creation_date": "2023-10-06",
        "last_update_date": "2025-10-13",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "health_height": {
        "name": "Health - User Entered Data - Height",
        "description": "Height entered by the user in Health"
                       "This change parses data entered by the user of the device "
                       "through the Fitness Application (Personalize Fitness and Health) "
                       "for height. Once parsed height is displayed with the timestamp "
                       "the data was entered followed by height in meters, centimeters, "
                       "feet and inches.",
        "author": "@SQLMcGee",
        "creation_date": "2023-04-04",
        "last_update_date": "2025-10-13",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "health_weight": {
        "name": "Health - User Entered Data - Weight",
        "description": "Weight entered by the user in Health"
                       "This change parses data entered by the user of the device through "
                       "the Fitness Application (Personalize Fitness and Health) for weight. """
                       "Once parsed weight is displayed with the timestamp the data was entered "
                       "followed by weight in kilograms, stones, and pounds.",
        "author": "@SQLMcGee",
        "creation_date": "2023-04-04",
        "last_update_date": "2025-10-13",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "health_watch_worn_data": {
        "name": "Health - Device - Watch Worn Data",
        "description": "Parses Apple Watch Worn Data from the healthdb_secure.sqlite database"
                       "This artifact provides an 'at a glance' review of time periods "
                       "in which the Apple Watch is worn. "
                       "This data can lend to pattern of life analysis as well as providing "
                       "structure to periods in which data such as heart rate data will be "
                       "generated and recorded. "
                       "Additional details published within 'Apple Watch Worn Data Analysis' at "
                       "https://metadataperspective.com/2024/05/20/apple-watch-worn-data-analysis/",
        "author": "@SQLMcGee for Metadata Forensics, LLC",
        "creation_date": "2024-05-20",
        "last_update_date": "2025-10-13",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "watch"
    },
    'health_all_watch_sleep_data': {
        'name': 'Health - Sleep - All Watch Sleep Data',
        'description': 'Parses Apple Health Sleep Data from the healthdb_secure.sqlite database',
        'author': '@SQLMcGee for Metadata Forensics, LLC',
        'creation_date': '2024-08-01',
        'last_update_date': '2025-10-13',
        'requirements': 'none',
        'category': 'Health',
        'notes': "This artifact provides an 'at a glance' review of sleep periods \
            when the Apple Watch is worn, given required user settings.\
            Additional details published within 'Sleepless in Cupertino: \
            A Forensic Dive into Apple Watch Sleep Tracking' at \
            https://metadataperspective.com/2024/08/01/sleepless-in-cupertino-a-\
            forensic-dive-into-apple-watch-sleep-tracking/",
        'paths': ('*Health/healthdb_secure.sqlite*',),
        'output_types': 'standard',
        'artifact_icon': 'moon'
    },
    "health_watch_by_sleep_period": {
        "name": "Health - Sleep - Watch By Sleep Period",
        "description": "Parses Apple Health Sleep Data from the healthdb_secure.sqlite database"
                       "This artifact provides an 'at a glance' review of sleep periods "
                       "when the Apple Watch is worn, given required user settings. "
                       "Additional details published within 'Sleepless in Cupertino: "
                       "A Forensic Dive into Apple Watch Sleep Tracking' at "
                       "https://metadataperspective.com/2024/08/01/sleepless-in-cupertino-a-"
                       "forensic-dive-into-apple-watch-sleep-tracking/",
        "author": "@SQLMcGee for Metadata Forensics, LLC",
        "creation_date": "2024-08-01",
        "last_update_date": "2025-10-13",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "moon"
    },
    "health_source_devices": {
        "name": "Health - Source Devices",
        "description": "Parses Apple Health device info from the healthdb.sqlite database,\
            including make/model/software information.",
        "author": "@stark4n6",
        "creation_date": "2025-03-03",
        "last_update_date": "2025-10-13",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb.sqlite*",),
        "output_types": "standard",
        "artifact_icon": "smartphone"
    },
    "health_wrist_temperature": {
        "name": "Health - Wrist Temperature",
        "description": "Parses Apple Health Wrist Temperature, as outlined within \
            Health Application > Summary > Show All Health Data > Wrist Temperature >\
            Show All Data > All Recorded Data",
        "author": "@SQLMcGee for Metadata Forensics, LLC",
        "creation_date": "2025-06-20",
        "last_update_date": "2025-10-13",
        "requirements": "none",
        "category": "Health",
        "notes": "",
        "paths": ("*Health/healthdb_secure.sqlite*", "*Health/healthdb.sqlite*"),
        "output_types": "standard",
        "artifact_icon": "thermometer"
    }
}

from packaging import version
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    attach_sqlite_db_readonly, does_table_exist_in_db, convert_cocoa_core_data_ts_to_utc


@artifact_processor
def health_workouts(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_list = []

    celcius_temp = None

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
            CASE
                WHEN "metadata_keys"."key" = 'HKAverageMETs'
                THEN round(metadata_values.numerical_value, 1)
                ELSE NULL
            END)
        AS 'Average METs',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutMinHeartRate'
                THEN CAST(round(metadata_values.numerical_value * 60) AS INT)
                ELSE NULL
            END)
        AS 'Min. Heart Rate (BPM)',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutMaxHeartRate'
                THEN CAST(round(metadata_values.numerical_value * 60) AS INT)
                ELSE NULL
            END)
        AS 'Max. Heart Rate (BPM)',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutAverageHeartRate'
                THEN CAST(round(metadata_values.numerical_value * 60) AS INT)
                ELSE NULL
            END)
        AS 'Average Heart Rate (BPM)',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = 'HKWeatherTemperature'
                THEN round(metadata_values.numerical_value, 2)
                ELSE NULL
            END)
        AS 'Temperature (°F)',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = 'HKWeatherHumidity'
                THEN CAST(metadata_values.numerical_value AS INT)
                ELSE NULL
            END)
        AS 'Humidity (%)',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutWeatherLocationCoordinatesLatitude'
                THEN metadata_values.numerical_value
                ELSE NULL
            END)
        AS 'Latitude',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutWeatherLocationCoordinatesLongitude'
                THEN metadata_values.numerical_value
                ELSE NULL
            END)
        AS 'Longitude',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutMinGroundElevation'
                THEN round(metadata_values.numerical_value, 2)
                ELSE NULL
            END)
        AS 'Min. ground elevation (in Meters)',
        MAX(
            CASE
                WHEN "metadata_keys"."key" = '_HKPrivateWorkoutMaxGroundElevation'
                THEN round(metadata_values.numerical_value, 2)
                ELSE NULL
            END)
        AS 'Max ground elevation (in Meters)',
    '''

    source = '''
        healthdb.source_devices.hardware AS 'Hardware',
        healthdb.sources.name AS 'Source',
        data_provenances.source_version AS 'Software Version',
        data_provenances.tz_name AS 'Timezone',
        objects.creation_date
    '''

    attach_query = attach_sqlite_db_readonly(healthdb, 'healthdb')

    workout_activities_exists = does_table_exist_in_db(data_source, 'workout_activities')

    if workout_activities_exists:
        query = '''
        SELECT
            workout_activities.start_date,
            workout_activities.end_date,
            CASE workout_activities.activity_type''' + activity_types + '''
                ELSE "Unknown" || "-" || workout_activities.activity_type
            END AS 'Type',
            CASE workout_activities.location_type
                WHEN 2 THEN 'Indoor'
                WHEN 3 THEN 'Outdoor'
                ELSE workout_activities.location_type
            END AS 'Location Type',
            strftime('%H:%M:%S', samples.end_date - samples.start_date, 'unixepoch') AS 'Total Time Duration',
            strftime('%H:%M:%S', workout_activities.duration, 'unixepoch') AS 'Duration',
            ''' + distance_and_goals + '''
            MAX(
                CASE
                    WHEN workout_statistics.data_type = 10 THEN round(workout_statistics.quantity, 2)
                    ELSE NULL
                END)
            AS 'Total Active Energy (kcal)',
            MAX(
                CASE
                    WHEN workout_statistics.data_type = 9 THEN round(workout_statistics.quantity, 2)
                    ELSE NULL
                END)
            AS 'Total Resting Energy (kcal)',
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
    else:
        query = '''
        SELECT
            samples.start_date,
            samples.end_date,
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

    data_headers = (
        ('Start Timestamp', 'datetime'), ('End Timestamp', 'datetime'),
        'Activity Type', 'Location Type', 'Total Time Duration', 'Duration',
        'Distance (in KM)', 'Distance (in Miles)', 'Goal Type', 'Goal',
        'Total Active Energy (kcal)', 'Total Resting Energy (kcal)', 'Average METs',
        'Min. Heart Rate (BPM)', 'Max. Heart Rate (BPM)', 'Average Heart Rate (BPM)',
        'Temperature (°C)', 'Temperature (°F)', 'Humidity (%)', 'Latitude', 'Longitude',
        'Min. ground elevation (in Meters)', 'Max. ground elevation (in Meters)',
        'Device ID', 'Device Model', 'Source', 'Software Version', 'Timezone',
        ('Timestamp added to Health', 'datetime'))

    db_records = get_sqlite_db_records(data_source, query, attach_query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        added_timestamp = convert_cocoa_core_data_ts_to_utc(record[26])
        device_model = context.get_device_model(record[22])

        if record[16]:
            celcius_temp = round(((record[16] - 32) * (5 / 9)), 2)

        data_list.append(
            (start_timestamp, end_timestamp, str(record[2]).title(), record[3],
             record[4], record[5], record[6], record[7], record[8], record[9],
             record[10], record[11], record[12], record[13], record[14],
             record[15], celcius_temp, record[16], record[17], record[18],
             record[19], record[20], record[21], record[22], device_model,
             record[23], record[24], record[25], added_timestamp)
            )

    return data_headers, data_list, data_source


@artifact_processor
def health_provenances(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_list = []

    attach_query = attach_sqlite_db_readonly(healthdb, 'healthdb')

    query = '''
    SELECT
        data_provenances.ROWID AS 'Row ID',
        data_provenances.origin_product_type AS 'Origin Product Type',
        data_provenances.origin_build AS 'Origin OS Build',
        data_provenances.local_product_type AS 'Local Product Type',
        data_provenances.local_build AS 'Local OS Build',
        data_provenances.source_id AS 'Source ID',
        healthdb.sources.name AS ' Source Name',
        data_provenances.source_version AS 'Source Version',
        data_provenances.device_id AS 'Device ID',
        CASE
            WHEN healthdb.source_devices.name = '__NONE__' THEN ''
            ELSE healthdb.source_devices.name
        END AS 'Device',
        data_provenances.tz_name AS 'Timezone'
    FROM data_provenances
    LEFT OUTER JOIN healthdb.sources ON healthdb.sources.ROWID = data_provenances.source_id
    LEFT OUTER JOIN healthdb.source_devices ON healthdb.source_devices.ROWID = data_provenances.device_id
    ORDER BY data_provenances.ROWID
    '''

    data_headers = (
        'Row ID', 'Origin Product Type', 'Origin Product Model', 'Origin OS Build',
        'Origin OS Version', 'Local Product Type', 'Local Product Model',
        'Local OS Build', 'Local OS Version', 'Source ID', 'Source Name',
        'Source Version', 'Device ID', 'Device', 'Timezone')

    db_records = get_sqlite_db_records(data_source, query, attach_query)

    for record in db_records:
        origin_device_model = context.get_device_model(record[1])
        origin_os_version = context.get_os_version(record[2], record[1])
        local_device_model = context.get_device_model(record[3])
        local_os_version = context.get_os_version(record[4], record[3])

        data_list.append(
            (record[0], record[1], origin_device_model, record[2], origin_os_version,
             record[3], local_device_model, record[4], local_os_version, record[5],
             record[6], record[7], record[8], record[9], record[10])
            )

    return data_headers, data_list, data_source


@artifact_processor
def health_headphone_audio_levels(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_list = []

    attach_query = attach_sqlite_db_readonly(healthdb, 'healthdb')

    query = '''
    SELECT
        samples.start_date,
        samples.end_date,
        quantity_samples.quantity,
        metadata_values.string_value,
        healthdb.source_devices.name,
        healthdb.source_devices.manufacturer,
        healthdb.source_devices.model,
        healthdb.source_devices.localIdentifier,
        metadata_keys.key,
        samples.data_id
    FROM samples
    LEFT OUTER JOIN quantity_samples ON samples.data_id = quantity_samples.data_id
    LEFT OUTER JOIN metadata_values ON metadata_values.object_id = samples.data_id
    LEFT OUTER JOIN metadata_keys ON metadata_keys.ROWID = metadata_values.key_id
    LEFT OUTER JOIN objects ON samples.data_id = objects.data_id
    LEFT OUTER JOIN data_provenances ON objects.provenance = data_provenances.ROWID
    LEFT OUTER JOIN healthdb.source_devices ON healthdb.source_devices.ROWID = data_provenances.device_id
    WHERE samples.data_type = 173 AND metadata_keys.key != "_HKPrivateMetadataKeyHeadphoneAudioDataIsTransient"
    '''

    data_headers = (
        ('Start Timestamp', 'datetime'), ('End Timestamp', 'datetime'), 'Decibels',
        'Bundle Name', 'Device Name', 'Device Manufacturer', 'Device Model',
        'Local Identifier', 'Key', 'Data ID')

    db_records = get_sqlite_db_records(data_source, query, attach_query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        data_list.append(
            (start_timestamp, end_timestamp, record[2], record[3], record[4],
             record[5], record[6], record[7], record[8], record[9]))

    return data_headers, data_list, data_source


@artifact_processor
def health_heart_rate(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_list = []
    os_version = context.get_installed_os_version()

    attach_query = attach_sqlite_db_readonly(healthdb, 'healthdb')

    query = '''
    SELECT
        samples.start_date,
        samples.end_date,
        CAST(round(quantity_samples.quantity * 60) AS INT),
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
        END,
        objects.creation_date,
        CASE healthdb.source_devices.name
            WHEN '__NONE__' THEN ''
            ELSE healthdb.source_devices.name
        END,
        healthdb.source_devices.manufacturer,
        healthdb.source_devices.hardware,
        healthdb.sources.name,
        data_provenances.source_version,
        data_provenances.tz_name,
        quantity_sample_series.hfd_key,
        quantity_sample_series.count,
        healthdb.sources.source_options
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
    '''

    db_records = get_sqlite_db_records(data_source, query, attach_query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        added_timestamp = convert_cocoa_core_data_ts_to_utc(record[4])
        device_model = context.get_device_model(record[7])
        if version.parse(os_version) >= version.parse("15"):
            if record[11] and record[12] > 0:
                quantity_series_data_query = '''
                SELECT
                    quantity_series_data.timestamp,
                    CAST(round(quantity_series_data.value *60) AS INT)
                FROM quantity_series_data
                WHERE quantity_series_data.series_identifier = ''' + str(record[11]) + '''
                ORDER BY quantity_series_data.timestamp DESC
                '''
                quantity_series_data_records = get_sqlite_db_records(data_source, quantity_series_data_query)
                for qsd_record in quantity_series_data_records:
                    series_data_date = convert_cocoa_core_data_ts_to_utc(qsd_record[0])
                    data_list.append(
                        (series_data_date, qsd_record[1], record[3], added_timestamp,
                         record[5], record[6], record[7], device_model, record[8],
                         record[9], record[10]))
            else:
                data_list.append(
                    (start_timestamp, record[2], record[3], added_timestamp, record[5],
                     record[6], record[7], device_model, record[8], record[9], record[10]))
        else:
            data_list.append(
                (start_timestamp, end_timestamp, record[2], record[3], added_timestamp,
                 record[5], record[6], record[7], device_model, record[8], record[9], record[10]))

    if version.parse(os_version) >= version.parse("15"):
        data_headers = (
            ('Date', 'datetime'), 'Heart Rate (BPM)', 'Heart Rate Context',
            ('Date added to Health', 'datetime'), 'Device ID', 'Device Model',
            'Manufacturer', 'Hardware', 'Source', 'Software Version', 'Timezone')
    else:
        data_headers = (
            ('Start Date', 'datetime'), ('End Date', 'datetime'), 'Heart Rate (BPM)',
            'Heart Rate Context', ('Date added to Health', 'datetime'),
            'Device ID', 'Device Model', 'Manufacturer', 'Hardware', 'Source',
            'Software Version', 'Timezone')

    return data_headers, data_list, data_source


@artifact_processor
def health_resting_heart_rate(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_list = []

    attach_query = attach_sqlite_db_readonly(healthdb, 'healthdb')

    query = '''
    SELECT
        samples.start_date,
        samples.end_date,
        CAST(quantity_samples.quantity AS INT),
        objects.creation_date,
        healthdb.sources.product_type,
        healthdb.sources.name
    FROM samples
    LEFT JOIN quantity_samples ON samples.data_id = quantity_samples.data_id
    LEFT JOIN objects ON samples.data_id = objects.data_id
    LEFT JOIN data_provenances ON objects.provenance = data_provenances.ROWID
    LEFT JOIN healthdb.sources ON data_provenances.source_id = healthdb.sources.ROWID
    WHERE samples.data_type = 118 AND quantity_samples.quantity NOT NULL
    ORDER BY samples.start_date DESC
    '''

    data_headers = (
        ('Start Date', 'datetime'), ('End Date', 'datetime'), 'Resting Heart Rate (BPM)',
        ('Date added to Health', 'datetime'), 'Hardware ID',
        'Device Model', 'Source')

    db_records = get_sqlite_db_records(data_source, query, attach_query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        added_timestamp = convert_cocoa_core_data_ts_to_utc(record[3])
        device_model = context.get_device_model(record[4])
        data_list.append(
            (start_timestamp, end_timestamp, record[2], added_timestamp, record[4],
             device_model, record[5]))

    return data_headers, data_list, data_source


@artifact_processor
def health_achievements(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        created_date,
        earned_date,
        template_unique_name,
        value_in_canonical_unit,
        value_canonical_unit,
        creator_device
    FROM ACHAchievementsPlugin_earned_instances
    '''

    data_headers = (
        ('Created Timestamp', 'datetime'), ('Earned Date', 'date'), 'Achievement',
        'Value', 'Unit', 'Creator Device')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        created_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        data_list.append((created_timestamp, record[1], record[2], record[3],
                          record[4], record[5]))

    return data_headers, data_list, data_source


@artifact_processor
def health_steps(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        samples.start_date AS "Start Date",
        samples.end_date AS "End Date",
        quantity_samples.quantity AS "Steps",
        (samples.end_date - samples.start_date) AS "Duration (Seconds)",
        data_provenances.origin_product_type AS "Device"
    FROM samples, quantity_samples, data_provenances, objects
    WHERE samples.data_type = 7
    AND samples.data_id = quantity_samples.data_id
    AND samples.data_id = objects.data_id
    AND objects.provenance = data_provenances.rowid
    '''

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'date'), 'Steps',
        'Duration (Seconds)', 'Device ID', 'Device Model')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        hardware = context.get_device_model(record[4])
        data_list.append((start_timestamp, end_timestamp, record[2], record[3],
                          record[4], hardware))

    return data_headers, data_list, data_source


@artifact_processor
def health_height(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        samples.start_date AS "Height Value Timestamp",
        quantity_samples.quantity AS "Height (in Meters)",
        CAST((quantity_samples.quantity * 100) AS INT) AS "Height (in Centimeters)",
        replace(quantity_samples.quantity * '3.281', substr(
            (quantity_samples.quantity * '3.281'),2,8),"'" ||
        rtrim((substr((substr((quantity_samples.quantity * '3.281'),2,8) * '12'),1,2)), '.')
          || '"') AS "Height (Feet and Inches)"
    FROM samples
    LEFT OUTER JOIN quantity_samples ON samples.data_id = quantity_samples.data_id
    WHERE samples.data_type = '2'
    ORDER BY samples.start_date DESC
    '''

    data_headers = (
        ('Height Value Timestamp', 'datetime'), 'Height (in Meters)',
        'Height (in Centimeters)', 'Height (Feet and Inches)')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        height_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        data_list.append((height_timestamp, record[1], record[2], record[3]))

    return data_headers, data_list, data_source


@artifact_processor
def health_weight(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        samples.start_date AS "Weight Value Timestamp",
        SUBSTR(quantity_samples.quantity,1,5) AS "Weight (in Kilograms)",
        CASE
            WHEN SUBSTR(CAST(ROUND(((quantity_samples.quantity / 6.35029317) -
                CAST(quantity_samples.quantity / 6.35029317 AS INT)) * 14) AS VARCHAR),
                1, INSTR(CAST(ROUND(((quantity_samples.quantity / 6.35029317) -
                CAST(quantity_samples.quantity / 6.35029317 AS INT)) * 14) AS VARCHAR),
                '.') - 1) = '14'
            THEN ((CAST(quantity_samples.quantity / 6.35029317 AS INT) + 1) || ' Stone 0 Pounds')
            ELSE ((CAST(quantity_samples.quantity / 6.35029317 AS INT) || ' Stone ' ||
                SUBSTR(CAST(ROUND(((quantity_samples.quantity / 6.35029317) -
                CAST(quantity_samples.quantity / 6.35029317 AS INT)) * 14) AS VARCHAR),
                1, INSTR(CAST(ROUND(((quantity_samples.quantity / 6.35029317) -
                CAST(quantity_samples.quantity / 6.35029317 AS INT)) * 14) AS VARCHAR), '.')
                - 1) || ' Pounds'))
            END AS "Weight (in Stones and Pounds)",
        SUBSTR((quantity_samples.quantity * '2.20462262'),1,6) AS "Weight (Approximate in Pounds)"
    FROM samples
    LEFT OUTER JOIN quantity_samples ON samples.data_id = quantity_samples.data_id
    WHERE samples.data_type = '3'
    ORDER BY samples.start_date DESC
    '''

    data_headers = (
        ('Weight Value Timestamp', 'datetime'), 'Weight (in Kilograms)',
        'Weight (in Stone)', 'Weight (Approximate in Pounds)')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        weight_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        data_list.append((weight_timestamp, record[1], record[2], record[3]))

    return data_headers, data_list, data_source


@artifact_processor
def health_watch_worn_data(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    WITH TimeData AS (
        SELECT
            start_date AS "Start Time",
            end_date AS "End Time",
            LAG(start_date) OVER (ORDER BY start_date) AS "Prev Start Time",
            LAG(end_date) OVER (ORDER BY start_date) AS "Prev End Time"
        FROM samples
        WHERE data_type = "70"
    ),
    PeriodData AS (
        SELECT
            *,
            "Start Time" - "Prev End Time" AS "Gap in Seconds",
            CASE
                WHEN "Start Time" - "Prev End Time" > 3600 THEN 1
                ELSE 0
            END AS "New Period"
        FROM TimeData
    ),
    PeriodGroup AS (
        SELECT
            *,
            SUM("New Period") OVER
                (ORDER BY "Start Time" ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS "Period ID"
        FROM PeriodData
    ),
    Summary AS (
        SELECT
            "Period ID",
            MIN("Start Time") AS "Watch Worn Start Time",
            MAX("End Time") AS "Last Watch Worn Hour Time",
            (MAX("End Time") - MIN("Start Time")) / 3600.0 AS "Hours Worn"
        FROM PeriodGroup
        GROUP BY "Period ID"
    )
    SELECT
        s1."Watch Worn Start Time",
        CAST(s1."Hours Worn" AS INT),
        s1."Last Watch Worn Hour Time",
        CAST(
            (s2."Watch Worn Start Time" - s1."Last Watch Worn Hour Time") / 3600 AS INT
        ) AS "Hours Off Before Next Worn"
    FROM
        Summary s1
    LEFT JOIN
        Summary s2 ON s1."Period ID" + 1 = s2."Period ID"
    ORDER BY s1."Period ID";
    '''

    data_headers = (
        ('Watch Worn Start Time', 'datetime'), 'Hours Worn',
        ('Last Watch Worn Hour Time', 'datetime'), 'Hours Off Before Next Worn Start Time')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        last_hour_time = convert_cocoa_core_data_ts_to_utc(record[2])
        data_list.append((start_timestamp, record[1], last_hour_time, record[3]))

    return data_headers, data_list, data_source


@artifact_processor
def health_all_watch_sleep_data(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    SELECT
        SAMPLES.START_DATE,
        CASE
            WHEN category_samples.value IS 2 THEN "AWAKE"
            WHEN category_samples.value IS 3 THEN "CORE"
            WHEN category_samples.value IS 4 THEN "DEEP"
            WHEN category_samples.value IS 5 THEN "REM"
        END,
        SAMPLES.END_DATE,
        STRFTIME('%H:%M:%S', (samples.end_date - samples.start_date), 'unixepoch')
    FROM samples
    LEFT OUTER JOIN category_samples ON samples.data_id = category_samples.data_id
    LEFT OUTER JOIN objects on samples.data_id = objects.data_id
    LEFT OUTER JOIN data_provenances on objects.provenance = data_provenances.ROWID
    WHERE samples.data_type IS 63 AND category_samples.value != 0 AND\
        category_samples.value != 1 AND data_provenances.origin_product_type like "%Watch%"
    ORDER BY category_samples.data_id;
    '''

    data_headers = (
        ('Sleep Start Time', 'datetime'), 'Sleep State',
        ('Sleep End Time', 'datetime'), 'Sleep State (HH:MM:SS)')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[2])
        data_list.append((start_timestamp, record[1], end_timestamp, record[3]))

    return data_headers, data_list, data_source


@artifact_processor
def health_watch_by_sleep_period(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    data_list = []

    query = '''
    WITH lagged_samples AS (
        SELECT
            samples.start_date,
            samples.end_date,
            samples.data_id,
            samples.start_date AS start_time,
            samples.end_date AS end_time,
            (samples.end_date - samples.start_date) / 60 AS duration_minutes,
            samples.data_type,
            category_samples.value,
            LAG(samples.data_id) OVER (ORDER BY samples.data_id) AS prev_data_id,
            CASE
                WHEN category_samples.value = 2 THEN "AWAKE"
                WHEN category_samples.value = 3 THEN "CORE"
                WHEN category_samples.value = 4 THEN "DEEP"
                WHEN category_samples.value = 5 THEN "REM"
            END AS sleep_value
        FROM samples
        LEFT OUTER JOIN category_samples ON samples.data_id = category_samples.data_id
        LEFT OUTER JOIN objects on samples.data_id = objects.data_id
        LEFT OUTER JOIN data_provenances on objects.provenance = data_provenances.ROWID
        WHERE samples.data_type IS 63 AND category_samples.value != 0\
            AND category_samples.value != 1 AND data_provenances.origin_product_type like "%Watch%"
        ORDER BY category_samples.data_id
    ),
    grouped_samples AS (
        SELECT
            start_time,
            start_date,
            sleep_value,
            end_time,
            end_date,
            duration_minutes,
            data_type,
            value,
            CASE
                WHEN data_id - prev_data_id > 1 OR prev_data_id IS NULL THEN 1
                ELSE 0
            END AS is_new_group,
            SUM(CASE
                    WHEN data_id - prev_data_id > 1 OR prev_data_id IS NULL THEN 1
                    ELSE 0
                END) OVER (ORDER BY data_id) AS group_number
        FROM lagged_samples
    )
    SELECT
        MIN(start_time),
        MAX(end_time),
        STRFTIME('%H:%M:%S',
            SUM(CASE WHEN sleep_value IN ('AWAKE', 'REM', 'CORE', 'DEEP')
            THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S',
            SUM(CASE WHEN sleep_value IN ('REM', 'CORE', 'DEEP')
            THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S',
            SUM(CASE WHEN sleep_value = 'AWAKE' THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S',
            SUM(CASE WHEN sleep_value = 'REM' THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S',
            SUM(CASE WHEN sleep_value = 'CORE' THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        STRFTIME('%H:%M:%S',
            SUM(CASE WHEN sleep_value = 'DEEP' THEN duration_minutes * 60 ELSE 0 END), 'unixepoch'),
        ROUND(SUM(CASE WHEN sleep_value = 'AWAKE'
            THEN duration_minutes ELSE 0 END) * 100.0 / SUM(duration_minutes), 2),
        ROUND(SUM(CASE WHEN sleep_value = 'REM'
            THEN duration_minutes ELSE 0 END) * 100.0 / SUM(duration_minutes), 2),
        ROUND(SUM(CASE WHEN sleep_value = 'CORE'
            THEN duration_minutes ELSE 0 END) * 100.0 / SUM(duration_minutes), 2),
        ROUND(SUM(CASE WHEN sleep_value = 'DEEP'
            THEN duration_minutes ELSE 0 END) * 100.0 / SUM(duration_minutes), 2)
    FROM grouped_samples
    GROUP BY group_number;
    '''

    data_headers = (
        ('Sleep Start Time', 'datetime'), ('Sleep End Time', 'datetime'),
        'Time in Bed (HH:MM:SS)', 'Time Asleep (HH:MM:SS)', 'Awake Duration (HH:MM:SS)',
        'REM Duration (HH:MM:SS)', 'Core Duration (HH:MM:SS)',
        'Deep Duration (HH:MM:SS)', 'Awake %', 'REM %', 'Core %', 'Deep %')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        data_list.append(
            (start_timestamp, end_timestamp, record[2], record[3], record[4], record[5],
             record[6], record[7], record[8], record[9], record[10], record[11]))

    return data_headers, data_list, data_source


@artifact_processor
def health_source_devices(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb.sqlite')
    data_list = []

    # https://theapplewiki.com/wiki/Bluetooth_PIDs
    bluetooth_pid = {
        "0x0034": "Apple Watch Series 5",
        "0x003b": "Apple Watch Series 9",
        "0x0040": "iPhone10,4",
        "0x0267": "Magic Keyboard (1st generation)",
        "0x2002": "AirPods (1st generation)",
        "0x200A": "AirPods Max",
        "0x200E": "AirPods Pro (1st generation)",
        "0x2013": "AirPods (3rd generation)",
        "0x2014": "AirPods Pro (2nd generation) (Lightning)",
        "0x2016": "Beats Studio Buds +",
        "0x201b": "AirPods 4 (ANC)",
        "0x2024": "AirPods Pro (2nd generation) (USB-C)",
    }

    query = '''
    SELECT
        creation_date,
        name,
        manufacturer,
        model,
        hardware,
        firmware,
        software,
        localIdentifier,
        sync_provenance,
        sync_identity
    FROM source_devices
    WHERE name NOT LIKE '__NONE__' AND localIdentifier NOT LIKE '__NONE__'
    '''

    data_headers = (
        ('Creation Date', 'datetime'), 'Device Name', 'Manufacturer', 'Model',
        'Device ID', 'Device Model', 'Firmware', 'Software', 'Local ID', 'Sync Provenance', 'Sync ID')

    db_records = get_sqlite_db_records(data_source, query)

    for record in db_records:
        creation_date = convert_cocoa_core_data_ts_to_utc(record[0])
        model = bluetooth_pid.get(record[3], record[3])
        device_model = context.get_device_model(record[4])
        local_id = ''
        if str(record[7]).endswith('-tacl'):
            local_id = str(record[7])[:-5]
        data_list.append(
            (creation_date, record[1], record[2], model, record[4], device_model, record[5],
             record[6], local_id, record[8], record[9]))

    return data_headers, data_list, data_source


@artifact_processor
def health_wrist_temperature(context):
    """ See artifact description """
    data_source = context.get_source_file_path('healthdb_secure.sqlite')
    healthdb = context.get_source_file_path('healthdb.sqlite')

    data_list = []

    attach_query = attach_sqlite_db_readonly(healthdb, 'healthdb')

    query = '''
    WITH surface_temp AS (
        SELECT
            metadata_values.object_id,
            metadata_values.numerical_value
        FROM metadata_values
        JOIN metadata_keys ON metadata_values.key_id = metadata_keys.ROWID
        WHERE metadata_keys.key = '_HKPrivateMetadataKeySkinSurfaceTemperature'
    ),
    algorithm_version AS (
        SELECT
            metadata_values.object_id,
            metadata_values.numerical_value
        FROM metadata_values
        JOIN metadata_keys ON metadata_values.key_id = metadata_keys.ROWID
        WHERE metadata_keys.key = 'HKAlgorithmVersion'
    )
    SELECT
        samples.start_date AS "Start Time",
        samples.end_date AS "End Time",
        objects.creation_date AS "Date Added to Health",
        quantity_samples.quantity AS "Wrist Temperature (°C)",
        ((quantity_samples.quantity * 1.8) + 32) AS "Wrist Temperature (°F)",
        healthdb.sources.name AS "Source",
        algorithm_version.numerical_value AS "Algorithm Version",
        surface_temp.numerical_value AS "Surface Temperature (°C)",
        ((surface_temp.numerical_value * 1.8) + 32) AS "Surface Temperature (°F)",
        healthdb.source_devices.name AS "Name",
        healthdb.source_devices.manufacturer AS "Manufacturer",
        healthdb.source_devices.model AS "Model",
        healthdb.source_devices.hardware AS "Hardware Version",
        healthdb.source_devices.software AS "Software Version"
    FROM samples
    LEFT OUTER JOIN quantity_samples ON quantity_samples.data_id = samples.data_id
    LEFT OUTER JOIN objects ON samples.data_id = objects.data_id
    LEFT OUTER JOIN data_provenances ON objects.provenance = data_provenances.ROWID
    LEFT OUTER JOIN surface_temp ON surface_temp.object_id = samples.data_id
    LEFT OUTER JOIN algorithm_version ON algorithm_version.object_id = samples.data_id
    LEFT OUTER JOIN healthdb.sources ON healthdb.sources.ROWID = data_provenances.source_id
    LEFT OUTER JOIN healthdb.source_devices ON healthdb.source_devices.ROWID = data_provenances.device_id
    WHERE samples.data_type = 256
    '''

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'),
        ('Date Added to Health', 'datetime'), 'Wrist Temperature (°C)',
        'Wrist Temperature (°F)', 'Source', 'Algorithm Version',
        'Surface Temperature (°C)', 'Surface Temperature (°F)', 'Name',
        'Manufacturer', 'Model', 'Hardware Version', 'Software Version')

    db_records = get_sqlite_db_records(data_source, query, attach_query)

    for record in db_records:
        start_timestamp = convert_cocoa_core_data_ts_to_utc(record[0])
        end_timestamp = convert_cocoa_core_data_ts_to_utc(record[1])
        added_timestamp = convert_cocoa_core_data_ts_to_utc(record[2])
        data_list.append(
            (start_timestamp, end_timestamp, added_timestamp, record[3], record[4],
             record[5], record[6], record[7], record[8], record[9], record[10],
             record[11], record[12], record[13]))

    return data_headers, data_list, data_source
