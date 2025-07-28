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
        "version": "0.2",
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
                'App Bundle ID', 'Artist', 'Album', 'Title', 'Genre', 'Media Duration', 'AirPLay Video', 
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
