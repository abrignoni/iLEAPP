# Module Description: Parses Apple Health details
# Author: @KevinPagano3
# Date: 2022-08-15
# Artifact version: 0.0.3
# Requirements: none

# Queries are a derivitive of research provided by Heather Mahalik and Jared Barnhart as part of their SANS DFIR Summit 2022 talk
# as well as research provided by Sarah Edwards as part of her APOLLO project.
# https://for585.com/dfirsummit22
# https://github.com/mac4n6/APOLLO

import sqlite3
import textwrap
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

og_os_build = ''
local_os_build = ''

OS_dict = {
"15A372":"iOS 11.0",
"15A402":"iOS 11.0.1",
"15A403":"iOS 11.0.1",
"15A8391":"iOS 11.0.1",
"15A421":"iOS 11.0.2",
"15A432":"iOS 11.0.3",
"15B93":"iOS 11.1",
"15B101":"iOS 11.1",
"15B150":"iOS 11.1.1",
"15B202":"iOS 11.1.2",
"15C114":"iOS 11.2",
"15C153":"iOS 11.2.1",
"15C202":"iOS 11.2.2",
"15D60":"iOS 11.2.5",
"15D100":"iOS 11.2.6",
"15E216":"iOS 11.3",
"15E218":"iOS 11.3",
"15E302":"iOS 11.3.1",
"15F79":"iOS 11.4",
"15G77":"iOS 11.4.1",
"16A366":"iOS 12.0",
"16A404":"iOS 12.0.1",
"16A405":"iOS 12.0.1",
"16B92":"iOS 12.1",
"16B93":"iOS 12.1",
"16B94":"iOS 12.1",
"16C50":"iOS 12.1.1",
"16C104":"iOS 12.1.2",
"16D39":"iOS 12.1.3",
"16D40":"iOS 12.1.3",
"16D57":"iOS 12.1.4",
"16E227":"iOS 12.2",
"16F156":"iOS 12.3",
"16F203":"iOS 12.3.1",
"16F8202":"iOS 12.3.1",
"16F250":"iOS 12.3.2",
"16G77":"iOS 12.4",
"16G102":"iOS 12.4.1",
"16G114":"iOS 12.4.2",
"16G130":"iOS 12.4.3",
"16G140":"iOS 12.4.4",
"16G161":"iOS 12.4.5",
"16G183":"iOS 12.4.6",
"16G192":"iOS 12.4.7",
"16G201":"iOS 12.4.8",
"16H5":"iOS 12.4.9",
"16H20":"iOS 12.5",
"16H22":"iOS 12.5.1",
"16H30":"iOS 12.5.2",
"16H41":"iOS 12.5.3",
"16H50":"iOS 12.5.4",
"16H62":"iOS 12.5.5",   
"17A577":"iOS 13.0",
"17A844":"iOS 13.1",
"17A854":"iOS 13.1.1",
"17A860":"iOS 13.1.2",
"17A861":"iOS 13.1.2",
"17A878":"iOS 13.1.3",
"17B84":"iOS 13.2",
"17B90":"iOS 13.2.1",
"17B102":"iOS 13.2.2",
"17B111":"iOS 13.2.3",
"17C54":"iOS 13.3",
"17D50":"iOS 13.3.1",
"17E255":"iOS 13.4",
"17E8255":"iOS 13.4",
"17E262":"iOS 13.4.1",
"17E8258":"iOS 13.4.1",
"17F75":"iOS 13.5",
"17F80":"iOS 13.5.1",
"17G68":"iOS 13.6",
"17G80":"iOS 13.6.1",
"17H35":"iOS 13.7",
"18A373":"iOS 14.0",
"18A393":"iOS 14.0.1",
"18A8395":"iOS 14.1",
"18B92":"iOS 14.2",
"18B111":"iOS 14.2",
"18B121":"iOS 14.2.1",
"18C66":"iOS 14.3",
"18D52":"iOS 14.4",
"18D61":"iOS 14.4.1",
"18D70":"iOS 14.4.2",
"18E199":"iOS 14.5",
"18E212":"iOS 14.5.1",
"18F72":"iOS 14.6",
"18G69":"iOS 14.7",
"18G82":"iOS 14.7.1",
"18H17":"iOS 14.8",
"18H107":"iOS 14.8.1",
"19A346":"iOS 15.0",
"19A348":"iOS 15.0.1",
"19A404":"iOS 15.0.2",
"19B74":"iOS 15.1",
"19B81":"iOS 15.1.1",
"19C56":"iOS 15.2",
"19C57":"iOS 15.2",
"19C63":"iOS 15.2.1",
"19D50":"iOS 15.3",
"19D52":"iOS 15.3.1",
"19E241":"iOS 15.4",
"19E258":"iOS 15.4.1",
"19F77":"iOS 15.5",
"19G71":"iOS 15.6",
"19G82":"iOS 15.6.1",
"19H12":"iOS 15.7",
"20A362":"iOS 16.0",
"20A371":"iOS 16.0.1",
"20A380":"iOS 16.0.2",
"20A392":"iOS 16.0.3",
"12S507":"watchOS 1.0",
"12S632":"watchOS 1.0.1",
"13S344":"watchOS 2.0",
"13S428":"watchOS 2.0.1",
"13S661":"watchOS 2.1",
"13V144":"watchOS 2.2",
"13V420":"watchOS 2.2.1",
"13V604":"watchOS 2.2.2",
"14S326":"watchOS 3.0",
"14S471":"watchOS 3.1",
"14S883":"watchOS 3.1.1",
"14S960":"watchOS 3.1.3",
"14V249":"watchOS 3.2",
"14V485":"watchOS 3.2.2",
"14V753":"watchOS 3.2.3",
"15R372":"watchOS 4.0",
"15R654":"watchOS 4.0.1",
"15R846":"watchOS 4.1",
"15S102":"watchOS 4.2",
"15S542":"watchOS 4.2.2",
"15S600b":"watchOS 4.2.3",
"15T212":"watchOS 4.3",
"15T567":"watchOS 4.3.1",
"15U70":"watchOS 4.3.2",
"16R364":"watchOS 5.0",
"16R381":"watchOS 5.0.1",
"16R382":"watchOS 5.0.1",
"16R591":"watchOS 5.1",
"16R600":"watchOS 5.1.1",
"16S46":"watchOS 5.1.2",
"16S535":"watchOS 5.1.3",
"16T225":"watchOS 5.2",
"16U113":"watchOS 5.2.1",
"16U569":"watchOS 5.3",
"16U600":"watchOS 5.3.1",
"16U611":"watchOS 5.3.2",
"16U620":"watchOS 5.3.3",
"16U627":"watchOS 5.3.4",
"16U652":"watchOS 5.3.5",
"16U662":"watchOS 5.3.6",
"16U674":"watchOS 5.3.7",
"16U680":"watchOS 5.3.8",
"16U693":"watchOS 5.3.9",
"17R575":"watchOS 6.0",
"17R604":"watchOS 6.0.1",
"17R605":"watchOS 6.0.1",
"17S84":"watchOS 6.1",
"17S449":"watchOS 6.1.1",
"17S796":"watchOS 6.1.2",
"17S811":"watchOS 6.1.3",
"17T529":"watchOS 6.2",
"17T530":"watchOS 6.2.1",
"17T608":"watchOS 6.2.5",
"17T620":"watchOS 6.2.6",
"17U63":"watchOS 6.2.8",
"17U203":"watchOS 6.2.9",
"17U208":"watchOS 6.3",
"18R382":"watchOS 7.0",
"18R395":"watchOS 7.0.1",
"18R402":"watchOS 7.0.2",
"18R410":"watchOS 7.0.3",
"18R590":"watchOS 7.1",
"18S563":"watchOS 7.2",
"18S564":"watchOS 7.2",
"18S801":"watchOS 7.3",
"18S811":"watchOS 7.3.1",
"18S821":"watchOS 7.3.2",
"18S830":"watchOS 7.3.3",
"18T195":"watchOS 7.4",
"18T201":"watchOS 7.4.1",
"18T567":"watchOS 7.5",
"18U63":"watchOS 7.6",
"18U70":"watchOS 7.6.1",
"18U80":"watchOS 7.6.2",
"19R343":"watchOS 8.0",
"19R346":"watchOS 8.0",
"19R354":"watchOS 8.0.1",
"19R570":"watchOS 8.1",
"19R580":"watchOS 8.1.1",
"19S55":"watchOS 8.3",
"19S546":"watchOS 8.4",
"19S550":"watchOS 8.4.1",
"19S553":"watchOS 8.4.2",
"19T242":"watchOS 8.5",
"19T252":"watchOS 8.5.1",
"19T572":"watchOS 8.6",
"19U66":"watchOS 8.7",
"19U67":"watchOS 8.7.1",
"20R361":"watchOS 9.0",
"20R8380":"watchOS 9.0.1",
"20R8383":"watchOS 9.0.2",
}

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
        
            for key, value in OS_dict.items():
                if str(row[2]) == key:
                    og_os_build = value
                    break
                else: og_os_build = row[2]
            
            for key2, value2 in OS_dict.items():
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
    select
    datetime(samples.start_date+978307200,'unixepoch') as "Start Date",
    datetime(samples.end_date+978307200,'unixepoch') as "End Date",
    case
    when samples.data_type = 5 then "Heart Rate"
    when samples.data_type = 118 then "Resting Heart Rate"
    end as "Heart Rate",
    quantity_samples.quantity,
    quantity_samples.original_quantity,
    metadata_keys.key,
    samples.data_id
    from samples
    left outer join quantity_samples on samples.data_id = quantity_samples.data_id
    left outer join metadata_values on metadata_values.object_id = samples.data_id
    left outer join metadata_keys on metadata_keys.ROWID = metadata_values.key_id
    where samples.data_type in (5,118) and samples.start_date not null
    order by "Start Date" desc
    ''')
    
    heart_rate = ''
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            if row[2] == 'Heart Rate':
                heart_rate = row[4]
            if row[2] == 'Resting Heart Rate':
                heart_rate = row[3]
        
            data_list.append((row[0], row[1], row[2], heart_rate, row[5], row[6]))

        report = ArtifactHtmlReport('Health - Heart Rate')
        report.start_artifact_report(report_folder, 'Health - Heart Rate')
        report.add_script()
        data_headers = (
            'Start Timestamp', 'End Timestamp', 'Type', 'Heart Rate', 'Key', 'Data ID')
        report.write_artifact_data_table(data_headers, data_list, healthdb_secure)
        report.end_artifact_report()

        tsvname = 'Health - Heart Rate'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Health - Heart Rate'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No data available in Health - Heart Rate')
    
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
        ('*/Health/healthdb_secure.sqlite*','*/Health/healthdb.sqlite*'),
        get_Health)
}