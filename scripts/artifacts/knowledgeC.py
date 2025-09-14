__artifacts_v2__ = {
    "knowledgeC_BatteryPercentage": {
        "name": "knowledgeC - Battery Percentage",
        "description": "Battery Percentages extracted from knowledgeC database",
        "author": "@JohannPLW",
        "version": "0.2",
        "date": "2023-11-05",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard"
    },
    "knowledgeC_DevicePluginStatus": {
        "name": "knowledgeC - Device Plugin Status",
        "description": "Is Device Plugged In events extracted from knowledgeC database",
        "author": "@JohannPLW",
        "version": "0.2",
        "date": "2023-11-05",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard"
    },
    "knowledgeC_MediaPlaying": {
        "name": "knowledgeC - Media Playing",
        "description": "Media playing events extracted from knowledgeC database",
        "author": "@JohannPLW",
        "version": "0.2.1",
        "date": "2023-10-31",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Query is a derivative of research provided by \
            - Sarah Edwards as part of her APOLLO project https://github.com/mac4n6/APOLLO \
            - Ian Wiffin blog post https://www.doubleblak.com/blogPosts.php?id=29",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard"
    },
    "knowledgeC_DoNotDisturb": {
        "name": "knowledgeC - Do Not Disturb",
        "description": "Do Not Disturb Status from knowledgeC Database",
        "author": "Geraldine Blay",
        "version": "0.2",
        "date": "2024-02-24",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Based on research by Geraldine Blay and Dan Ogden",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard"
    },
    "knowledgeC_AppUsage": {
        "name": "knowledgeC - App Usage",
        "description": "parses /app/usage events from knowledgeC Database",
        "author": "mxkrt@lsjam.nl",
        "version": "0.1",
        "date": "2025-09-13",
        "requirements": "none",
        "category": "App Usage",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "knowledgeC_AppUsage_EndTime": {
        "name": "knowledgeC - App Usage End",
        "description": "include End Time in timeline for /app/usage events from knowledgeC Database",
        "author": "mxkrt@lsjam.nl",
        "version": "0.1",
        "date": "2025-09-13",
        "requirements": "none",
        "category": "App Usage",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "timeline",
        "artifact_icon": "activity"
    },
    "knowledgeC_isLocked": {
        "name": "knowledgeC - Device Lock Status",
        "description": "parses /device/isLocked events from knowledgeC Database",
        "author": "mxkrt@lsjam.nl",
        "version": "0.1",
        "date": "2025-09-13",
        "requirements": "none",
        "category": "Device Usage",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "smartphone"
    },
    "knowledgeC_isBacklit": {
        "name": "knowledgeC - Device Screen Status",
        "description": "parses /display/isBacklit evemts from knowledgeC Database",
        "author": "mxkrt@lsjam.nl",
        "version": "0.1",
        "date": "2025-09-13",
        "requirements": "none",
        "category": "Device Usage",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "output_types": "standard",
        "artifact_icon": "smartphone"
    }
}

import plistlib
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, does_column_exist_in_db, \
    convert_ts_human_to_timezone_offset

@artifact_processor
def knowledgeC_BatteryPercentage(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
def knowledgeC_DevicePluginStatus(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
def knowledgeC_MediaPlaying(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
def knowledgeC_DoNotDisturb(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
def knowledgeC_AppUsage(files_found, report_folder, seeker, wrap_text, timezone_offset):
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

    return data_headers, data_list, file_found


@artifact_processor
def knowledgeC_AppUsage_EndTime(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
    return data_headers, data_list, file_found


@artifact_processor
def knowledgeC_isLocked(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
    return data_headers, data_list, file_found


@artifact_processor
def knowledgeC_isBacklit(files_found, report_folder, seeker, wrap_text, timezone_offset):
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
    return data_headers, data_list, file_found
