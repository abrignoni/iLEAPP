__artifacts_v2__ = {
    "life360CircleDrives": {
        "name": "Life360 - Circle Drives",
        "description": "Drives Life360 stored in its DriveModelStore database, with the start and end time, duration, "
                       "distance, speed, score and driving event counts as stored, and the user ID and circle IDs "
                       "stored for each drive.",
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from ZDRIVEMODEL in DriveModelStore.sqlite, with circle IDs from ZCIRCLEDRIVEMODEL. All '
                 'times are Cocoa seconds. Duration, distance and speed are as stored, without units. User ID is '
                 'ZUSERID as stored; the tested store held four distinct values. On the tested image Drive Type, '
                 'User Mode and User Tag held 2, 0 and -1, Score held 80, Rideshare Vendor was null, and Created '
                 'At equalled Updated At on every row. These are cached drive summaries; they do not show who '
                 'was in a vehicle. ZDRIVEEVENTMODEL and ZDRIVEWAYPOINTMODEL were empty and are not parsed. '
                 'Times render in UTC. Tested on Life360 26.34.0.5 (iOS 18.6); other versions may differ. Reads '
                 'only the main app container (container identifier com.life360.safetymap); extension containers '
                 'and iTunes backups are not read, and skipped files are named in the run log. Only the live '
                 'database with its WAL applied is read; older records left in the main database file are not '
                 'recovered.',
        "paths": ('*/Library/Application Support/DriveModelStore.sqlite*',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "car",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 0 rows",
        },
    },
    "life360Places": {
        "name": "Life360 - Places",
        "description": "The saved Places Life360 stored in its L360CoreDataStore database, with the name, centre "
                       "coordinates, radius, address, circle and owner as stored.",
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from ZPLACEMODEL in L360CoreDataStore.sqlite. Coordinates and Radius are as stored; the '
                 'radius unit is not recorded. Type, Source and Selection Type are as stored and undocumented. '
                 'Has Alerts shows 1 as Yes and 0 as No. Category is blank where the table has no ZCATEGORY '
                 'column (Life360 24.x). Last Retrieved is Cocoa seconds and is not a creation time. On the '
                 'tested image Type held 0, Owner ID held one value, Selection Type held an empty string and '
                 'Category was null on every row, and Address was null on 9 of 10 rows. Source ID equalled Place '
                 'ID on both iphone11_ios17 rows and on 11 of 54 felix_ios17 rows. ZPLACEOFINTERESTMODEL and '
                 'ZRESIDENCYMODEL are not parsed. Times render in UTC. Tested on Life360 26.34.0.5 (iOS 18.6); '
                 'other versions may differ. Reads only the main app container (container identifier '
                 'com.life360.safetymap); extension containers and iTunes backups are not read, and skipped '
                 'files are named in the run log. Only the live database with its WAL applied is read; older '
                 'records left in the main database file are not recovered.',
        "paths": ('*/Library/Application Support/L360CoreDataStore.sqlite*',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 54 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 2 rows",
        },
    },
    "life360PlaceAlerts": {
        "name": "Life360 - Place Alerts",
        "description": "The per-member arrival and departure alert settings Life360 stored for its saved "
                       "Places.",
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from ZPLACEALERTMODEL in L360CoreDataStore.sqlite, with the place name and coordinates '
                 'from ZPLACEMODEL. Arrival Alerts and Departure Alerts show 1 as Yes and 0 as No. A row is a '
                 'setting the app retrieved, not an alert that was sent. Arrival Alerts and Departure Alerts '
                 'were identical on every row of the tested image, felix_ios17 and iphone11_ios17. Last '
                 'Retrieved is Cocoa seconds. Circle ID held one value on every row of iphone11_ios17. Times '
                 'render in UTC. Tested on Life360 26.34.0.5 (iOS 18.6); other versions may differ. Reads only '
                 'the main app container (container identifier com.life360.safetymap); extension containers and '
                 'iTunes backups are not read, and skipped files are named in the run log. Only the live '
                 'database with its WAL applied is read; older records left in the main database file are not '
                 'recovered.',
        "paths": ('*/Library/Application Support/L360CoreDataStore.sqlite*',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 50 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 4 rows",
        },
    },
    "life360DriverReports": {
        "name": "Life360 - Driver Reports",
        "description": "The daily and weekly driver report rows Life360 stored in its L360CoreDataStore "
                       "database, with the period, member, trip count, distance, duration, top speed and "
                       "event counts as stored.",
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from ZDRIVERREPORTITEMMODEL in L360CoreDataStore.sqlite, joined to its daily or weekly '
                 'ZDRIVERREPORTMODEL row; Granularity says which. Start Day, End Day, Coverage Start, Coverage '
                 'End and Last Retrieved are Cocoa seconds; the day values can fall on local midnight, so read '
                 'them as dates. Counts and distances are as stored, without units. Report Type and Week are as '
                 'stored and undocumented. On the tested image Time Zone held one value and Crash Count held 0 '
                 'on every row. On felix_ios17 (Life360 24.34.0) Member ID had no value on any row and Report '
                 'Type held 1 on every row. Crash Count is a stored total, not a crash record. Times render in '
                 'UTC. Tested on Life360 26.34.0.5 (iOS 18.6); other versions may differ. Reads only the main '
                 'app container (container identifier com.life360.safetymap); extension containers and iTunes '
                 'backups are not read, and skipped files are named in the run log. Only the live database with '
                 'its WAL applied is read; older records left in the main database file are not recovered.',
        "paths": ('*/Library/Application Support/L360CoreDataStore.sqlite*',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "report",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 24 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 0 rows",
        },
    },
    "life360Account": {
        "name": "Life360 - Account and Device",
        "description": "Account, device registration, permission and session values Life360 stored in its "
                       "preferences plist, reported as key and value pairs.",
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Key and value pairs from com.life360.safetymap.plist: the CurrentUser object, '
                 'deviceRegistrationInfo, lpseRegistrationInfo, loggedInUserData, memberInfo, '
                 'L360LocationHealthStorage and selected scalar keys (user, circle, locale, device IDs, first '
                 'launch, current trip and permission status). Section names the plist key. Rendered Time is '
                 'added for created, dob, lastRetrieved and expiration (Cocoa seconds) for createdAt and '
                 'dateOfBirth (Unix seconds) and for values stored as plist dates; on the tested image the two '
                 'copies differed by exactly 978,307,200 seconds, the gap between the epochs. The '
                 'L360LocationHealthStorage time is left as stored; its epoch is not established. Permission '
                 'keys are as stored, not findings about a feature. A missing key is not evidence of anything. '
                 'location_state.data is read by the Location State Samples artifact. Not parsed: region_state.data, nk_v4_failed_network_requests.data, '
                 'Cache.db, UberIntegration.sqlite, GRPCModelStore.sqlite, Recommendations.sqlite, '
                 'FeatureSet.sqlite, ObservabilityEngineDataModel.sqlite, DEDataStore.sqlite, '
                 'ZoneCoreDataStore.sqlite, the modelstore and corelocation Realm files, the tmp/ProdLogs '
                 'driving log, empty L360CoreDataStore tables, and third-party SDK and ad stores. The main '
                 'database files held older records not in the live view, none of them reported: on the tested '
                 'image 352 drive_session, 119 BreachTopic, 87 trip_session, 53 FailedLocationTopic, 47 '
                 'DwellTopic and 13 dwell_session entries and 45 ZDRIVEMODEL drives. Times render in UTC. Tested '
                 'on Life360 26.34.0.5 (iOS 18.6); other versions may differ. Reads only the main app container '
                 '(container identifier com.life360.safetymap); iTunes backups are not read.',
        "paths": ('*/Library/Preferences/com.life360.safetymap.plist',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 83 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 64 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 57 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 88 rows",
        },
    },
    "life360Circles": {
        "name": "Life360 - Circles",
        "description": "The circles Life360 stored in its preferences plist, with the circle name, type, "
                       "creation time and the invite code the app cached for it.",
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from the com.life360.datakit.Circle.Type array in com.life360.safetymap.plist, joined on '
                 'circle ID to CircleCode.Type (invite code, deeplink and expiration) and memberRoles (role). '
                 'Created At, Invite Expiration and Last Retrieved are Cocoa seconds; Created At matched '
                 'ZCHATCIRCLE.ZCREATEDAT in Messaging.sqlite on the tested image. A circle with only an invite '
                 'code gets a row with blank name, type and Created At. A circle missing here may still exist in '
                 'the account. Role was empty on every row of the tested image. On abe_ios16, felix_ios17 and '
                 'iphone11_ios17 (Life360 23.x and 24.x) the single circle row had no Type, Invite Code, Invite '
                 'Deeplink or Invite Expiration value. Times render in UTC. Tested on Life360 26.34.0.5 (iOS '
                 '18.6); other versions may differ. Reads only the main app container (container identifier '
                 'com.life360.safetymap); iTunes backups are not read.',
        "paths": ('*/Library/Preferences/com.life360.safetymap.plist',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 1 row",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 1 row",
        },
    },
    "life360MemberSettings": {
        "name": "Life360 - Member and Circle Settings",
        "description": "The per-member, per-circle and per-user setting values Life360 cached in its "
                       "preferences plist, such as drive detection status and drive alert flags, decoded from "
                       "their base64 JSON form.",
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from the MemberCircleSettings.Type, CircleSettings.Type and UserSettings.Type arrays in '
                 'com.life360.safetymap.plist. Each holds alternating setting names and base64 JSON values; '
                 'Value is the decoded JSON, or the stored text when it does not decode. Scope says which array. '
                 'Last Retrieved is Cocoa seconds. What each setting controls is not established beyond its '
                 'name. Times render in UTC. Tested on Life360 26.34.0.5 (iOS 18.6); other versions may differ. '
                 'Reads only the main app container (container identifier com.life360.safetymap); iTunes backups '
                 'are not read.',
        "paths": ('*/Library/Preferences/com.life360.safetymap.plist',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 23 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 9 rows",
        },
    },
    "life360GeofenceStates": {
        "name": "Life360 - Geofence State Cache",
        "description": 'The place geometry and direction values Life360 stored in its preferences geofence-state '
                       'cache.',
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from AwarenessEngineGate.BreachRule.breachStateCache in com.life360.safetymap.plist: '
                 'name, coordinates, radius, circle and direction per place. No timestamp key was present in the '
                 'cache on the tested image, so its age is not known. On the tested image Direction held egress '
                 'and Unit held m on every row. Times render in UTC. Tested on Life360 26.34.0.5 (iOS 18.6); '
                 'other versions may differ. Reads only the main app container (container identifier '
                 'com.life360.safetymap); iTunes backups are not read.',
        "paths": ('*/Library/Preferences/com.life360.safetymap.plist',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "all",
        "artifact_icon": "circle-dashed",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 0 rows",
        },
    },
    "life360PopDwells": {
        "name": "Life360 - Pop Dwells Seen",
        "description": "The pop-dwell entries Life360 recorded as seen in its preferences plist, each with a "
                       "date, coordinates, circle and recurrence identifier.",
        "author": '@CyberMike81, Claude, OpenAI Codex',
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Life360",
        "notes": 'Read from the pop-dwell_seen array in com.life360.safetymap.plist. Date is the stored plist '
                 'date. What a pop dwell is in the app is not established; the key name is the only label. A row '
                 'does not show who was at the coordinates. Circle ID held one value on every row of the tested '
                 'image. Times render in UTC. Tested on Life360 26.34.0.5 (iOS 18.6); other versions may differ. '
                 'Reads only the main app container (container identifier com.life360.safetymap); iTunes backups '
                 'are not read.',
        "paths": ('*/Library/Preferences/com.life360.safetymap.plist',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | Life360 23.43.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 0 rows",
        },
    },
    "life360LocationState": {
        "name": "Life360 - Location State Samples",
        "description": "The location samples Life360 kept in its location_state.data archive, with the "
                       "coordinates, altitude, speed, course, accuracy and the Wi-Fi BSSID stored with each "
                       "sample.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Life360",
        "notes": ('Read from location_state.data in Library/Application Support, an NSKeyedArchiver archive of an '
                  'L360LocationPersistentState, decoded with nska_deserialize. One row per L360CLLocation in its '
                  'location array (20 on each tested image) and one for unsentFilteredSample when it holds a sample '
                  "(7 of 8 images); Store Key says which. Timestamp and Sample Timestamp are the sample's timestamp "
                  'and sampleTimestamp, rendered in UTC; Sample Timestamp was later on all 167 tested samples, by '
                  'up to about 240 seconds. On the 5 tested images whose logs carry sample lines (the Location '
                  'Samples artifact), 103 of 105 archive samples matched a log sample at the same coordinates to 4 '
                  "decimal places, and Timestamp was within 1 second of that log sample's time on 100 of the 103 "
                  '(Sample Timestamp on 94). On the other 3 images (Life360 25.37.0, 26.22.0 and an iOS 26 image) '
                  'the logs had no sample lines. Latitude, Longitude, Altitude, Speed, Course, Horizontal Accuracy '
                  'and Vertical Accuracy are as stored, with no units established. Wi-Fi BSSID (as stored) is '
                  'wifi_bssid: set on 46 of 167 samples on 6 images and empty on every sample on dexter_ios18 and '
                  'otto_ios17. 37 of the 46 drop a leading zero in at least one octet, so compare BSSIDs by value, '
                  'not as text. Location Mode (as stored) is locationmode, an integer whose names are not '
                  'established. Not reported: wifi_enabled (true on all 167 samples), mutated_sample (false on all '
                  "167) and json_violation_string (empty on all 167), and the archive's other keys (battery, smart "
                  'real-time, drive sampling and location request values, and three location strings that were '
                  'empty on all 8 images). A row records that the app kept a sample with those values; it does not '
                  'say who carried the device. Reads only the main app container (container identifier '
                  'com.life360.safetymap); iTunes backups are not read.'),
        "paths": ('*/Library/Application Support/location_state.data',
                  '*/.com.apple.mobile_container_manager.metadata.plist',),
        "output_types": "all",
        "artifact_icon": "wifi",
        "sample_data": {
            "abe_ios16": "iOS 16.5 | Life360 23.19.0 | 21 rows",
            "felix_ios17": "iOS 17.6.1 | Life360 24.34.0 | 21 rows",
            "hc_ios17_2": "iOS 17.2.1 | 21 rows",
            "hc_ios18_7": "iOS 18.7.8 | Life360 26.22.0 | 21 rows",
            "hc_ios26": "iOS 26.5.2 | 21 rows",
            "iphone11_ios17": "iOS 17.3 | Life360 24.28.0 | 21 rows",
            "otto_ios17": "iOS 17.5.1 | Life360 24.31.0 | 21 rows",
            "dexter_ios18": "iOS 18.3.2 | Life360 25.37.0 | 20 rows",
        },
    },
}

import base64
import json
import plistlib
from xml.parsers.expat import ExpatError
from datetime import datetime, timezone

import nska_deserialize as nd

from scripts.ilapfuncs import (artifact_processor, device_info, does_column_exist_in_db,
                               get_plist_file_content, logfunc)
from scripts.life360_common import (columns_first, get_life360_files, read_life360_rows,
                                   seconds_to_utc, stored_dict, stored_list)

_JSON_ERRORS = (json.JSONDecodeError, TypeError, ValueError, UnicodeDecodeError)


def _cocoa(value):
    return seconds_to_utc(value, 2001)


def _unix(value):
    return seconds_to_utc(value, 1970)


def _as_stored(value):
    return '' if value is None else value


def _yes_no(value):
    return {1: 'Yes', 0: 'No'}.get(value, _as_stored(value))


def _find(context, suffix):
    found = []
    for file_found in get_life360_files(context):
        file_found = str(file_found)
        if file_found.endswith(suffix) and file_found not in found:
            found.append(file_found)
    return found


@artifact_processor
def life360CircleDrives(context):
    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Duration (as stored)', 'Distance (as stored)',
        'Average Speed (as stored)', 'Top Speed (as stored)', 'Score (as stored)', 'Distracted Count',
        'Hard Braking Count', 'Rapid Acceleration Count', 'Speeding Count', 'Drive Type (as stored)',
        'User Mode (as stored)', 'User Tag (as stored)', 'Rideshare Vendor', 'User ID', 'Circle IDs',
        'Drive ID', ('Created At', 'datetime'), ('Updated At', 'datetime'), ('Last Retrieved', 'datetime'),
        'Source File',
    )
    data_list = []
    paths = _find(context, 'DriveModelStore.sqlite')
    query = '''
    SELECT d.ZSTARTTIME, d.ZENDTIME, d.ZDURATION, d.ZDISTANCE, d.ZAVERAGESPEED, d.ZTOPSPEED, d.ZSCORE,
           d.ZDISTRACTEDCOUNT, d.ZHARDBRAKINGCOUNT, d.ZRAPIDACCELERATIONCOUNT, d.ZSPEEDINGCOUNT,
           d.ZDRIVETYPE, d.ZUSERMODE, d.ZUSERTAG, d.ZRIDESHAREVENDOR, d.ZUSERID,
           (SELECT group_concat(c.ZCIRCLEID, ', ') FROM ZCIRCLEDRIVEMODEL c WHERE c.ZDRIVE = d.Z_PK),
           d.ZID, d.ZCREATEDAT, d.ZUPDATEDAT, d.ZLASTRETRIEVED
    FROM ZDRIVEMODEL d
    ORDER BY d.ZSTARTTIME
    '''
    for path in paths:
        rel = context.get_relative_path(path)
        for row in read_life360_rows(path, query, rel):
            data_list.append((_cocoa(row[0]), _cocoa(row[1])) + tuple(_as_stored(v) for v in row[2:18]) +
                             (_cocoa(row[18]), _cocoa(row[19]), _cocoa(row[20]), rel))
    data_headers, data_list = columns_first(data_headers, data_list, ('Start Time', 'End Time', 'Created At',
        'Updated At', 'Last Retrieved', 'Drive ID', 'User ID', 'Circle IDs'))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in paths)


@artifact_processor
def life360Places(context):
    data_headers = (
        'Name', 'Latitude', 'Longitude', 'Radius (as stored)', 'Address', 'Has Alerts', 'Type (as stored)',
        'Source (as stored)', 'Selection Type (as stored)', 'Category', 'Circle ID', 'Owner ID', 'Source ID',
        'Place ID', ('Last Retrieved', 'datetime'), 'Source File',
    )
    data_list = []
    paths = _find(context, 'L360CoreDataStore.sqlite')
    for path in paths:
        rel = context.get_relative_path(path)
        # ZCATEGORY is absent from the Life360 24.x schema
        category = 'ZCATEGORY' if does_column_exist_in_db(path, 'ZPLACEMODEL', 'ZCATEGORY') else 'NULL'
        query = f'''
        SELECT ZNAME, ZLATITUDE, ZLONGITUDE, ZRADIUS, ZADDRESS, ZHASALERTS, ZTYPE, ZSOURCE, ZSELECTIONTYPE,
               {category}, ZCIRCLEID, ZOWNERID, ZSOURCEID, ZID, ZLASTRETRIEVED
        FROM ZPLACEMODEL ORDER BY ZNAME
        '''
        for row in read_life360_rows(path, query, rel):
            data_list.append(tuple(_as_stored(v) for v in row[:5]) + (_yes_no(row[5]),) +
                             tuple(_as_stored(v) for v in row[6:14]) + (_cocoa(row[14]), rel))
    data_headers, data_list = columns_first(data_headers, data_list, ('Last Retrieved', 'Place ID',
        'Circle ID', 'Owner ID', 'Source ID'))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in paths)


@artifact_processor
def life360PlaceAlerts(context):
    data_headers = (
        'Place Name', 'Member ID', 'Arrival Alerts', 'Departure Alerts', 'Latitude', 'Longitude', 'Circle ID',
        'Place ID', 'Alert ID', ('Last Retrieved', 'datetime'), 'Source File',
    )
    data_list = []
    paths = _find(context, 'L360CoreDataStore.sqlite')
    query = '''
    SELECT p.ZNAME, a.ZMEMBERID, a.ZRECEIVESARRIVALALERTS, a.ZRECEIVESDEPARTUREALERTS, p.ZLATITUDE,
           p.ZLONGITUDE, a.ZCIRCLEID, a.ZPLACEID, a.ZID, a.ZLASTRETRIEVED
    FROM ZPLACEALERTMODEL a LEFT JOIN ZPLACEMODEL p ON p.ZID = a.ZPLACEID
    ORDER BY p.ZNAME, a.ZMEMBERID
    '''
    for path in paths:
        rel = context.get_relative_path(path)
        for row in read_life360_rows(path, query, rel):
            data_list.append((_as_stored(row[0]), _as_stored(row[1]), _yes_no(row[2]), _yes_no(row[3])) +
                             tuple(_as_stored(v) for v in row[4:9]) + (_cocoa(row[9]), rel))
    data_headers, data_list = columns_first(data_headers, data_list, ('Last Retrieved', 'Alert ID',
        'Place ID', 'Member ID', 'Circle ID'))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in paths)


@artifact_processor
def life360DriverReports(context):
    data_headers = (
        ('Start Day', 'datetime'), ('End Day', 'datetime'), 'Granularity', 'Member ID', 'Trips',
        'Distance (as stored)', 'Duration (as stored)', 'Top Speed (as stored)', 'Score (as stored)',
        'Distracted Count', 'Hard Braking Count', 'Rapid Acceleration Count', 'Speeding Count', 'Crash Count',
        'Report Type (as stored)', 'Week', 'Time Zone', ('Coverage Start', 'datetime'),
        ('Coverage End', 'datetime'), 'Circle ID', 'Report ID', 'Item ID', ('Last Retrieved', 'datetime'),
        'Source File',
    )
    data_list = []
    paths = _find(context, 'L360CoreDataStore.sqlite')
    query = '''
    SELECT i.ZSTARTDAY, i.ZENDDAY,
           CASE WHEN i.ZDRIVERREPORTDAILY IS NOT NULL THEN 'daily'
                WHEN i.ZDRIVERREPORTWEEK IS NOT NULL THEN 'weekly' ELSE '' END,
           r.ZMEMBERID, i.ZTRIPS, i.ZDISTANCE, i.ZDURATION, i.ZTOPSPEED, i.ZSCORE, i.ZDISTRACTEDCOUNT,
           i.ZHARDBRAKINGCOUNT, i.ZRAPIDACCELERATIONCOUNT, i.ZSPEEDINGCOUNT, i.ZCRASHCOUNT, r.ZREPORTTYPE,
           r.ZWEEK, r.ZTIMEZONE, r.ZCOVERAGESTARTDATE, r.ZCOVERAGEENDDATE, r.ZCIRCLEID, r.ZID, i.ZID,
           i.ZLASTRETRIEVED
    FROM ZDRIVERREPORTITEMMODEL i
    LEFT JOIN ZDRIVERREPORTMODEL r ON r.Z_PK = COALESCE(i.ZDRIVERREPORTDAILY, i.ZDRIVERREPORTWEEK)
    ORDER BY i.ZSTARTDAY, r.ZMEMBERID
    '''
    for path in paths:
        rel = context.get_relative_path(path)
        for row in read_life360_rows(path, query, rel):
            data_list.append((_cocoa(row[0]), _cocoa(row[1])) + tuple(_as_stored(v) for v in row[2:17]) +
                             (_cocoa(row[17]), _cocoa(row[18])) + tuple(_as_stored(v) for v in row[19:22]) +
                             (_cocoa(row[22]), rel))
    data_headers, data_list = columns_first(data_headers, data_list, ('Start Day', 'End Day',
        'Coverage Start', 'Coverage End', 'Last Retrieved', 'Report ID', 'Item ID', 'Member ID', 'Circle ID'))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in paths)


def _json_key(plist, key):
    """A com.life360.datakit.*.Type value: bytes holding a JSON array."""
    raw = plist.get(key)
    if raw is None:
        return []
    if isinstance(raw, (bytes, str)):
        try:
            raw = json.loads(raw)
        except _JSON_ERRORS:
            logfunc(f'Life360 preferences key {key} did not hold JSON and was skipped')
            return []
    if isinstance(raw, dict):
        return [raw]
    if not isinstance(raw, list):
        logfunc(f'Life360 preferences key {key} was neither an array nor an object and was skipped')
        return []
    objects = []
    for index, value in enumerate(raw):
        if isinstance(value, dict):
            objects.append(value)
        else:
            logfunc(f'Life360 preferences key {key} array element {index} was not an object and was skipped')
    return objects


def _dict_key(plist, key):
    """Some preference dictionaries are stored as JSON bytes rather than plist dictionaries."""
    raw = plist.get(key)
    if raw is None:
        return {}
    if isinstance(raw, (bytes, str)):
        try:
            raw = json.loads(raw)
        except _JSON_ERRORS:
            logfunc(f'Life360 preferences key {key} did not hold a JSON dictionary and was skipped')
            return {}
    if not isinstance(raw, dict):
        logfunc(f'Life360 preferences key {key} did not hold a dictionary and was skipped')
    return raw if isinstance(raw, dict) else {}


def _text(value):
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, datetime):
        return _plist_date(value).strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str, sort_keys=True)
    return _as_stored(value)


def _plist_date(value):
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if value is not None:
        logfunc('Life360 plist date was not a datetime; rendered time left blank')
    return ''


def _flatten(obj, prefix=''):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from _flatten(value, f'{prefix}.{key}' if prefix else str(key))
    else:
        yield prefix, obj


_SCALAR_KEYS = (
    'kL360UserDefaultsStoreuserEmail', 'kL360UserDefaultsStoreuserPhone', 'kL360UserDefaultsStoreuserFirstName',
    'kL360UserDefaultsStoreuserLastName', 'kL360UserDefaultsStoreselectedCircleID', 'kL360UserDefaultsStoretimeZone',
    'kL360UserDefaultsStorelocale', 'kL360UserDefaultsStoreunitOfMeasure', 'kL360UserDefaultsStoredateFormat',
    'firstCircleID', 'memberDeviceID', 'deviceUUID', 'ldDeviceIdentifier', 'preAuthUserKey', 'FirstLaunch',
    'first_launch', 'AppsFlyerInstallDate', 'AppsFlyerFirstLaunchDate', 'CURRENTTRIPID', 'TripCompletionFlag',
    'preciseLocationPermissionsAccess', 'queryLocationPermissionAccess', 'queryLocationServicesAccess',
    'queryBackgroundRefreshStatus', 'queryNotificationServicesAccess', 'queryActivityPermissionsStatus',
    'activity_permissions', 'flightDetectionSettingsStatus', 'privacyAndSecurityDrivingServicesStateKey',
    'pushAuthStatusUserDefaultsKey', 'isPushEnabledUserDefaultKey', 'hasEverBeenAuthorized',
    'appTrackingPermissionStatus', 'savedLocale', 'lastSuccessfulInboxUpdate',
)
_UNIX_KEYS = {'createdAt', 'dateOfBirth'}
_COCOA_KEYS = {'created', 'dob', 'lastRetrieved', 'expiration'}
_DICT_KEYS = ('deviceRegistrationInfo', 'lpseRegistrationInfo', 'kL360UserDefaultsStoreloggedInUserData',
              'L360LocationHealthStorage', 'kL360UserDefaultsStorememberInfo')


def _rendered(key, value):
    leaf = key.rsplit('.', 1)[-1]
    if isinstance(value, datetime):
        return _plist_date(value)
    if leaf in _COCOA_KEYS:
        return _cocoa(value)
    if leaf in _UNIX_KEYS:
        return _unix(value)
    return ''


@artifact_processor
def life360Account(context):
    data_headers = ('Section', 'Key', 'Value', ('Rendered Time', 'datetime'), 'Source File')
    data_list = []
    paths = _find(context, 'com.life360.safetymap.plist')
    for path in paths:
        plist = get_plist_file_content(path)
        if not isinstance(plist, dict):
            logfunc('Life360 preferences root was not an object and was skipped')
            continue
        rel = context.get_relative_path(path)

        def add(section, key, value, rel=rel):
            data_list.append((section, key, _text(value), _rendered(key, value), rel))

        for user in _json_key(plist, 'com.life360.datakit.CurrentUser.Type'):
            if not isinstance(user, dict):
                logfunc('Life360 CurrentUser array entry was not an object and was skipped')
                continue
            for key, value in _flatten(user):
                add('CurrentUser', key, value)
            for label, key in (('User ID', 'id'), ('Login Email', 'loginEmail'), ('Login Phone', 'loginPhone'),
                               ('First Name', 'firstName'), ('Last Name', 'lastName')):
                if user.get(key) not in (None, ''):
                    device_info('Life360', label, user.get(key), path)
        for section in _DICT_KEYS:
            for key, value in _flatten(_dict_key(plist, section)):
                add(section, key, value)
        registration = plist.get('deviceRegistrationInfo')
        if isinstance(registration, dict):
            for label, key in (('Device UDID', 'deviceUdid'), ('Device Model', 'deviceModel'),
                               ('App Version', 'appVersion'), ('Carrier', 'carrier')):
                if registration.get(key) not in (None, ''):
                    device_info('Life360', label, registration.get(key), path)
        for key in _SCALAR_KEYS:
            if key in plist:
                add('preferences', key, plist[key])
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in paths)


@artifact_processor
def life360Circles(context):
    data_headers = (
        'Circle Name', 'Circle ID', 'Type (as stored)', ('Created At', 'datetime'), 'Role (as stored)',
        'Invite Code', 'Invite Deeplink', ('Invite Expiration', 'datetime'), ('Last Retrieved', 'datetime'),
        'Source File',
    )
    data_list = []
    paths = _find(context, 'com.life360.safetymap.plist')
    for path in paths:
        plist = get_plist_file_content(path)
        if not isinstance(plist, dict):
            logfunc('Life360 preferences root was not an object and was skipped')
            continue
        rel = context.get_relative_path(path)
        codes = {c.get('circleID'): c for c in _json_key(plist, 'com.life360.datakit.CircleCode.Type')
                 if isinstance(c, dict)}
        roles = _dict_key(plist, 'memberRoles')
        seen = set()
        for circle in _json_key(plist, 'com.life360.datakit.Circle.Type'):
            if not isinstance(circle, dict):
                continue
            circle_id = circle.get('id')
            seen.add(circle_id)
            code = codes.get(circle_id, {})
            data_list.append((
                _as_stored(circle.get('name')), _as_stored(circle_id), _as_stored(circle.get('type')),
                _cocoa(circle.get('createdAt')), _as_stored(roles.get(circle_id)), _as_stored(code.get('code')),
                _as_stored(code.get('deeplink')), _cocoa(code.get('expiration')),
                _cocoa(circle.get('lastRetrieved')), rel,
            ))
        for circle_id, code in codes.items():
            if circle_id in seen:
                continue
            data_list.append(('', _as_stored(circle_id), '', '', _as_stored(roles.get(circle_id)),
                              _as_stored(code.get('code')), _as_stored(code.get('deeplink')),
                              _cocoa(code.get('expiration')), _cocoa(code.get('lastRetrieved')), rel))
    data_headers, data_list = columns_first(data_headers, data_list, ('Created At', 'Invite Expiration',
        'Last Retrieved', 'Circle ID'))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in paths)


def _decode_setting(raw):
    if not isinstance(raw, str):
        return _text(raw)
    try:
        decoded = base64.b64decode(raw, validate=True).decode('utf-8')
        return _text(json.loads(decoded))
    except _JSON_ERRORS:
        logfunc('Life360 setting could not be decoded as base64 JSON; raw value retained')
        return raw


@artifact_processor
def life360MemberSettings(context):
    data_headers = ('Scope', 'Member ID', 'Circle ID', 'Setting', 'Value', ('Last Retrieved', 'datetime'),
                    'Source File')
    data_list = []
    paths = _find(context, 'com.life360.safetymap.plist')
    for path in paths:
        plist = get_plist_file_content(path)
        if not isinstance(plist, dict):
            logfunc('Life360 preferences root was not an object and was skipped')
            continue
        rel = context.get_relative_path(path)
        for scope, key in (('member', 'com.life360.datakit.MemberCircleSettings.Type'),
                           ('circle', 'com.life360.datakit.CircleSettings.Type'),
                           ('user', 'com.life360.datakit.UserSettings.Type')):
            for block in _json_key(plist, key):
                if not isinstance(block, dict):
                    continue
                store = block.get('store')
                if not isinstance(store, list):
                    if store is not None:
                        logfunc('Life360 settings store was not an array and was skipped')
                    continue
                if len(store) % 2:
                    logfunc('Life360 settings store had an unpaired trailing key; paired settings retained')
                for index in range(0, len(store) - 1, 2):
                    data_list.append((scope, _as_stored(block.get('memberID')), _as_stored(block.get('circleID')),
                                      _as_stored(store[index]), _decode_setting(store[index + 1]),
                                      _cocoa(block.get('lastRetrieved')), rel))
    data_headers, data_list = columns_first(data_headers, data_list, ('Last Retrieved', 'Member ID',
        'Circle ID'))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in paths)


@artifact_processor
def life360GeofenceStates(context):
    data_headers = ('Place Name', 'Direction (as stored)', 'Latitude', 'Longitude', 'Radius', 'Unit', 'Circle ID',
                    'Place ID', 'Source File')
    data_list = []
    paths = _find(context, 'com.life360.safetymap.plist')
    for path in paths:
        plist = get_plist_file_content(path)
        if not isinstance(plist, dict):
            logfunc('Life360 preferences root was not an object and was skipped')
            continue
        rel = context.get_relative_path(path)
        raw = plist.get('AwarenessEngineGate.BreachRule.breachStateCache')
        try:
            cache = json.loads(raw) if isinstance(raw, (bytes, str)) else raw
        except _JSON_ERRORS:
            logfunc('Life360 breachStateCache did not hold JSON and was skipped')
            continue
        cache = stored_dict(cache, 'breachStateCache')
        states = stored_dict(cache.get('stateDictionary'), 'breach stateDictionary')
        for place_id, state in states.items():
            if not isinstance(state, dict):
                logfunc('Life360 breach state entry was not an object and was skipped')
                continue
            radius = stored_dict(state.get('radius'), 'breach state radius')
            unit = stored_dict(radius.get('unit'), 'breach state radius unit')
            data_list.append((_as_stored(state.get('name')), _as_stored(state.get('direction')),
                              _as_stored(state.get('latitude')), _as_stored(state.get('longitude')),
                              _as_stored(radius.get('value')), _as_stored(unit.get('symbol')),
                              _as_stored(state.get('circleId')), _as_stored(state.get('id', place_id)), rel))
    data_list.sort(key=lambda row: (str(row[6]), str(row[0])))
    data_headers, data_list = columns_first(data_headers, data_list, ('Place ID', 'Circle ID'))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in paths)


@artifact_processor
def life360PopDwells(context):
    data_headers = (('Date', 'datetime'), 'Latitude', 'Longitude', 'Circle ID', 'Recurrence ID', 'Source File')
    data_list = []
    paths = _find(context, 'com.life360.safetymap.plist')
    for path in paths:
        plist = get_plist_file_content(path)
        if not isinstance(plist, dict):
            logfunc('Life360 preferences root was not an object and was skipped')
            continue
        rel = context.get_relative_path(path)
        raw = plist.get('pop-dwell_seen')
        entries = raw
        if isinstance(raw, bytes):
            try:
                entries = plistlib.loads(raw)
            except (plistlib.InvalidFileException, ValueError, OverflowError, ExpatError):
                logfunc(f'Life360 pop-dwell_seen in {rel!r} did not parse as a plist and was skipped')
                continue
        entries = stored_list(entries, 'pop-dwell_seen')
        for entry in entries:
            if not isinstance(entry, dict):
                logfunc('Life360 pop-dwell_seen entry was not an object and was skipped')
                continue
            data_list.append((_plist_date(entry.get('date')), _as_stored(entry.get('latitude')),
                              _as_stored(entry.get('longitude')), _as_stored(entry.get('circleId')),
                              _as_stored(entry.get('recurrenceId')), rel))
    data_list.sort(key=lambda row: str(row[0]))
    data_headers, data_list = columns_first(data_headers, data_list, ('Date', 'Circle ID', 'Recurrence ID'))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in paths)


def _state_time(value):
    return value.replace(tzinfo=timezone.utc) if isinstance(value, datetime) else ''


@artifact_processor
def life360LocationState(context):
    data_headers = (('Timestamp', 'datetime'), ('Sample Timestamp', 'datetime'), 'Latitude', 'Longitude',
                    'Wi-Fi BSSID (as stored)', 'Altitude', 'Speed', 'Course', 'Horizontal Accuracy',
                    'Vertical Accuracy', 'Location Mode (as stored)', 'Store Key', 'Source File')
    data_list = []
    paths = _find(context, 'location_state.data')
    for path in paths:
        rel = context.get_relative_path(path)
        try:
            # deserialize_plist(path) opens the file and never closes it.
            with open(path, 'rb') as state_file:
                state = nd.deserialize_plist_from_string(state_file.read())
        except (nd.DeserializeError, plistlib.InvalidFileException, OSError, ValueError) as error:
            logfunc(f'Life360 location_state.data in {rel!r} did not deserialize and was skipped: {error}')
            continue
        if not isinstance(state, dict):
            logfunc('Life360 location_state.data root was not an object and was skipped')
            continue
        samples = [('location', s) for s in stored_list(state.get('location'), 'location_state location')]
        if isinstance(state.get('unsentFilteredSample'), dict):
            samples.append(('unsentFilteredSample', state['unsentFilteredSample']))
        for key, sample in samples:
            if not isinstance(sample, dict):
                logfunc('Life360 location_state sample was not an object and was skipped')
                continue
            data_list.append((
                _state_time(sample.get('timestamp')), _state_time(sample.get('sampleTimestamp')),
                _as_stored(sample.get('latitude')), _as_stored(sample.get('longitude')),
                _as_stored(sample.get('wifi_bssid')), _as_stored(sample.get('altitude')),
                _as_stored(sample.get('speed')), _as_stored(sample.get('course')),
                _as_stored(sample.get('horizontalaccuracy')), _as_stored(sample.get('verticalaccuracy')),
                _as_stored(sample.get('locationmode')), key, rel))
    data_list.sort(key=lambda row: (row[-1], str(row[0])))
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in paths)
