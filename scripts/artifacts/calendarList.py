__artifacts_v2__ = {
    "calendarList": {
        "name": "Calendar List",
        "description": "List of Calendars",
        "author": "@JohannPLW",
        "version": "0.1",
        "date": "2023-11-08",
        "requirements": "none",
        "category": "Calendar",
        "notes": "",
        "paths": ('**/Calendar.sqlitedb',),
        "function": "get_calendarList"
    }
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_calendarList(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlitedb'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT Calendar.title AS 'Calendar Name',
            Calendar.color AS 'Calendar Color',
            Store.name AS 'Account Name',
            Store.owner_name AS 'Owner Name',
            CASE
                WHEN Calendar.self_identity_email IS NULL THEN Calendar.owner_identity_email
                ELSE Calendar.self_identity_email
            END AS 'Owner Email',
            Calendar.notes AS 'Notes',
            CASE Calendar.sharing_status
                WHEN 0 THEN 'Not shared'
                WHEN 1 THEN 'Shared by me'
                WHEN 2 THEN 'Shared with me'
                ELSE Calendar.sharing_status
            END AS 'Sharing Status',
            Calendar.shared_owner_name,
            Calendar.shared_owner_address
            FROM Calendar
            LEFT JOIN Store ON Calendar.store_id = Store.ROWID
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = []
                for row in all_rows:
                    color = row[1]
                    if color:
                        color = f'''<span class="colored_dot" style="background-color: {color};"></span>'''

                    data_list.append((row[0], color, row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
    
                description = "List of Calendars"
                report = ArtifactHtmlReport('Calendar - List')
                report.start_artifact_report(report_folder, 'Calendar - List', description)
                report.add_script()

                data_headers = ('Calendar Name', 'Calendar Color', 'Account Name', 'Owner Name', 'Owner Email', 
                                'Notes', 'Sharing Status', 'Shared Owner Name', 'Shared Owner Address')   
                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Calendar Color'])
                report.end_artifact_report()

                tsvname = 'Calendar - List'
                tsv(report_folder, data_headers, data_list, tsvname)

            else:
                logfunc('No calendar found')

