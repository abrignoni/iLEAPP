__artifacts_v2__ = {
    "Media Playing": {
        "name": "knowledgeC Media Playing",
        "description": "Media played from knowledgeC database",
        "author": "@JohannPLW",
        "version": "0.1",
        "date": "2023-10-31",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "Query is a derivative of research provided by \
            - Sarah Edwards as part of her APOLLO project https://github.com/mac4n6/APOLLO \
            - Ian Wiffin blog post https://www.doubleblak.com/blogPosts.php?id=29",
        "paths": ('**/CoreDuet/Knowledge/knowledgeC.db',),
        "function": "get_knowledgeC_MediaPlaying"
    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, does_column_exist_in_db, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_knowledgeC_MediaPlaying(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

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
            SELECT datetime('2001-01-01', ZOBJECT.ZSTARTDATE || ' seconds') AS 'Start Time',
            datetime('2001-01-01', ZOBJECT.ZENDDATE || ' seconds') AS 'End Time',
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
            datetime('2001-01-01', ZOBJECT.ZCREATIONDATE || ' seconds') AS 'Time Added'
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
