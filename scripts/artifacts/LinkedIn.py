# LinkedIn App (com.linkedin.LinkedIn)
# Author:  Marco Neumann (kalinko@be-binary.de)
# 
# Tested with the following versions:
# 2024-09-16: iOS 17.5.1, App: 2024.0828.0932

# Requirements:  ccl_bplist


__artifacts_v2__ = {

    
    "get_linkedin_account": {
        "name": "LinkedIn - Account",
        "description": "Existing account in LinkedIn App. The Public Identifier can be used to visit the public profile on the LinkedIn Website (https://www.linkedin.com/in/[Public Identifier])",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.2",
        "creation_date": "2024-10-01",
        "last_update_date": "2025-04-23",
        "requirements": "ccl_bplist",
        "category": "LinkedIn",
        "notes": "",
        "paths": ('*/Library/Preferences/com.linkedin.LinkedIn.plist'),
        "output_types": "html",
        "artifact_icon": "user"
    },
    "get_linkedin_messages": {
        "name": "LinkedIn - Messages",
        "description": "Messages sent and received in the LinkedIn App.",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.2",
        "creation_date": "2024-10-01",
        "last_update_date": "2025-04-23",
        "requirements": "",
        "category": "LinkedIn",
        "notes": "",
        "paths": ('*/Documents/msg_database.sqlite'),
        "output_types": "standard",
        "artifact_icon": "message-square"
    },
    "get_linkedin_conversations": {
        "name": "LinkedIn - Conversations",
        "description": "LinkedIn Conversations",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.2",
        "creation_date": "2024-10-01",
        "last_update_date": "2025-04-23",
        "requirements": "",
        "category": "LinkedIn",
        "notes": "Messages threaded",
        "paths": ('*/Documents/msg_database.sqlite'),
        "output_types": "all", 
        "data_views": {
            "chat": {
                "directionSentValue": 1,
                "threadDiscriminatorColumn": "Conversation-ID",
                "textColumn": "Message",
                "directionColumn": "Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name",
                "threadLabelColumn": "Conversation Name"
            }
        },
        "artifact_icon": "message-circle"
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.ccl import ccl_bplist

@artifact_processor
def get_linkedin_account(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):    
    
    with open(files_found[0], 'rb') as bplist_file:
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

    data_list.append((member_id, lastname, firstname, headline, location, public_identifier))

    return data_headers, data_list, files_found[0]





@artifact_processor
def get_linkedin_messages(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    query = ('''
        SELECT
        strftime('%Y-%m-%d %H:%M:%S.', "deliveredAt"/1000, 'unixepoch') || ("deliveredAt"%1000) [deliveredAt],
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

    db_records = get_sqlite_db_records(str(files_found[0]), query)


    data_list = []
    for record in db_records:
    
        delivery_date = record[0]
        delivery_status = record[1]
        sender_firstname = record[2]
        sender_lastname = record[3]
        sender_headline = record[4]
        sender_profile_url = record[5]
        sender_distance = record[6]
        message = record[7]
        conversationurn = record[8]

        data_list.append((delivery_date, delivery_status, sender_firstname, sender_lastname, sender_headline, sender_profile_url, sender_distance, message, conversationurn))

    data_headers = ('Delivery Date', 'Delivery Status', 'Sender First Name', 'Sender Last Name', 'Sender Headline', 'Sender Profile Url', 'Sender Distance', 'Message', 'Conversation Urn')

    return data_headers, data_list, files_found[0]


@artifact_processor
def get_linkedin_conversations(files_found, _report_folder, _seeker, _wrap_text, _timezone_offset):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
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
		CASE WHEN json_extract(serializedConversation, '$.conversationParticipants[0].participantType.member.distance') = 'SELF'
        THEN CONCAT (json_extract(serializedConversation, '$.conversationParticipants[1].participantType.member.firstName.text'), ' ', 
		        json_extract(serializedConversation, '$.conversationParticipants[1].participantType.member.lastName.text'))
        ELSE CONCAT (json_extract(serializedConversation, '$.conversationParticipants[0].participantType.member.firstName.text'), ' ', 
		        json_extract(serializedConversation, '$.conversationParticipants[0].participantType.member.lastName.text'))
        END [data-name],
		messages.conversationUrn [conversationUrn]
        FROM messages
		INNER JOIN conversations c on messages.conversationUrn = c.conversationUrn
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)
    data_list = []

    for record in db_records:
        delivery_date = convert_unix_ts_to_utc(record[0])
        conversation_urn = record[5]
        conversation_label = record[4]
        message = record[3]
        sent = record[2]
        sender_name = record[1]


        data_list.append((delivery_date, conversation_urn, conversation_label, message, sent, sender_name))

    data_headers = ( 'Timestamp', 'Conversation-ID', 'Conversation Name', 'Message', 'Sent', 'Sender Name')

    return data_headers, data_list, files_found[0]
