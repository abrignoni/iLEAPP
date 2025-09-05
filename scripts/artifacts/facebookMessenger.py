__artifacts_v2__ = {
    'facebookMessengerCalls': {
        'name': 'Facebook Messenger - Calls',
        'description': 'Extract call history from Facebook Messenger.',
        'author': '@stark4n6',
        'creation_date': '2021-03-03',
        'last_update_date': '2025-04-09',
        'requirements': 'none',
        'category': 'Facebook Messenger',
        'notes': '',
        'paths': (
            '*/lightspeed-userDatabases/*.db*',),
        'output_types': 'standard',
        'artifact_icon': 'phone-call',
    },
    'facebookMessengerChats': {
        'name': 'Facebook Messenger - Chats',
        'description': 'Extract messages from Facebook Messenger.',
        'author': '@stark4n6',
        'creation_date': '2021-03-03',
        'last_update_date': '2025-08-27',
        'requirements': 'none',
        'category': 'Facebook Messenger',
        'notes': '',
        'paths': (
            '*/lightspeed-userDatabases/*.db*',),
        'output_types': 'standard',
        'artifact_icon': 'message-circle',
        'data_views': {
            'chat': {
                'threadDiscriminatorColumn': 'Thread ID',
                'textColumn': 'Message',
                'directionColumn': 'Message Direction',
                'directionSentValue': 'Sent',
                'timeColumn': 'Timestamp',
                'senderColumn': 'Sender Name'
            }
        }
    },
    'facebookMessengerSecretConversations': {
        'name': 'Facebook Messenger - Secret Conversations',
        'description': 'Extract secret conversations from Facebook Messenger.',
        'author': '@stark4n6',
        'creation_date': '2021-03-03',
        'last_update_date': '2025-04-10',
        'requirements': 'none',
        'category': 'Facebook Messenger',
        'notes': '',
        'paths': (
            '*/lightspeed-userDatabases/*.db*',),
        'output_types': 'standard',
        'artifact_icon': 'lock',
    },
    'facebookMessengerConversationGroups': {
        'name': 'Facebook Messenger - Conversation Groups',
        'description': 'Extract conversation groups from Facebook Messenger.',
        'author': '@stark4n6',
        'creation_date': '2021-03-03',
        'last_update_date': '2025-04-10',
        'requirements': 'none',
        'category': 'Facebook Messenger',
        'notes': '',
        'paths': (
            '*/lightspeed-userDatabases/*.db*',),
        'output_types': 'standard',
        'artifact_icon': 'facebook',
    },
    'facebookMessengerContacts': {
        'name': 'Facebook Messenger - Contacts',
        'description': 'Extract contacts from Facebook Messenger.',
        'author': '@stark4n6',
        'creation_date': '2021-03-03',
        'last_update_date': '2025-04-09',
        'requirements': 'none',
        'category': 'Facebook Messenger',
        'notes': '',
        'paths': (
            '*/lightspeed-userDatabases/*.db*',),
        'output_types': 'standard',
        'artifact_icon': 'users',
    }
}


from os.path import basename

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly
from scripts.ilapfuncs import artifact_processor, \
    does_table_exist_in_db, does_view_exist_in_db, get_sqlite_multiple_db_records, \
    convert_unix_ts_to_utc


@artifact_processor
def facebookMessengerCalls(files_found, report_folder, seeker, wrap_text, timezone_offset):
    db_path_list = []
    data_list = []

    for file_found in files_found:
        if file_found.endswith('.db'):
            if does_view_exist_in_db(file_found, 'thread_messages'):
                db_path_list.append(file_found)

    query = '''
    SELECT
        thread_messages.timestamp_ms,
        contacts.name,
        thread_messages.thread_key,
        attachments.title_text,
        attachments.subtitle_text
    FROM thread_messages
    LEFT JOIN contacts
        ON thread_messages.sender_id = contacts.id
    LEFT JOIN attachments
        ON thread_messages.message_id = attachments.message_id
    WHERE attachments.title_text like '%call%'
    '''

    data_headers = (
        ('Timestamp', 'datetime'), 'Sender Name', 'Sender ID',
        'Call Type', 'Call Duration/Subtitle')

    data_headers, db_records, source_path = get_sqlite_multiple_db_records(
        db_path_list, query, data_headers)

    for record in db_records:
        record_data = []
        for key in record.keys():
            if key == 'timestamp_ms':
                timestamp_ms = convert_unix_ts_to_utc(record['timestamp_ms'])
                record_data.append(timestamp_ms)
            else:
                record_data.append(record[key])
        data_list.append(tuple(record_data))

    return data_headers, data_list, source_path


@artifact_processor
def facebookMessengerChats(files_found, report_folder, seeker, wrap_text, timezone_offset):
    db_path_list = []
    data_list = []

    for file_found in files_found:
        if file_found.endswith('.db'):
            if does_view_exist_in_db(file_found, 'thread_messages'):
                db_path_list.append(file_found)

    query = '''
    SELECT
	thread_messages.timestamp_ms,
	CASE 
        WHEN (SELECT CASE
		WHEN _user_info.facebook_user_id IS NOT NULL THEN 'Sent'
		ELSE 'Received'
	END) = 'Sent' THEN concat(contacts.name, ' (Local User)')
        ELSE contacts.name
    END,
	contacts.id,
	CASE
		WHEN _user_info.facebook_user_id IS NOT NULL THEN 'Sent'
		ELSE 'Received'
	END AS "Message Direction",
	thread_messages.text,
	CASE thread_messages.has_attachment
		WHEN NULL THEN ''
		WHEN 1 THEN 'Yes'
	END AS Attachment,
	attachments.filename,
	attachments.filesize,
	attachment_items.title_text,
    attachment_items.subtitle_text,
    thread_messages.thread_key
    FROM thread_messages
    LEFT JOIN contacts
        ON thread_messages.sender_id = contacts.id
    LEFT JOIN attachments
        ON thread_messages.message_id = attachments.message_id
    LEFT JOIN attachment_items
        ON thread_messages.message_id = attachment_items.message_id
    LEFT JOIN _user_info
        ON thread_messages.sender_id = _user_info.facebook_user_id
    WHERE attachment_items.title_text IS NULL or attachment_items.title_text NOT LIKE '%call%'
    ORDER BY thread_messages.timestamp_ms ASC
    '''

    data_headers = (
        ('Timestamp', 'datetime'), 'Sender Name', 'Sender ID', 'Message Direction', 'Message', 
        'Attachment', 'Attachment Name', 'Attachment Size', 'Title Text', 'Subtitle Text', 'Thread ID')

    data_headers, db_records, source_path = get_sqlite_multiple_db_records(
        db_path_list, query, data_headers)

    for record in db_records:
        record_data = []
        for key in record.keys():
            if key == 'timestamp_ms':
                timestamp_ms = convert_unix_ts_to_utc(record['timestamp_ms'])
                record_data.append(timestamp_ms)
            else:
                record_data.append(record[key])
           
        data_list.append(tuple(record_data))

    return data_headers, data_list, source_path


@artifact_processor
def facebookMessengerSecretConversations(files_found, report_folder, seeker, wrap_text, timezone_offset):
    db_path_list = []
    data_list = []

    for file_found in files_found:
        if file_found.endswith('.db'):
            if does_table_exist_in_db(file_found, 'contacts'):
                db_path_list.append(file_found)

    query = '''
    SELECT
        secure_messages.timestamp_ms,
        secure_messages.thread_key,
        contacts.name,
        secure_messages.text,
        secure_messages.secure_message_attachments_encrypted
    FROM secure_messages
    LEFT JOIN contacts
        ON secure_messages.sender_id = contacts.id
    '''

    data_headers = (
        ('Timestamp', 'datetime'), 'Thread Key', 'Sender Name',
        'Message (Encrypted)', 'Attachment (Encrypted)')

    data_headers, db_records, source_path = get_sqlite_multiple_db_records(
        db_path_list, query, data_headers)

    for record in db_records:
        record_data = []
        for key in record.keys():
            if key == 'timestamp_ms':
                timestamp_ms = convert_unix_ts_to_utc(record['timestamp_ms'])
                record_data.append(timestamp_ms)
            else:
                record_data.append(record[key])
        data_list.append(tuple(record_data))

    return data_headers, data_list, source_path


@artifact_processor
def facebookMessengerConversationGroups(files_found, report_folder, seeker, wrap_text, timezone_offset):
    db_path_list = []
    data_list = []

    for file_found in files_found:
        if file_found.endswith('.db'):
            if does_table_exist_in_db(file_found, 'thread_participant_detail'):
                db_path_list.append(file_found)

    query = '''
    SELECT
        threads.last_activity_timestamp_ms,
        thread_participant_detail.thread_key,
        group_concat(thread_participant_detail.name, ';') 
    FROM thread_participant_detail
    JOIN threads
        OM threads.thread_key = thread_participant_detail.thread_key
    GROUP BY thread_participant_detail.thread_key
    '''

    data_headers = (
        ('Timestamp (Last Activity)', 'datetime'), 'Thread Key', 'Thread Participants')

    data_headers, db_records, source_path = get_sqlite_multiple_db_records(
        db_path_list, query, data_headers)

    for record in db_records:
        record_data = []
        for key in record.keys():
            if key == 'timestamp_ms':
                timestamp_ms = convert_unix_ts_to_utc(record['timestamp_ms'])
                record_data.append(timestamp_ms)
            else:
                record_data.append(record[key])
        data_list.append(tuple(record_data))

    return data_headers, data_list, source_path


@artifact_processor
def facebookMessengerContacts(files_found, report_folder, seeker, wrap_text, timezone_offset):
    db_path_list = []
    data_list = []

    for file_found in files_found:
        if file_found.endswith('.db'):
            if does_table_exist_in_db(file_found, 'contacts'):
                db_path_list.append(file_found)

    query = '''
    SELECT
        id,
        name,
        normalized_name_for_search,
        profile_picture_url,
        CASE is_messenger_user
            WHEN 0 THEN ''
            WHEN 1 THEN 'Yes'
        END AS is_messenger_user
    FROM contacts
    '''

    data_headers = (
        'User ID', 'Username', 'Normalized Username', 'Profile Pic URL', 'Is App User')

    data_headers, db_records, source_path = get_sqlite_multiple_db_records(
        db_path_list, query, data_headers)

    for record in db_records:
        data_list.append(tuple(record))

    return data_headers, data_list, source_path
