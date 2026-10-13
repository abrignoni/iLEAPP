# LinkedIn App (com.linkedin.LinkedIn)
# Author:  Marco Neumann (kalinko@be-binary.de)
# 
# Tested with the following versions:
# 2024-09-16: iOS 17.5.1, App: 2024.0828.0932

# Requirements:  ccl_bplist


__artifacts_v2__ = {    
    "linkedin_account": {
        "name": "LinkedIn - Account",
        "description": 'Member identifier and profile fields from the voy.authenticatedMemberId and voy.authenticatedDashProfileModel keys of the LinkedIn preferences plist. A plist lacking both keys, or whose root is not a dictionary, produces no row; the existing six-field projection is retained when either key is present.',
        "author": '@AlexisBrignoni, Codex',
        "creation_date": "2024-10-01",
        "last_update_date": '2026-10-09',
        "requirements": "ccl_bplist",
        "category": "LinkedIn",
        "notes": 'Row retention tests presence of the two top-level keys, not truthiness or presence of every nested field. A present empty, null or partial profile value retains the existing projection and can still produce blank cells. A decoded root that is not a dictionary produces no row. A row does not establish an account, authentication or ownership. Original contribution: Marco Neumann (kalinko@be-binary.de).',
        "paths": ('*/Library/Preferences/com.linkedin.LinkedIn.plist'),
        "output_types": "html",
        "artifact_icon": "user"
    },
    "linkedin_messages": {
        "name": "LinkedIn - Messages",
        "description": "Messages stored in the LinkedIn app's msg_database.sqlite, with the sender "
                       "fields each message record carries. Delivery Status is reported as stored.",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-10-01",
        "last_update_date": "2026-06-15",
        "requirements": "none",
        "category": "LinkedIn",
        "notes": "",
        "paths": ('*/Documents/msg_database.sqlite*'),
        "output_types": "standard",
        "artifact_icon": "message"
    },
    "linkedin_conversations": {
        "name": "LinkedIn - Conversations",
        "description": "LinkedIn Conversations",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-10-01",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "LinkedIn",
        "notes": "Messages with their conversation record where one exists. Sent is 1 when the "
                 "sender's distance value in the message record is SELF and 0 otherwise; no other "
                 "field was used to confirm direction. A message whose conversationUrn has no row "
                 "in the conversations table is reported with a blank Conversation Name. "
                 "Conversation Name lists, separated by commas, the first and last name of each "
                 "member in the conversation record's conversationParticipants whose distance "
                 "value is not SELF; a participant stored with no member name is not listed, and "
                 "the column is blank when none is. No registered corpus holds this database; the "
                 "query was run on a constructed database only.",
        "paths": ('*/Documents/msg_database.sqlite*'),
        "output_types": "all", 
        "data_views": {
            "conversation": {
                "directionSentValue": 1,
                "conversationDiscriminatorColumn": "Conversation-ID",
                "textColumn": "Message",
                "directionColumn": "Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name",
                "conversationLabelColumn": "Conversation Name"
            }
        },
        "artifact_icon": "message-circle"
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, get_file_path
from scripts.ccl import ccl_bplist

@artifact_processor
def linkedin_account(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "com.linkedin.LinkedIn.plist")
    
    with open(source_path, 'rb') as bplist_file:
        bplist_data = ccl_bplist.load(bplist_file)

    data_headers = ( 'Member ID', 'Last Name', 'First Name', 'Headline', 'Location', 'Public Identifier')
    data_list = []
    try: 
        member_id = bplist_data['voy.authenticatedMemberId']
    except (IndexError, TypeError, KeyError):
        member_id = ''
    try:
        firstname = bplist_data['voy.authenticatedDashProfileModel']['firstName']
    except (IndexError, TypeError, KeyError):
        firstname = ''
    try:
        lastname = bplist_data['voy.authenticatedDashProfileModel']['lastName']
    except (IndexError, TypeError, KeyError):
        lastname = ''
    try:
        headline = bplist_data['voy.authenticatedDashProfileModel']['headline']
    except (IndexError, TypeError, KeyError):
        headline = ''
    try:
        location = bplist_data['voy.authenticatedDashProfileModel']['geoLocation']['geo']['defaultLocalizedName']
    except (IndexError, TypeError, KeyError):
        location = ''
    try:
        public_identifier = bplist_data['voy.authenticatedDashProfileModel']['publicIdentifier']
    except (IndexError, TypeError, KeyError):
        public_identifier = ''

    if isinstance(bplist_data, dict) and (
            'voy.authenticatedMemberId' in bplist_data
            or 'voy.authenticatedDashProfileModel' in bplist_data):
        data_list.append((member_id, lastname, firstname, headline, location, public_identifier))

    return data_headers, data_list, source_path

@artifact_processor
def linkedin_messages(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "msg_database.sqlite")
    
    query = ('''
        SELECT
        deliveredAt,
        deliveryStatus,
        json_extract(serializedMessage, '$.sender.participantType.member.firstName.text') [sender_firstname],
		json_extract(serializedMessage, '$.sender.participantType.member.lastName.text') [sender_lastname],
		json_extract(serializedMessage, '$.sender.participantType.member.headline.text') [sender_headline],
		json_extract(serializedMessage, '$.sender.participantType.member.profileUrl') [sender_profile_url],
		json_extract(serializedMessage, '$.sender.participantType.member.distance') [sender_distance],
		json_extract(serializedMessage, '$.body.text') [message],
		conversationUrn
        FROM messages
    ''')

    db_records = get_sqlite_db_records(source_path, query)
    data_list = []
    for record in db_records:
        delivery_date = convert_unix_ts_to_utc(record[0])
        delivery_status = record[1]
        sender_firstname = record[2]
        sender_lastname = record[3]
        sender_headline = record[4]
        sender_profile_url = record[5]
        sender_distance = record[6]
        message = record[7]
        conversationurn = record[8]

        data_list.append((delivery_date, delivery_status, sender_firstname, sender_lastname, sender_headline, sender_profile_url, sender_distance, message, conversationurn))

    data_headers = (('Delivery Date','datetime'), 'Delivery Status', 'Sender First Name', 'Sender Last Name', 'Sender Headline', 'Sender Profile Url', 'Sender Distance', 'Message', 'Conversation Urn')

    return data_headers, data_list, source_path


@artifact_processor
def linkedin_conversations(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "msg_database.sqlite")
    
    query = ('''
        SELECT
        deliveredAt [data-time],
        CONCAT (json_extract(serializedMessage, '$.sender.participantType.member.firstName.text'), ' ', 
		        json_extract(serializedMessage, '$.sender.participantType.member.lastName.text')) [Sender Name],
		CASE WHEN json_extract(serializedMessage, '$.sender.participantType.member.distance') = 'SELF'
        THEN 1
        ELSE 0
        END [Sent],
		json_extract(serializedMessage, '$.body.text') [message], 
		(SELECT group_concat(participant_name, ', ') FROM (
            SELECT trim(coalesce(json_extract(p.value, '$.participantType.member.firstName.text'), '') || ' ' ||
                        coalesce(json_extract(p.value, '$.participantType.member.lastName.text'), '')) AS participant_name
            FROM json_each(c.serializedConversation, '$.conversationParticipants') p
            WHERE coalesce(json_extract(p.value, '$.participantType.member.distance'), '') != 'SELF')
         WHERE participant_name != '') [data-name],
		messages.conversationUrn [conversationUrn]
        FROM messages
		LEFT JOIN conversations c on messages.conversationUrn = c.conversationUrn
    ''')

    db_records = get_sqlite_db_records(source_path, query)
    data_list = []

    for record in db_records:
        delivery_date = convert_unix_ts_to_utc(record[0])
        conversation_urn = record[5]
        conversation_label = record[4] or ''
        message = record[3]
        sent = record[2]
        sender_name = record[1]


        data_list.append((delivery_date, sent, sender_name, conversation_label, message, conversation_urn))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Sent',
        'Sender Name',
        'Conversation Name',
        'Message',
        'Conversation-ID',
    )

    return data_headers, data_list, source_path
