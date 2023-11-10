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
from urllib.parse import unquote
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone


def get_sharees(cursor):
    cursor.execute('''
    SELECT Sharee.owner_id,
    Identity.address, Identity.display_name,
    CASE Sharee.access_level
        WHEN 1 THEN 'View Only'
        WHEN 2 THEN 'View & Edit'
    ELSE Sharee.access_level
    END AS 'Access Level'
    FROM Sharee
    LEFT JOIN Identity ON Sharee.identity_id = Identity.ROWID
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_dict = {}
    if usageentries > 0:
        for row in all_rows:
            key = row[0]
            address = row[1].replace('mailto:', '') if row[1] else ''
            name = f' ({row[2]})' if row[2] else ''
            participant = f'{address}{name}'
            sharing_participant = f'''{participant} -> {row[3]}'''
            sharing_participants = data_dict.get(key, '')
            if sharing_participants:
                sharing_participants += f',<br>{sharing_participant}'
            else:
                sharing_participants = sharing_participant
            data_dict[key] = sharing_participants

    return data_dict


def get_calendarList(files_found, report_folder, seeker, wrap_text, timezone_offset):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlitedb'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT Calendar.ROWID,
            Calendar.title AS 'Calendar Name',
            Calendar.color AS 'Calendar Color',
            Store.name AS 'Account Name',
            CASE
                WHEN Calendar.self_identity_email IS NULL THEN Calendar.owner_identity_email
                ELSE Calendar.self_identity_email
            END AS 'Account Email',
			Identity.display_name AS 'Owner Name',
			Identity.address AS 'Owner Email',
            CASE Calendar.sharing_status
                WHEN 0 THEN 'Not shared'
                WHEN 1 THEN 'Shared by me'
                WHEN 2 THEN 'Shared with me'
                ELSE Calendar.sharing_status
            END AS 'Sharing Status',
            Calendar.notes AS 'Notes'
            FROM Calendar
            LEFT JOIN Store ON Calendar.store_id = Store.ROWID
			LEFT JOIN Identity ON Calendar.owner_identity_id = Identity.ROWID
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = []
                sharees = get_sharees(cursor)
                for row in all_rows:
                    color = row[2]
                    owner_email = row[6].replace('mailto:', '') if row[6] else ''
                    owner_email = unquote(owner_email)
                    if color:
                        color = f'''<span class="colored_dot" style="background-color: {color};"></span>'''
                    if sharees:
                        sharing_participants = sharees.get(row[0], '')
                        data_list.append((row[1], color, row[3], row[4], row[5], owner_email, row[7], 
                                            sharing_participants, row[8]))
                    else:
                        data_list.append((row[1], color, row[3], row[4], row[5], owner_email, row[7], row[8]))
    
                description = "List of Calendars"
                report = ArtifactHtmlReport('Calendar - List')
                report.start_artifact_report(report_folder, 'Calendar - List', description)
                report.add_script()

                if sharees:
                    data_headers = ('Calendar Name', 'Calendar Color', 'Account Name', 'Account Email', 'Owner Name', 
                                    'Owner Email', 'Sharing Status', 'Sharing Participants', 'Notes')
                else:
                    data_headers = ('Calendar Name', 'Calendar Color', 'Account Name', 'Account Email', 'Owner Name', 
                                    'Owner Email', 'Sharing Status', 'Notes')

                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Calendar Color', 'Sharing Participants'])
                report.end_artifact_report()

                tsvname = 'Calendar - List'
                tsv(report_folder, data_headers, data_list, tsvname)

            else:
                logfunc('No calendar found')

