__artifacts_v2__ = {
    "Battery Percentage": {
        "name": "knowledgeC Battery Percentage",
        "description": "Battery Percentage from knowledgeC database",
        "author": "@JohannPLW",
        "version": "0.1",
        "date": "2023-01-05",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "",
        "paths": ('**/CoreDuet/Knowledge/knowledgeC.db',),
        "function": "get_knowledgeC_BatteryPercentage"
    }
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_knowledgeC_BatteryPercentage(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT datetime('2001-01-01', ZOBJECT.ZSTARTDATE || ' seconds') AS 'Start Time',
            datetime('2001-01-01', ZOBJECT.ZENDDATE || ' seconds') AS 'End Time',
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

