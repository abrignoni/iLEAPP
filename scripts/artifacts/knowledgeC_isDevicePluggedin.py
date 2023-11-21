__artifacts_v2__ = {
    "Device Plugin Status": {
        "name": "knowledgeC is Device Plugged In",
        "description": "Is Device Plugged In events from knowledgeC database",
        "author": "@JohannPLW",
        "version": "0.1",
        "date": "2023-01-05",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "",
        "paths": ('**/CoreDuet/Knowledge/knowledgeC.db',),
        "function": "get_knowledgeC_isDevicePluggedIn"
    }
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, does_column_exist_in_db, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_knowledgeC_isDevicePluggedIn(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

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
            SELECT datetime('2001-01-01', ZOBJECT.ZSTARTDATE || ' seconds') AS 'Start Time',
            datetime('2001-01-01', ZOBJECT.ZENDDATE || ' seconds') AS 'End Time',
            CASE ZOBJECT.ZVALUEINTEGER
                WHEN '0' THEN 'Unplugged' 
                WHEN '1' THEN 'Plugged in'
                ELSE ZOBJECT.ZVALUEINTEGER
            END AS "Device Plugin Status",
            {adapter_is_wireless}
            datetime('2001-01-01', ZOBJECT.ZCREATIONDATE || ' seconds') AS 'Time Added'
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

