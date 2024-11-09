__artifacts_v2__ = {
    "get_calendarBirthdays": {
        "name": "Calendar Birthdays",
        "description": "List of calendar birthdays",
        "author": "@JohannPLW, @JohnHyla",
        "version": "0.2",
        "date": "2024-10-30",
        "requirements": "none",
        "category": "Calendar",
        "notes": "",
        "paths": ('**/Calendar.sqlitedb',),
        "output_types": ["lava", "tsv"]

    }
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import open_sqlite_db_readonly, get_birthdate, artifact_processor


def get_calendar_name(name, color):
    if color:
        calendar_name = f'<span style="color: {color};">&#9673; </span>{name}'
    else:
        calendar_name = f'&#9711; {name}'
    return calendar_name

@artifact_processor
def get_calendarBirthdays(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_list = []
    data_list_csv = []
    data_headers = ['Person Name', 'Date of Birth', 'Calendar Name', 'Account Name']
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlitedb'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            report_file = file_found

            # Birthdays

            cursor.execute(
            f'''
            SELECT 
            CalendarItem.summary AS 'Person Name',
            CAST(CalendarItem.start_date AS INT) AS 'Date of Birth',
            Calendar.title AS 'Calendar Name',
            Calendar.color AS 'Calendar Color',
            Store.name AS 'Account Name'
            FROM CalendarItem
            LEFT JOIN Calendar ON CalendarItem.calendar_id = Calendar.ROWID
            LEFT JOIN Store ON Calendar.store_id = Store.ROWID
            WHERE CalendarItem.calendar_scale IS 'gregorian'
            ''')

            all_rows = cursor.fetchall()


            for row in all_rows:
                birthdate = get_birthdate(row[1])
                calendar_name = row[2]
                calendar_name_tag = get_calendar_name(row[2], row[3])

                data_list.append((row[0], birthdate, calendar_name_tag, row[4]))
                data_list_csv.append((row[0], birthdate, calendar_name, row[4]))

            # Handle HTML Manually due to html_no_escape
            if data_list:
                report = ArtifactHtmlReport('Calendar Birthdays')
                report.start_artifact_report(report_folder, 'Calendar Birthdays')
                report.add_script()
                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Calendar Name'])
                report.end_artifact_report()

    data_headers[1] = (data_headers[1], 'datetime')

    return data_headers, data_list_csv, report_file

