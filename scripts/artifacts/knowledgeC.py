__artifacts_v2__ = {
    "knowledgeC_BatteryPercentage": {
        "name": "knowledgeC - Battery Percentage",
        "description": "Battery Percentages extracted from knowledgeC database",
        "author": "@JohannPLW",
        "creation_date": "2023-11-05",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "ZHASSTRUCTUREDMETADATA indicates whether a structured-metadata row exists; the "
                 "fully-charged flag lives in the structured metadata itself per APOLLO's "
                 "knowledge_device_batterylevel module. In tested data this knowledgeC stream "
                 "carries rows on the iOS 12.4-15.0.2 images and no rows on any iOS 16.1.1-26.5.2 "
                 "image checked (the registered corpora; a comparison by Mattia Epifani in "
                 "2026-08 across 21 extractions of iOS 16.1.1 to 26.5.2 reported the same, and no "
                 "publication of it is cited here). An empty result on an image of those versions "
                 "matches what the tested images showed; it is not by itself evidence about the "
                 "device. Battery level on those images is available from the Power Log and Biome "
                 "battery artifacts. Reference: Sarah Edwards, APOLLO, "
                 "https://github.com/mac4n6/APOLLO/blob/bd725461fbd22c8ceadd04f0c4ded49b66147439/modules/knowledge_device_batterylevel.txt",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1408 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 2796 rows",
            "hickman_ios14": "iOS 14.3 | 3487 rows",
            "jess_ios15": "iOS 15.0.2 | 622 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "knowledgeC_DevicePluginStatus": {
        "name": "knowledgeC - Device Plugin Status",
        "description": "Is Device Plugged In events extracted from knowledgeC database",
        "author": "@JohannPLW",
        "creation_date": "2023-11-05",
        "last_update_date": "2023-11-05",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "The Unplugged (0) and Plugged in (1) labels follow Sarah Edwards, APOLLO, "
                 "https://github.com/mac4n6/APOLLO/blob/bd725461fbd22c8ceadd04f0c4ded49b66147439/modules/knowledge_device_pluggedin.txt, "
                 "written for iOS 11 to 14; any other value is reported as stored. Is Adapter "
                 "Wireless? is reported when the store has that column; it shows Yes for a stored "
                 "1, No for 0 and Not specified otherwise, and no source for that column was "
                 "found. In tested data this knowledgeC stream carries rows on the iOS "
                 "12.4-15.0.2 images and no rows on any iOS 16.1.1-26.5.2 image checked (the "
                 "registered corpora; a comparison by Mattia Epifani in 2026-08 across 21 "
                 "extractions of iOS 16.1.1 to 26.5.2 reported the same, and no publication of it "
                 "is cited here). An empty result on an image of those versions matches what the "
                 "tested images showed; it is not by itself evidence about the device. See the "
                 "Power Log and Biome cable-plug artifacts for those images.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 53 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 81 rows",
            "hickman_ios14": "iOS 14.3 | 147 rows",
            "jess_ios15": "iOS 15.0.2 | 50 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "knowledgeC_MediaPlaying": {
        "name": "knowledgeC - Media Playing",
        "description": "Media playing events extracted from knowledgeC database",
        "author": "@JohannPLW",
        "creation_date": "2023-10-31",
        "last_update_date": "2023-10-31",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Playing State labels the stored value (0 Stop, 1 Play, 2 Pause, 3 Loading, 4 "
                 "Interruption); no source for those labels was found, and any other value is "
                 "reported as stored. Rows with an empty bundle id are not reported. Output "
                 "Device is reported when the store has the AirPlay video column; it is the "
                 "seventh object of the stored output device archive and may not be a device name "
                 "on every row. The query follows Sarah Edwards, APOLLO, "
                 "https://github.com/mac4n6/APOLLO/blob/bd725461fbd22c8ceadd04f0c4ded49b66147439/modules/knowledge_audio_media_nowplaying.txt. "
                 "An Ian Whiffin (doubleblak.com) post was also credited; its link no longer "
                 "resolves.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "music",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 14 rows",
            "dexter_ios18": "iOS 18.3.2 | 449 rows",
            "felix_ios17": "iOS 17.6.1 | 13 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 65 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 78 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 177 rows",
            "hickman_ios14": "iOS 14.3 | 333 rows",
            "jess_ios15": "iOS 15.0.2 | 56 rows",
            "magnet_ios16": "iOS 16.1.1 | 10 rows",
        }
    },
    "knowledgeC_DoNotDisturb": {
        "name": "knowledgeC - Do Not Disturb",
        "description": "Do Not Disturb Status from knowledgeC Database",
        "author": "Geraldine Blay",
        "creation_date": "2024-02-24",
        "last_update_date": "2024-02-24",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Based on research by Geraldine Blay and Dan Ogden; no title or link for that "
                 "research is given here. The Do Not Disturb? column shows Yes for a stored value "
                 "of 1 and No for 0; any other value is shown as Not Specified. In tested data "
                 "rows are recorded only on the iOS 13.3.1 and 14.3 images; the iOS 12.4 and "
                 "15.0.2 images and every iOS 16.1.1-26.5.2 image checked (the registered "
                 "corpora; a comparison by Mattia Epifani in 2026-08 across 21 extractions of iOS "
                 "16.1.1 to 26.5.2 reported the same, and no publication of it is cited here) "
                 "yield no rows. An empty result on an image of those versions matches what the "
                 "tested images showed; it is not by itself evidence about the device.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 44 rows",
            "hickman_ios14": "iOS 14.3 | 57 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
        }
    },
    "knowledgeC_AppUsage": {
        "name": "knowledgeC - App Usage",
        "description": "parses /app/usage events from knowledgeC Database",
        "author": "mxkrt@lsjam.nl",
        "creation_date": "2025-09-13",
        "last_update_date": "2025-09-13",
        "requirements": "none",
        "category": "App Usage",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 691 rows",
            "dexter_ios18": "iOS 18.3.2 | 363 rows",
            "felix_ios17": "iOS 17.6.1 | 152 rows",
            "fsfull002_ios17": "iOS 17.1 | 65 rows",
            "hc_ios18_7": "iOS 18.7.8 | 184 rows",
            "iphone11_ios17": "iOS 17.3 | 435 rows",
            "iphone14plus_ios18": "iOS 18.0 | 143 rows",
            "otto_ios17": "iOS 17.5.1 | 676 rows",
            "abe_ios16": "iOS 16.5 | 1467 rows",
            "felix23_ios16": "iOS 16.5 | 116 rows",
            "hickman_ios13": "iOS 13.3.1 | 623 rows",
            "hickman_ios14": "iOS 14.3 | 611 rows",
            "jess_ios15": "iOS 15.0.2 | 162 rows",
            "magnet_ios16": "iOS 16.1.1 | 202 rows",
        }
    },
    "knowledgeC_AppUsage_EndTime": {
        "name": "knowledgeC - App Usage End",
        "description": "include End Time in timeline for /app/usage events from knowledgeC Database",
        "author": "mxkrt@lsjam.nl",
        "creation_date": "2025-09-13",
        "last_update_date": "2025-09-13",
        "requirements": "none",
        "category": "App Usage",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "timeline",
        "artifact_icon": "activity",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 691 rows",
            "dexter_ios18": "iOS 18.3.2 | 363 rows",
            "felix_ios17": "iOS 17.6.1 | 152 rows",
            "fsfull002_ios17": "iOS 17.1 | 65 rows",
            "hc_ios18_7": "iOS 18.7.8 | 184 rows",
            "iphone11_ios17": "iOS 17.3 | 435 rows",
            "iphone14plus_ios18": "iOS 18.0 | 143 rows",
            "otto_ios17": "iOS 17.5.1 | 676 rows",
            "abe_ios16": "iOS 16.5 | 1467 rows",
            "felix23_ios16": "iOS 16.5 | 116 rows",
            "hickman_ios13": "iOS 13.3.1 | 623 rows",
            "hickman_ios14": "iOS 14.3 | 611 rows",
            "jess_ios15": "iOS 15.0.2 | 162 rows",
            "magnet_ios16": "iOS 16.1.1 | 202 rows",
        }
    },
    "knowledgeC_isLocked": {
        "name": "knowledgeC - Device Lock Status",
        "description": "Rows of the /device/isLocked stream of knowledgeC.db. The Unlocked (0) "
                       "and Locked (1) labels follow Sarah Edwards, APOLLO, "
                       "https://github.com/mac4n6/APOLLO/blob/bd725461fbd22c8ceadd04f0c4ded49b66147439/modules/knowledge_device_locked.txt, "
                       "written for iOS 11 to 14; any other value is reported as stored.",
        "author": "mxkrt@lsjam.nl",
        "creation_date": "2025-09-13",
        "last_update_date": "2025-09-13",
        "requirements": "none",
        "category": "Device Usage",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 287 rows",
            "felix_ios17": "iOS 17.6.1 | 136 rows",
            "fsfull002_ios17": "iOS 17.1 | 49 rows",
            "hc_ios18_7": "iOS 18.7.8 | 164 rows",
            "iphone11_ios17": "iOS 17.3 | 91 rows",
            "iphone14plus_ios18": "iOS 18.0 | 33 rows",
            "otto_ios17": "iOS 17.5.1 | 60 rows",
            "abe_ios16": "iOS 16.5 | 710 rows",
            "felix23_ios16": "iOS 16.5 | 97 rows",
            "hickman_ios13": "iOS 13.3.1 | 277 rows",
            "hickman_ios14": "iOS 14.3 | 137 rows",
            "jess_ios15": "iOS 15.0.2 | 64 rows",
            "magnet_ios16": "iOS 16.1.1 | 95 rows",
        }
    },
    "knowledgeC_isBacklit": {
        "name": "knowledgeC - Device Screen Status",
        "description": "Rows of the /display/isBacklit stream of knowledgeC.db. The Backlight off "
                       "(0) and Backlight on (1) labels follow the 0 = no, 1 = yes reading of "
                       "'screen is backlit' in Sarah Edwards, APOLLO, "
                       "https://github.com/mac4n6/APOLLO/blob/bd725461fbd22c8ceadd04f0c4ded49b66147439/modules/knowledge_device_is_backlit.txt, "
                       "written for iOS 11 to 14; any other value is reported as stored.",
        "author": "mxkrt@lsjam.nl",
        "creation_date": "2025-09-13",
        "last_update_date": "2025-09-13",
        "requirements": "none",
        "category": "Device Usage",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "device-mobile",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 1331 rows",
            "dexter_ios18": "iOS 18.3.2 | 1767 rows",
            "felix_ios17": "iOS 17.6.1 | 383 rows",
            "fsfull002_ios17": "iOS 17.1 | 182 rows",
            "hc_ios18_7": "iOS 18.7.8 | 515 rows",
            "iphone11_ios17": "iOS 17.3 | 784 rows",
            "iphone14plus_ios18": "iOS 18.0 | 227 rows",
            "otto_ios17": "iOS 17.5.1 | 2237 rows",
            "abe_ios16": "iOS 16.5 | 5140 rows",
            "felix23_ios16": "iOS 16.5 | 274 rows",
            "hickman_ios13": "iOS 13.3.1 | 1494 rows",
            "hickman_ios14": "iOS 14.3 | 1189 rows",
            "jess_ios15": "iOS 15.0.2 | 398 rows",
            "magnet_ios16": "iOS 16.1.1 | 623 rows",
        }
    },
    "knowledgeC_LocationActivity": {
        "name": "knowledgeC - Location Activity",
        "description": "Places recorded in the knowledgeC /app/locationActivity stream, with the other "
                       "coordinate pairs found in the same record's payload",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-30",
        "last_update_date": "2026-09-30",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Reads each ZOBJECT row in the /app/locationActivity stream of knowledgeC.db with the "
                 "ZSTRUCTUREDMETADATA row it points to. Location Name, Display Name, Address, Place Latitude "
                 "and Place Longitude are that row's Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__ LOCATIONNAME, "
                 "DISPLAYNAME, FULLYFORMATTEDADDRESS, LATITUDE and LONGITUDE, as stored. Activity UUID is "
                 "Z_DKAPPLICATIONACTIVITYMETADATAKEY__USERACTIVITYUUID and Bundle ID is ZOBJECT.ZVALUESTRING. "
                 "Start Time is ZSTARTDATE, which equalled the row's end date and fell on a whole minute on all "
                 "48 tested rows; Creation Time is ZCREATIONDATE. "
                 "The user activity's required string (Z_DKAPPLICATIONACTIVITYMETADATAKEY__"
                 "USERACTIVITYREQUIREDSTRING) can carry a compressed payload: base64 between the two $ signs after "
                 "'bs'=, four bytes, then bzip2 holding a protobuf. Reference: Sarah Edwards, 'Providing Context to "
                 "iOS App Usage with knowledgeC.db and APOLLO', "
                 "https://www.mac4n6.com/blog/2020/1/13/apollo-into-the-details-with-application-activities. "
                 "Compressed Payload says whether that payload was present and whether it decoded. Other Coordinate "
                 "Pairs in Payload lists each nested protobuf message whose fields 1 and 2 are doubles within "
                 "latitude and longitude range (0, 0 excluded), with its distance from Place Latitude and Place "
                 "Longitude, the first field path it was found at and how many more held it, leaving out pairs "
                 "within 1 m of the place coordinates. Farthest "
                 "Other Pair (m) is the largest of those distances. What each pair represents is not established. "
                 "They are listed so that a coordinate another tool reads from this record can be checked against "
                 "the place the record names. Neither the place coordinates nor any other pair is established as "
                 "the device's location. "
                 "Tested on 22 registered images from iOS 12.4 to 26.5.2. Of those, only hickman_ios13 (8 rows) and "
                 "hickman_ios15 (40 rows) hold rows in this stream, so an empty result means only that the database "
                 "held none. Bundle ID held com.apple.Maps on all 48 rows. Rows repeat: one Activity UUID "
                 "covered all 8 hickman_ios13 rows, on which Location Name, Address, Place Latitude and Place "
                 "Longitude each held one value, and on hickman_ios15 one Activity UUID covered 33 rows naming two "
                 "places (7 rows naming one place, then 26 whose Location Name is Dropped Pin) while another covered "
                 "the other 7. The payload was present on 28 rows and "
                 "decoded on all 28. On the 26 Dropped Pin rows the only pair more than 1 m from the pin was at "
                 "field 1.5: 29 m away on 17 rows and 3,659 m away on 4; on the other 5 no pair was more than 1 m "
                 "away. On hickman_ios13 the 2 rows with a payload "
                 "listed pairs up to 1,287 m and 1,240 m from the place. "
                 "The required string also carries a maps.apple.com link on 21 of the 48 rows; its ll value was "
                 "within 0.00001 degrees of Place Latitude and Place Longitude on all 21, so it is not reported "
                 "separately. The title in the required string equalled Display Name on all 48 rows. The city, "
                 "state, postal code, street, street number and country columns each appeared within Address on all "
                 "48 rows and are not reported separately; the phone numbers column is not reported. "
                 "Not parsed here: com.apple.Maps rows in the /app/intents stream (INIntent verbs such as "
                 "Show and PlaceCardTap, whose parameters name the place; on hickman_ios13 a pin there is titled "
                 "Marked Location) and the 96 com.apple.Maps rows in /app/activity on hickman_ios13, none of which "
                 "has these place columns filled.",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 0 rows",
            "hickman_ios13": "iOS 13.3.1 | 8 rows",
            "hickman_ios14": "iOS 14.3 | 0 rows",
            "jess_ios15": "iOS 15.0.2 | 0 rows",
            "hickman_ios15": "iOS 15.3.1 | 40 rows",
            "magnet_ios16": "iOS 16.1.1 | 0 rows",
            "abe_ios16": "iOS 16.5 | 0 rows",
            "felix23_ios16": "iOS 16.5 | 0 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 0 rows",
            "fsfull002_ios17": "iOS 17.1 | 0 rows",
            "adams_iphone12mini": "iOS 17.1.1 | 0 rows",
            "hc_ios17_2": "iOS 17.2.1 | 0 rows",
            "iphone11_ios17": "iOS 17.3 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | 0 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 0 rows",
            "felix_ios17": "iOS 17.6.1 | 0 rows",
            "iphone14plus_ios18": "iOS 18.0 | 0 rows",
            "iphone14plus_ios18_mvs2025": "iOS 18.0 | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | 0 rows",
            "falken_ios26": "iOS 26.2.1 | 0 rows",
            "hc_ios26": "iOS 26.5.2 | 0 rows",
        }
    }
}

import base64
import binascii
import bz2
import math
import plistlib
import re
import struct
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, does_column_exist_in_db, \
    convert_ts_human_to_utc, convert_cocoa_core_data_ts_to_utc, logfunc

@artifact_processor
def knowledgeC_BatteryPercentage(context):
    data_list = []
    db_file = ''

    for file_found in context.get_files_found():
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS 'Start Time',
        datetime(ZOBJECT.ZENDDATE + 978307200, 'unixepoch') AS 'End Time',
        ZOBJECT.ZVALUEINTEGER AS 'Battery Percentage',
        CASE ZOBJECT.ZHASSTRUCTUREDMETADATA
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        ELSE ZOBJECT.ZHASSTRUCTUREDMETADATA
        END AS 'Has Structured Metadata',
        datetime('2001-01-01', ZOBJECT.ZCREATIONDATE || ' seconds') AS 'Time Added'
        FROM ZOBJECT
        WHERE ZOBJECT.ZSTREAMNAME = '/device/batteryPercentage'
        ORDER BY ZOBJECT.ZSTARTDATE
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            end_time = convert_ts_human_to_utc(row[1])
            added_time = convert_ts_human_to_utc(row[-1])
            data_list.append((start_time, end_time, row[2], row[3], added_time))

    data_headers = (
         ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Battery Percentage', 'Has Structured Metadata',
         ('Time Added', 'datetime'))
    return data_headers, data_list, db_file

@artifact_processor
def knowledgeC_DevicePluginStatus(context):
    data_list = []
    data_headers = ()
    db_file = ''

    for file_found in context.get_files_found():
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()

        does_adapteriswireless_exist = does_column_exist_in_db(
            db_file, 'ZSTRUCTUREDMETADATA', 'Z_DKDEVICEISPLUGGEDINMETADATAKEY__ADAPTERISWIRELESS')
        if does_adapteriswireless_exist:
            adapter_is_wireless = '''
            CASE ZSTRUCTUREDMETADATA.Z_DKDEVICEISPLUGGEDINMETADATAKEY__ADAPTERISWIRELESS
                WHEN '0' THEN 'No'
                WHEN '1' THEN 'Yes'
                ELSE 'Not specified'
            END AS "Adapter Is Wireless?",
            '''
            data_headers = (
                ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Device Plugin Status',
                'Is Adapter Wireless?', ('Time Added', 'datetime'))
        else:
            adapter_is_wireless = ''
            data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'Device Plugin Status',
                            ('Time Added', 'datetime'))

        cursor.execute(f'''
        SELECT
        datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS 'Start Time',
        datetime(ZOBJECT.ZENDDATE + 978307200, 'unixepoch') AS 'End Time',
        CASE ZOBJECT.ZVALUEINTEGER
            WHEN '0' THEN 'Unplugged'
            WHEN '1' THEN 'Plugged in'
            ELSE ZOBJECT.ZVALUEINTEGER
        END AS "Device Plugin Status",
        {adapter_is_wireless}
        datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'unixepoch') AS 'Time Added'
        FROM ZOBJECT
        LEFT OUTER JOIN ZSTRUCTUREDMETADATA ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
        WHERE ZOBJECT.ZSTREAMNAME = '/device/isPluggedIn'
        ORDER BY ZOBJECT.ZSTARTDATE, ZOBJECT.Z_PK
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            end_time = convert_ts_human_to_utc(row[1])
            added_time = convert_ts_human_to_utc(row[-1])
            if does_adapteriswireless_exist:
                data_list.append((start_time, end_time, row[2], row[3], added_time))
            else:
                data_list.append((start_time, end_time, row[2], added_time))

    return data_headers, data_list, db_file

@artifact_processor
def knowledgeC_MediaPlaying(context):
    data_list = []
    data_headers = ()
    db_file = ''

    for file_found in context.get_files_found():
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()

        does_airplayvideo_exist = does_column_exist_in_db(
            db_file, 'ZSTRUCTUREDMETADATA', 'Z_DKNOWPLAYINGMETADATAKEY__ISAIRPLAYVIDEO')
        if does_airplayvideo_exist:
            is_airplay_video = '''
            CASE ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__ISAIRPLAYVIDEO
                WHEN 0 THEN 'No'
                WHEN 1 THEN 'Yes'
                ELSE ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__ISAIRPLAYVIDEO
            END AS 'Is AirPlay Video',
            ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__OUTPUTDEVICEIDS AS 'Output Device',
            '''
            data_headers = (
                ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Playing State', 'Playing Duration',
                'App Bundle ID', 'Artist', 'Album', 'Title', 'Genre', 'Media Duration', 'AirPlay Video',
                'Output Device', ('Time Added', 'datetime'))
        else:
            is_airplay_video = ''
            data_headers = (
                ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Playing State', 'Playing Duration',
                'App Bundle ID', 'Artist', 'Album', 'Title', 'Genre', 'Media Duration', ('Time Added', 'datetime'))

        cursor.execute(f'''
        SELECT
        datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS 'Start Time',
        datetime(ZOBJECT.ZENDDATE + 978307200, 'unixepoch') AS 'End Time',
        CASE ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__PLAYING
            WHEN 0 THEN 'Stop'
            WHEN 1 THEN 'Play'
            WHEN 2 THEN 'Pause'
            WHEN 3 THEN 'Loading'
            WHEN 4 THEN 'Interruption'
            ELSE ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__PLAYING
        END AS 'Playing State',
        strftime('%H:%M:%S', ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE, 'unixepoch') AS 'Playing Time',
        ZOBJECT.ZVALUESTRING AS 'App Bundle ID',
        ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__ARTIST AS 'Artist',
        ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__ALBUM AS 'Album',
        ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__TITLE AS 'Title',
        ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__GENRE AS 'Genre',
        strftime('%H:%M:%S', ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__DURATION, 'unixepoch')	AS 'Media Duration',
        {is_airplay_video}
        datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'unixepoch') AS 'Time Added'
        FROM ZOBJECT
        LEFT OUTER JOIN ZSTRUCTUREDMETADATA ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
        WHERE ZOBJECT.ZSTREAMNAME = '/media/nowPlaying' AND ZOBJECT.ZVALUESTRING != ''
        ORDER BY ZOBJECT.ZSTARTDATE, ZOBJECT.Z_PK
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            end_time = convert_ts_human_to_utc(row[1])
            added_time = convert_ts_human_to_utc(row[-1])

            if does_airplayvideo_exist:
                output_device = ''
                output_device_ids = row[-2]
                if isinstance(output_device_ids, bytes):
                    output_device_bplist = plistlib.loads(output_device_ids)
                    for key, val in output_device_bplist.items():
                        if key == '$objects':
                            output_device = val[6]
                data_list.append((start_time, end_time, row[2], row[3], row[4], row[5],
                                row[6], row[7], row[8], row[9], row[10], output_device,
                                added_time))
            else:
                data_list.append((start_time, end_time, row[2], row[3], row[4], row[5],
                                row[6], row[7], row[8], row[9], added_time))

    return data_headers, data_list, db_file

@artifact_processor
def knowledgeC_DoNotDisturb(context):
    data_list = []
    db_file = ''

    for file_found in context.get_files_found():
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()

        cursor.execute('''
        SELECT
        datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS 'Start Time',
        datetime(ZOBJECT.ZENDDATE + 978307200, 'unixepoch') AS 'End Time',
        CASE
            ZOBJECT.ZVALUEINTEGER
            WHEN '0' THEN 'No'
            WHEN '1' THEN 'Yes'
            ELSE 'Not Specified'
        END AS 'Is Do Not Disturb On?',
        datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'unixepoch') AS 'Date Added'
        FROM ZOBJECT
        WHERE ZOBJECT.ZSTREAMNAME = '/settings/doNotDisturb'
        ORDER BY ZOBJECT.ZSTARTDATE
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            end_time = convert_ts_human_to_utc(row[1])
            added_time = convert_ts_human_to_utc(row[3])
            data_list.append((start_time, end_time, row[2], added_time))

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Do Not Disturb?', ('Time Added', 'datetime'))
    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_AppUsage(context):
    ''' parse /app/usage entries from knowledgeC.db '''

    db_file = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break

    data_list = []

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()

        cursor.execute('''
            SELECT datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS 'Start Time',
                   datetime(ZOBJECT.ZENDDATE + 978307200, 'unixepoch') AS 'End Time',
                   datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'unixepoch') AS 'Date Added',
                   ZVALUESTRING
            FROM ZOBJECT
            WHERE ZSTREAMNAME = '/app/usage'
            ORDER BY ZOBJECT.ZSTARTDATE, ZOBJECT.Z_PK''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            end_time = convert_ts_human_to_utc(row[1])
            added_time = convert_ts_human_to_utc(row[2])
            data_list.append((start_time, end_time, added_time, row[3]))

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Time Added', 'datetime'), 'Application')

    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_AppUsage_EndTime(context):
    ''' Parse /app/usage entries from knowledgeC.db with End Time as first column'''

    # NOTE: there is no need to add this to html and lava output, the only
    # purpose of this additional parsing is to add the End Time as separate
    # event in the tl.db

    db_file = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break

    data_list = []

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()

        cursor.execute('''
            SELECT datetime(ZOBJECT.ZENDDATE + 978307200, 'unixepoch') AS 'End Time',
                   datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS 'Start Time',
                   datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'unixepoch') AS 'Date Added',
                   ZVALUESTRING
            FROM ZOBJECT
            WHERE ZSTREAMNAME = '/app/usage'
            ORDER BY ZOBJECT.ZENDDATE, ZOBJECT.rowid''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            end_time = convert_ts_human_to_utc(row[0])
            start_time = convert_ts_human_to_utc(row[1])
            added_time = convert_ts_human_to_utc(row[2])
            data_list.append((end_time, start_time, added_time, row[3]))

    data_headers = (
        ('End Time', 'datetime'), ('Start Time', 'datetime'), ('Time Added', 'datetime'), 'Application')
    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_isLocked(context):
    ''' parse /device/isLocked entries from knowledgeC.db '''

    db_file = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break

    data_list = []

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()

        cursor.execute('''
            SELECT datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS 'Start Time',
                   datetime(ZOBJECT.ZENDDATE + 978307200, 'unixepoch') AS 'End Time',
                   datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'unixepoch') AS 'Date Added',
                   CASE ZOBJECT.ZVALUEINTEGER
                      WHEN '0' THEN 'Unlocked'
                      WHEN '1' THEN 'Locked'
                      ELSE ZOBJECT.ZVALUEINTEGER
                   END AS 'Device Lock Status'
            FROM ZOBJECT
            WHERE ZSTREAMNAME = '/device/isLocked'
            ORDER BY ZOBJECT.ZSTARTDATE''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            end_time = convert_ts_human_to_utc(row[1])
            added_time = convert_ts_human_to_utc(row[2])
            data_list.append((start_time, end_time, added_time, row[3]))

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Time Added', 'datetime'), 'Device Lock Status')
    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_isBacklit(context):
    ''' parse /display/isBacklit entries from knowledgeC.db '''

    db_file = ''

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break

    data_list = []

    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()

        cursor.execute('''
            SELECT datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS 'Start Time',
                   datetime(ZOBJECT.ZENDDATE + 978307200, 'unixepoch') AS 'End Time',
                   datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'unixepoch') AS 'Date Added',
                   CASE ZOBJECT.ZVALUEINTEGER
                      WHEN '0' THEN 'Backlight off'
                      WHEN '1' THEN 'Backlight on'
                      ELSE ZOBJECT.ZVALUEINTEGER
                   END AS 'Device Screen Status'
            FROM ZOBJECT
            WHERE ZSTREAMNAME = '/display/isBacklit'
            ORDER BY ZOBJECT.ZSTARTDATE, ZOBJECT.rowid''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            end_time = convert_ts_human_to_utc(row[1])
            added_time = convert_ts_human_to_utc(row[2])
            data_list.append((start_time, end_time, added_time, row[3]))

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Time Added', 'datetime'), 'Device Screen Status')
    return data_headers, data_list, db_file


_LOCATION_ACTIVITY_KEY = 'Z_DKLOCATIONAPPLICATIONACTIVITYMETADATAKEY__'
_APP_ACTIVITY_KEY = 'Z_DKAPPLICATIONACTIVITYMETADATAKEY__'
_PROTOBUF_ERRORS = (ValueError, IndexError, struct.error)


def _pb_varint(buf, pos):
    result = shift = 0
    while True:
        byte = buf[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        shift += 7
        if byte < 0x80:
            return result, pos
        if shift > 63:
            raise ValueError('varint longer than 10 bytes')


def _pb_fields(buf):
    """Read one protobuf message as (field, wire type, value) triples. Raises ValueError
    when the bytes are not a complete message, so a string is never read as one."""
    fields = []
    pos = 0
    while pos < len(buf):
        key, pos = _pb_varint(buf, pos)
        field, wire = key >> 3, key & 7
        if field == 0:
            raise ValueError('field number 0')
        if wire == 0:
            value, pos = _pb_varint(buf, pos)
        elif wire == 1:
            if pos + 8 > len(buf):
                raise ValueError('truncated fixed64')
            value = struct.unpack('<d', buf[pos:pos + 8])[0]
            pos += 8
        elif wire == 2:
            length, pos = _pb_varint(buf, pos)
            if pos + length > len(buf):
                raise ValueError('truncated length-delimited field')
            value = buf[pos:pos + length]
            pos += length
        elif wire == 5:
            if pos + 4 > len(buf):
                raise ValueError('truncated fixed32')
            value = None
            pos += 4
        else:
            raise ValueError(f'wire type {wire}')
        fields.append((field, wire, value))
    return fields


def _pb_coordinate_pairs(buf, path='', depth=0, found=None):
    """Every nested message whose field 1 and field 2 are doubles within latitude and
    longitude range, with the dotted field path to that message."""
    if found is None:
        found = []
    try:
        fields = _pb_fields(buf)
    except _PROTOBUF_ERRORS:
        return found
    doubles = {field: value for field, wire, value in fields if wire == 1}
    lat, lon = doubles.get(1), doubles.get(2)
    if (path and lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180
            and (lat, lon) != (0.0, 0.0)):
        found.append((path, lat, lon))
    if depth < 16:
        for field, wire, value in fields:
            if wire == 2 and value:
                _pb_coordinate_pairs(value, f'{path}.{field}' if path else str(field), depth + 1, found)
    return found


def _location_activity_payload(required_string):
    """The compressed payload in a user activity's required string: base64 between the
    two $ signs after 'bs'=, four bytes, then a bzip2 stream holding a protobuf (Sarah
    Edwards, mac4n6.com, 2020-01-14). Returns (payload bytes or None, status)."""
    match = re.search(r"'bs'=\$([A-Za-z0-9+/=]+)\$", required_string or '')
    if not match:
        return None, 'Not present'
    try:
        raw = base64.b64decode(match.group(1), validate=True)
    except (binascii.Error, ValueError) as ex:
        return None, f'Not decoded (base64: {ex})'
    if raw[4:7] != b'BZh':
        return None, 'Not decoded (no bzip2 header after the first 4 bytes)'
    try:
        return bz2.decompress(raw[4:]), 'Decoded'
    except (OSError, EOFError, ValueError) as ex:
        return None, f'Not decoded (bzip2: {ex})'


def _metres_between(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi, d_lambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    h = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(h))


@artifact_processor
def knowledgeC_LocationActivity(context):
    data_headers = (
        ('Start Time', 'datetime'), ('Creation Time', 'datetime'), 'Location Name', 'Display Name',
        'Address', 'Place Latitude', 'Place Longitude', 'Other Coordinate Pairs in Payload',
        'Farthest Other Pair (m)', 'Compressed Payload', 'Activity UUID', 'Bundle ID')
    data_list = []
    db_file = ''

    for file_found in context.get_files_found():
        if file_found.endswith('knowledgeC.db'):
            db_file = file_found
            break
    if not db_file:
        return data_headers, data_list, db_file

    wanted = (f'{_LOCATION_ACTIVITY_KEY}LOCATIONNAME', f'{_LOCATION_ACTIVITY_KEY}DISPLAYNAME',
              f'{_LOCATION_ACTIVITY_KEY}FULLYFORMATTEDADDRESS', f'{_LOCATION_ACTIVITY_KEY}LATITUDE',
              f'{_LOCATION_ACTIVITY_KEY}LONGITUDE', f'{_APP_ACTIVITY_KEY}USERACTIVITYREQUIREDSTRING',
              f'{_APP_ACTIVITY_KEY}USERACTIVITYUUID')
    with open_sqlite_db_readonly(db_file) as db:
        cursor = db.cursor()
        present = {row[1] for row in cursor.execute('PRAGMA table_info(ZSTRUCTUREDMETADATA)')}
        columns = ', '.join(f'ZSTRUCTUREDMETADATA.{name}' if name in present else 'NULL'
                            for name in wanted)
        cursor.execute(f'''
        SELECT ZOBJECT.ZSTARTDATE, ZOBJECT.ZCREATIONDATE, ZOBJECT.ZVALUESTRING, {columns}
        FROM ZOBJECT
        LEFT OUTER JOIN ZSTRUCTUREDMETADATA ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
        WHERE ZOBJECT.ZSTREAMNAME = '/app/locationActivity'
        ORDER BY ZOBJECT.ZSTARTDATE, ZOBJECT.ZCREATIONDATE, ZOBJECT.Z_PK
        ''')
        all_rows = cursor.fetchall()

    for (start, created, bundle, location_name, display_name, address, lat, lon,
         required_string, activity_uuid) in all_rows:
        payload, status = _location_activity_payload(required_string)
        if status.startswith('Not decoded'):
            logfunc(f'knowledgeC - Location Activity: payload {status}')
        others = {}
        for path, p_lat, p_lon in (_pb_coordinate_pairs(payload) if payload else []):
            key = (round(p_lat, 6), round(p_lon, 6))
            others.setdefault(key, []).append(path)
        described, farthest = [], None
        for (p_lat, p_lon), paths in others.items():
            paths = list(dict.fromkeys(paths))
            where = paths[0] + (f' and {len(paths) - 1} more' if len(paths) > 1 else '')
            if lat is None or lon is None:
                described.append(f'{p_lat:.6f}, {p_lon:.6f} (field {where})')
                continue
            metres = _metres_between(lat, lon, p_lat, p_lon)
            if metres < 1:
                continue
            farthest = max(farthest or 0, round(metres))
            described.append(f'{p_lat:.6f}, {p_lon:.6f} ({round(metres):,} m from the place coordinates; '
                             f'field {where})')
        data_list.append((
            convert_cocoa_core_data_ts_to_utc(start), convert_cocoa_core_data_ts_to_utc(created),
            location_name, display_name, address, lat, lon, '\n'.join(described),
            farthest if farthest is not None else '', status, activity_uuid, bundle))

    return data_headers, data_list, db_file
