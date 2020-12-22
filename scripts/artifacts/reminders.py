import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_reminders(files_found, report_folder, seeker):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT
            DATETIME(ZCREATIONDATE+978307200,'UNIXEPOCH'),
            DATETIME(ZLASTMODIFIEDDATE+978307200,'UNIXEPOCH'),
            ZNOTES,
            ZTITLE1
            FROM ZREMCDOBJECT
            WHERE ZTITLE1 <> ''
            ''')
    
        all_rows = cursor.fetchall()
        entries = len(all_rows)
    if entries > 0:
        filelocation = file_found
        for row in all_rows:
            data_list.append((row[0], row[3], row[2], row[1], filelocation))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Reminders')
        report.start_artifact_report(report_folder, 'Reminders')
        report.add_script()
        data_headers = ('Creation Date', 'Title', 'Note', 'Last Modified', 'File Location')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Reminders'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Reminders'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Reminders data available')

    db.close()
    return
