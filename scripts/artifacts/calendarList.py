__artifacts_v2__ = {
    "get_calendarList": {
        "name": "Calendar List",
        "description": "List of calendars",
        "author": "@JohannPLW, @JohnHyla",
        "version": "0.2",
        "date": "2023-11-11",
        "requirements": "none",
        "category": "Calendar",
        "notes": "",
        "paths": ('**/Calendar.sqlitedb',),
        "output_types": ["lava", "tsv"]
    }
}

from scripts.artifact_report import ArtifactHtmlReport
from urllib.parse import unquote
from scripts.ilapfuncs import open_sqlite_db_readonly, artifact_processor


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


def get_invitees(cursor):
    cursor.execute('''
    SELECT Participant.owner_id,
    Identity.display_name,
    Participant.email,
    CASE Participant.status
        WHEN 0 THEN 'No response'
        WHEN 1 THEN 'Accepted'
        WHEN 2 THEN 'Declined'
        WHEN 3 THEN 'Maybe'
        WHEN 7 THEN 'No response'
        ELSE Participant.status
    END AS 'Status'
    FROM Participant
    LEFT JOIN Identity ON Participant.identity_id = Identity.ROWID
    WHERE Participant.entity_type = 7
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_dict = {}
    data_dict_csv = {}
    if usageentries > 0:
        for row in all_rows:
            key = row[0]
            participant = f'{row[1]} - {row[2]}' if row[1] else row[2]
            status = row[3]
            if status == 'No response':
                html_status = '<span style="color: gray;" title="No response">&#11044;</span>'
            elif status == 'Accepted':
                html_status = '<span style="color: green;" title="Accepted">&#11044;</span>'
            elif status == 'Declined':
                html_status = '<span style="color: red;" title="Declined">&#11044;</span>'
            elif status == 'Maybe':
                html_status = '<span style="color: orange;" title="Maybe">&#11044;</span>'
            else:
                html_status = ''
            sharing_participant = f'{html_status} {participant}'

            sharing_participants = data_dict.get(key, '')
            if sharing_participants:
                sharing_participants += f',<br>{sharing_participant}'
            else:
                sharing_participants = sharing_participant
            data_dict[key] = sharing_participants

            participants = data_dict_csv.get(key, '')
            if participants:
                participants += f', {participant}'
            else:
                participants = participant
            data_dict_csv[key] = participants

    return data_dict, data_dict_csv


def get_calendar_name(name, color):
    if color:
        calendar_name = f'<span style="color: {color};">&#9673; </span>{name}'
    else:
        calendar_name = f'&#9711; {name}'
    return calendar_name

@artifact_processor
def get_calendarList(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_list = []
    data_list_csv = []

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.sqlitedb'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            # Calendar List

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

                sharees = get_sharees(cursor)
                for row in all_rows:
                    calendar_name = row[1]
                    calendar_name_tag = get_calendar_name(row[1], row[2])
                    owner_email = row[6].replace('mailto:', '') if row[6] else ''
                    owner_email = unquote(owner_email)
                    if sharees:
                        sharing_participants_html = sharees.get(row[0], '')
                        sharing_participants = sharees.get(row[0], '').replace('<br>', ' ')
                        data_list.append((calendar_name_tag, row[3], row[4], row[5], owner_email, row[7], 
                                            sharing_participants_html, row[8]))
                        data_list_csv.append((calendar_name, row[3], row[4], row[5], owner_email, row[7], 
                                            sharing_participants, row[8]))
                    else:
                        data_list.append((calendar_name_tag, row[3], row[4], row[5], owner_email, row[7], row[8]))
                        data_list_csv.append((calendar_name, row[3], row[4], row[5], owner_email, row[7], row[8]))
    
                report = ArtifactHtmlReport('Calendar List')
                report.start_artifact_report(report_folder, 'Calendar List')
                report.add_script()

                if sharees:
                    data_headers = ('Calendar Name', 'Account Name', 'Account Email', 'Owner Name', 
                                    'Owner Email', 'Sharing Status', 'Sharing Participants', 'Notes')
                else:
                    data_headers = ('Calendar Name', 'Account Name', 'Account Email', 'Owner Name', 
                                    'Owner Email', 'Sharing Status', 'Notes')

                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Calendar Name', 'Sharing Participants'])
                report.end_artifact_report()

    return data_headers, data_list_csv, file_found
