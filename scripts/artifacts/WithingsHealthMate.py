# Withings Health Mate App (com.withings.wiScaleNG)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# 
# Tested with the following versions:
# 2024-09-16: iOS 17.5.1, App: 6.3.1

# Requirements:  datetime, json

__artifacts_v2__ = {

    
    "get_healthmate_accounts": {
        "name": "Health Mate - Accounts",
        "description": "Existing account in Health Mate App from Withings.\n This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creatin_date": "2024-09-22",
        "last_update_date": "2025-04-23",
        "requirements": "json",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('*/Containers/Data/Application/*/Library/Application Support/account'),
        "output_types": "html",
        "artifact_icon": "user"
    },
    "get_healthmate_sleep_tracking": {
        "name": "Health Mate - Sleep Tracking",
        "description": "Tracked sleep by Withings devices/app.\n This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2024-09-23",
        "last_update_date": "2025-04-23",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('*/Library/Application Support/coredata/*_Tracks*'),
        "output_types": "standard",
        "artifact_icon": "moon"
    },
    "get_healthmate_daily_summary": {
        "name": "Health Mate - Daily Summary",
        "description": "Daily Summary of activities.\n This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2024-09-24",
        "last_update_date": "2025-04-23",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('*/Library/Application Support/coredata/*_Tracks*'),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "get_healthmate_tracked_activities": {
        "name": "Health Mate - Tracked Activities",
        "description": "Tracked activities.\n This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2024-09-24",
        "last_update_date": "2025-04-23",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('*/Library/Application Support/coredata/*_Tracks*'),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "get_healthmate_messages": {
        "name": "Health Mate - Messages",
        "description": "Existing Message data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2024-09-23",
        "last_update_date": "2025-04-23",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('*/Library/Application Support/coredata/*_HM3Timeline*'),
        "output_types": "standard",
        "artifact_icon": "message-square"
    },
    "get_healthmate_measurements": {
        "name": "Health Mate - Measurements",
        "description": "Existing Measurements data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html.",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2024-09-23",
        "last_update_date": "2025-04-23",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('*/Library/Application Support/coredata/*_vasistas*'),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "get_healthmate_devices": {
        "name": "Health Mate - Devices",
        "description": "Existing Devices data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2024-09-16",
        "last_update_date": "2025-04-23",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('*/Library/Application Support/coredata/associated_device.sqlite'),
        "output_types": "standard",
        "artifact_icon": "watch"
    }
}

import datetime
import json

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records

@artifact_processor
def get_healthmate_accounts(files_found, report_folder, seeker, wrap_text, time_offset):
    
    with open (str(files_found[0])) as json_file:
        json_data = json.load(json_file)

    data_list = []
    for user in json_data['account']['sources'][0]['users']:
        id = user['userId']
        lastname = user['lastName']
        firstname = user['firstName']
        shortname = user['shortName']
        birthdate = datetime.datetime.fromtimestamp(user['birthday'] + 978307200).strftime('%Y-%m-%d %H:%M:%S')
        email = user['email']
        creationdate = datetime.datetime.fromtimestamp(user['created']).strftime('%Y-%m-%d %H:%M:%S')
        modifieddate = datetime.datetime.fromtimestamp(user['modified']).strftime('%Y-%m-%d %H:%M:%S')

        data_list.append((creationdate, modifieddate, id, lastname, firstname, shortname, birthdate, email))

    data_headers = ( 'Creation Timestamp', 'Last Modified Timestamp', 'User ID', 'Last Name', 'First Name', 'Short Name', 'Birthdate', 'E-mail')

    return data_headers, data_list, files_found[0]

@artifact_processor
def get_healthmate_sleep_tracking(files_found, report_folder, seeker, wrap_text, time_offset):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    query = ('''
        SELECT  
        ZDEVICEID,
        DATETIME('2001-01-01', "ZSTARTDATE" || ' seconds') [STARTDATE],
        DATETIME('2001-01-01', "ZENDDATE" || ' seconds') [ENDDATE],
        DATETIME('2001-01-01', "ZREFERENCEDATE" || ' seconds') [REFERENCEDATE],
        DATETIME('2001-01-01', "ZMODIFIEDDATE" || ' seconds') [MODIFIEDDATE],
        DATETIME('2001-01-01', "ZMANUALSTARTDATE" || ' seconds') [MANUALSTARTDATE],
        DATETIME('2001-01-01', "ZMANUALENDDATE" || ' seconds') [MANUALENDDATE],
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
        id = row[0]
        startdate = row[1]
        enddate = row[2]
        refrencedate = row[3]
        moddate = row[4]
        man_start = row[5]
        man_end = row[6]
        dur_light = row[7]
        dur_rem = row[8]
        dur_deep = row[9]
        dur_to_sleep = row[10]
        getup = row[11]
        num_wakeup = row[12]
        dur_awake = row[13]
        timezone = row[14]

        data_list.append((startdate, enddate, refrencedate, moddate, man_start, man_end, id, dur_light, dur_rem, dur_deep, dur_to_sleep, getup, num_wakeup, dur_awake, timezone))

    data_headers = ('Start Date', 'End Date', 'Reference Date','Modified Date', 'Manual Start Date','Manual End Date','Device ID', 'Duration Light Sleep','Duration REM Sleep', 'Duration Deep Sleep', 'Duration To Sleep', 'Time To Get Up', 'Wake up count', 'Duration Awake', 'Timezone')
    
    return data_headers, data_list, files_found[0]

@artifact_processor
def get_healthmate_daily_summary(files_found, report_folder, seeker, wrap_text, time_offset):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    query = ('''
        SELECT  
        DATETIME('2001-01-01', "ZSTARTDATE" || ' seconds') [STARTDATE],
        DATETIME('2001-01-01', "ZENDDATE" || ' seconds') [ENDDATE],
        DATETIME('2001-01-01', "ZREFERENCEDATE" || ' seconds') [REFERENCEDATE],
        DATETIME('2001-01-01', "ZMODIFIEDDATE" || ' seconds') [MODIFIEDDATE],
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
        startdate = row[0]
        enddate = row[1]
        refrencedate = row[2]
        moddate = row[3]
        dur_inactive = row[4]
        dur_intense = row[5]
        dur_moderate = row[6]
        dur_soft = row[7]
        steps = row[8]
        distance = row[9]
        timezone = row[10]

        data_list.append((startdate, enddate, refrencedate, moddate, dur_inactive, dur_intense, dur_moderate, dur_soft, steps, distance, timezone))

    data_headers = ('Start Date', 'End Date', 'Reference Date','Modified Date','Duration Inactive','Duration Intense', 'Duration Moderate', 'Duration Soft', 'Steps', 'Distance', 'Timezone')

    return data_headers, data_list, files_found[0]

@artifact_processor
def get_healthmate_tracked_activities(files_found, report_folder, seeker, wrap_text, time_offset):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    query = ('''
        SELECT
        t.ZDEVICEID,
        sc.ZNAME,
        t.ZISREMOVED,
        t.ZPAUSEDURATION,
        DATETIME('2001-01-01', "ZSTARTDATE" || ' seconds') [STARTDATE],
        DATETIME('2001-01-01', "ZENDDATE" || ' seconds') [ENDDATE],
        DATETIME('2001-01-01', "ZREFERENCEDATE" || ' seconds') [REFERENCEDATE],
        DATETIME('2001-01-01', "ZMODIFIEDDATE" || ' seconds') [MODIFIEDDATE],
        DATETIME('2001-01-01', "ZMANUALSTARTDATE" || ' seconds') [MANUALSTARTDATE],
        DATETIME('2001-01-01', "ZMANUALENDDATE" || ' seconds') [MANUALENDDATE],
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
        id = row[0]
        act_type = row[1]
        is_removed = row[2]
        dur_pause = row[3]
        startdate = row[4]
        enddate = row[5]
        refrencedate = row[6]
        moddate = row[7]
        man_start = row[8]
        man_end = row[9]
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

        data_list.append((startdate, enddate, refrencedate, moddate, man_start, man_end, id, track, act_type, is_removed, dur_pause, dur_intense, dur_moderate, dur_light, heart_min, heart_avg, heart_max, steps, distance, speed_min, speed_avg, speed_max, distance_gps, start_lat, start_lon, end_lat, end_lon, center_lat, center_lon, temp_min, temp_avg, temp_max, timezone))

    data_headers = ('Start Date', 'End Date', 'Reference Date','Modified Date', 'Manual Start Date','Manual End Date', 'Device ID', 'Track ID', 'Type', 'Is Removed', 'Pause Duration', 'Duration Intense', 'Duration Moderate', 'Duration Light', 'Heart Rate MIN', 'Heart Rate AVG', 'Heart Rate MAX', 'Steps', 'Distance (no GPS)', 'Speed MIN', 'Speed AVG', 'Speed MAX', 'Distance (GPS)', 'Start Latitude', 'Start Longitude', 'Region Center Latitude', 'Region Center Longitude', 'End Latitude', 'End Longitude', 'Temperature MIN', 'Temperature AVG', 'Temperature MAX', 'Timezone')
    
    return data_headers, data_list, files_found[0]
     
@artifact_processor
def get_healthmate_messages(files_found, report_folder, seeker, wrap_text, time_offset):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]

    query = ('''
        SELECT
        ZUSERID,
        ZSENDERID,
        ZRECEIVERID,
        ZSENDERLASTNAME,
        ZSENDERFIRSTNAME,
        datetime('2001-01-01', "ZDATE" || ' seconds'),
        datetime('2001-01-01', "ZWSMODIFIEDDATE" || ' seconds'),
        datetime('2001-01-01', "ZEXPIRATIONDATE" || ' seconds'),
        ZTYPEMESSAGE,
        ZMESSAGE2
        FROM ZHMTIMELINEEVENT
        WHERE ZTYPE = 'HMTimelineMessageEvent'
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        id = row[0]
        senderid = row[1]
        receiverid = row[2]
        sender_name = row[3]
        sender_first_name = row[4]
        date = row[5]
        date_mod = row[6]
        date_exp = row[7]
        message_type = row[8]
        message = row[9]   

        data_list.append((date, date_mod, date_exp, id, senderid, receiverid, sender_name, sender_first_name, message_type, message))

    data_headers = ('Timestamp [Local Time]', 'Timestamp Modified', 'Timestamp Expiration', 'Account ID', 'Sender ID', 'Receiver ID', 'Sender Last Name', 'Sender First Name', 'Type', 'Message')

    return data_headers, data_list, files_found[0]  

@artifact_processor
def get_healthmate_measurements(files_found, report_folder, seeker, wrap_text, time_offset):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    

    query = ('''
        SELECT
        ZCATEGORY [CATEGORYID],
        ZDEVICEID,
        ZDURATION,
        datetime('2001-01-01', "ZTIMESTAMP" || ' seconds') [TIMESTAMP],
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
        timestamp = row[3]
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


        data_list.append((timestamp, category_id, category, device_id, duration, steps, distance, calories, heartrate, lat, lon, alt, direction, radius, speed, spo2, ascent, temperature))
    data_headers = ('Timestamp', 'Category ID', 'Category', 'Device ID', 'Duration', 'Steps', 'Distance', 'Calories', 'Heart Rate', 'Latitude', 'Longitude', 'Altitude', 'Direction', 'Radius', 'Speed', 'SPO2', 'Ascent', 'Temperature')

    return data_headers, data_list, files_found[0]

@artifact_processor
def get_healthmate_devices(files_found, report_folder, seeker, wrap_text, time_offset):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
   
    query = ('''
        SELECT  
        ZDEVICE_ID,   
        ZUSERID,   
        DATETIME("ZCREATED", 'unixepoch'),  
        DATETIME('2001-01-01', "ZLAST_CONNECTION" || ' seconds'),  
        DATETIME('2001-01-01', "ZLAST_WEIGHIN" || ' seconds'),  
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
        id = row[0]
        userid = row[1]
        assdate = row[2]
        lastdate = row[3]
        lastweighin = row[4]
        mac = row[5]
        firmware = row[6]
        lat = row[7]
        lon = row[8]  
        dev_timezone = row[9]  
        sync_disabled = row[10]      

        data_list.append((assdate, lastdate, lastweighin, id, userid, mac, firmware, lat, lon, dev_timezone, sync_disabled))

    data_headers = ('Association Timestamp', 'Last Used Timestamp', 'Last Weighin Timestamp', 'ID', 'User ID', 'MAC', 'Firmware', 'Latitude', 'Longitude', 'Device Timezone', 'Sync Disabled')
    
    return data_headers, data_list, files_found[0]