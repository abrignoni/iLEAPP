__artifacts_v2__ = {
    "addressBook": {
        "name": "Address Book",
        "description": "Extract information from the native contacts application",
        "author": "@AlexisBrignoni - @JohannPLW",
        "version": "0.5",
        "date": "2020-12-22",
        "requirements": "none",
        "category": "Contacts",
        "notes": "",
        "paths": ('*/mobile/Library/AddressBook/AddressBook*.sqlitedb*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "media_style": ("height: 80px; border-radius: 50%;", "height: 80px;")
    }
}

import inspect

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, check_in_embedded_media, \
    convert_cocoa_core_data_ts_to_utc, get_birthdate


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

@artifact_processor
def addressBook(files_found, report_folder, seeker, wrap_text, timezone_offset):
    source_path = get_file_path(files_found, "AddressBook.sqlitedb")
    address_book_images_db = get_file_path(files_found, "AddressBookImages.sqlitedb")

    data_list = []
    artifact_info = inspect.stack()[0]
    
    attach_query = '''ATTACH DATABASE "file:''' + address_book_images_db + '''?mode=ro" AS ABI '''
    
    query = '''
    SELECT    
    ABPerson.ROWID,
    ABPerson.CreationDate,
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
    (SELECT group_concat(ifnull(ABMultiValueLabel.value, ' ') || ': ' || ABMultiValue.value, CHAR(13))
    FROM ABMultiValue
    LEFT JOIN ABMultiValueLabel ON ABMultiValue.label = ABMultiValueLabel.ROWID
    WHERE ABMultiValue.property = 3 AND ABMultiValue.record_id = ABPerson.ROWID
    GROUP BY ABMultiValue.record_id) AS 'Phone Numbers',
    (SELECT group_concat(ifnull(ABMultiValueLabel.value, ' ') || ': ' || ABMultiValue.value, CHAR(13))
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
        SELECT group_concat(ifnull(label, ' ') || ': ' || address, CHAR(13))
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
    SELECT group_concat(ifnull(label, ' ') || ': ' || uv || ' (' || sv || ')', CHAR(13))
    FROM MV
    LEFT JOIN MVE_U ON uid = up
    LEFT JOIN MVE_S ON up = sp
    GROUP BY rid) AS 'Instant Message',
    (SELECT group_concat(ifnull(ABMultiValueLabel.value, ' ') || ': ' || ABMultiValue.value, CHAR(13))
    FROM ABMultiValue
    LEFT JOIN ABMultiValueLabel ON ABMultiValue.label = ABMultiValueLabel.ROWID
    WHERE ABMultiValue.property = 22 AND ABMultiValue.record_id = ABPerson.ROWID
    GROUP BY ABMultiValue.record_id) AS 'URL',
    (SELECT group_concat(ifnull(ABMultiValueLabel.value, ' ') || ': ' || ABMultiValue.value, CHAR(13))
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
    ABPerson.ModificationDate
    FROM ABPerson
    LEFT JOIN ABStore ON ABPerson.StoreID = ABStore.ROWID
    '''

    data_headers = [('Creation Date', 'datetime'), ('Thumbnail', 'media'), ('Full Size Image', 'media'), 'Prefix', 'First Name', 'Middle Name', 
                    'Last Name', 'Suffix', 'Display Name', 'First Name Phonetic', 'Middle Name Phonetic', 
                    'Last Name Phonetic', 'Company', 'Department', 'Job Title', 'Phone Numbers', 
                    'Email addresses', 'Addresses', 'Instant Messages', 'URL', 'Related Names',
                    'Profiles', 'Nickname', 'Notes', 'Birthday', 'Group Name', 'Storage Place', 
                    ('Modification Date', 'datetime')]

    db_records = get_sqlite_db_records(source_path, query, attach_query)

    for record in db_records:
        creation_date = convert_cocoa_core_data_ts_to_utc(record[1])
        
        thumbnail = record[2]
        if thumbnail:
            thumbnail_item = check_in_embedded_media(seeker, address_book_images_db, thumbnail, artifact_info)
            thumbnail = thumbnail_item.id

        full_size_image = record[3]
        if full_size_image:
                image_item = check_in_embedded_media(seeker, address_book_images_db, full_size_image, artifact_info)
                full_size_image = image_item.id

        phone_numbers = record[16]
        if phone_numbers:
            phone_numbers = clean_label(phone_numbers)
        phone_numbers_html = html_tag(phone_numbers) if phone_numbers else phone_numbers
        
        email_addresses = record[17]
        if email_addresses:
            email_addresses = clean_label(email_addresses)
        email_addresses_html = html_tag(email_addresses) if email_addresses else email_addresses
        
        addresses = record[18]
        if addresses:
            addresses = clean_label(addresses)
        addresses_html = html_tag(addresses) if addresses else addresses
        
        instant_message = record[19]
        if instant_message:
            instant_message = clean_label(instant_message)
        instant_message_html = html_tag(instant_message) if instant_message else instant_message
        
        url = record[20]
        if url:
            url = clean_label(url)
        url_html = html_tag(url) if url else url
        
        related_name = record[21]
        if related_name:
            related_name = clean_label(related_name)
        related_name_html = html_tag(related_name) if related_name else related_name
        
        profile = record[22]
        if profile:
            profile = clean_label(profile)
        profile_html = html_tag(profile) if profile else profile
        
        birthday = record[-4]
        birthday = get_birthdate(birthday) if birthday else ''

        modified_date = convert_cocoa_core_data_ts_to_utc(record[-1])
        
        data_list.append([creation_date, thumbnail, full_size_image, record[4], record[5], record[6], record[7], record[8], 
                          record[9], record[10], record[11], record[12], record[13], record[14], record[15], 
                          phone_numbers, email_addresses, addresses, instant_message, url, related_name, profile, 
                          record[23], record[24], birthday, record[26], record[27], modified_date])

        # html_data_list.append([creation_date, thumbnail_tag, record[4], record[5], record[6], record[7], record[8], record[9], 
        #                     record[10], record[11], record[12], record[13], record[14], record[15], 
        #                     phone_numbers_html, email_addresses_html, addresses_html, instant_message_html, url_html, related_name_html, 
        #                     profile_html, record[23], record[24], birthday, record[26], record[27],modified_date])

    remove_empty_cols_query = '''
    SELECT 'Create', count(ABI.ABThumbnailImage.data), count(ABI.ABFullSizeImage.data), count(ABPerson.Prefix), 'First', count(ABPerson.Middle), 'Last', 
    count(ABPerson.Suffix), count(ABPerson.DisplayName), count(ABPerson.FirstPhonetic), count(ABPerson.MiddlePhonetic), count(ABPerson.LastPhonetic), 
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
    LEFT JOIN ABI.ABFullSizeImage ON ABPerson.ROWID = ABI.ABFullSizeImage.record_id
    '''

    # Removing unused columns

    empty_cols_records = get_sqlite_db_records(source_path, remove_empty_cols_query, attach_query)

    data_headers = remove_unused_rows(data_headers, empty_cols_records)
    data_list = [remove_unused_rows(data, empty_cols_records) for data in data_list]

    # Generate HTML report
    
    # report = ArtifactHtmlReport('Address Book')
    # report.start_artifact_report(report_folder, 'Address Book')
    # report.add_script()
    # data_headers = strip_tuple_from_headers(data_headers)
    # report.write_artifact_data_table(data_headers, html_data_list, source_path, html_no_escape=['Thumbnail', 'Phone Numbers', 'Email addresses', 'Addresses', 'Instant Messages', 'URL', 'Related Names', 'Profiles'])
    # report.end_artifact_report()
    
    return data_headers, data_list, source_path
