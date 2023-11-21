__artifacts_v2__ = {
    "knowledgeC": {
        "name": "knowledgeC",
        "description": "Extract Pattern of Life from knowledgeC database",
        "author": "@JohannPLW",
        "version": "0.1.1",
        "date": "2023-11-21",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "function": "get_knowledgeC_data"
    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, does_column_exist_in_db, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_knowledgeC_data(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('/knowledgeC.db'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    # Battery Percentage

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
    usageentries = len(all_rows)
    
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            start_time = convert_utc_human_to_timezone(start_time,timezone_offset)

            end_time = convert_ts_human_to_utc(row[1])
            end_time = convert_utc_human_to_timezone(end_time,timezone_offset)
            
            added_time = convert_ts_human_to_utc(row[-1])
            added_time = convert_utc_human_to_timezone(added_time,timezone_offset)

            data_list.append((start_time, end_time, row[2], row[3], added_time))

        description = "Battery Percentages extracted from knowledgeC database"
        report = ArtifactHtmlReport('knowledgeC - Battery Percentage')
        report.start_artifact_report(report_folder, 'knowledgeC - Battery Percentage', description)
        report.add_script()

        data_headers = ('Start Time', 'End Time', 'Battery Percentage', 'Is Fully Charged?', 'Time Added')   
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'knowledgeC - Battery Percentage'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'knowledgeC - Battery Percentage'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Battery Percentage event found in knowledgeC database')
    
    
    # Device Plugin Status

    does_adapteriswireless_exist = does_column_exist_in_db(db, 'ZSTRUCTUREDMETADATA', 'Z_DKDEVICEISPLUGGEDINMETADATAKEY__ADAPTERISWIRELESS')
    if does_adapteriswireless_exist:
        adapter_is_wireless = '''
        CASE ZSTRUCTUREDMETADATA.Z_DKDEVICEISPLUGGEDINMETADATAKEY__ADAPTERISWIRELESS
            WHEN '0' THEN 'No'
            WHEN '1' THEN 'Yes'
            ELSE 'Not specified'
        END AS "Adapter Is Wireless?",
        '''
        data_headers = ('Start Time', 'End Time', 'Device Plugin Status', 'Is Adapter Wireless?', 'Time Added')   
    else:
        adapter_is_wireless = ''
        data_headers = ('Start Time', 'End Time', 'Device Plugin Status', 'Time Added')   

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
    usageentries = len(all_rows)
    
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            start_time = convert_utc_human_to_timezone(start_time,timezone_offset)

            end_time = convert_ts_human_to_utc(row[1])
            end_time = convert_utc_human_to_timezone(end_time,timezone_offset)
            
            added_time = convert_ts_human_to_utc(row[-1])
            added_time = convert_utc_human_to_timezone(added_time,timezone_offset)

            if does_adapteriswireless_exist:
                data_list.append((start_time, end_time, row[2], row[3], added_time))
            else:
                data_list.append((start_time, end_time, row[2], added_time))

        description = "Is Device Plugged In events extracted from knowledgeC database"
        report = ArtifactHtmlReport('knowledgeC - Device Plugin Status')
        report.start_artifact_report(report_folder, 'knowledgeC - Device Plugin Status', description)
        report.add_script()

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'knowledgeC - Device Plugin Status'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'knowledgeC - Device Plugin Status'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No isDevicePluggedIn event found in knowledgeC database')
    

    # Media Playing

    does_airplayvideo_exist = does_column_exist_in_db(db, 'ZSTRUCTUREDMETADATA', 'Z_DKNOWPLAYINGMETADATAKEY__ISAIRPLAYVIDEO')
    if does_airplayvideo_exist:
        is_airplay_video = '''
        CASE ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__ISAIRPLAYVIDEO
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
            ELSE ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__ISAIRPLAYVIDEO
        END AS 'Is AirPlay Video',                
        ZSTRUCTUREDMETADATA.Z_DKNOWPLAYINGMETADATAKEY__OUTPUTDEVICEIDS AS 'Output Device',
        '''
        data_headers = ('Start Time', 'End Time', 'Playing State', 'Playing Duration', 'App Bundle ID', 'Artist', 'Album', 
                        'Title', 'Genre', 'Media Duration', 'AirPLay Video', 'Output Device', 'Time Added')   
    else:
        is_airplay_video = ''
        data_headers = ('Start Time', 'End Time', 'Playing State', 'Playing Duration', 'App Bundle ID', 'Artist', 'Album', 
                        'Title', 'Genre', 'Media Duration', 'Time Added')   

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
    usageentries = len(all_rows)
    
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            start_time = convert_utc_human_to_timezone(start_time,timezone_offset)

            end_time = convert_ts_human_to_utc(row[1])
            end_time = convert_utc_human_to_timezone(end_time,timezone_offset)
            
            added_time = convert_ts_human_to_utc(row[-1])
            added_time = convert_utc_human_to_timezone(added_time,timezone_offset)

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

        description = "Media playing events extracted from knowledgeC database"
        report = ArtifactHtmlReport('knowledgeC - Media Playing')
        report.start_artifact_report(report_folder, 'knowledgeC - Media Playing', description)
        report.add_script()

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'knowledgeC - Media Playing'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'knowledgeC - Media Playing'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Media Playing event found in knowledgeC database')
    
    db.close()

