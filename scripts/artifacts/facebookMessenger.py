__artifacts_v2__ = {
    "facebookMessengerCalls": {
        "name": "Facebook Messenger - Calls",
        "description": "Extract call history from Facebook Messenger.",
        "author": "@stark4n6",
        "creation_date": "2021-03-03",
        "last_update_date": "2025-04-09",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ("*/lightspeed-userDatabases/*.db*",),
        "output_types": "standard",
        "artifact_icon": "phone-call",
    },
    "facebookMessengerChats": {
        "name": "Facebook Messenger - Chats",
        "description": "Extract messages from Facebook Messenger.",
        "author": "@stark4n6",
        "creation_date": "2021-03-03",
        "last_update_date": "2025-08-27",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ("*/lightspeed-userDatabases/*.db*",),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "chat": {
                "threadDiscriminatorColumn": "Thread ID",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name",
            }
        },
    },
    "facebook_messenger_client_chats": {
        "name": "Facebook Messenger - Client Messages",
        "description": "Extract messages from Facebook Messenger.",
        "author": "Sukochev",
        "creation_date": "2026-06-24",
        "last_update_date": "2026-06-24",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": (
            "*/lightspeed-userDatabases/*.db*",
            "*/lightspeed-TAMStorage/media_bank/AdvancedCrypto/*/persistent/*.jpg",
        ),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "chat": {
                "threadDiscriminatorColumn": "Thread ID",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name",
                "mediaColumn": "Image",
            }
        },
    },
    "facebookMessengerSecretConversations": {
        "name": "Facebook Messenger - Secret Conversations",
        "description": "Extract secret conversations from Facebook Messenger.",
        "author": "@stark4n6",
        "creation_date": "2021-03-03",
        "last_update_date": "2025-04-10",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ("*/lightspeed-userDatabases/*.db*",),
        "output_types": "standard",
        "artifact_icon": "lock",
    },
    "facebookMessengerConversationGroups": {
        "name": "Facebook Messenger - Conversation Groups",
        "description": "Extract conversation groups from Facebook Messenger.",
        "author": "@stark4n6",
        "creation_date": "2021-03-03",
        "last_update_date": "2025-04-10",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ("*/lightspeed-userDatabases/*.db*",),
        "output_types": "standard",
        "artifact_icon": "facebook",
    },
    "facebookMessengerContacts": {
        "name": "Facebook Messenger - Contacts",
        "description": "Extract contacts from Facebook Messenger.",
        "author": "@stark4n6",
        "creation_date": "2021-03-03",
        "last_update_date": "2025-04-09",
        "requirements": "none",
        "category": "Facebook Messenger",
        "notes": "",
        "paths": ("*/lightspeed-userDatabases/*.db*",),
        "output_types": "standard",
        "artifact_icon": "users",
    },
}


from pathlib import Path

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    does_view_exist_in_db,
    get_sqlite_db_records,
)

CLIENT_MESSAGES = "client_messages"
CONTACTS = "contacts"
THREAD_MESSAGES = "thread_messages"
THREAD_PARTICIPANT_DETAIL = "thread_participant_detail"


def _database_files_with_view(context, view):
    db_list = []
    for file_found in context.get_files_found():
        if str(file_found).endswith(".db") and does_view_exist_in_db(file_found, view):
            db_list.append(file_found)
        else:
            continue
    return db_list


def _database_files_with_table(context, table):
    db_list = []
    for file_found in context.get_files_found():
        if str(file_found).endswith(".db") and does_table_exist_in_db(
            file_found, table
        ):
            db_list.append(file_found)
        else:
            continue
    return db_list


def _media_files(context):
    return [
        str(file_found)
        for file_found in context.get_files_found()
        if str(file_found).endswith(".jpg")
    ]


def _source_path(context, files_found):
    if not files_found:
        return ""
    return "\n".join(
        context.get_relative_path(file_found) for file_found in files_found
    )


@artifact_processor
def facebookMessengerCalls(context):
    data_list = []

    database_files_found = _database_files_with_view(context, THREAD_MESSAGES)
    source_path = _source_path(context, database_files_found)

    data_headers = (
        ("Timestamp", "datetime"),
        "Sender Name",
        "Sender ID",
        "Call Type",
        "Call Duration/Subtitle",
    )

    query = """
    SELECT
        thread_messages.timestamp_ms,
        contacts.name,
        thread_messages.sender_id,
        attachments.title_text,
        attachments.subtitle_text
    FROM thread_messages
    LEFT JOIN contacts
        ON thread_messages.sender_id = contacts.id
    LEFT JOIN attachments
        ON thread_messages.message_id = attachments.message_id
    WHERE attachments.title_text like '%call%'
    """

    if database_files_found:
        for file_found in database_files_found:
            db_records = get_sqlite_db_records(file_found, query)
            for record in db_records:
                timestamp = ""
                sender_name = ""
                sender_id = ""
                call_type = ""
                call_duration = ""

                if record[0] > 0:
                    timestamp = convert_unix_ts_to_utc(record[0])
                else:
                    timestamp = record[0]

                sender_name = record[1]
                sender_id = record[2]
                call_type = record[3]
                call_duration = record[4]

                data_list.append(
                    (
                        timestamp,
                        sender_name,
                        sender_id,
                        call_type,
                        call_duration,
                    )
                )

        return data_headers, data_list, source_path
    else:
        return data_headers, data_list, source_path


@artifact_processor
def facebookMessengerChats(context):
    data_list = []

    database_files_found = _database_files_with_view(context, THREAD_MESSAGES)
    source_path = _source_path(context, database_files_found)

    data_headers = (
        ("Timestamp", "datetime"),
        "Sender Name",
        "Sender ID",
        "Message Direction",
        "Message",
        "Attachment",
        "Attachment Name",
        "Attachment Size",
        "Title Text",
        "Subtitle Text",
        "Thread ID",
    )

    query = """
    SELECT
	thread_messages.timestamp_ms,
	CASE 
        WHEN (SELECT CASE
		WHEN _user_info.facebook_user_id IS NOT NULL THEN 'Sent'
		ELSE 'Received'
	END) = 'Sent' THEN COALESCE(contacts.name, '') || ' (Local User)'
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
    """

    if database_files_found:
        for file_found in database_files_found:
            db_records = get_sqlite_db_records(file_found, query)
            for record in db_records:
                timestamp = ""
                sender_name = ""
                sender_id = ""
                message_direction = ""
                message = ""
                attachment = ""
                attachment_name = ""
                attachment_size = ""
                title_text = ""
                subtitle_text = ""
                thread_id = ""

                if record[0] > 0:
                    timestamp = convert_unix_ts_to_utc(record[0])
                else:
                    timestamp = record[0]

                sender_name = record[1]
                sender_id = record[2]
                message_direction = record[3]
                message = record[4]
                attachment = record[5]
                attachment_name = record[6]
                attachment_size = record[7]
                title_text = record[8]
                subtitle_text = record[9]
                thread_id = record[10]

                data_list.append(
                    (
                        timestamp,
                        sender_name,
                        sender_id,
                        message_direction,
                        message,
                        attachment,
                        attachment_name,
                        attachment_size,
                        title_text,
                        subtitle_text,
                        thread_id,
                    )
                )

        return data_headers, data_list, source_path
    else:
        return data_headers, data_list, source_path


@artifact_processor
def facebook_messenger_client_chats(context):
    data_list = []

    database_files_found = _database_files_with_table(context, CLIENT_MESSAGES)
    source_path = _source_path(context, database_files_found)

    media_files_found = _media_files(context)

    data_headers = (
        ("Timestamp", "datetime"),
        "Thread ID",
        "Sender Name",
        "Sender ID",
        "Message Direction",
        "Message",
        "Attachment-Image",
        "Attachment Name",
        "Attachment Size",
        "Attachment Persisted Path",
        ("Image", "media"),
    )

    query = """
    SELECT
	client_messages.display_ts_ms,
    client_messages.thread_pk,
	CASE
        WHEN (SELECT CASE
		WHEN _user_info.facebook_user_id IS NOT NULL THEN 'Sent'
		ELSE 'Received'
	END) = 'Sent' THEN contacts.name || ' (Local User)'
        ELSE contacts.name
    END,
	contacts.id,
	CASE
		WHEN _user_info.facebook_user_id IS NOT NULL THEN 'Sent'
		ELSE 'Received'
	END AS "Message Direction",
	client_messages.text,
	CASE client_messages.message_content_type
		WHEN 2 THEN 'Yes'
        ELSE ''
	END AS "Attachment-Image",
    client_attachments.filename,
	client_attachments.filesize,
    client_attachment_store_keys.persisted_path
    FROM client_messages
    LEFT JOIN contacts
        ON client_messages.sender_contact_pk = contacts.id
    LEFT JOIN client_attachments
        ON client_messages.pk = client_attachments.message_pk
    LEFT JOIN client_attachment_store_keys
        ON client_attachments.content_token = client_attachment_store_keys.content_token
    LEFT JOIN _user_info
        ON client_messages.sender_contact_pk = _user_info.facebook_user_id
    ORDER BY client_messages.display_ts_ms ASC
    """

    if database_files_found:
        for file_found in database_files_found:
            db_records = get_sqlite_db_records(file_found, query)
            for record in db_records:
                timestamp = ""
                thread_id = ""
                sender_name = ""
                sender_id = ""
                message_direction = ""
                message = ""
                is_attachment_image = ""
                attachment_name = ""
                attachment_size = ""
                attachment_persisted_path = ""
                media_file_found = ""

                if record[0] > 0:
                    timestamp = convert_unix_ts_to_utc(record[0])
                else:
                    timestamp = record[0]

                thread_id = record[1]
                sender_name = record[2]
                sender_id = record[3]
                message_direction = record[4]
                message = record[5]
                is_attachment_image = record[6]
                attachment_name = record[7]
                attachment_size = record[8]
                attachment_persisted_path = record[9]

                if media_files_found and attachment_persisted_path:
                    attachment_persisted_path_formatted = Path(attachment_persisted_path)
                    attachment_name_formatted = attachment_persisted_path_formatted.name
                    for image in media_files_found:
                        if image.endswith(str(attachment_name_formatted)):
                            media_file = image
                            media_path = Path(media_file)
                            media_filename = media_path.name
                            media_file_found = check_in_media(
                                media_file, media_filename
                            )

                data_list.append(
                    (
                        timestamp,
                        thread_id,
                        sender_name,
                        sender_id,
                        message_direction,
                        message,
                        is_attachment_image,
                        attachment_name,
                        attachment_size,
                        attachment_persisted_path,
                        media_file_found,
                    )
                )

        return data_headers, data_list, source_path
    else:
        return data_headers, data_list, source_path


@artifact_processor
def facebookMessengerSecretConversations(context):
    data_list = []

    database_files_found = _database_files_with_table(context, CONTACTS)
    source_path = _source_path(context, database_files_found)

    data_headers = (
        ("Timestamp", "datetime"),
        "Thread Key",
        "Sender Name",
        "Message (Encrypted)",
        "Attachment (Encrypted)",
    )

    query = """
    SELECT
        secure_messages.timestamp_ms,
        secure_messages.thread_key,
        contacts.name,
        secure_messages.text,
        secure_messages.secure_message_attachments_encrypted
    FROM secure_messages
    LEFT JOIN contacts
        ON secure_messages.sender_id = contacts.id
    """

    if database_files_found:
        for file_found in database_files_found:
            db_records = get_sqlite_db_records(file_found, query)
            for record in db_records:
                timestamp = ""
                thread_key = ""
                sender_name = ""
                message = ""
                attachment = ""

                if record[0] > 0:
                    timestamp = convert_unix_ts_to_utc(record[0])
                else:
                    timestamp = record[0]

                thread_key = record[1]
                sender_name = record[2]
                message = record[3]
                attachment = record[4]

                data_list.append(
                    (
                        timestamp,
                        thread_key,
                        sender_name,
                        message,
                        attachment,
                    )
                )

        return data_headers, data_list, source_path
    else:
        return data_headers, data_list, source_path


@artifact_processor
def facebookMessengerConversationGroups(context):
    data_list = []

    database_files_found = _database_files_with_view(context, THREAD_PARTICIPANT_DETAIL)
    source_path = _source_path(context, database_files_found)

    data_headers = (
        ("Timestamp (Last Activity)", "datetime"),
        "Thread Key",
        "Thread Participants",
    )

    query = """
    SELECT
        threads.last_activity_timestamp_ms,
        thread_participant_detail.thread_key,
        group_concat(thread_participant_detail.name, ';') 
    FROM thread_participant_detail
    JOIN threads
        ON threads.thread_key = thread_participant_detail.thread_key
    GROUP BY thread_participant_detail.thread_key
    """

    if database_files_found:
        for file_found in database_files_found:
            db_records = get_sqlite_db_records(file_found, query)
            for record in db_records:
                timestamp = ""
                thread_key = ""
                thread_participants = ""

                if record[0] > 0:
                    timestamp = convert_unix_ts_to_utc(record[0])
                else:
                    timestamp = record[0]

                thread_key = record[1]
                thread_participants = record[2]

                data_list.append(
                    (
                        timestamp,
                        thread_key,
                        thread_participants,
                    )
                )

        return data_headers, data_list, source_path
    else:
        return data_headers, data_list, source_path


@artifact_processor
def facebookMessengerContacts(context):
    data_list = []

    database_files_found = _database_files_with_table(context, CONTACTS)
    source_path = _source_path(context, database_files_found)

    data_headers = (
        "User ID",
        "Username",
        "Normalized Username",
        "Profile Pic URL",
        "Is App User",
    )

    query = """
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
    """

    if database_files_found:
        for file_found in database_files_found:
            db_records = get_sqlite_db_records(file_found, query)
            for record in db_records:
                user_id = ""
                contact_name = ""
                normalized_contact_name = ""
                profile_picture_url = ""
                is_app_user = ""

                user_id = record[0]
                contact_name = record[1]
                normalized_contact_name = record[2]
                profile_picture_url = record[3]
                is_app_user = record[4]

                data_list.append(
                    (
                        user_id,
                        contact_name,
                        normalized_contact_name,
                        profile_picture_url,
                        is_app_user,
                    )
                )

        return data_headers, data_list, source_path
    else:
        return data_headers, data_list, source_path
