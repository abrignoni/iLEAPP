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
    if usageentries > 0:
        for row in all_rows:
            key = row[0]
            participant = f'{row[1]} - {row[2]}' if row[1] else row[2]
            status = row[3]
            if status == 'No response':
                html_status = '<span style="color: gray;" title="No response">&#10687;</span>'
            elif status == 'Accepted':
                html_status = '<span style="color: green;" title="Accepted">&#10687;</span>'
            elif status == 'Declined':
                html_status = '<span style="color: red;" title="Declined">&#10687;</span>'
            elif status == 'Maybe':
                html_status = '<span style="color: orange;" title="Maybe">&#10687;</span>'
            else:
                html_status = ''
            sharing_participant = f'{html_status} {participant}'

            sharing_participants = data_dict.get(key, '')
            if sharing_participants:
                sharing_participants += f',<br>{sharing_participant}'
            else:
                sharing_participants = sharing_participant
            data_dict[key] = sharing_participants

    return data_dict


def get_calendar_name(name, color):
    if color:
        calendar_name = f'<span style="color: {color};">&#9673; </span>{name}'
    else:
        calendar_name = f'&#9711; {name}'
    return calendar_name


def get_calendarList(files_found, report_folder, seeker, wrap_text, timezone_offset):

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
                data_list = []
                sharees = get_sharees(cursor)
                for row in all_rows:
                    calendar_name = get_calendar_name(row[1], row[2])
                    owner_email = row[6].replace('mailto:', '') if row[6] else ''
                    owner_email = unquote(owner_email)
                    if sharees:
                        sharing_participants = sharees.get(row[0], '')
                        data_list.append((calendar_name, row[3], row[4], row[5], owner_email, row[7], 
                                            sharing_participants, row[8]))
                    else:
                        data_list.append((calendar_name, row[3], row[4], row[5], owner_email, row[7], row[8]))
    
                description = "List of Calendars"
                report = ArtifactHtmlReport('Calendar - List')
                report.start_artifact_report(report_folder, 'Calendar - List', description)
                report.add_script()

                if sharees:
                    data_headers = ('Calendar Name', 'Account Name', 'Account Email', 'Owner Name', 
                                    'Owner Email', 'Sharing Status', 'Sharing Participants', 'Notes')
                else:
                    data_headers = ('Calendar Name', 'Account Name', 'Account Email', 'Owner Name', 
                                    'Owner Email', 'Sharing Status', 'Notes')

                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Calendar Name', 'Sharing Participants'])
                report.end_artifact_report()

                tsvname = 'Calendar - List'
                tsv(report_folder, data_headers, data_list, tsvname)

            else:
                logfunc('No calendar found')


            # Calendar Events

            cursor.execute(
            """
            SELECT CalendarItem.ROWID, 
            datetime('2001-01-01', CalendarItem.start_date || ' seconds') AS 'Start Time',
            datetime('2001-01-01', CalendarItem.end_date || ' seconds') AS 'End Time',
            CalendarItem.start_tz AS 'Timezone',
            CalendarItem.summary AS 'Event Title',
            Calendar.title AS 'Calendar Name',
			Calendar.color AS 'Calendar Color',
            Store.name AS 'Account Name',
            Location.title AS 'Location Name',
            Location.address AS 'Location Address',
            Location.latitude AS 'Location Latitude',
            Location.longitude AS 'Location Longitude',
            Identity.display_name AS 'Organizer Name',
            Participant.email AS 'Organizer email',
            CalendarItem.has_attendees AS 'Has Attendees',
            CalendarItem.description AS 'Notes',
            datetime('2001-01-01', CalendarItem.creation_date || ' seconds') AS 'Creation Time',
            datetime('2001-01-01', CalendarItem.last_modified || ' seconds') AS 'Last Modification Time'
            FROM CalendarItem
            LEFT JOIN Location ON CalendarItem.location_id = Location.ROWID
            LEFT JOIN Calendar ON CalendarItem.calendar_id = Calendar.ROWID
            LEFT JOIN Store ON Calendar.store_id = Store.ROWID
            LEFT JOIN Participant  ON CalendarItem.organizer_id = Participant.ROWID
			LEFT JOIN Identity ON Participant.identity_id = Identity.ROWID
			WHERE CalendarItem.contact_name IS NULL
            """)

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)

            if usageentries > 0:
                data_list = []    
                invitees = get_invitees(cursor)
                for row in all_rows:
                    start_time = convert_ts_human_to_utc(row[1])
                    start_time = convert_utc_human_to_timezone(start_time,timezone_offset)

                    end_time = convert_ts_human_to_utc(row[2])
                    end_time = convert_utc_human_to_timezone(end_time,timezone_offset)

                    if row[-2]:
                        creation_time = convert_ts_human_to_utc(row[-2])
                        creation_time = convert_utc_human_to_timezone(creation_time,timezone_offset)
                    else:
                        creation_time = ''

                    if row[-1]:
                        modification_time = convert_ts_human_to_utc(row[-1])
                        modification_time = convert_utc_human_to_timezone(modification_time,timezone_offset)
                    else:
                        modification_time = ''
                    
                    timezone = row[3] if row[3] != '_float' else ''
                    
                    calendar_name = get_calendar_name(row[5], row[6])

                    invitation_from = f'{row[12]} - {row[13]}' if row[12] else row[13]

                    attendees = invitees.get(row[0], '')

                    data_list.append((start_time, end_time, timezone, row[4], calendar_name, row[7], row[8], 
                                      row[9], row[10], row[11], invitation_from, attendees, row[15], 
                                      creation_time, modification_time))
            
                description = ''
                report = ArtifactHtmlReport('Calendar Items')
                report.start_artifact_report(report_folder, 'Items', description)
                report.add_script()
                data_headers = ('Start Time', 'End Time', 'Timezone', 'Event Title', 'Calendar Name', 'Account Name', 
                                'Location Name', 'Location Address', 'Location Latitude', 'Location Longitude', 
                                'Invitation From', 'Invitees', 'Notes',
                                'Creation Time', 'Last Modification Time')

                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Calendar Name', 'Invitees'])
                report.end_artifact_report()
                
                tsvname = 'Calendar Items'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Calendar Items'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No data available for Calendar Items')
            
