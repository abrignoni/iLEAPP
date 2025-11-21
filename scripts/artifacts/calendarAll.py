__artifacts_v2__ = {
    "calendarEvents": {
        "name": "Calendar Events",
        "description": "List of calendar events",
        "author": "@JohannPLW, @JohnHyla",
        "creation_date": "2023-11-11",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Calendar",
        "notes": "",
        "paths": ('*/Calendar.sqlitedb',),
        "html_columns": ['Calendar Name', 'Location Coordinates', 'Invitees'],
        "output_types": "standard"
    },
    "calendarBirthdays": {
        "name": "Calendar Birthdays",
        "description": "List of calendar birthdays",
        "author": "@JohannPLW, @JohnHyla",
        "creation_date": "2024-10-30",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Calendar",
        "notes": "",
        "paths": ('*/Calendar.sqlitedb',),
        "html_columns": ['Calendar Name'],
        "output_types": "standard"
    },
    "calendarList": {
        "name": "Calendar List",
        "description": "List of calendars",
        "author": "@JohannPLW, @JohnHyla",
        "creation_date": "2023-11-11",
        "last_update_date": "2025-11-12",
        "requirements": "none",
        "category": "Calendar",
        "notes": "",
        "paths": ('*/Calendar.sqlitedb',),
        "html_columns": ['Calendar Name', 'Sharing Participants'],
        "output_types": "standard"
    }
}

from urllib.parse import unquote
from scripts.ilapfuncs import open_sqlite_db_readonly, does_table_exist_in_db, does_column_exist_in_db,\
    convert_ts_human_to_utc, artifact_processor, get_birthdate


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
def calendarEvents(context):
    data_list_html = []
    data_list = []
    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'Timezone', 'Calendar Name', 'Account Name', 'Event Title',
                    'Location Name', 'Location Address', 'Location Coordinates', 'Invitation From', 'Invitees',
                    'Conference URL', 'Attachments', 'Notes', ('Creation Time', 'datetime'), ('Last Modification Time', 'datetime'), 'Source File')

    for file_found in context.get_files_found():
        file_found = str(file_found)

        if file_found.endswith('.sqlitedb'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            # Calendar Events

            attachment_file_exists = does_table_exist_in_db(file_found, 'AttachmentFile')

            if attachment_file_exists:
                attachments = '''
                (SELECT group_concat(AttachmentFile.filename || ' (' || AttachmentFile.file_size || ' bytes)')
                FROM Attachment
                LEFT JOIN AttachmentFile ON Attachment.file_id = AttachmentFile.ROWID
                WHERE CalendarItem.ROWID = Attachment.owner_id
                GROUP BY Attachment.owner_id) AS 'Attachments',
                '''
            else:
                attachments = '''
                (SELECT group_concat(Attachment.filename || ' (' || Attachment.file_size || ' bytes)')
                FROM Attachment
                WHERE CalendarItem.ROWID = Attachment.owner_id
                GROUP BY Attachment.owner_id) AS 'Attachments',
                '''
            
            conference_url_detected_exists = does_column_exist_in_db(file_found, 'CalendarItem', 'conference_url_detected')
            conference_url = f"CalendarItem.conference_url{'_detected' if conference_url_detected_exists else ''} AS 'Conference URL',"


            cursor.execute(
            f'''
            SELECT CalendarItem.ROWID, 
            datetime('2001-01-01', CalendarItem.start_date || ' seconds') AS 'Start Time',
            datetime('2001-01-01', CalendarItem.end_date || ' seconds') AS 'End Time',
            CalendarItem.start_tz AS 'Timezone',
            Calendar.title AS 'Calendar Name',
            Calendar.color AS 'Calendar Color',
            Store.name AS 'Account Name',
            CalendarItem.summary AS 'Event Title',
            Location.title AS 'Location Name',
            Location.address AS 'Location Address',
            Location.latitude AS 'Location Latitude',
            Location.longitude AS 'Location Longitude',
            Identity.display_name AS 'Organizer Name',
            Participant.email AS 'Organizer email',
            CalendarItem.has_attendees AS 'Has Attendees',
            {conference_url}
            {attachments}
            CalendarItem.description AS 'Notes',
            datetime('2001-01-01', CalendarItem.creation_date || ' seconds') AS 'Creation Time',
            datetime('2001-01-01', CalendarItem.last_modified || ' seconds') AS 'Last Modification Time'
            FROM CalendarItem
            LEFT JOIN Location ON CalendarItem.location_id = Location.ROWID
            LEFT JOIN Calendar ON CalendarItem.calendar_id = Calendar.ROWID
            LEFT JOIN Store ON Calendar.store_id = Store.ROWID
            LEFT JOIN Participant  ON CalendarItem.organizer_id = Participant.ROWID
            LEFT JOIN Identity ON Participant.identity_id = Identity.ROWID
            WHERE CalendarItem.calendar_scale IS NOT 'gregorian'
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)

            if usageentries > 0:

                invitees = get_invitees(cursor)
                for row in all_rows:
                    start_time = convert_ts_human_to_utc(row[1])
                    end_time = convert_ts_human_to_utc(row[2])

                    if row[-2]:
                        creation_time = convert_ts_human_to_utc(row[-2])
                    else:
                        creation_time = ''

                    if row[-1]:
                        modification_time = convert_ts_human_to_utc(row[-1])
                    else:
                        modification_time = ''
                    
                    timezone = row[3] if row[3] != '_float' else ''
                    
                    calendar_name = row[4]
                    calendar_name_tag = get_calendar_name(row[4], row[5])

                    latitude = row[10]
                    longitude = row [11]
                    location_coordinates = f'{latitude}, {longitude}' if latitude and longitude else ''

                    if latitude and longitude:
                        location_coordinates_tag = f'''
                        {location_coordinates} &nbsp; 
                        <a href="https://www.openstreetmap.org/?lat={latitude}&lon=%20{longitude}&zoom=17&layers=M" target="_blank">
                        &#x1F5FA;</a>
                        '''
                    else:
                        location_coordinates_tag = ''

                    invitation_from = f'{row[12]} - {row[13]}' if row[12] else row[13]

                    attendees_tag = invitees[0].get(row[0], '')
                    attendees = invitees[1].get(row[0], '')

                    data_list_html.append((start_time, end_time, timezone, calendar_name_tag, row[6], row[7], row[8], 
                                      row[9], location_coordinates_tag, invitation_from, attendees_tag, row[15], 
                                      row[16], row[17], creation_time, modification_time, file_found))
            
                    data_list.append((start_time, end_time, timezone, calendar_name, row[6], row[7], row[8], 
                                      row[9], location_coordinates, invitation_from, attendees, row[15], row[16],
                                      row[17], creation_time, modification_time, file_found))
                    

    return data_headers, (data_list, data_list_html), 'see Source File for more info'


@artifact_processor
def calendarBirthdays(context):

    data_list_html = []
    data_list = []
    data_headers = (('Date of Birth', 'datetime'), 'Person Name', 'Calendar Name', 'Account Name', 'Source File')

    for file_found in context.get_files_found():
        file_found = str(file_found)

        if file_found.endswith('.sqlitedb'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            # Birthdays

            cursor.execute(
            '''
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

                data_list_html.append((birthdate, row[0], calendar_name_tag, row[4], file_found))
                data_list.append((birthdate, row[0], calendar_name, row[4], file_found))

    return data_headers, (data_list, data_list_html), 'see Source File for more info'


@artifact_processor
def calendarList(context):
    data_list_html = []
    data_list = []
    data_headers = ('Calendar Name', 'Account Name', 'Account Email', 'Owner Name',
                    'Owner Email', 'Sharing Status', 'Sharing Participants', 'Notes', 'Source File')

    for file_found in context.get_files_found():
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
                        data_list_html.append((calendar_name_tag, row[3], row[4], row[5], owner_email, row[7],
                                          sharing_participants_html, row[8], file_found))
                        data_list.append((calendar_name, row[3], row[4], row[5], owner_email, row[7],
                                              sharing_participants, row[8], file_found))
                    else:
                        data_list_html.append((calendar_name_tag, row[3], row[4], row[5], owner_email, row[7], None, row[8], file_found))
                        data_list.append((calendar_name, row[3], row[4], row[5], owner_email, row[7], None, row[8], file_found))
                
    return data_headers, (data_list, data_list_html), 'see Source File for more info'
