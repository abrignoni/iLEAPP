from os.path import dirname

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_reminders(files_found, report_folder, seeker):
    data_list = []
    for file_found in files_found:
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

    if len(all_rows) > 0:
        location_file_found = file_found.split('Stores/', 1)[1]
        for row in all_rows:
            data_list.append((row[0], row[3], row[2], row[1], location_file_found))

        dir_file_found = dirname(file_found).split('Stores', 1)[0] + 'Stores'

        report = ArtifactHtmlReport('Reminders')
        report.start_artifact_report(report_folder, 'Reminders')
        report.add_script()
        data_headers = ('Creation Date', 'Title', 'Note to Reminder', 'Last Modified', 'File Location')
        report.write_artifact_data_table(data_headers, data_list, dir_file_found)
        report.end_artifact_report()

        tsvname = 'Reminders'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Reminders'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Reminders available')

    db.close()
    return
