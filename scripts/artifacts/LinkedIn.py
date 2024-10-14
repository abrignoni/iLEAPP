# LinkedIn App (com.linkedin.LinkedIn)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# 
# Tested with the following versions:
# 2024-09-16: iOS 17.5.1, App: 2024.0828.0932

# Requirements:  datetime, json, panda, ccl_bplist




__artifacts_v2__ = {

    
    "LinkedInAccounts": {
        "name": "LinkedIn - Account",
        "description": "LinkedIn Account",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-10-01",
        "requirements": "ccl_bplist",
        "category": "LinkedIn",
        "notes": "",
        "paths": ('*/Library/Preferences/com.linkedin.LinkedIn.plist'),
        "function": "get_linkedin_account"
    },
    "LinkedInMessages": {
        "name": "LinkedIn - Messages",
        "description": "LinkedIn Messages",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-10-01",
        "requirements": "json",
        "category": "LinkedIn",
        "notes": "",
        "paths": ('*/Documents/msg_database.sqlite'),
        "function": "get_linkedin_messages"
    },
    "LinkedInConversations": {
        "name": "LinkedIn - Conversations",
        "description": "LinkedIn Conversations",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-10-01",
        "requirements": "panda, json",
        "category": "LinkedIn",
        "notes": "Messages threaded",
        "paths": ('*/Documents/msg_database.sqlite'),
        "function": "get_linkedin_conversations"
    }
}


import json
import pandas as pd
import re

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly
from scripts.chat_rendering import render_chat, chat_HTML
from scripts.ccl import ccl_bplist

def get_linkedin_account(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for LinkedIn - Account")
    
    with open(files_found[0], 'rb') as bplist_file:
        bplist_data = ccl_bplist.load(bplist_file)

    
    if bplist_data :
        logfunc(f"Found LinkedIn - Account")
        description = f"Existing account in LinkedIn App. The Public Identifier can be used to visit the public profile on the LinkedIn Website (https://www.linkedin.com/in/[Public Identifier])"
        report = ArtifactHtmlReport('LinkedIn - Account')
        report.start_artifact_report(report_folder, 'LinkedIn - Account', description)
        report.add_script()
        data_headers = ( 'Member ID', 'Last Name', 'First Name', 'Headline', 'Location', 'Public Identifier')
        data_list = []
        try: 
            member_id = bplist_data['voy.authenticatedMemberId']
        except:
            member_id = ''
        try:
            firstname = bplist_data['voy.authenticatedDashProfileModel']['firstName']
        except:
            firstname = ''
        try:
            lastname = bplist_data['voy.authenticatedDashProfileModel']['lastName']
        except:
            lastname = ''
        try:
            headline = bplist_data['voy.authenticatedDashProfileModel']['headline']
        except:
            headline = ''
        try:
            location = bplist_data['voy.authenticatedDashProfileModel']['geoLocation']['geo']['defaultLocalizedName']
        except:
            location = ''
        try:
            public_identifier = bplist_data['voy.authenticatedDashProfileModel']['publicIdentifier']
        except:
            public_identifier = ''

        data_list.append((member_id, lastname, firstname, headline, location, public_identifier))

        tableID = 'linkedin_account'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

    else:
        logfunc('No LinkedIn Account data found!')



def get_linkedin_messages(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for LinkedIn - Messages")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    db = open_sqlite_db_readonly(str(files_found[0]))
    cursor = db.cursor()
    cursor.execute('''
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
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  LinkedIn - Messages")
        description = f"Messages from the LinkedIn App."
        report = ArtifactHtmlReport('LinkedIn - Messages')
        report.start_artifact_report(report_folder, 'LinkedIn - Messages', description)
        report.add_script()
        data_headers = ('Delivery Date', 'Delivery Status', 'Sender First Name', 'Sender Last Name', 'Sender Headline', 'Sender Profile Url', 'Sender Distance', 'Message', 'Conversation Urn')
        data_list = []
        for row in all_rows:
            delivery_date = row[0]
            delivery_status = row[1]
            sender_firstname = row[2]
            sender_lastname = row[3]
            sender_headline = row[4]
            sender_profile_url = row[5]
            sender_distance = row[6]
            message = row[7]
            conversationurn = row[8]

            data_list.append((delivery_date, delivery_status, sender_firstname, sender_lastname, sender_headline, sender_profile_url, sender_distance, message, conversationurn))

        tableID = 'linkedin_messages'
 

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'LinkedIn - Messages'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'LinkedIn - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No LinkedIn Messages data found!')

    db.close()

def get_linkedin_conversations(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for LinkedIn - Conversations - Threaded Messages")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    db = open_sqlite_db_readonly(str(files_found[0]))
    df = pd.read_sql_query('''
        SELECT
		row_number() OVER(ORDER BY deliveredAt ASC) [message-id],
        deliveredAt [data-time],
        deliveryStatus,
        CONCAT (json_extract(serializedMessage, '$.sender.participantType.member.firstName.text'), ' ', 
		        json_extract(serializedMessage, '$.sender.participantType.member.lastName.text')) [Sender Name],
		CASE WHEN json_extract(serializedMessage, '$.sender.participantType.member.distance') = 'SELF'
        THEN 1
        ELSE 0
        END [from_me],
		json_extract(serializedMessage, '$.body.text') [message], 
		CASE WHEN json_extract(serializedConversation, '$.conversationParticipants[0].participantType.member.distance') = 'SELF'
        THEN CONCAT (json_extract(serializedConversation, '$.conversationParticipants[1].participantType.member.firstName.text'), ' ', 
		        json_extract(serializedConversation, '$.conversationParticipants[1].participantType.member.lastName.text'))
        ELSE CONCAT (json_extract(serializedConversation, '$.conversationParticipants[0].participantType.member.firstName.text'), ' ', 
		        json_extract(serializedConversation, '$.conversationParticipants[0].participantType.member.lastName.text'))
        END [data-name]
        FROM messages
		INNER JOIN conversations c on messages.conversationUrn = c.conversationUrn
    ''', db)

    usageentries = df.shape[0]
    if usageentries > 0:
        #data_list = df.to_records(index=False)
        logfunc(f"Found {usageentries}  LinkedIn - Conversations")
        description = f"LinkedIn conversations."
        report = ArtifactHtmlReport('LinkedIn - Conversations')
        report.start_artifact_report(report_folder, 'LinkedIn - Conversations', description)
        report.add_script()

        df["data-time"] = pd.to_datetime(df["data-time"], unit='ms')
        df["file-path"] = ''


        num_entries = df.shape[0]
        report.write_minor_header(f'Total number of entries: {num_entries}', 'h6')
    
        report.write_lead_text(f'LinkedIn Conversations (Threaded) located at: {files_found[0]}')
        report.write_raw_html(chat_HTML)
        report.add_script(render_chat(df))
        report.end_artifact_report()    

    else:
        logfunc('No LinkedIn - Conversations data found!')

    db.close()