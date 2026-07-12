__artifacts_v2__ = {
    "knowledgeC_BatteryPercentage": {
        "name": "knowledgeC - Battery Percentage",
        "description": "Battery Percentages extracted from knowledgeC database",
        "author": "@JohannPLW",
        "creation_date": "2023-11-05",
        "last_update_date": "2023-11-05",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "",
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
        "notes": "",
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
        "notes": "Query is a derivative of research provided by \
            - Sarah Edwards as part of her APOLLO project https://github.com/mac4n6/APOLLO \
            - Ian Wiffin blog post https://www.doubleblak.com/blogPosts.php?id=29",
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
        "notes": "Based on research by Geraldine Blay and Dan Ogden",
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
            "ctf2020_ios12": "iOS 12.4 | files found",
            "dexter_ios18": "iOS 18.3.2 | files found",
            "felix_ios17": "iOS 17.6.1 | files found",
            "fsfull002_ios17": "iOS 17.1 | files found",
            "hc_ios18_7": "iOS 18.7.8 | files found",
            "iphone11_ios17": "iOS 17.3 | files found",
            "iphone14plus_ios18": "iOS 18.0 | files found",
            "otto_ios17": "iOS 17.5.1 | files found",
            "abe_ios16": "iOS 16.5 | files found",
            "felix23_ios16": "iOS 16.5 | files found",
            "hickman_ios13": "iOS 13.3.1 | files found",
            "hickman_ios14": "iOS 14.3 | files found",
            "jess_ios15": "iOS 15.0.2 | files found",
            "magnet_ios16": "iOS 16.1.1 | files found",
        }
    },
    "knowledgeC_isLocked": {
        "name": "knowledgeC - Device Lock Status",
        "description": "parses /device/isLocked events from knowledgeC Database",
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
        "description": "parses /display/isBacklit events from knowledgeC Database",
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
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, does_column_exist_in_db, \
    convert_ts_human_to_timezone_offset

@artifact_processor
def knowledgeC_BatteryPercentage(files_found, _report_folder, _seeker, _wrap_text, timezone_offset):
    data_list = []
    db_file = ''

    for file_found in files_found:
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
        END AS 'Is Fully Charged?',
        datetime('2001-01-01', ZOBJECT.ZCREATIONDATE || ' seconds') AS 'Time Added'
        FROM ZOBJECT
        WHERE ZOBJECT.ZSTREAMNAME = '/device/batteryPercentage'
        ORDER BY ZOBJECT.ZSTARTDATE
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            end_time = convert_ts_human_to_timezone_offset(row[1], timezone_offset)
            added_time = convert_ts_human_to_timezone_offset(row[-1],timezone_offset)
            data_list.append((start_time, end_time, row[2], row[3], added_time))

    data_headers = (
         ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Battery Percentage', 'Is Fully Charged?',
         ('Time Added', 'datetime'))
    return data_headers, data_list, db_file

@artifact_processor
def knowledgeC_DevicePluginStatus(files_found, _report_folder, _seeker, _wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    db_file = ''

    for file_found in files_found:
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
        ORDER BY ZOBJECT.ZSTARTDATE
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            end_time = convert_ts_human_to_timezone_offset(row[1], timezone_offset)
            added_time = convert_ts_human_to_timezone_offset(row[-1],timezone_offset)
            if does_adapteriswireless_exist:
                data_list.append((start_time, end_time, row[2], row[3], added_time))
            else:
                data_list.append((start_time, end_time, row[2], added_time))

    return data_headers, data_list, db_file

@artifact_processor
def knowledgeC_MediaPlaying(files_found, _report_folder, _seeker, _wrap_text, timezone_offset):
    data_list = []
    data_headers = ()
    db_file = ''

    for file_found in files_found:
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
        ORDER BY ZOBJECT.ZSTARTDATE
        ''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            end_time = convert_ts_human_to_timezone_offset(row[1], timezone_offset)
            added_time = convert_ts_human_to_timezone_offset(row[-1],timezone_offset)

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
def knowledgeC_DoNotDisturb(files_found, _report_folder, _seeker, _wrap_text, timezone_offset):
    data_list = []
    db_file = ''

    for file_found in files_found:
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
            start_time = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            end_time = convert_ts_human_to_timezone_offset(row[1], timezone_offset)
            added_time = convert_ts_human_to_timezone_offset(row[3],timezone_offset)
            data_list.append((start_time, end_time, row[2], added_time))

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Do Not Disturb?', ('Time Added', 'datetime'))
    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_AppUsage(files_found, _report_folder, _seeker, _wrap_text, timezone_offset):
    ''' parse /app/usage entries from knowledgeC.db '''

    db_file = ''

    for file_found in files_found:
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
            ORDER BY ZOBJECT.ZSTARTDATE''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            end_time = convert_ts_human_to_timezone_offset(row[1], timezone_offset)
            added_time = convert_ts_human_to_timezone_offset(row[2],timezone_offset)
            data_list.append((start_time, end_time, added_time, row[3]))

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Time Added', 'datetime'), 'Application')

    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_AppUsage_EndTime(files_found, _report_folder, _seeker, _wrap_text, timezone_offset):
    ''' Parse /app/usage entries from knowledgeC.db with End Time as first column'''

    # NOTE: there is no need to add this to html and lava output, the only
    # purpose of this additional parsing is to add the End Time as separate
    # event in the tl.db

    db_file = ''

    for file_found in files_found:
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
            ORDER BY ZOBJECT.ZENDDATE''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            end_time = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            start_time = convert_ts_human_to_timezone_offset(row[1], timezone_offset)
            added_time = convert_ts_human_to_timezone_offset(row[2],timezone_offset)
            data_list.append((end_time, start_time, added_time, row[3]))

    data_headers = (
        ('End Time', 'datetime'), ('Start Time', 'datetime'), ('Time Added', 'datetime'), 'Application')
    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_isLocked(files_found, _report_folder, _seeker, _wrap_text, timezone_offset):
    ''' parse /device/isLocked entries from knowledgeC.db '''

    db_file = ''

    for file_found in files_found:
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
            start_time = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            end_time = convert_ts_human_to_timezone_offset(row[1], timezone_offset)
            added_time = convert_ts_human_to_timezone_offset(row[2],timezone_offset)
            data_list.append((start_time, end_time, added_time, row[3]))

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Time Added', 'datetime'), 'Device Lock Status')
    return data_headers, data_list, db_file


@artifact_processor
def knowledgeC_isBacklit(files_found, _report_folder, _seeker, _wrap_text, timezone_offset):
    ''' parse /display/isBacklit entries from knowledgeC.db '''

    db_file = ''

    for file_found in files_found:
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
            ORDER BY ZOBJECT.ZSTARTDATE''')

        all_rows = cursor.fetchall()

        for row in all_rows:
            start_time = convert_ts_human_to_timezone_offset(row[0], timezone_offset)
            end_time = convert_ts_human_to_timezone_offset(row[1], timezone_offset)
            added_time = convert_ts_human_to_timezone_offset(row[2],timezone_offset)
            data_list.append((start_time, end_time, added_time, row[3]))

    data_headers = (
        ('Start Time', 'datetime'), ('End Time', 'datetime'), ('Time Added', 'datetime'), 'Device Screen Status')
    return data_headers, data_list, db_file
