# Withings Health Mate App (com.withings.wiScaleNG)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# 
# Tested with the following versions:
# 2024-09-16: iOS 17.5.1, App: 6.3.1

# Requirements:  datetime, json




__artifacts_v2__ = {

    
    "HealthMateAccounts": {
        "name": "Health Mate - Accounts",
        "description": "Health Mate Accounts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-09-22",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('/private/var/mobile/Containers/Data/Application/*/Library/Application Support/account'),
        "function": "get_healthmate_accounts"
    },
    "HealthMateSleepTracking": {
        "name": "Health Mate - Sleep Tracking",
        "description": "Health Mate Sleep Tracking",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-09-23",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('*/Library/Application Support/coredata/*_Tracks*'),
        "function": "get_healthmate_sleep_tracking"
    },
    "HealthMateDailySummary": {
        "name": "Health Mate - Daily Summary",
        "description": "Health Mate Daily Summary",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-09-24",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('*/Library/Application Support/coredata/*_Tracks*'),
        "function": "get_healthmate_daily_summary"
    },
    "HealthMateTrackedActivities": {
    "name": "Health Mate - Tracked Activities",
    "description": "Health Mate Tracked Activities",
    "author": "Marco Neumann {kalinko@be-binary.de}",
    "version": "0.0.1",
    "date": "2024-09-24",
    "requirements": "none",
    "category": "Withings Health Mate",
    "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
    "paths": ('*/Library/Application Support/coredata/*_Tracks*'),
    "function": "get_healthmate_tracked_activities"
    },
    "HealthMateMessages": {
        "name": "Health Mate - Messages",
        "description": "Health Mate Messages",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-09-23",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('*/Library/Application Support/coredata/*_HM3Timeline*'),
        "function": "get_healthmate_messages"
    },
    "HealthMateMeasurements": {
        "name": "Health Mate - Measurements",
        "description": "Health Mate Measurements",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-09-23",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('*/Library/Application Support/coredata/*_vasistas*'),
        "function": "get_healthmate_measurements"
    },
    "HealthMateDevices": {
        "name": "Health Mate - Devices",
        "description": "Health Mate Devices",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-09-16",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html",
        "paths": ('*/Library/Application Support/coredata/associated_device.sqlite'),
        "function": "get_healthmate_devices"
    }
}



import datetime
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_healthmate_accounts(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Health Mate App - Accounts")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    with open (str(files_found[0])) as json_file:
        json_data = json.load(json_file)

        
    usageentries = len(json_data['account']['sources'])
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Accounts")
        description = f"Existing account in Health Mate App from Withings.\n This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html"
        report = ArtifactHtmlReport('Withings Health Mate - Accounts')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Accounts', description)
        report.add_script()
        data_headers = ( 'Creation Timestamp', 'Last Modified Timestamp', 'User ID', 'Last Name', 'First Name', 'Short Name', 'Birthdate', 'E-mail')
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

        tableID = 'healthmate_accounts'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Accounts'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Accounts'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate Account data found!')



def get_healthmate_sleep_tracking(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Health Mate App - Sleep Tracking")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    db = open_sqlite_db_readonly(str(files_found[0]))
    cursor = db.cursor()
    cursor.execute('''
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
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Sleep Tracking")
        description = f"Tracked sleep by Withings devices/app.\n This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html"
        report = ArtifactHtmlReport('Withings Health Mate - Sleep Tracking')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Sleep Tracking', description)
        report.add_script()
        data_headers = ('Start Date', 'End Date', 'Reference Date','Modified Date', 'Manual Start Date','Manual End Date','Device ID', 'Duration Light Sleep','Duration REM Sleep', 'Duration Deep Sleep', 'Duration To Sleep', 'Time To Get Up', 'Wake up count', 'Duration Awake', 'Timezone')
        data_list = []
        for row in all_rows:
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

        tableID = 'healthmate_sleep_racking'
 

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Sleep Tracking'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Sleep Tracking'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate Sleep Tracking data found!')

    db.close()

def get_healthmate_daily_summary(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Health Mate - Daily Summary")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    db = open_sqlite_db_readonly(str(files_found[0]))
    cursor = db.cursor()
    cursor.execute('''
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
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Daily Summary")
        description = f"Daily Summary of activities.\n This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html"
        report = ArtifactHtmlReport('Withings Health Mate - Daily Summary')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Daily Summary', description)
        report.add_script()
        data_headers = ('Start Date', 'End Date', 'Reference Date','Modified Date','Duration Inactive','Duration Intense', 'Duration Moderate', 'Duration Soft', 'Steps', 'Distance', 'Timezone')
        data_list = []
        for row in all_rows:
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

        tableID = 'healthmate_sleep_racking'
 

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Daily Summary'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Daily Summary'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate - Daily Summary data found!')

    db.close()

def get_healthmate_tracked_activities(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Health Mate - Tracked Activities")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    db = open_sqlite_db_readonly(str(files_found[0]))
    cursor = db.cursor()
    cursor.execute('''
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
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Tracked Activities")
        description = f"Tracked activities.\n This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/withings-healthmate-on-ios.html"
        report = ArtifactHtmlReport('Withings Health Mate - Tracked Activities')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Tracked Activities', description)
        report.add_script()
        data_headers = ('Start Date', 'End Date', 'Reference Date','Modified Date', 'Manual Start Date','Manual End Date', 'Device ID', 'Track ID', 'Type', 'Is Removed', 'Pause Duration', 'Duration Intense', 'Duration Moderate', 'Duration Light', 'Heart Rate MIN', 'Heart Rate AVG', 'Heart Rate MAX', 'Steps', 'Distance (no GPS)', 'Speed MIN', 'Speed AVG', 'Speed MAX', 'Distance (GPS)', 'Start Latitude', 'Start Longitude', 'Region Center Latitude', 'Region Center Longitude', 'End Latitude', 'End Longitude', 'Temperature MIN', 'Temperature AVG', 'Temperature MAX', 'Timezone')
        data_list = []
        for row in all_rows:
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

        tableID = 'healthmate_tracked_activities'
 

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Tracked Activities'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Tracked Activities'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate - Tracked Activities data found!')

    db.close()


def get_healthmate_messages(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Health Mate App - Messages")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
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

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Messages")
        description = "Existing Message data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html"
        report = ArtifactHtmlReport('Withings Health Mate - Messages')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Messages', description)
        report.add_script()
        data_headers = ('Timestamp [Local Time]', 'Timestamp Modified', 'Timestamp Expiration', 'Account ID', 'Sender ID', 'Receiver ID', 'Sender Last Name', 'Sender First Name', 'Type', 'Message')
        data_list = []
        #message_list = []
        for row in all_rows:
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

        tableID = 'healthmate_messages'

        
        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        #report.add_chat()
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Messages'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate Message data found!')

    db.close()


def get_healthmate_measurements(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Health Mate App - Measurements")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
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

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Measurements")
        description = "Existing Measurements data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html."
        report = ArtifactHtmlReport('Withings Healthmate - Measurements')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Measurements', description)
        report.add_script()
        data_headers = ('Timestamp', 'Category ID', 'Category', 'Device ID', 'Duration', 'Steps', 'Distance', 'Calories', 'Heart Rate', 'Latitude', 'Longitude', 'Altitude', 'Direction', 'Radius', 'Speed', 'SPO2', 'Ascent', 'Temperature')
        data_list = []
        for row in all_rows:
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

        tableID = 'healthmate_measurements'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Measurements'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Measurements'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate Measurements data found!')

    db.close()

def get_healthmate_devices(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Health Mate App - Devices")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
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

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Devices")
        description = "Existing Devices data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2024/09/app-healthmate-on-ios.html"
        report = ArtifactHtmlReport('Withings Health Mate - Devices')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Devices', description)
        report.add_script()
        data_headers = ('Association Timestamp', 'Last Used Timestamp', 'Last Weighin Timestamp', 'ID', 'User ID', 'MAC', 'Firmware', 'Latitude', 'Longitude', 'Device Timezone', 'Sync Disabled')
        data_list = []
        for row in all_rows:
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

        tableID = 'healthmate_devices'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Devices'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Devices'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate Devices data found!')

    db.close()