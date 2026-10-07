# Withings Health Mate App (com.withings.wiScaleNG)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# Tested with the following versions:
# 2024-09-16: iOS 17.5.1, App: 6.3.1

# Requirements:  datetime, json
__artifacts_v2__ = {
    "get_healthmate_accounts": {
        "name": "Health Mate - Accounts",
        "description": "The account recorded in the Health Mate app's Application Support/account "
                       "file, with user id, names, birthdate and email and its creation and "
                       "modification times.",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2024-09-22",
        "last_update_date": "2026-10-04",
        "requirements": "json",
        "category": "Withings Health Mate",
        "notes": "Field meanings follow the Be-binary 4n6 blog post 'Withings HealthMate on iOS', "
                 "https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html (one "
                 "test device, iOS 17.5.1). No sample data is recorded for this artifact. "
                 "Birthdate is reported as the stored birthday value in a text column without "
                 "assigning an epoch, time or zone. Every source entry in every matched account "
                 "file is read.",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/account'),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "get_healthmate_sleep_tracking": {
        "name": "Health Mate - Sleep Tracking",
        "description": "ZTRACK records with no subcategory and ZTYPE 36 from the Health Mate "
                       "app's Core Data track store, which the cited post identifies as tracked "
                       "sleep on its test device, with start and end, sleep stage durations, time "
                       "to sleep and to get up, wake-up count and the device id.",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-09-23",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Field meanings follow the Be-binary 4n6 blog post 'Withings HealthMate on iOS', "
                 "https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html (one "
                 "test device, iOS 17.5.1). No sample data is recorded for this artifact. Rows "
                 "are the ZTRACK records where ZSUBCATEGORY is null and ZTYPE is 36. Duration "
                 "columns are reported as stored and their units are not stated here. Only the "
                 "first matched store file is read.",
        "paths": ('*/Library/Application Support/coredata/*_Tracks*'),
        "output_types": "standard",
        "artifact_icon": "moon"
    },
    "get_healthmate_daily_summary": {
        "name": "Health Mate - Daily Summary",
        "description": "ZTRACK records with no track id and no device id from the Health Mate "
                       "app's Core Data track store, which the cited post identifies as the "
                       "summary of a day on its test device, with the day's inactive, soft, "
                       "moderate and intense durations, steps and distance.",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-09-24",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Field meanings follow the Be-binary 4n6 blog post 'Withings HealthMate on iOS', "
                 "https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html (one "
                 "test device, iOS 17.5.1). No sample data is recorded for this artifact. Rows "
                 "are the ZTRACK records where ZTRACKID and ZDEVICEID are both null. Duration, "
                 "step and distance columns are reported as stored and their units are not stated "
                 "here. Only the first matched store file is read.",
        "paths": ('*/Library/Application Support/coredata/*_Tracks*'),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "get_healthmate_tracked_activities": {
        "name": "Health Mate - Tracked Activities",
        "description": "ZTRACK records that have an activity subcategory, a track extension "
                       "record and a step value in the Health Mate app's Core Data track store, "
                       "with start and end, type, durations, the ZMIN, ZAVG and ZMAX values of "
                       "the track extension (as stored), step, distance, speed and temperature "
                       "values and start, end and region centre coordinates as stored.",
        "author": '@AlexisBrignoni, Codex',
        "creation_date": "2024-09-24",
        "last_update_date": '2026-10-07',
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Original parser and cited research credit: Marco Neumann {kalinko@be-binary.de}. Field meanings follow the Be-binary 4n6 blog post 'Withings HealthMate on iOS', https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html (one test device, iOS 17.5.1). No sample data is recorded for this artifact. Tracks lacking an activity subcategory, a track extension record or a step value are not reported. The cited post reads Is Removed 1 as a track removed in the app whose row remains in the database. The column headed Heart Rate MIN holds ZMIN, the column headed Heart Rate AVG holds ZMAX and the column headed Heart Rate MAX holds ZAVG; the cited post does not say these three are heart rate values. End Latitude and End Longitude hold the selected ZENDCOORDINATELATITUDE and ZENDCOORDINATELONGITUDE values; Region Center Latitude and Region Center Longitude hold ZREGIONCENTERLATITUDE and ZREGIONCENTERLONGITUDE. These labels follow the stored field names; coordinate units, device ownership and collection circumstances are not established here. Manual End Date is handled as a date column in the LAVA output. Only the first matched store file is read.",
        "paths": ('*/Library/Application Support/coredata/*_Tracks*'),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "get_healthmate_messages": {
        "name": "Health Mate - Messages",
        "description": "Rows of type HMTimelineMessageEvent from the ZHMTIMELINEEVENT table of "
                       "the Health Mate timeline store, with sender, receiver, type and text as "
                       "stored.",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2024-09-23",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Field meanings follow the Be-binary 4n6 blog post 'Withings HealthMate on iOS', "
                 "https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html (one "
                 "test device, iOS 17.5.1). No sample data is recorded for this artifact. Only "
                 "rows whose ZTYPE is HMTimelineMessageEvent are read; the cited post says other "
                 "row types exist. The cited post describes ZDATE as local time; because its "
                 "zone is not established, ZDATE is reported as stored text without conversion. "
                 "Only the first matched store file is read.",
        "paths": ('*/Library/Application Support/coredata/*_HM3Timeline*'),
        "output_types": "standard",
        "artifact_icon": "message"
    },
    "get_healthmate_measurements": {
        "name": "Health Mate - Measurements",
        "description": "Rows of the ZVASISTAS table of the Health Mate measurements store, as "
                       "stored.",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-09-23",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Field meanings follow the Be-binary 4n6 blog post 'Withings HealthMate on iOS', "
                 "https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html (one "
                 "test device, iOS 17.5.1). No sample data is recorded for this artifact. "
                 "Category labels 0, 2, 5, 6 and 12 follow the cited post, which took them from "
                 "one test device and says other values may exist; any other stored value is "
                 "shown as Unknown beside its Category ID. Units are not stated in the report. "
                 "Only the first matched store file is read.",
        "paths": ('*/Library/Application Support/coredata/*_vasistas*'),
        "output_types": "all",
        "artifact_icon": "activity"
    },
    "get_healthmate_devices": {
        "name": "Health Mate - Devices",
        "description": "Rows of the ZWTDEVICE table of the Health Mate associated device store, "
                       "as stored.",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2024-09-16",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Field meanings follow the Be-binary 4n6 blog post 'Withings HealthMate on iOS', "
                 "https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html (one "
                 "test device, iOS 17.5.1). No sample data is recorded for this artifact. "
                 "ZCREATED is read as Unix seconds. ZLAST_CONNECTION is read as Cocoa Core Data epoch, which the cited post reads as "
                 "the last connection or sync. Latitude and Longitude are described there as the "
                 "place of the last sync and as not precise. Only the first matched store file is "
                 "read.",
        "paths": ('*/Library/Application Support/coredata/associated_device*.sqlite*'),
        "output_types": "all",
        "artifact_icon": "device-watch"
    }
}

import json
from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_records,
    convert_cocoa_core_data_ts_to_utc,
    convert_unix_ts_to_utc
    )


@artifact_processor
def get_healthmate_accounts(context):
    files_found = context.get_files_found()
    data_list = []
    for file_found in files_found:
        with open(str(file_found), encoding="utf-8") as json_file:
            json_data = json.load(json_file)
        for source in json_data['account']['sources']:
            for user in source.get('users', []):
                user_id = user['userId']
                lastname = user['lastName']
                firstname = user['firstName']
                shortname = user['shortName']
                birthdate = str(user['birthday'])
                email = user['email']
                creationdate = convert_unix_ts_to_utc(user['created'])
                modifieddate = convert_unix_ts_to_utc(user['modified'])

                data_list.append((
                    creationdate,
                    modifieddate,
                    user_id,
                    lastname,
                    firstname,
                    shortname,
                    birthdate,
                    email
                    ))

    data_headers = (
        ('Creation Timestamp', 'datetime'),
        ('Last Modified Timestamp', 'datetime'),
        'User ID',
        'Last Name',
        'First Name',
        'Short Name',
        'birthday (as stored)',
        'E-mail',
        )

    order = (0, 1, 6, 2, 3, 4, 5, 7)
    data_headers = tuple(data_headers[i] for i in order)
    data_list = [tuple(row[i] for i in order) for row in data_list]
    return data_headers, data_list, '\n'.join(str(f) for f in files_found)


@artifact_processor
def get_healthmate_sleep_tracking(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]
    query = ('''
        SELECT
        ZDEVICEID,
        ZSTARTDATE,
        ZENDDATE,
        ZREFERENCEDATE,
        ZMODIFIEDDATE,
        ZMANUALSTARTDATE,
        ZMANUALENDDATE,
        ZLIGHTSLEEPDURATION,
        ZREMSLEEPDURATION,
        ZDEEPSLEEPDURATION,
        ZDURATIONTOSLEEP,
        ZTIMETOGETUP,
        ZWAKEUPCOUNT,
        ZWAKEUPDURATION,
        ZTIMEZONE
        FROM ZTRACK
        WHERE ZSUBCATEGORY IS NULL AND ZTYPE = 36
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        dev_id = row[0]
        startdate = convert_cocoa_core_data_ts_to_utc(row[1])
        enddate = convert_cocoa_core_data_ts_to_utc(row[2])
        refrencedate = convert_cocoa_core_data_ts_to_utc(row[3])
        moddate = convert_cocoa_core_data_ts_to_utc(row[4])
        man_start = convert_cocoa_core_data_ts_to_utc(row[5])
        man_end = convert_cocoa_core_data_ts_to_utc(row[6])
        dur_light = row[7]
        dur_rem = row[8]
        dur_deep = row[9]
        dur_to_sleep = row[10]
        getup = row[11]
        num_wakeup = row[12]
        dur_awake = row[13]
        timezone = row[14]

        data_list.append((
            startdate,
            enddate,
            refrencedate,
            moddate,
            man_start,
            man_end,
            dev_id,
            dur_light,
            dur_rem,
            dur_deep,
            dur_to_sleep,
            getup,
            num_wakeup,
            dur_awake,
            timezone
            ))

    data_headers = (
        ('Start Date', 'datetime'),
        ('End Date', 'datetime'),
        ('Reference Date', 'datetime'),
        ('Modified Date', 'datetime'),
        ('Manual Start Date', 'datetime'),
        ('Manual End Date', 'datetime'),
        'Device ID',
        'Duration Light Sleep',
        'Duration REM Sleep',
        'Duration Deep Sleep',
        'Duration To Sleep',
        'Time To Get Up',
        'Wake up count',
        'Duration Awake',
        'Timezone',
        )
    return data_headers, data_list, files_found[0]


@artifact_processor
def get_healthmate_daily_summary(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]
    query = ('''
        SELECT
        ZSTARTDATE,
        ZENDDATE,
        ZREFERENCEDATE,
        ZMODIFIEDDATE,
        ZDURATIONINACTIVE,
        ZDURATIONINTENSE,
        ZDURATIONMODERATE,
        ZDURATIONSOFT,
        ZSTEPS1,
        ZDISTANCE1,
        ZTIMEZONE
        FROM ZTRACK
        WHERE ZTRACKID IS NULL AND ZDEVICEID IS NULL
    ''')
    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        startdate = convert_cocoa_core_data_ts_to_utc(row[0])
        enddate = convert_cocoa_core_data_ts_to_utc(row[1])
        refrencedate = convert_cocoa_core_data_ts_to_utc(row[2])
        moddate = convert_cocoa_core_data_ts_to_utc(row[3])
        dur_inactive = row[4]
        dur_intense = row[5]
        dur_moderate = row[6]
        dur_soft = row[7]
        steps = row[8]
        distance = row[9]
        timezone = row[10]

        data_list.append((
            startdate,
            enddate,
            refrencedate,
            moddate,
            dur_inactive,
            dur_intense,
            dur_moderate,
            dur_soft,
            steps,
            distance,
            timezone
            ))

    data_headers = (
        ('Start Date', 'datetime'),
        ('End Date', 'datetime'),
        ('Reference Date', 'datetime'),
        ('Modified Date', 'datetime'),
        'Duration Inactive',
        'Duration Intense',
        'Duration Moderate',
        'Duration Soft',
        'Steps',
        'Distance',
        'Timezone',
        )

    return data_headers, data_list, files_found[0]


@artifact_processor
def get_healthmate_tracked_activities(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]
    query = ('''
        SELECT
        t.ZDEVICEID,
        sc.ZNAME,
        t.ZISREMOVED,
        t.ZPAUSEDURATION,
        ZSTARTDATE,
        ZENDDATE,
        ZREFERENCEDATE,
        ZMODIFIEDDATE,
        ZMANUALSTARTDATE,
        ZMANUALENDDATE,
        te.ZINTENSEDURATION,
        te.ZMODERATEDURATION,
        te.ZLIGHTDURATION,
        te.ZMIN,
        te.ZMAX,
        te.ZAVG,
        t.ZSTEPS,
        t.ZDISTANCE,
        te.ZMINSPEED,
        te.ZAVERAGESPEED,
        te.ZMAXSPEED,
        te.ZDISTANCE,
        te.ZSTARTCOORDINATELATITUDE,
        te.ZSTARTCOORDINATELONGITUDE,
        te.ZENDCOORDINATELATITUDE,
        te.ZENDCOORDINATELONGITUDE,
        te.ZREGIONCENTERLATITUDE,
        te.ZREGIONCENTERLONGITUDE,
        te.ZMINTEMPERATURE,
        te.ZAVGTEMPERATURE,
        te.ZMAXTEMPERATURE,
        t.ZTIMEZONE,
        te.ZTRACK
        FROM ZTRACK t
        INNER JOIN ZACTIVITYSUBCATEGORY sc ON t.ZSUBCATEGORY = sc.Z_PK
        INNER JOIN ZTRACKEXTENSION te ON t.Z_PK = te.ZTRACK
        WHERE t.ZSTEPS IS NOT NULL
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)
    data_list = []
    for row in db_records:
        dev_id = row[0]
        act_type = row[1]
        is_removed = row[2]
        dur_pause = row[3]
        startdate = convert_cocoa_core_data_ts_to_utc(row[4])
        enddate = convert_cocoa_core_data_ts_to_utc(row[5])
        refrencedate = convert_cocoa_core_data_ts_to_utc(row[6])
        moddate = convert_cocoa_core_data_ts_to_utc(row[7])
        man_start = convert_cocoa_core_data_ts_to_utc(row[8])
        man_end = convert_cocoa_core_data_ts_to_utc(row[9])
        dur_intense = row[10]
        dur_moderate = row[11]
        dur_light = row[12]
        heart_min = row[13]
        heart_avg = row[14]
        heart_max = row[15]
        steps = row[16]
        distance = row[17]
        speed_min = row[18]
        speed_avg = row[19]
        speed_max = row[20]
        distance_gps = row[21]
        start_lat = row[22]
        start_lon = row[23]
        end_lat = row[24]
        end_lon = row[25]
        center_lat = row[26]
        center_lon = row[27]
        temp_min = row[28]
        temp_avg = row[29]
        temp_max = row[30]
        timezone = row[31]
        track = row[32]

        data_list.append((
            startdate,
            enddate,
            refrencedate,
            moddate,
            man_start,
            man_end,
            dev_id,
            track,
            act_type,
            is_removed,
            dur_pause,
            dur_intense,
            dur_moderate,
            dur_light,
            heart_min,
            heart_avg,
            heart_max,
            steps,
            distance,
            speed_min,
            speed_avg,
            speed_max,
            distance_gps,
            start_lat,
            start_lon,
            end_lat,
            end_lon,
            center_lat,
            center_lon,
            temp_min,
            temp_avg,
            temp_max,
            timezone
            ))

    data_headers = (
        ('Start Date', 'datetime'),
        ('End Date', 'datetime'),
        ('Reference Date', 'datetime'),
        ('Modified Date', 'datetime'),
        ('Manual Start Date', 'datetime'),
        ('Manual End Date', 'datetime'),
        'Device ID',
        'Track ID',
        'Type',
        'Is Removed',
        'Pause Duration',
        'Duration Intense',
        'Duration Moderate',
        'Duration Light',
        'Heart Rate MIN',
        'Heart Rate AVG',
        'Heart Rate MAX',
        'Steps',
        'Distance (no GPS)',
        'Speed MIN',
        'Speed AVG',
        'Speed MAX',
        'Distance (GPS)',
        'Start Latitude',
        'Start Longitude',
        'End Latitude',
        'End Longitude',
        'Region Center Latitude',
        'Region Center Longitude',
        'Temperature MIN',
        'Temperature AVG',
        'Temperature MAX',
        'Timezone',
        )
    return data_headers, data_list, files_found[0]


@artifact_processor
def get_healthmate_messages(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]

    query = ('''
        SELECT
        ZUSERID,
        ZSENDERID,
        ZRECEIVERID,
        ZSENDERLASTNAME,
        ZSENDERFIRSTNAME,
        ZDATE,
        ZWSMODIFIEDDATE,
        ZEXPIRATIONDATE,
        ZTYPEMESSAGE,
        ZMESSAGE2
        FROM ZHMTIMELINEEVENT
        WHERE ZTYPE = 'HMTimelineMessageEvent'
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        accountid = row[0]
        senderid = row[1]
        receiverid = row[2]
        sender_name = row[3]
        sender_first_name = row[4]
        date = str(row[5]) if row[5] is not None else ''
        date_mod = convert_cocoa_core_data_ts_to_utc(row[6])
        date_exp = convert_cocoa_core_data_ts_to_utc(row[7])
        message_type = row[8]
        message = row[9]

        data_list.append((
            date,
            date_mod,
            date_exp,
            accountid,
            senderid,
            receiverid,
            sender_name,
            sender_first_name,
            message_type,
            message
            ))

    data_headers = (
        'ZDATE (as stored)',
        ('Timestamp Modified', 'datetime'),
        ('Timestamp Expiration', 'datetime'),
        'Account ID',
        'Sender ID',
        'Receiver ID',
        'Sender Last Name',
        'Sender First Name',
        'Type',
        'Message'
        )

    return data_headers, data_list, files_found[0]


@artifact_processor
def get_healthmate_measurements(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]
    query = ('''
        SELECT
        ZCATEGORY [CATEGORYID],
        ZDEVICEID,
        ZDURATION,
        ZTIMESTAMP,
        ZSTEPS,
        ZDISTANCE,
        ZCALORIESEARNED,
        ZHEARTRATE1,
        ZLATITUDE,
        ZLONGITUDE,
        ZALTITUDE,
        ZDIRECTION,
        ZRADIUS,
        ZSPEED,
        ZSPO2,
        ZASCENT1,
        ZTEMPERATURE,
        CASE
            WHEN ZCATEGORY = 0 THEN 'Steps'
            WHEN ZCATEGORY = 2 THEN 'Heart Rate'
            WHEN ZCATEGORY = 5 THEN 'Location'
            WHEN ZCATEGORY = 6 THEN 'SPO2'
            WHEN ZCATEGORY = 12 THEN 'Body Temperature'
            ELSE 'Unknown'
        END [CATEGORY]
        FROM ZVASISTAS
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)
    data_list = []
    for row in db_records:
        category_id = row[0]
        category = row[17]
        device_id = row[1]
        duration = row[2]
        timestamp = convert_cocoa_core_data_ts_to_utc(row[3])
        steps = row[4]
        distance = row[5]
        calories = row[6]
        heartrate = row[7]
        lat = row[8]
        lon = row[9]
        alt = row[10]
        direction = row[11]
        radius = row[12]
        speed = row[13]
        spo2 = row[14]
        ascent = row[15]
        temperature = row[16]
        data_list.append((
            timestamp,
            category_id,
            category,
            device_id,
            duration,
            steps,
            distance,
            calories,
            heartrate,
            lat,
            lon,
            alt,
            direction,
            radius,
            speed,
            spo2,
            ascent,
            temperature
            ))
    data_headers = (
        ('Timestamp', 'datetime'),
        'Category ID',
        'Category',
        'Device ID',
        'Duration',
        'Steps',
        'Distance',
        'Calories',
        'Heart Rate',
        'Latitude',
        'Longitude',
        'Altitude',
        'Direction',
        'Radius',
        'Speed',
        'SPO2',
        'Ascent',
        'Temperature',
        )
    return data_headers, data_list, files_found[0]


@artifact_processor
def get_healthmate_devices(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]
    query = ('''
        SELECT
        ZDEVICE_ID,
        ZUSERID,
        ZCREATED,
        ZLAST_CONNECTION,
        ZLAST_WEIGHIN,
        ZMAC,
        ZFIRMWARE,
        ZLATITUDE,
        ZLONGITUDE,
        ZTIMEZONE,
        ZISSYNCDISABLED
        FROM ZWTDEVICE;
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        entid = row[0]
        userid = row[1]
        assdate = convert_unix_ts_to_utc(row[2])
        lastdate = convert_cocoa_core_data_ts_to_utc(row[3])
        lastweighin = convert_cocoa_core_data_ts_to_utc(row[4])
        mac = row[5]
        firmware = row[6]
        lat = row[7]
        lon = row[8]
        dev_timezone = row[9]  
        sync_disabled = row[10]

        data_list.append((
            assdate,
            lastdate,
            lastweighin,
            entid,
            userid,
            mac,
            firmware,
            lat,
            lon,
            dev_timezone,
            sync_disabled
            ))

    data_headers = (
        ('ZCREATED', 'datetime'),
        ('ZLAST_CONNECTION', 'datetime'),
        ('Last Weighin Timestamp', 'datetime'),
        'ID',
        'User ID',
        'MAC',
        'Firmware',
        'Latitude',
        'Longitude',
        'Device Timezone',
        'Sync Disabled',
        )
    return data_headers, data_list, files_found[0]
