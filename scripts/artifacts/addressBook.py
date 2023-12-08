__artifacts_v2__ = {
    "addressbook": {
        "name": "Address Book",
        "description": "Extract information from the native contacts application",
        "author": "@AlexisBrignoni - @JohannPLW",
        "version": "0.4",
        "date": "2022-11-18",
        "requirements": "none",
        "category": "Contacts",
        "notes": "",
        "paths": ('*/mobile/Library/AddressBook/AddressBook*.sqlitedb*',),
        "function": "get_addressBook"
    }
}


import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone, get_birthdate
from base64 import b64encode


def clean_label(data):
    return data.replace('_$!<', '').replace('>!$_', '')


def html_tag(data):
    return data.replace(chr(13), '<br>')


def remove_unused_rows(data, count_rows):
    data_count_rows = count_rows[0]
    rows_to_remove = []

    for i in range(len(data_count_rows)):
        if data_count_rows[i] == 0:
            rows_to_remove.append(i)
    
    data = [i for r, i in enumerate(data) if r not in rows_to_remove]
    return tuple(data)


def get_addressBook(files_found, report_folder, seeker, wrap_text, timezone_offset):
    address_book_db = ''
    address_book_images_db = ''

    for file_found in files_found:
        file_found = str(file_found)
    
        if file_found.endswith('AddressBook.sqlitedb'):
            address_book_db = file_found
        elif file_found.endswith('AddressBookImages.sqlitedb'):
            address_book_images_db = file_found
    
    db = open_sqlite_db_readonly(address_book_db)
    cursor = db.cursor()

    cursor.execute('''ATTACH DATABASE "''' + address_book_images_db + '''" AS ABI ''')

    cursor.execute('''SELECT    
    ABPerson.ROWID,
    datetime(ABPerson.CreationDate + 978307200, 'unixepoch') AS 'Creation Time',
    (SELECT ABI.ABThumbnailImage.data
    FROM ABI.ABThumbnailImage
    WHERE ABI.ABThumbnailImage.record_id = ABPerson.ROWID AND ABI.ABThumbnailImage.format = 0) AS 'Thumbnail',
    (SELECT ABI.ABFullSizeImage.data
    FROM ABI.ABFullSizeImage
    WHERE ABI.ABFullSizeImage.record_id = ABPerson.ROWID) AS 'Full Image',
    ABPerson.Prefix,
    ABPerson.First,
    ABPerson.Middle,
    ABPerson.Last,
    ABPerson.Suffix,
    ABPerson.DisplayName,
    ABPerson.FirstPhonetic,
    ABPerson.MiddlePhonetic,
    ABPerson.LastPhonetic,
    ABPerson.Organization,
    ABPerson.Department,
    ABPerson.JobTitle,
    (SELECT group_concat(ifnull(ABMultiValueLabel.value, '_') || ': ' || ABMultiValue.value, CHAR(13))
    FROM ABMultiValue
    LEFT JOIN ABMultiValueLabel ON ABMultiValue.label = ABMultiValueLabel.ROWID
    WHERE ABMultiValue.property = 3 AND ABMultiValue.record_id = ABPerson.ROWID
    GROUP BY ABMultiValue.record_id) AS 'Phone Numbers',
    (SELECT group_concat(ifnull(ABMultiValueLabel.value, '_') || ': ' || ABMultiValue.value, CHAR(13))
    FROM ABMultiValue
    LEFT JOIN ABMultiValueLabel ON ABMultiValue.label = ABMultiValueLabel.ROWID
    WHERE ABMultiValue.property = 4 AND ABMultiValue.record_id = ABPerson.ROWID
    GROUP BY ABMultiValue.record_id) AS 'Email addresses',
    (WITH 
        addresses(id, address) AS
        (WITH MVE(p, k, v) AS
            (SELECT ABMultiValueEntry.parent_id, ABMultiValueEntry.key, ABMultiValueEntry.value 
            FROM ABMultiValueEntry 
            ORDER BY ABMultiValueEntry.parent_id, ABMultiValueEntry.key)
        SELECT p, group_concat(v, ' - ') FROM MVE GROUP BY p),
        MV(label, rid, uid) AS 
            (SELECT ABMultiValueLabel.value, ABMultiValue.record_id, ABMultiValue.UID
            FROM ABMultiValue
            LEFT JOIN ABMultiValueLabel ON ABMultiValue.label = ABMultiValueLabel.ROWID
            WHERE ABMultiValue.property = 5 AND ABMultiValue.record_id = ABPerson.ROWID)
        SELECT group_concat(ifnull(label, '_') || ': ' || address, CHAR(13))
        FROM MV
        LEFT JOIN addresses ON uid = id
        GROUP BY rid) as 'Addresses',
    (WITH
        MVE_U(up, uv) AS
        (SELECT ABMultiValueEntry.parent_id, ABMultiValueEntry.value
        FROM ABMultiValueEntry
        LEFT JOIN ABMultiValueEntryKey ON ABMultiValueEntry.key = ABMultiValueEntryKey.ROWID
        WHERE ABMultiValueEntryKey.value = 'username'),
        MVE_S(sp, sv) AS
        (SELECT ABMultiValueEntry.parent_id, ABMultiValueEntry.value
        FROM ABMultiValueEntry
        LEFT JOIN ABMultiValueEntryKey ON ABMultiValueEntry.key = ABMultiValueEntryKey.ROWID
        WHERE ABMultiValueEntryKey.value = 'service'),
        MV(label, rid, uid) AS 
        (SELECT ABMultiValueLabel.value, ABMultiValue.record_id, ABMultiValue.UID
        FROM ABMultiValue
        LEFT JOIN ABMultiValueLabel ON ABMultiValue.label = ABMultiValueLabel.ROWID
        WHERE ABMultiValue.property = 13 AND ABMultiValue.record_id = ABPerson.ROWID)
    SELECT group_concat(ifnull(label, '_') || ': ' || uv || ' (' || sv || ')', CHAR(13))
    FROM MV
    LEFT JOIN MVE_U ON uid = up
    LEFT JOIN MVE_S ON up = sp
    GROUP BY rid) AS 'Instant Message',
    (SELECT group_concat(ifnull(ABMultiValueLabel.value, '_') || ': ' || ABMultiValue.value, CHAR(13))
    FROM ABMultiValue
    LEFT JOIN ABMultiValueLabel ON ABMultiValue.label = ABMultiValueLabel.ROWID
    WHERE ABMultiValue.property = 22 AND ABMultiValue.record_id = ABPerson.ROWID
    GROUP BY ABMultiValue.record_id) AS 'URL',
    (SELECT group_concat(ifnull(ABMultiValueLabel.value, '_') || ': ' || ABMultiValue.value, CHAR(13))
    FROM ABMultiValue
    LEFT JOIN ABMultiValueLabel ON ABMultiValue.label = ABMultiValueLabel.ROWID
    WHERE ABMultiValue.property = 23 AND ABMultiValue.record_id = ABPerson.ROWID
    GROUP BY ABMultiValue.record_id) AS 'Related Name',
    (WITH
        MVE(p, k, v) AS
        (SELECT ABMultiValueEntry.parent_id, ABMultiValueEntryKey.value, ABMultiValueEntry.value
        FROM ABMultiValueEntry
        LEFT JOIN ABMultiValueEntryKey ON ABMultiValueEntry.key = ABMultiValueEntryKey.ROWID),
        MV(label, rid, uid) AS 
        (SELECT ABMultiValueLabel.value, ABMultiValue.record_id, ABMultiValue.UID
        FROM ABMultiValue
        LEFT JOIN ABMultiValueLabel ON ABMultiValue.label = ABMultiValueLabel.ROWID
        WHERE ABMultiValue.property = 46 AND ABMultiValue.record_id = ABPerson.ROWID)
    SELECT group_concat(k || ': ' || v, CHAR(13))
    FROM MV
    LEFT JOIN MVE ON uid = p
    GROUP BY rid) AS 'Profile',
    ABPerson.Nickname,
    ABPerson.Note,
    CAST(ABPerson.Birthday AS INT) AS 'Birthday',
    (SELECT group_concat(ABGroup.Name, ', ')
    FROM ABGroupMembers
    LEFT JOIN ABGroup ON ABGroupMembers.group_id = ABGroup.ROWID
    WHERE ABGroupMembers.member_id = ABPerson.ROWID
    GROUP BY ABGroupMembers.member_id) AS 'Group',
    ABStore.Name,
    datetime(ABPerson.ModificationDate + 978307200, 'unixepoch') AS 'Modification Time'
    FROM ABPerson
    LEFT JOIN ABStore ON ABPerson.StoreID = ABStore.ROWID
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)

    if usageentries > 0:
        data_list = []
        html_data_list = []

        for row in all_rows:
            creation_date = row[1]
            if creation_date:
                creation_date = convert_ts_human_to_utc(creation_date)
                creation_date = convert_utc_human_to_timezone(creation_date,timezone_offset)
            
            thumbnail = row[2]
            if thumbnail:
                base64_thumbnail = b64encode(thumbnail).decode('utf-8')
                if row[3]:
                    file_extension = row[3][:4]
                    if file_extension.startswith(b'\xff\xd8\xff'):
                        file_extension = '.jpg'
                    elif file_extension.startswith(b'\x89PNG'):
                        file_extension = '.png'
                    else:
                        file_extension = ''
                    full_image_filename = f'{row[0]}.{file_extension}'
                    full_image_path = os.path.join(report_folder, full_image_filename)
                    with open(full_image_path, "wb") as full_image_file:
                        full_image_file.write(row[3])
                thumbnail_tag = f'<a href="{full_image_path}" target="_blank">'
                thumbnail_tag += f'<img src="data:image/jpeg;base64,{base64_thumbnail}" alt="Contact thumbnail" style="width: 90px; border-radius: 50%"></a>'
            else:
                thumbnail_tag = ''

            phone_numbers = row[16]
            if phone_numbers:
                phone_numbers = clean_label(phone_numbers)
            phone_numbers_html = html_tag(phone_numbers) if phone_numbers else phone_numbers
            
            email_addresses = row[17]
            if email_addresses:
                email_addresses = clean_label(email_addresses)
            email_addresses_html = html_tag(email_addresses) if email_addresses else email_addresses
            
            addresses = row[18]
            if addresses:
                addresses = clean_label(addresses)
            addresses_html = html_tag(addresses) if addresses else addresses
            
            instant_message = row[19]
            if instant_message:
                instant_message = clean_label(instant_message)
            instant_message_html = html_tag(instant_message) if instant_message else instant_message
            
            url = row[20]
            if url:
                url = clean_label(url)
            url_html = html_tag(url) if url else url
            
            related_name = row[21]
            if related_name:
                related_name = clean_label(related_name)
            related_name_html = html_tag(related_name) if related_name else related_name
            
            profile = row[22]
            if profile:
                profile = clean_label(profile)
            profile_html = html_tag(profile) if profile else profile
            
            birthday = row[-4]
            birthday = get_birthdate(birthday) if birthday else ''

            modified_date = row[-1]
            if modified_date:
                modified_date = convert_ts_human_to_utc(modified_date)
                modified_date = convert_utc_human_to_timezone(modified_date,timezone_offset)
            
            data_list.append([creation_date, row[2], row[4], row[5], row[6], row[7], row[8], row[9], 
                              row[10], row[11], row[12], row[13], row[14], row[15], 
                              row[16], row[17], row[18], row[19], row[20], row[21], 
                              row[22], row[23], row[24], birthday, row[26], row[27], modified_date])

            html_data_list.append([creation_date, thumbnail_tag, row[4], row[5], row[6], row[7], row[8], row[9], 
                              row[10], row[11], row[12], row[13], row[14], row[15], 
                              phone_numbers_html, email_addresses_html, addresses_html, instant_message_html, url_html, related_name_html, 
                              profile_html, row[23], row[24], birthday, row[26], row[27],modified_date])

        # Removing unused columns

        cursor.execute('''
        SELECT 'Create', count(ABI.ABThumbnailImage.data), count(ABPerson.Prefix), 'First', count(ABPerson.Middle), 'Last', count(ABPerson.Suffix), 
        count(ABPerson.DisplayName), count(ABPerson.FirstPhonetic), count(ABPerson.MiddlePhonetic), count(ABPerson.LastPhonetic), 
        count(ABPerson.Organization), count(ABPerson.Department), count(ABPerson.JobTitle), 
        count((SELECT ABMultiValue.property FROM ABMultiValue WHERE ABMultiValue.property = 3 AND ABMultiValue.record_id = ABPerson.ROWID)), 
        count((SELECT ABMultiValue.property FROM ABMultiValue WHERE ABMultiValue.property = 4 AND ABMultiValue.record_id = ABPerson.ROWID)), 
        count((SELECT ABMultiValue.property FROM ABMultiValue WHERE ABMultiValue.property = 5 AND ABMultiValue.record_id = ABPerson.ROWID)), 
        count((SELECT ABMultiValue.property FROM ABMultiValue WHERE ABMultiValue.property = 13 AND ABMultiValue.record_id = ABPerson.ROWID)), 
        count((SELECT ABMultiValue.property FROM ABMultiValue WHERE ABMultiValue.property = 22 AND ABMultiValue.record_id = ABPerson.ROWID)), 
        count((SELECT ABMultiValue.property FROM ABMultiValue WHERE ABMultiValue.property = 23 AND ABMultiValue.record_id = ABPerson.ROWID)), 
        count((SELECT ABMultiValue.property FROM ABMultiValue WHERE ABMultiValue.property = 46 AND ABMultiValue.record_id = ABPerson.ROWID)), 
        count(ABPerson.Nickname), count(ABPerson.Note), count(ABPerson.Birthday), count(ABGroupMembers.member_id), 'Store', 'Modif'
        FROM ABPerson
        LEFT JOIN ABGroupMembers ON ABPerson.ROWID = ABGroupMembers.member_id
        LEFT JOIN ABI.ABThumbnailImage ON ABPerson.ROWID = ABI.ABThumbnailImage.record_id
        ''')

        count_rows = cursor.fetchall()

        data_headers = ['Creation Date', 'Thumbnail', 'Prefix', 'First Name', 'Middle Name', 'Last Name', 'Suffix', 'Display Name', 
                        'First Name Phonetic', 'Middle Name Phonetic', 'Last Name Phonetic', 'Company', 'Department', 'Job Title', 
                        'Phone Numbers', 'Email addresses', 'Addresses', 'Instant Messages', 'URL', 'Related Names',
                        'Profiles', 'Nickname', 'Notes', 'Birthday', 'Group', 'Storage Place', 'Modification Date']

        data_headers = remove_unused_rows(data_headers, count_rows)
        html_data_list = [remove_unused_rows(data, count_rows) for data in html_data_list]
        data_list = [remove_unused_rows(data, count_rows) for data in data_list]

        # Removing thumbnail if exists in CSV
        if data_headers[1] == 'Thumbnail':
            csv_data_headers = list(data_headers)
            csv_data_headers.remove(csv_data_headers[1])
            csv_data_headers = tuple(csv_data_headers)

            csv_data_list = []
            for data in data_list:
                data = list(data)
                data.remove(data[1])
                data = tuple(data)
                csv_data_list.append(data)
        else:
            csv_data_headers = data_headers
            csv_data_list = data_list


        report = ArtifactHtmlReport('Address Book')
        report.start_artifact_report(report_folder, 'Address Book')
        report.add_script()
        report.write_artifact_data_table(data_headers, html_data_list, address_book_db, html_no_escape=['Thumbnail', 'Phone Numbers', 'Email addresses', 'Addresses', 'Instant Messages', 'URL', 'Related Names', 'Profiles'])
        report.end_artifact_report()

        tsvname = 'Address Book'
        tsv(report_folder, csv_data_headers, csv_data_list, tsvname)

        tlactivity = 'Address Book'
        timeline(report_folder, tlactivity, csv_data_list, data_headers)
    else:
        logfunc('No Address Book data available')

    db.close()
    return
