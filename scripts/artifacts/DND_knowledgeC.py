__artifacts_v2__ = {
    "DND_knowledgeC": {
        "name": "DNDknowledgeC",
        "description": "Do not Disturb Status from knowledgeC database. Based on research by Geraldine Blay and Dan Ogden",
        "author": "Geraldine Blay",
        "version": "0.0.1",
        "date": "2024-02-20",
        "requirements": "none",
        "category": "KnowledgeC",
        "notes": "",
        "paths": ('*/mobile/Library/CoreDuet/Knowledge/knowledgeC.db*',),
        "function": "get_DNDknowledgeC_state"
    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, does_column_exist_in_db, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_DNDknowledgeC_state(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('knowledgeC.db'):
            break

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

    # Do Not Disturb Status

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
    usageentries = len(all_rows)
    
    if usageentries > 0:
        data_list = []
        for row in all_rows:
            start_time = convert_ts_human_to_utc(row[0])
            start_time = convert_utc_human_to_timezone(start_time,timezone_offset)

            end_time = convert_ts_human_to_utc(row[1])
            end_time = convert_utc_human_to_timezone(end_time,timezone_offset)
            
            added_time = convert_ts_human_to_utc(row[3])
            added_time = convert_utc_human_to_timezone(added_time,timezone_offset)

            data_list.append((start_time, end_time, row[2], added_time))

        description = "Do Not Disturb Status from knowledgeC Database"
        report = ArtifactHtmlReport('knowledgeC - Do Not Disturb')
        report.start_artifact_report(report_folder, 'knowledgeC - Do Not Disturb', description)
        report.add_script()

        data_headers = ('Start Time', 'End Time', 'Do Not Disturb?', 'Time Added')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'knowledgeC - Do Not Disturb'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'knowledgeC - Do Not Disturb'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Do Not Disturb events found in knowledgeC database')

    
    db.close()

